from __future__ import annotations

import asyncio
import copy
import html
import logging
import re
import time
from difflib import SequenceMatcher
from typing import Any

import httpx

from app.core.config import get_settings


logger = logging.getLogger(__name__)

USPTO_SEARCH_URL = 'https://tmsearch.uspto.gov/prod-v1-0-0/tmsearch'
USPTO_TSDR_URL = 'https://tsdr.uspto.gov/#caseNumber=%s&caseSearchType=US_APPLICATION&caseType=DEFAULT&searchType=statusSearch'
USPTO_SOURCE_NAME = 'USPTO Trademark Search'

_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CACHE_LOCK = asyncio.Lock()

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


def _cache_key(query: str, limit: int) -> str:
    return f'{_normalize_mark(query)}:{limit}'


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_strip_highlight(item) for item in value if _strip_highlight(item)]
    text = _strip_highlight(value)
    return [text] if text else []


def build_wordmark_payload(query: str, limit: int = 10) -> dict[str, Any]:
    general_fields = ['goodsAndServices', 'markDescription', 'ownerName', 'translate', 'wordmark', 'wordmarkPseudoText']
    normalized_query = _normalize_mark(query)
    should = [
        {'query_string': {'query': f'{query}*', 'default_operator': 'AND', 'fields': general_fields}},
        {'term': {'WM': {'value': query, 'boost': 6}}},
        {'match_phrase': {'WMP5': {'query': query}}},
        {'query_string': {'query': query, 'default_operator': 'AND', 'fields': general_fields}},
        {'term': {'SN': {'value': query}}},
        {'term': {'RN': {'value': query}}},
    ]
    if len(normalized_query) >= 5:
        fuzzy_distance = 1 if len(normalized_query) <= 6 else 2
        should.append(
            {
                'query_string': {
                    'query': f'{normalized_query}~{fuzzy_distance}',
                    'default_operator': 'AND',
                    'fields': ['wordmark', 'wordmarkPseudoText'],
                }
            }
        )
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
    char_score = SequenceMatcher(None, normalized_query, normalized_mark).ratio()
    query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))
    mark_tokens = set(re.findall(r'[a-z0-9]+', wordmark.lower()))
    if not query_tokens or not mark_tokens:
        return round(char_score, 2)
    token_score = len(query_tokens & mark_tokens) / len(query_tokens | mark_tokens)
    return round(max(char_score, token_score), 2)


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


async def _get_cached_result(key: str) -> dict[str, Any] | None:
    now = time.monotonic()
    async with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if not cached:
            return None
        expires_at, value = cached
        if expires_at <= now:
            _CACHE.pop(key, None)
            return None
        result = copy.deepcopy(value)
        result['cached'] = True
        return result


async def _set_cached_result(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    async with _CACHE_LOCK:
        _CACHE[key] = (time.monotonic() + ttl_seconds, copy.deepcopy(value))


def _empty_result(query: str, status: str = 'empty') -> dict[str, Any]:
    return {
        'query': query,
        'total': 0,
        'hits': [],
        'source': USPTO_SOURCE_NAME,
        'sourceUrl': 'https://tmsearch.uspto.gov/',
        'lookupStatus': status,
        'cached': False,
    }


async def search_us_trademarks(query: str, limit: int = 10) -> dict[str, Any]:
    clean_query = query.strip()
    if not clean_query:
        return _empty_result(clean_query)
    settings = get_settings()
    if not settings.uspto_lookup_enabled:
        return _empty_result(clean_query, 'disabled')
    limit = max(1, min(limit, settings.uspto_max_results))
    key = _cache_key(clean_query, limit)
    cached_result = await _get_cached_result(key)
    if cached_result is not None:
        return cached_result

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Origin': 'https://tmsearch.uspto.gov',
        'Referer': 'https://tmsearch.uspto.gov/',
    }
    body: dict[str, Any] | None = None
    async with httpx.AsyncClient(timeout=settings.uspto_timeout_seconds, headers=headers) as client:
        for attempt in range(2):
            try:
                response = await client.post(USPTO_SEARCH_URL, json=build_wordmark_payload(clean_query, limit))
                if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                    await asyncio.sleep(0.6)
                    continue
                response.raise_for_status()
                body = response.json()
                break
            except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
                if attempt == 1:
                    logger.exception('USPTO lookup failed for query %s', clean_query)
                    raise
                await asyncio.sleep(0.6)
    if body is None:
        return _empty_result(clean_query, 'failed')

    hits = body.get('hits') or {}
    raw_hits = hits.get('hits') or []
    normalized_hits = [_normalize_hit(hit, clean_query) for hit in raw_hits]
    normalized_hits.sort(key=lambda item: (item['alive'], item['similarity'], item['score']), reverse=True)
    result = {
        'query': clean_query,
        'total': int(hits.get('totalValue') or 0),
        'hits': normalized_hits,
        'source': USPTO_SOURCE_NAME,
        'sourceUrl': 'https://tmsearch.uspto.gov/',
        'lookupStatus': 'ok',
        'cached': False,
    }
    await _set_cached_result(key, result, settings.uspto_cache_ttl_seconds)
    return result
