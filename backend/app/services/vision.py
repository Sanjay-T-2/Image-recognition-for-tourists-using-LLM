import json

import httpx

from ..config import get_settings

PROMPT = (
    "You are a travel assistant. Identify the tourist place in this photo. "
    'Reply with JSON only: {"place": "<most specific place name>", '
    '"city": "<city>", "country": "<country>", "confidence": <0-1>, '
    '"summary": "<one sentence about the place>"}'
)


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
        "response_format": {"type": "json_object"},
        "max_tokens": 300,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (httpx.HTTPError, KeyError, ValueError):
        return None
    place = parsed.get("place")
    if not place:
        return None
    location = ", ".join(
        part for part in [place, parsed.get("city"), parsed.get("country")] if part
    )
    return VisionResult(
        place=location,
        confidence=float(parsed.get("confidence", 0.6)),
        summary=parsed.get("summary", ""),
        source="llm",
    )
