from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.base import Evidence, Job, Report
from app.repositories import model_config_repository, report_repository
from app.services.uspto_service import USPTO_SOURCE_NAME, is_us_market, search_us_trademarks

logger = logging.getLogger(__name__)


def _risk_level(score: int) -> str:
    if score >= 75:
        return 'high'
    if score >= 45:
        return 'medium'
    return 'low'


def _demo_score(job: Job) -> int:
    seed = '|'.join([
        job.title or '',
        job.brand or '',
        job.category or '',
        job.market or '',
        job.product_link or '',
        ','.join(file.filename for file in job.files),
    ])
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return 38 + (int(digest[:8], 16) % 55)


def _category_scores_from_product(job: Job, score: int):
    text = f'{job.title} {job.brand} {job.category}'.lower()
    trademark_bias = 12 if any(token in text for token in ('logo', '品牌', '商标', '联名', '同款')) else 0
    design_bias = 14 if any(token in text for token in ('外观', '造型', '包装', '鞋', '包', '玩具', '饰品')) else 0
    copyright_bias = 14 if any(token in text for token in ('图片', '图案', '文案', '角色', '素材', '海报')) else 0
    return [
        {'type': 'trademark', 'label': '商标近似', 'score': min(score + trademark_bias, 100), 'hits': 1 if score + trademark_bias >= 55 else 0},
        {'type': 'design', 'label': '外观相似', 'score': min(max(score - 8 + design_bias, 0), 100), 'hits': 1 if score - 8 + design_bias >= 55 else 0},
        {'type': 'copyright', 'label': '版权素材', 'score': min(max(score - 16 + copyright_bias, 0), 100), 'hits': 1 if score - 16 + copyright_bias >= 55 else 0},
    ]


def _fallback_report_payload(job: Job):
    score = _demo_score(job)
    risk_level = _risk_level(score)
    product_name = job.title.strip() or job.brand.strip() or '当前商品'
    category = job.category if job.category and job.category != 'auto' else '未明确类目'
    market = job.market if job.market and job.market != 'global' else '目标市场'
    return {
        'id': f'r-{job.id}',
        'jobId': job.id,
        'title': f'{product_name} 上架风险预检报告',
        'riskLevel': risk_level,
        'riskScore': score,
        'summary': f'本次资料围绕“{product_name}”进行预检，当前可识别类目为{category}，面向{market}。系统根据商品描述、上传资料和默认检测方向生成降级判断；建议在正式上架前重点确认分项风险较高的内容。',
        'categoryScores': _category_scores_from_product(job, score),
        'evidence': [],
        'suggestions': [
            f'先核对“{product_name}”中出现的品牌词、Logo 或联名表达，避免让买家误以为与他人品牌有关。',
            f'如果商品图片或包装造型是核心卖点，建议把{category}同类热销商品和目标市场公开外观记录做一次人工比对。',
            '详情页图片、图案和文案尽量使用自有素材；来源不清的素材先替换或补充授权证明。',
        ],
    }


_PLACEHOLDER_BRANDS = {'', '待识别品牌', '未明确品牌', 'auto', 'unknown', 'n/a', 'na'}
_SEARCH_STOPWORDS = {
    'amazon',
    'shein',
    'target',
    'platform',
    'product',
    'listing',
    'shop',
    'store',
    'free',
    'test',
}


def _clean_search_term(value: str) -> str:
    text = re.sub(r'https?://\S+', ' ', value)
    text = re.sub(r'目标平台[:：].*', ' ', text)
    text = re.sub(r'平台[:：].*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip(' -_　')
    return text[:80]


def _us_official_search_term(job: Job) -> str:
    brand = _clean_search_term(job.brand or '')
    if brand.lower() not in _PLACEHOLDER_BRANDS:
        return brand

    title = _clean_search_term(job.title or '')
    english_terms = re.findall(r'[A-Za-z][A-Za-z0-9&\'-]{2,}', title)
    brand_like_terms = [term for term in english_terms if term.lower() not in _SEARCH_STOPWORDS]
    if brand_like_terms:
        return brand_like_terms[0]
    return title


def _status_label(hit: dict[str, Any]) -> str:
    return '有效/存续' if hit.get('alive') else '已失效或终止'


def _truncate_text(value: str, limit: int = 240) -> str:
    text = re.sub(r'\s+', ' ', value).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip(' ,;；') + '...'


def _format_hit_brief(hit: dict[str, Any]) -> str:
    classes = '、'.join(hit.get('classes') or []) or '未列明类别'
    registration = hit.get('registrationNumber') or '暂无注册号'
    goods = _truncate_text('；'.join((hit.get('goodsAndServices') or [])[:2]) or 'USPTO 未展示商品/服务摘要')
    return (
        f'序列号 {hit["serialNumber"]}，注册号 {registration}，状态{_status_label(hit)}，'
        f'权利人 {hit["owner"]}，类别 {classes}，商品/服务：{goods}'
    )


def _uspto_hit_score(hit: dict[str, Any]) -> int:
    similarity = float(hit.get('similarity') or 0)
    alive = bool(hit.get('alive'))
    registered = bool(hit.get('registrationNumber'))
    if alive and similarity >= 0.96:
        score = 88
    elif alive and similarity >= 0.8:
        score = 78
    elif alive and similarity >= 0.45:
        score = 66
    elif similarity >= 0.96:
        score = 58
    elif similarity >= 0.8:
        score = 50
    else:
        score = 42
    if alive and registered:
        score += 4
    return min(score, 96)


def _uspto_evidence_id(job: Job, suffix: str | int) -> str:
    job_hash = hashlib.sha1(job.id.encode('utf-8')).hexdigest()[:12]
    clean_suffix = re.sub(r'[^a-zA-Z0-9_-]+', '-', str(suffix)).strip('-') or 'item'
    return f'uspto-{job_hash}-{clean_suffix}'[:64]


def _build_uspto_report_payload(job: Job, result: dict[str, Any], min_similarity: float) -> dict[str, Any] | None:
    hits = result.get('hits') or []
    relevant_hits = [hit for hit in hits if float(hit.get('similarity') or 0) >= min_similarity]
    if not relevant_hits:
        return None

    top_hits = relevant_hits[:3]
    top_hit = top_hits[0]
    score = min(_uspto_hit_score(top_hit) + min(len(relevant_hits) - 1, 6), 98)
    risk_level = _risk_level(score)
    product_name = job.title.strip() or job.brand.strip() or result['query']
    classes = '、'.join(top_hit.get('classes') or []) or '未列明类别'
    design_score = 42 if any(hit.get('designCodeDescription') for hit in top_hits) else 24
    copyright_score = 18
    summary = (
        f'结论：不建议直接用“{result["query"]}”作为美国站商品品牌名、标题核心词或 Logo 展示。'
        f'系统已查询 USPTO 美国官方商标数据库，发现与“{result["query"]}”高度相关的官方记录；'
        f'最相关命中为“{top_hit["wordmark"]}”，状态为{_status_label(top_hit)}，类别覆盖 {classes}。'
    )
    if risk_level == 'high':
        summary += ' 这意味着买家或平台可能会把你的商品与已有商标权利人产生关联，直接上架存在较高商标投诉或下架风险。'
    elif risk_level == 'medium':
        summary += ' 该命中需要结合商品类目、页面展示位置和是否作为品牌使用进一步确认。'
    else:
        summary += ' 当前官方命中关联度不高，但仍建议在最终上架前确认品牌词和页面素材来源。'

    return {
        'id': f'r-{job.id}',
        'jobId': job.id,
        'title': f'{product_name} 美国商标官方预检报告',
        'riskLevel': risk_level,
        'riskScore': score,
        'summary': summary,
        'categoryScores': [
            {'type': 'trademark', 'label': '商标近似', 'score': score, 'hits': len(relevant_hits)},
            {'type': 'design', 'label': '外观相似', 'score': design_score, 'hits': 1 if design_score >= 45 else 0},
            {'type': 'copyright', 'label': '版权素材', 'score': copyright_score, 'hits': 0},
        ],
        'evidence': [
            {
                'id': _uspto_evidence_id(job, hit["serialNumber"] or index),
                'category': 'trademark',
                'matched': hit['wordmark'],
                'source': USPTO_SOURCE_NAME,
                'similarity': hit['similarity'],
                'description': _format_hit_brief(hit),
                'imageUrl': '',
            }
            for index, hit in enumerate(top_hits, start=1)
        ],
        'suggestions': [
            f'如果“{result["query"]}”不是你的自有商标或授权品牌，建议不要把它放在标题开头、主图 Logo、包装正面或店铺品牌位。',
            f'重点比对 USPTO 命中的商品/服务类别（{classes}）与当前商品类目是否接近；类目越接近，上架风险越高。',
            '如果你有授权或正规采购链路，先准备授权书、采购发票、品牌使用许可等材料，再考虑上架。',
            '如果没有授权，建议更换品牌词和包装展示，再重新做一次美国商标检测。',
        ],
    }


def _build_uspto_no_hit_evidence(job: Job, result: dict[str, Any], min_similarity: float) -> dict[str, Any] | None:
    if result.get('lookupStatus') != 'ok':
        return None
    query = result.get('query') or _us_official_search_term(job)
    if not query:
        return None
    weak_hits = [
        hit['wordmark']
        for hit in (result.get('hits') or [])[:3]
        if float(hit.get('similarity') or 0) < min_similarity
    ]
    weak_text = f' USPTO 返回的弱相关记录包括：{"、".join(weak_hits)}。' if weak_hits else ''
    return {
        'id': _uspto_evidence_id(job, 'no-hit'),
        'category': 'trademark',
        'matched': f'{query}（未发现明确命中）',
        'source': USPTO_SOURCE_NAME,
        'similarity': 0,
        'description': (
            f'已查询 USPTO 美国官方商标数据库，搜索词“{query}”未发现名称相似度达到 '
            f'{int(min_similarity * 100)}% 的明确商标命中。{weak_text}'
            '因此本报告继续使用智能预检判断，请结合品牌使用方式和商品类目复核。'
        ),
        'imageUrl': '',
    }


def _has_uspto_evidence(report: Report | None) -> bool:
    if not report:
        return False
    return any(USPTO_SOURCE_NAME in (item.source or '') for item in report.evidence)


def _has_uspto_positive_evidence(report: Report | None) -> bool:
    if not report:
        return False
    return any(USPTO_SOURCE_NAME in (item.source or '') and float(item.similarity or 0) > 0 for item in report.evidence)


async def _official_us_report_payload(job: Job) -> dict[str, Any] | None:
    if not is_us_market(job.market):
        return None
    query = _us_official_search_term(job)
    if not query:
        return None
    settings = get_settings()
    result = await search_us_trademarks(query, limit=settings.uspto_max_results)
    if result.get('lookupStatus') != 'ok':
        return None
    if not result.get('hits'):
        return None
    return _build_uspto_report_payload(job, result, settings.uspto_min_similarity)


async def _official_us_lookup(job: Job) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not is_us_market(job.market):
        return None, None
    query = _us_official_search_term(job)
    if not query:
        return None, None
    settings = get_settings()
    result = await search_us_trademarks(query, limit=settings.uspto_max_results)
    if result.get('lookupStatus') != 'ok':
        return None, None
    payload = _build_uspto_report_payload(job, result, settings.uspto_min_similarity)
    note = _build_uspto_no_hit_evidence(job, result, settings.uspto_min_similarity) if payload is None else None
    return payload, note


def _replace_existing_report(db: Session, existing: Report, payload: dict[str, Any]):
    db.delete(existing)
    db.commit()
    return report_repository.create_report(db, payload)


def _refresh_with_official_report_if_needed(db: Session, job: Job, existing: Report | None):
    if not existing or _has_uspto_positive_evidence(existing) or not is_us_market(job.market):
        return existing
    try:
        payload, note = asyncio.run(_official_us_lookup(job))
    except Exception:
        logger.exception('official report refresh failed for job %s', job.id)
        return existing
    if payload is not None:
        return _replace_existing_report(db, existing, payload)
    if note is not None and not _has_uspto_evidence(existing):
        existing.evidence.append(Evidence(report_id=existing.id, **{
            'id': note['id'],
            'category': note['category'],
            'matched': note['matched'],
            'source': note['source'],
            'similarity': note['similarity'],
            'description': note['description'],
            'image_url': note['imageUrl'],
        }))
        db.commit()
        db.refresh(existing)
    return existing


def _append_evidence(payload: dict[str, Any], item: dict[str, Any] | None) -> dict[str, Any]:
    if item is not None:
        payload.setdefault('evidence', []).append(item)
    return payload


def _format_prompt(job: Job) -> str:
    files = ', '.join(f'{file.filename} ({file.content_type or "unknown"}, {file.size} bytes)' for file in job.files) or '未上传图片'
    product_text = job.title.strip() or '用户未填写文字描述'
    product_link = job.product_link.strip() or '未提供'
    brand = job.brand.strip() or '未明确品牌'
    category = job.category.strip() or '未明确类目'
    market = job.market.strip() or '未明确市场'
    return f'''你是跨境电商上架前的知识产权风险预检助手。你的目标不是写模板报告，而是根据用户提交的具体商品资料，生成一份有差异、有判断、有下一步建议的 JSON 报告。

要求：
- 只返回 JSON，不要 Markdown，不要代码块，不要额外解释。
- JSON 必须包含字段：title, riskLevel, riskScore, summary, categoryScores, evidence, suggestions。
- title 必须包含具体商品名称或用户描述中的核心词，不要只写“知识产权风险报告”。
- summary 必须点名本次商品的关键元素，例如品牌词、Logo、图案、包装、外观、文案、使用场景或目标市场；不要写任何可以套用到所有商品的泛泛结论。
- categoryScores 必须恰好返回 3 项：商标近似、外观相似、版权素材。每项包含 type, label, score, hits；type 只能是 trademark / design / copyright。
- 每个分项分数必须根据商品资料差异化判断：品牌/Logo/联名表达影响商标；造型/包装/结构影响外观；图片/图案/角色/文案/素材来源影响版权。
- evidence 字段保留为兼容字段，但请返回空数组 []，不要编造命中证据。
- riskLevel 只能是 high / medium / low。
- riskScore 是 0-100 的整数，并且要和三个分项风险一致：整体高风险时至少一个分项应明显偏高。
- suggestions 返回 3-5 条，每条都必须针对本商品资料写下一步动作；不要出现“咨询专业人士”这类空泛建议，除非已经说明要核对什么资料。
- 如果用户只上传图片、文字很少，请明确说明“当前主要依据上传图片/文件名判断”，并把建议集中在图片可见元素、包装、Logo、图案和素材来源上。
- 如果资料不足，不要假装已经查到确切数据库命中；可以给低/中风险预检结论，并建议补充具体信息。

用户提交内容：
- 任务ID: {job.id}
- 用户文本/标题/描述: {product_text}
- 商品链接: {product_link}
- 上传图片/文件: {files}

后端兼容字段：
- 品牌: {brand}
- 类目: {category}
- 市场: {market}
- 默认检测类型: {job.type}
'''


def _parse_json_response(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError('model response must be an object')
    return data


def _normalize_evidence_items(job: Job, report_id: str, items: list[dict[str, Any]]):
    normalized = []
    seen_ids: set[str] = set()
    for index, item in enumerate(items, start=1):
        raw_id = str(item.get('id') or index)
        evidence_id = f'{report_id}-{raw_id}'
        if evidence_id in seen_ids:
            evidence_id = f'{report_id}-{index}'
        seen_ids.add(evidence_id)
        normalized.append({
            'id': evidence_id,
            'category': item.get('category') or job.type,
            'matched': str(item.get('matched') or ''),
            'source': item.get('source') or 'model',
            'similarity': float(item.get('similarity') or 0),
            'description': item.get('description') or '',
            'imageUrl': item.get('imageUrl') or '',
        })
    return normalized


def _build_report_payload(job: Job, data: dict[str, Any]):
    score = int(data.get('riskScore') or 0)
    risk_level = data.get('riskLevel') or _risk_level(score)
    title = data.get('title') or f'{job.brand.upper()} 知识产权风险预检报告'
    summary = data.get('summary') or f'{job.brand} 在 {job.market} 市场的 {job.category} 类目存在{risk_level}级知识产权风险。'
    category_scores = data.get('categoryScores') or []
    evidence = data.get('evidence') or []
    suggestions = data.get('suggestions') or []
    if not category_scores:
        raise ValueError('model response missing categoryScores')
    return {
        'id': f'r-{job.id}',
        'jobId': job.id,
        'title': title,
        'riskLevel': risk_level,
        'riskScore': score,
        'summary': summary,
        'categoryScores': category_scores,
        'evidence': _normalize_evidence_items(job, f'r-{job.id}', evidence),
        'suggestions': suggestions,
    }


def _model_url(base_url: str, provider: str) -> str:
    root = base_url.rstrip('/')
    if provider == 'anthropic':
        return f"{root}/messages" if root.endswith('/v1') else f"{root}/v1/messages"
    return f"{root}/chat/completions" if root.endswith('/v1') else f"{root}/v1/chat/completions"


def _openai_token_field(model_name: str, max_tokens: int) -> dict[str, int]:
    if model_name.lower().startswith(('gpt-5', 'o1', 'o3')):
        return {'max_completion_tokens': max_tokens}
    return {'max_tokens': max_tokens}


async def _call_openai_model(config, job: Job) -> dict[str, Any]:
    headers = {'content-type': 'application/json'}
    if config.api_key:
        headers['authorization'] = f'Bearer {config.api_key}'
    payload = {
        'model': config.model_name,
        'messages': [
            {'role': 'system', 'content': '你是专业的跨境知识产权风险分析助手。'},
            {'role': 'user', 'content': _format_prompt(job)},
        ],
        'temperature': config.temperature,
        **_openai_token_field(config.model_name, config.max_tokens),
    }
    print(f'[model] request provider=openai job_id={job.id} url={_model_url(config.base_url, "openai")} payload={payload}', flush=True)
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(_model_url(config.base_url, 'openai'), headers=headers, json=payload)
        response.raise_for_status()
        print(f'[model] raw provider=openai job_id={job.id} body={response.text}', flush=True)
        logger.info('openai raw response for job %s: %s', job.id, response.text)
        body = response.json()
    choice = body['choices'][0]
    content = choice.get('message', {}).get('content') or choice.get('text', '')
    print(f'[model] parsed provider=openai job_id={job.id} content={content}', flush=True)
    logger.info('openai parsed content for job %s: %s', job.id, content)
    return _parse_json_response(content)


async def _call_anthropic_model(config, job: Job) -> dict[str, Any]:
    headers = {
        'content-type': 'application/json',
        'x-api-key': config.api_key,
        'anthropic-version': '2023-06-01',
    }
    if config.api_key:
        headers['authorization'] = f'Bearer {config.api_key}'
    payload = {
        'model': config.model_name,
        'max_tokens': config.max_tokens,
        'temperature': config.temperature,
        'messages': [
            {'role': 'user', 'content': _format_prompt(job)},
        ],
    }
    print(f'[model] request provider=anthropic job_id={job.id} url={_model_url(config.base_url, "anthropic")} payload={payload}', flush=True)
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(_model_url(config.base_url, 'anthropic'), headers=headers, json=payload)
        response.raise_for_status()
        print(f'[model] raw provider=anthropic job_id={job.id} body={response.text}', flush=True)
        logger.info('anthropic raw response for job %s: %s', job.id, response.text)
        body = response.json()
    content = ''.join(block.get('text', '') for block in body.get('content', []) if isinstance(block, dict))
    print(f'[model] parsed provider=anthropic job_id={job.id} content={content}', flush=True)
    logger.info('anthropic parsed content for job %s: %s', job.id, content)
    return _parse_json_response(content)


async def _call_model_once(config, job: Job, provider: str) -> dict[str, Any]:
    if provider == 'anthropic':
        return await _call_anthropic_model(config, job)
    return await _call_openai_model(config, job)


def _preferred_provider_order(config) -> list[str]:
    provider = (config.provider or 'openai').lower()
    base_url = (config.base_url or '').lower()
    if any(token in base_url for token in ('newapi', 'anthropic')):
        return ['anthropic', 'openai'] if provider != 'anthropic' else ['anthropic', 'openai']
    if provider == 'anthropic':
        return ['anthropic', 'openai']
    return ['openai', 'anthropic']


async def _call_model(db: Session, job: Job) -> dict[str, Any]:
    config = model_config_repository.get_model_config(db)
    if not config or not config.enabled:
        raise RuntimeError('model config unavailable')
    last_error: Exception | None = None
    for provider in _preferred_provider_order(config):
        try:
            return await _call_model_once(config, job, provider)
        except Exception as exc:
            last_error = exc
            logger.exception('model call failed for provider %s', provider)
    if last_error:
        raise last_error
    raise RuntimeError('model call failed')


def generate_report_for_job(db: Session, job: Job):
    existing = report_repository.get_report(db, job.id)
    if existing:
        return _refresh_with_official_report_if_needed(db, job, existing)
    payload = None
    official_note = None
    try:
        payload, official_note = asyncio.run(_official_us_lookup(job))
    except Exception:
        logger.exception('official source lookup failed for job %s, falling back to model', job.id)
    if payload is None:
        try:
            data = asyncio.run(_call_model(db, job))
            payload = _append_evidence(_build_report_payload(job, data), official_note)
        except Exception:
            logger.exception('model report generation failed for job %s, using fallback report', job.id)
            payload = _append_evidence(_fallback_report_payload(job), official_note)
    return report_repository.create_report(db, payload)


def ensure_demo_report_for_job(db: Session, job: Job):
    existing = report_repository.get_report(db, job.id)
    if existing:
        return existing
    return report_repository.create_report(db, _fallback_report_payload(job))


def get_user_job_results(db: Session, job: Job):
    report = report_repository.get_report(db, job.id)
    report = _refresh_with_official_report_if_needed(db, job, report)
    return report_repository.report_to_dict(report) if report else None


def get_user_report(db: Session, report_id: str, user):
    report = report_repository.get_report(db, report_id)
    if not report or not report.job or report.job.owner_id != user.id:
        return None
    return report_repository.report_to_dict(report)


def list_user_reports(db: Session, user):
    query = (
        select(Report)
        .join(Report.job)
        .options(selectinload(Report.category_scores), selectinload(Report.evidence), selectinload(Report.job))
        .where(Job.owner_id == user.id)
        .order_by(Report.generated_at.desc())
    )
    return [report_repository.report_to_dict(report) for report in db.scalars(query).all()]
