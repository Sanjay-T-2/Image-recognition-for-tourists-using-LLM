import httpx

from ..config import get_settings
from ..models import Coordinates
from .http import get_json


async def road_route(origin: Coordinates, destination: Coordinates) -> tuple[float, float] | None:
    """Return (distance_km, duration_hours) for a driving route, if available."""
    settings = get_settings()
    if settings.offline:
        return None
    path = f"{origin.lon},{origin.lat};{destination.lon},{destination.lat}"
    try:
        data = await get_json(
            f"{settings.osrm_url}/route/v1/driving/{path}",
            {"overview": "false", "alternatives": "false"},
        )
    except (httpx.HTTPError, ValueError):
        return None
    routes = data.get("routes") or []
    if not routes:
        return None
    route = routes[0]
    return round(route["distance"] / 1000, 1), round(route["duration"] / 3600, 2)
