import json
import re

import httpx

from ..config import get_settings

PROMPT = (
    "You are a travel assistant. Identify the tourist place in this photo. "
    'Reply with JSON only: {"place": "<most specific place name>", '
    '"city": "<city>", "country": "<country>", "confidence": <0-1>, '
    '"summary": "<one sentence about the place>"}'
)


JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _parse(content: str) -> dict[str, object] | None:
    """Parse the model reply, tolerating markdown fences and stray prose."""
    match = JSON_BLOCK.search(content)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


class VisionResult:
    def __init__(self, place: str, confidence: float, summary: str, source: str) -> None:
        self.place = place
        self.confidence = confidence
        self.summary = summary
        self.source = source


async def identify_image(image_base64: str) -> VisionResult | None:
    """Identify a landmark from a base64 encoded image using an LLM.

    Returns None when no vision provider is configured or the call fails, so the
    caller can fall back to asking the user for a place name.
    """
    settings = get_settings()
    if not settings.vision_enabled:
        return None
    payload = {
        "model": settings.openai_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.vision_timeout) as client:
            response = await client.post(
                f"{settings.openai_base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, ValueError):
        return None
    parsed = _parse(content)
    if parsed is None:
        return None
    place = parsed.get("place")
    if not place:
        return None
    location = ", ".join(
        str(part) for part in [place, parsed.get("city"), parsed.get("country")] if part
    )
    try:
        confidence = float(parsed.get("confidence", 0.6))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        confidence = 0.6
    summary = parsed.get("summary", "")
    return VisionResult(
        place=location,
        confidence=max(0.0, min(1.0, confidence)),
        summary=str(summary) if summary else "",
        source="llm",
    )
