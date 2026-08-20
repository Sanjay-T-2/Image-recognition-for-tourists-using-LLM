import time
from typing import Any

import httpx

from ..config import get_settings

_cache: dict[str, tuple[float, Any]] = {}


def cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if expires_at < time.time():
        _cache.pop(key, None)
        return None
    return value


def cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.time() + get_settings().cache_ttl, value)


def cache_clear() -> None:
    _cache.clear()


async def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    settings = get_settings()
    key = f"GET {url} {sorted((params or {}).items())}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.get(url, params=params, headers={"User-Agent": settings.user_agent})
        response.raise_for_status()
        data = response.json()
    cache_set(key, data)
    return data


async def post_form_json(url: str, data: dict[str, Any]) -> Any:
    settings = get_settings()
    key = f"POST {url} {sorted(data.items())}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.post(url, data=data, headers={"User-Agent": settings.user_agent})
        response.raise_for_status()
        payload = response.json()
    cache_set(key, payload)
    return payload
