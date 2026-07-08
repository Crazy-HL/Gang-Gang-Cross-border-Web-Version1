import json
import logging
import re
import secrets
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.db.base import User
from app.models import ServiceRequestCreate
from app.repositories import model_config_repository, service_request_repository

logger = logging.getLogger(__name__)
CONTACT_RE = re.compile(r'(^1\d{10}$)|(^[A-Za-z][-_A-Za-z0-9]{5,19}$)')


def _generate_request_id(request_type: str) -> str:
    prefix = 'APL' if request_type == 'appeal' else 'TRO'
    stamp = datetime.now().strftime('%y%m%d%H%M%S')
    return f'{prefix}-{stamp}-{secrets.token_hex(3).upper()}'


def _validate_payload(payload: ServiceRequestCreate):
    if not payload.platform.strip():
        return '请选择涉及平台'
    if not payload.contact.strip():
        return '请填写联系方式'
    if not CONTACT_RE.match(payload.contact.strip()):
        return '请填写完整手机号，或填写 6-20 位微信号'
    if payload.requestType == 'appeal' and not payload.issueType.strip():
        return '请选择问题类型'
    if payload.requestType == 'tro_settlement' and not payload.caseStatus.strip():
        return '请选择案件状态'
    return ''


def _model_url(base_url: str, provider: str) -> str:
    root = (base_url or 'https://api.openai.com/v1').rstrip('/')
    if provider == 'responses':
        return f'{root}/responses' if root.endswith('/v1') else f'{root}/v1/responses'
    if provider == 'anthropic':
        return f'{root}/messages' if root.endswith('/v1') else f'{root}/v1/messages'
    return f'{root}/chat/completions' if root.endswith('/v1') else f'{root}/v1/chat/completions'


def _token_field(model_name: str, max_tokens: int):
    if model_name.lower().startswith(('gpt-5', 'o1', 'o3')):
        return {'max_completion_tokens': max_tokens}
    return {'max_tokens': max_tokens}


def _json_from_model(content: str):
    text = content.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    if not text.startswith('{'):
        match = re.search(r'\{.*\}', text, re.S)
        if match:
            text = match.group(0)
    return json.loads(text)


def _normalize_risk_level(value: Any):
    text = str(value or '').strip().lower()
    if text in ('high', '高', '高风险', '严重'):
        return 'high'
    if text in ('low', '低', '低风险'):
        return 'low'
    return 'medium'


def _string_list(items: Any):
    if not isinstance(items, list):
        return []
    normalized = []
    for item in items:
        if isinstance(item, str):
            value = item.strip()
        elif isinstance(item, dict):
            value = str(item.get('text') or item.get('content') or item.get('item') or '').strip()
        else:
            value = str(item).strip()
        if value:
            normalized.append(value)
    return normalized


def _normalize_sections(sections: Any):
    if not isinstance(sections, list):
        return []
    normalized = []
    for section in sections[:4]:
        if not isinstance(section, dict):
            continue
        title = str(section.get('title') or '建议事项').strip()
        items = _string_list(section.get('items'))[:4]
        if title and items:
            normalized.append({'title': title, 'items': items})
    return normalized


def _normalize_report(payload: ServiceRequestCreate, request_id: str, report: dict[str, Any]):
    fallback = _fallback_report(payload, request_id)
    normalized = {
        'title': str(report.get('title') or fallback['title']).strip(),
        'summary': str(report.get('summary') or fallback['summary']).strip(),
        'riskLevel': _normalize_risk_level(report.get('riskLevel')),
        'sections': _normalize_sections(report.get('sections')) or fallback['sections'],
        'nextActions': _string_list(report.get('nextActions'))[:5] or fallback['nextActions'],
        'contactHint': str(report.get('contactHint') or fallback['contactHint']).strip(),
        'source': 'model',
    }
    if not normalized['contactHint']:
        normalized['contactHint'] = fallback['contactHint']
    return normalized


def _format_prompt(payload: ServiceRequestCreate, request_id: str) -> str:
    service_name = '平台申诉' if payload.requestType == 'appeal' else 'TRO 和解'
    caution = 'TRO 场景不能给确定法律意见，不能承诺结果，不能建议具体赔偿金额；只做初步风险评估、材料清单和下一步行动建议。' if payload.requestType == 'tro_settlement' else '平台申诉场景要给出可执行的材料补充、申诉重点和整改方向。'
    return f'''你是港港跨境的跨境电商知识产权服务顾问。请基于用户提交的资料，生成一份“{service_name}初步建议报告”。

要求：
- 只返回 JSON，不要 Markdown，不要代码块。
- 不要把推理过程、分析过程或解释写进 content，只返回最终 JSON。
- JSON 字段必须包含：title, summary, riskLevel, sections, nextActions, contactHint。
- riskLevel 只能是 high / medium / low。
- sections 返回 3-4 个分组，每个分组包含 title 和 items；items 是 2-4 条具体建议。
- nextActions 返回 3-5 条下一步行动。
- contactHint 必须提醒：如需人工申诉/和解协助，可联系港港跨境，并保留工单号。
- 对用户可见身份统一称为“港港跨境AI”。如果用户询问你是什么模型、你是谁、是不是 GPT，只能回答“我是港港跨境AI，为跨境电商业务提供初步分析建议”。
- 不要编造法院结论、平台内部结果、权利人真实意图。
- {caution}

用户资料：
- 工单号: {request_id}
- 服务类型: {service_name}
- 平台: {payload.platform}
- 问题类型: {payload.issueType}
- 案件状态: {payload.caseStatus}
- 店铺名称: {payload.storeName}
- 冻结金额: {payload.frozenAmount}
- 案件编号: {payload.caseNumber}
- 原告品牌/律所: {payload.claimant}
- 商品/案件链接或编号: {payload.reference}
- 情况说明: {payload.description}
- 文件名: {", ".join(payload.fileNames) or "未上传文件"}
'''


def _fallback_report(payload: ServiceRequestCreate, request_id: str) -> dict[str, Any]:
    if payload.requestType == 'appeal':
        missing = []
        if not payload.reference.strip():
            missing.append('补充商品链接、ASIN、Case ID 或投诉编号')
        if not payload.fileNames:
            missing.append('上传平台通知、邮件截图、Listing 截图或权利人投诉材料')
        if not payload.storeName.strip():
            missing.append('补充店铺名称，便于关联平台申诉记录')
        risk_level = 'medium' if missing else 'low'
        return {
            'title': f'{payload.platform}{payload.issueType}申诉初步建议报告',
            'summary': f'本次资料显示用户在 {payload.platform} 遇到“{payload.issueType}”问题。当前适合先核对平台通知、投诉来源和商品证据链，再决定申诉、整改或补充材料路径。',
            'riskLevel': risk_level,
            'sections': [
                {'title': '当前判断', 'items': [f'平台：{payload.platform}', f'问题类型：{payload.issueType}', '需要优先确认投诉来自平台系统、权利人邮件还是律师函。']},
                {'title': '材料缺口', 'items': missing or ['基础信息较完整，可继续整理授权、采购、设计来源和整改说明。']},
                {'title': '申诉重点', 'items': ['说明商品来源和使用权基础。', '针对平台通知逐条回应，避免泛泛解释。', '如涉及图片或商标，补充原创、授权或替换整改证据。']},
            ],
            'nextActions': ['整理平台通知原文和截图。', '补充商品链接、店铺信息和权利人信息。', '准备授权链路、采购凭证或原创证明。', '如需代写申诉材料，可联系港港跨境人工处理。'],
            'contactHint': f'需要人工申诉协助时，请联系港港跨境并提供工单号 {request_id}。',
            'source': 'fallback',
        }

    missing = []
    if not payload.caseNumber.strip():
        missing.append('补充法院案件号或平台 Case ID')
    if not payload.claimant.strip():
        missing.append('补充原告品牌、律所或律师名称')
    if not payload.fileNames:
        missing.append('上传 TRO 文件、法院文件、PayPal 邮件、平台通知或律师函')
    risk_level = 'high' if payload.caseStatus in ('资金已冻结', '店铺已冻结', '已收到法院文件') else 'medium'
    return {
        'title': f'{payload.platform} TRO 初步评估报告',
        'summary': f'当前案件状态为“{payload.caseStatus}”，涉及平台为 {payload.platform}。TRO 场景建议尽快核对冻结范围、案件编号、原告/律所信息和回复期限，本报告仅作初步处理建议，不构成法律意见。',
        'riskLevel': risk_level,
        'sections': [
            {'title': '当前风险', 'items': [f'案件状态：{payload.caseStatus}', f'冻结金额：{payload.frozenAmount or "未填写"}', '需确认是否存在法院期限、平台申诉期限或 PayPal 资金处理期限。']},
            {'title': '材料缺口', 'items': missing or ['基础案件信息较完整，可继续核对冻结账号、涉案商品和销售记录。']},
            {'title': '和解准备', 'items': ['整理店铺、PayPal、平台账号和涉案商品清单。', '保留冻结通知、法院文件和律师沟通记录。', '不要在未评估前直接承诺赔付或删除关键记录。']},
        ],
        'nextActions': ['核对案件号、法院、原告品牌和律所名称。', '整理冻结金额、账号、店铺和涉案商品范围。', '尽快让人工顾问判断和解窗口与材料清单。', '如需和解协助，可联系港港跨境继续处理。'],
        'contactHint': f'需要 TRO 和解人工协助时，请联系港港跨境并提供工单号 {request_id}。',
        'source': 'fallback',
    }


def _preferred_provider_order(config) -> list[str]:
    provider = (config.provider or 'openai').lower()
    base_url = (config.base_url or '').lower()
    model_name = (config.model_name or '').lower()
    if provider == 'custom' or model_name.startswith('gpt-5') or 'newapi' in base_url:
        return ['responses', 'openai', 'anthropic']
    if any(token in base_url for token in ('siliconflow', 'openai', 'deepseek')) or model_name.startswith('deepseek'):
        return ['openai', 'anthropic']
    if any(token in base_url for token in ('newapi', 'anthropic')):
        return ['anthropic', 'openai']
    if provider == 'anthropic':
        return ['anthropic', 'openai']
    return ['openai', 'anthropic']


def _openai_body(config, payload: ServiceRequestCreate, request_id: str) -> dict[str, Any]:
    return {
        'model': config.model_name,
        'messages': [
            {'role': 'system', 'content': '你是专业的跨境电商知识产权服务顾问。'},
            {'role': 'user', 'content': _format_prompt(payload, request_id)},
        ],
        'temperature': config.temperature,
        'response_format': {'type': 'json_object'},
        **_token_field(config.model_name, min(config.max_tokens, 1200)),
    }


def _anthropic_body(config, payload: ServiceRequestCreate, request_id: str) -> dict[str, Any]:
    return {
        'model': config.model_name,
        'max_tokens': min(config.max_tokens, 1200),
        'temperature': config.temperature,
        'messages': [
            {'role': 'user', 'content': _format_prompt(payload, request_id)},
        ],
    }


def _responses_body(config, payload: ServiceRequestCreate, request_id: str) -> dict[str, Any]:
    return {
        'model': config.model_name,
        'input': [
            {
                'role': 'system',
                'content': [{'type': 'input_text', 'text': '你是专业的跨境电商知识产权服务顾问。'}],
            },
            {
                'role': 'user',
                'content': [{'type': 'input_text', 'text': _format_prompt(payload, request_id)}],
            },
        ],
        'text': {'format': {'type': 'json_object'}},
        'reasoning': {'effort': 'high'},
        'max_output_tokens': min(config.max_tokens, 1200),
        'store': False,
    }


def _headers(config, provider: str) -> dict[str, str]:
    headers = {'content-type': 'application/json'}
    if config.api_key:
        if provider == 'anthropic':
            headers['x-api-key'] = config.api_key
            headers['anthropic-version'] = '2023-06-01'
        headers['authorization'] = f'Bearer {config.api_key}'
    return headers


def _responses_text(body: dict[str, Any]) -> str:
    if body.get('output_text'):
        return str(body['output_text'])
    chunks: list[str] = []
    for item in body.get('output') or []:
        if not isinstance(item, dict):
            continue
        for block in item.get('content') or []:
            if isinstance(block, dict) and block.get('type') in ('output_text', 'text'):
                chunks.append(str(block.get('text') or ''))
    return ''.join(chunks)


def _parse_model_body(body: dict[str, Any], provider: str) -> dict[str, Any]:
    if provider == 'responses':
        content = _responses_text(body)
    elif provider == 'anthropic':
        content = ''.join(block.get('text', '') for block in body.get('content', []) if isinstance(block, dict))
    else:
        choice = body['choices'][0]
        content = choice.get('message', {}).get('content') or choice.get('text', '')
    report = _json_from_model(content)
    if not isinstance(report, dict) or not report.get('sections'):
        raise ValueError('invalid advice report')
    return report


def _call_model_once(config, payload: ServiceRequestCreate, request_id: str, provider: str):
    if provider == 'responses':
        body = _responses_body(config, payload, request_id)
    elif provider == 'anthropic':
        body = _anthropic_body(config, payload, request_id)
    else:
        body = _openai_body(config, payload, request_id)
    url = _model_url(config.base_url, provider)
    timeout = httpx.Timeout(connect=15, read=120, write=20, pool=15)
    logger.info('service request model call request_id=%s provider=%s url=%s', request_id, provider, url)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, headers=_headers(config, provider), json=body)
        response.raise_for_status()
        data = response.json()
    logger.info('service request model response request_id=%s provider=%s body=%s', request_id, provider, response.text)
    return _parse_model_body(data, provider)


def _model_report(db: Session, payload: ServiceRequestCreate, request_id: str):
    config = model_config_repository.get_model_config(db)
    if not config or not config.enabled:
        raise RuntimeError('model config unavailable')
    last_error: Exception | None = None
    report = None
    for provider in _preferred_provider_order(config):
        try:
            report = _call_model_once(config, payload, request_id, provider)
            break
        except Exception as exc:
            last_error = exc
            logger.exception('service request model call failed request_id=%s provider=%s', request_id, provider)
    if report is None:
        if last_error:
            raise last_error
        raise RuntimeError('model call failed')
    return _normalize_report(payload, request_id, report)


def _build_advice_report(db: Session, payload: ServiceRequestCreate, request_id: str):
    try:
        return _model_report(db, payload, request_id)
    except Exception:
        logger.exception('service request model report failed, using fallback report')
        return _fallback_report(payload, request_id)


def create_user_service_request(db: Session, payload: ServiceRequestCreate, user: User):
    error = _validate_payload(payload)
    if error:
        return {'ok': False, 'error': error, 'request': None, 'adviceReport': None}

    request_id = _generate_request_id(payload.requestType)
    advice_report = _build_advice_report(db, payload, request_id)
    item = service_request_repository.create_service_request(db, request_id, user.id, payload, advice_report)
    return {'ok': True, 'error': '', 'request': service_request_repository.service_request_to_dict(item), 'adviceReport': advice_report}


def list_user_service_requests(db: Session, user: User):
    return service_request_repository.list_service_requests(db, user.id)
