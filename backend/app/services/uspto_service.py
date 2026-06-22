from __future__ import annotations

import html
import re
from typing import Any

import httpx


USPTO_SEARCH_URL = 'https://tmsearch.uspto.gov/prod-v1-0-0/tmsearch'
USPTO_TSDR_URL = 'https://tsdr.uspto.gov/#caseNumber=%s&caseSearchType=US_APPLICATION&caseType=DEFAULT&searchType=statusSearch'

_SOURCE_FIELDS = [
    'abandonDate',
    'alive',
    'attorney',
    'cancelDate',
    'coordinatedClass',
    'currentBasis',
    'designCodeDescription',
    'disclaimer',
    'drawingCode',
    'filedDate',
    'goodsAndServices',
    'id',
    'internationalClass',
    'markDescription',
    'markType',
    'originalBasis',
    'ownerFullText',
    'ownerName',
    'ownerType',
    'priorityDate',
    'publishForOppositionDate',
    'registrationDate',
    'registrationId',
    'registrationType',
    'supplementalRegistrationDate',
    'translation',
    'usClass',
    'wordmark',
    'wordmarkPseudoText',
]

_HIGHLIGHT_FIELDS = {
    key: {}
    for key in [
        'abandonDate',
        'attorney',
        'alive',
        'cancelDate',
        'coordinatedClass',
        'currentBasis',
        'drawingCode',
        'designCodeDescription',
        'disclaimer',
        'filedDate',
        'goodsAndServices',
        'id',
        'internationalClass',
        'markDescription',
        'markType',
        'originalBasis',
        'ownerFullText',
        'ownerName',
        'ownerType',
        'priorityDate',
        'publishForOppositionDate',
        'registrationDate',
        'registrationId',
        'registrationType',
        'supplementalRegistrationDate',
        'translation',
        'usClass',
        'wordmarkPseudoText',
    ]
}


def is_us_market(market: str | None) -> bool:
    value = (market or '').strip().lower()
    return value in {'us', 'usa', 'u.s.', 'u.s.a.', 'united states', 'america', '美国', '美國'}


def _strip_highlight(value: Any) -> str:
    if value is None:
        return ''
    text = value if isinstance(value, str) else str(value)
    text = re.sub(r'</?em>', '', text)
    return html.unescape(text).strip()


def _normalize_mark(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_strip_highlight(item) for item in value if _strip_highlight(item)]
    text = _strip_highlight(value)
    return [text] if text else []


def build_wordmark_payload(query: str, limit: int = 10) -> dict[str, Any]:
    general_fields = ['goodsAndServices', 'markDescription', 'ownerName', 'translate', 'wordmark', 'wordmarkPseudoText']
    should = [
        {'query_string': {'query': f'{query}*', 'default_operator': 'AND', 'fields': general_fields}},
        {'term': {'WM': {'value': query, 'boost': 6}}},
        {'match_phrase': {'WMP5': {'query': query}}},
        {'query_string': {'query': query, 'default_operator': 'AND', 'fields': general_fields}},
        {'term': {'SN': {'value': query}}},
        {'term': {'RN': {'value': query}}},
    ]
    return {
        'query': {'bool': {'must': [{'bool': {'should': should}}]}},
        'size': limit,
        'from': 0,
        'track_total_hits': True,
        '_source': _SOURCE_FIELDS,
        'aggs': {
            'alive': {'terms': {'field': 'alive'}},
            'cancelDate': {'value_count': {'field': 'cancelDate'}},
        },
        'highlight': {
            'fields': _HIGHLIGHT_FIELDS,
            'pre_tags': ['<em>'],
            'post_tags': ['</em>'],
            'number_of_fragments': 0,
        },
        'min_score': 8,
    }


def _similarity(query: str, wordmark: str) -> float:
    normalized_query = _normalize_mark(query)
    normalized_mark = _normalize_mark(wordmark)
    if not normalized_query or not normalized_mark:
        return 0
    if normalized_query == normalized_mark:
        return 0.98
    if normalized_query in normalized_mark or normalized_mark in normalized_query:
        return 0.86
    query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))
    mark_tokens = set(re.findall(r'[a-z0-9]+', wordmark.lower()))
    if not query_tokens or not mark_tokens:
        return 0.45
    return round(len(query_tokens & mark_tokens) / len(query_tokens | mark_tokens), 2)


def _normalize_hit(hit: dict[str, Any], query: str) -> dict[str, Any]:
    source = hit.get('source') or hit.get('_source') or {}
    serial = _strip_highlight(source.get('id') or hit.get('id'))
    wordmark = _strip_highlight(source.get('wordmark') or '')
    goods = [
        item.replace('(ABANDONED) ', '').replace('(CANCELLED) ', '')
        for item in _as_list(source.get('goodsAndServices'))
    ]
    owner_names = _as_list(source.get('ownerName'))
    classes = _as_list(source.get('internationalClass'))
    registration_id = _strip_highlight(source.get('registrationId') or '')
    alive = bool(source.get('alive'))
    return {
        'serialNumber': serial,
        'wordmark': wordmark or serial,
        'status': 'Live' if alive else 'Dead',
        'alive': alive,
        'registrationNumber': registration_id,
        'owner': owner_names[0] if owner_names else 'Unknown',
        'classes': classes,
        'goodsAndServices': goods[:5],
        'filedDate': _strip_highlight(source.get('filedDate') or ''),
        'registrationDate': _strip_highlight(source.get('registrationDate') or ''),
        'markType': _as_list(source.get('markType')),
        'designCodeDescription': _as_list(source.get('designCodeDescription')),
        'score': float(hit.get('score') or 0),
        'similarity': _similarity(query, wordmark),
        'detailUrl': USPTO_TSDR_URL % serial if serial else '',
    }


async def search_us_trademarks(query: str, limit: int = 10) -> dict[str, Any]:
    clean_query = query.strip()
    if not clean_query:
        return {'query': clean_query, 'total': 0, 'hits': []}
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Origin': 'https://tmsearch.uspto.gov',
        'Referer': 'https://tmsearch.uspto.gov/',
    }
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        response = await client.post(USPTO_SEARCH_URL, json=build_wordmark_payload(clean_query, limit))
        response.raise_for_status()
        body = response.json()
    hits = body.get('hits') or {}
    raw_hits = hits.get('hits') or []
    normalized_hits = [_normalize_hit(hit, clean_query) for hit in raw_hits]
    normalized_hits.sort(key=lambda item: (item['alive'], item['similarity'], item['score']), reverse=True)
    return {
        'query': clean_query,
        'total': int(hits.get('totalValue') or 0),
        'hits': normalized_hits,
        'source': 'USPTO Trademark Search',
        'sourceUrl': 'https://tmsearch.uspto.gov/',
    }
