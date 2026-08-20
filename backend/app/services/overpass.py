import httpx

from ..config import get_settings
from ..models import Attraction, Coordinates, Hospital, Hotel, TransportHub
from .geo import haversine_km
from .http import post_form_json

HUB_QUERIES: dict[str, str] = {
    "airport": 'node["aeroway"="aerodrome"];way["aeroway"="aerodrome"];',
    "railway_station": 'node["railway"="station"];way["railway"="station"];',
    "bus_station": 'node["amenity"="bus_station"];way["amenity"="bus_station"];',
    "ferry_terminal": 'node["amenity"="ferry_terminal"];way["amenity"="ferry_terminal"];',
}

ATTRACTION_FILTER = (
    'node["tourism"~"attraction|museum|viewpoint|artwork|zoo|theme_park"];'
    'way["tourism"~"attraction|museum|viewpoint|zoo|theme_park"];'
    'node["historic"~"monument|castle|fort|memorial|ruins"];'
    'way["historic"~"monument|castle|fort|memorial|ruins"];'
)


def _build_query(filters: str, coords: Coordinates, radius_m: int) -> str:
    around = f"(around:{radius_m},{coords.lat},{coords.lon})"
    body = filters.replace(";", f"{around};").rstrip(";")
    return f"[out:json][timeout:25];({body};);out center 40;"


def _element_coords(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center")
    if center:
        return float(center["lat"]), float(center["lon"])
    return None


async def _query(filters: str, coords: Coordinates, radius_m: int) -> list[dict]:
    settings = get_settings()
    if settings.offline:
        return []
    try:
        data = await post_form_json(
            settings.overpass_url, {"data": _build_query(filters, coords, radius_m)}
        )
    except (httpx.HTTPError, ValueError):
        return []
    return data.get("elements", [])


async def nearby_hubs(
    coords: Coordinates, side: str, radius_km: int = 60, per_kind: int = 3
) -> list[TransportHub]:
    hubs: list[TransportHub] = []
    for kind, filters in HUB_QUERIES.items():
        elements = await _query(filters, coords, radius_km * 1000)
        found: list[TransportHub] = []
        for element in elements:
            point = _element_coords(element)
            name = (element.get("tags") or {}).get("name")
            if point is None or not name:
                continue
            found.append(
                TransportHub(
                    name=name,
                    kind=kind,  # type: ignore[arg-type]
                    lat=point[0],
                    lon=point[1],
                    distance_km=round(haversine_km(coords.lat, coords.lon, point[0], point[1]), 1),
                    side=side,  # type: ignore[arg-type]
                )
            )
        found.sort(key=lambda hub: hub.distance_km)
        hubs.extend(found[:per_kind])
    return hubs


async def nearby_hospitals(
    coords: Coordinates, radius_km: int = 15, limit: int = 8
) -> list[Hospital]:
    elements = await _query(
        'node["amenity"~"hospital|clinic"];way["amenity"~"hospital|clinic"];',
        coords,
        radius_km * 1000,
    )
    hospitals: list[Hospital] = []
    for element in elements:
        point = _element_coords(element)
        tags = element.get("tags") or {}
        if point is None or not tags.get("name"):
            continue
        hospitals.append(
            Hospital(
                name=tags["name"],
                lat=point[0],
                lon=point[1],
                distance_km=round(haversine_km(coords.lat, coords.lon, point[0], point[1]), 1),
                phone=tags.get("phone") or tags.get("contact:phone"),
                emergency=tags.get("emergency") == "yes" or tags.get("amenity") == "hospital",
            )
        )
    hospitals.sort(key=lambda item: (not item.emergency, item.distance_km))
    return hospitals[:limit]


PRICE_BANDS = {"hostel": "budget", "guest_house": "budget", "motel": "mid-range"}


async def nearby_hotels(coords: Coordinates, radius_km: int = 10, limit: int = 8) -> list[Hotel]:
    elements = await _query(
        'node["tourism"~"hotel|hostel|guest_house|motel|resort"];'
        'way["tourism"~"hotel|hostel|guest_house|motel|resort"];',
        coords,
        radius_km * 1000,
    )
    hotels: list[Hotel] = []
    for element in elements:
        point = _element_coords(element)
        tags = element.get("tags") or {}
        name = tags.get("name")
        if point is None or not name:
            continue
        tourism = tags.get("tourism", "hotel")
        stars = tags.get("stars")
        hotels.append(
            Hotel(
                name=name,
                lat=point[0],
                lon=point[1],
                distance_km=round(haversine_km(coords.lat, coords.lon, point[0], point[1]), 1),
                stars=stars,
                price_band=PRICE_BANDS.get(
                    tourism, "premium" if tourism == "resort" else "mid-range"
                ),
                booking_url=(
                    "https://www.booking.com/searchresults.html?ss=" + name.replace(" ", "+")
                ),
            )
        )
    hotels.sort(key=lambda item: item.distance_km)
    return hotels[:limit]


async def nearby_attractions(
    coords: Coordinates, radius_km: int = 20, limit: int = 12
) -> list[Attraction]:
    elements = await _query(ATTRACTION_FILTER, coords, radius_km * 1000)
    attractions: list[Attraction] = []
    seen: set[str] = set()
    for element in elements:
        point = _element_coords(element)
        tags = element.get("tags") or {}
        name = tags.get("name")
        if point is None or not name or name in seen:
            continue
        seen.add(name)
        attractions.append(
            Attraction(
                name=name,
                kind=tags.get("tourism") or tags.get("historic") or "attraction",
                lat=point[0],
                lon=point[1],
                distance_km=round(haversine_km(coords.lat, coords.lon, point[0], point[1]), 1),
            )
        )
    attractions.sort(key=lambda item: item.distance_km)
    return attractions[:limit]
