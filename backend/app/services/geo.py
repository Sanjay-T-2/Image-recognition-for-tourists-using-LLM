import math

import httpx

from ..config import get_settings
from ..models import Place
from . import offline_data
from .http import get_json

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _place_from_nominatim(item: dict) -> Place:
    address = item.get("address") or {}
    return Place(
        name=item.get("name") or item.get("display_name", "").split(",")[0],
        display_name=item.get("display_name", ""),
        lat=float(item["lat"]),
        lon=float(item["lon"]),
        country=address.get("country"),
        country_code=address.get("country_code"),
        category=item.get("type"),
    )


async def geocode(query: str) -> Place | None:
    """Resolve a free-text place name to coordinates."""
    settings = get_settings()
    if not settings.offline:
        try:
            data = await get_json(
                f"{settings.nominatim_url}/search",
                {
                    "q": query,
                    "format": "jsonv2",
                    "limit": 1,
                    "addressdetails": 1,
                },
            )
            if data:
                return _place_from_nominatim(data[0])
        except (httpx.HTTPError, ValueError, KeyError):
            pass
    return offline_data.lookup(query)


async def reverse_geocode(lat: float, lon: float) -> Place | None:
    settings = get_settings()
    if settings.offline:
        return None
    try:
        data = await get_json(
            f"{settings.nominatim_url}/reverse",
            {"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1},
        )
    except (httpx.HTTPError, ValueError):
        return None
    if not data or "lat" not in data:
        return None
    return _place_from_nominatim(data)
