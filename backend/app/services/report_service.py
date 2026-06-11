from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import Job, Report
from app.repositories import model_config_repository, report_repository

logger = logging.getLogger(__name__)


def _risk_level(score: int) -> str:
    if score >= 75:
        return 'high'
    if score >= 45:
        return 'medium'
    return 'low'


def _demo_score(job: Job) -> int:
    base = 45 + (len(job.brand) * 7 + len(job.market) * 3) % 45
    return min(base, 92)


def _fallback_report_payload(job: Job):
    score = _demo_score(job)
    risk_level = _risk_level(score)
    brand = job.brand.upper() or 'DRAFT BRAND'
    image_url = job.files[0].file_url if job.files else '/evidence/activewear.svg'
    return {
        'id': f'r-{job.id}',
        'jobId': job.id,
        'title': f'{brand} 知识产权风险预检报告',
        'riskLevel': risk_level,
        'riskScore': score,
        'summary': f'{brand} 在 {job.market} 市场的 {job.category} 类目存在{risk_level}级知识产权风险，当前报告为模型调用失败后的降级结果。',
        'categoryScores': [
            {'type': 'trademark', 'label': '商标', 'score': min(score + 5, 100), 'hits': 2 if score >= 60 else 1},
            {'type': 'design', 'label': '外观', 'score': max(score - 8, 0), 'hits': 1},
            {'type': 'copyright', 'label': '版权', 'score': max(score - 18, 0), 'hits': 0 if score < 75 else 1},
        ],
        'evidence': [
            {
                'id': f'ev-{job.id}',
                'category': job.type,
                'matched': brand,
                'source': 'Fallback IP Index',
                'similarity': round(score / 100, 2),
                'description': '模型调用失败时使用的降级报告，用于保证业务链路可用。',
                'imageUrl': image_url,
            }
        ],
        'suggestions': ['检查模型配置和 API Key。', '确认模型服务可访问。', '必要时重新运行检测任务。'],
    }


def _format_prompt(job: Job) -> str:
    return f'''你是跨境知识产权风险分析助手，请根据以下任务生成结构化 JSON 报告。

要求：
- 只返回 JSON，不要 Markdown，不要代码块，不要额外解释。
- JSON 必须包含字段：title, riskLevel, riskScore, summary, categoryScores, evidence, suggestions。
- categoryScores 为数组，每项包含 type, label, score, hits。
- evidence 为数组，每项包含 id, category, matched, source, similarity, description, imageUrl。
- riskLevel 只能是 high / medium / low。
- riskScore 0-100 的整数。
- suggestions 至少 3 条。

任务信息：
- 任务ID: {job.id}
- 品牌: {job.brand}
- 类目: {job.category}
- 市场: {job.market}
- 检测类型: {job.type}
- 标题: {job.title}
- 商品链接: {job.product_link}
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
    evidence = data.get('evidence') or [
        {
            'id': 'model-no-hit',
            'category': job.type,
            'matched': '',
            'source': 'model',
            'similarity': 0,
            'description': '模型未返回直接命中证据。',
            'imageUrl': job.files[0].file_url if job.files else '',
        }
    ]
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
        return existing
    try:
        data = asyncio.run(_call_model(db, job))
        payload = _build_report_payload(job, data)
    except Exception:
        logger.exception('model report generation failed for job %s, using fallback report', job.id)
        payload = _fallback_report_payload(job)
    return report_repository.create_report(db, payload)


def ensure_demo_report_for_job(db: Session, job: Job):
    existing = report_repository.get_report(db, job.id)
    if existing:
        return existing
    return report_repository.create_report(db, _fallback_report_payload(job))


def get_user_job_results(db: Session, job: Job):
    report = report_repository.get_report(db, job.id)
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
