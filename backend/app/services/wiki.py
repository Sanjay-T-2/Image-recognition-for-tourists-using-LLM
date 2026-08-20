import urllib.parse

import httpx

from ..config import get_settings
from .http import get_json


async def summary(title: str) -> tuple[str, str | None]:
    """Return (history/description text, source url) for a place."""
    settings = get_settings()
    if settings.offline:
        return ("", None)
    slug = urllib.parse.quote(title.replace(" ", "_"), safe="")
    try:
        data = await get_json(f"{settings.wikipedia_url}/page/summary/{slug}")
    except (httpx.HTTPError, ValueError):
        return ("", None)
    extract = data.get("extract") or ""
    url = (data.get("content_urls", {}).get("desktop", {}) or {}).get("page")
    return extract, url
