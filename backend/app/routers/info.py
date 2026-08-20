import asyncio

from fastapi import APIRouter, HTTPException

from ..models import Coordinates, DestinationInfo, Place
from ..services import geo, offline_data, overpass, wiki

router = APIRouter(tags=["info"])


@router.get("/destination-info", response_model=DestinationInfo)
async def destination_info(lat: float, lon: float, name: str) -> DestinationInfo:
    """History, best places, hotels, hospitals and emergency numbers."""
    coords = Coordinates(lat=lat, lon=lon)
    resolved = await geo.reverse_geocode(lat, lon)
    place = resolved or Place(name=name, display_name=name, lat=lat, lon=lon)
    place.name = name or place.name

    history_task = wiki.summary(name)
    attractions_task = overpass.nearby_attractions(coords)
    hotels_task = overpass.nearby_hotels(coords)
    hospitals_task = overpass.nearby_hospitals(coords)
    (history, history_url), attractions, hotels, hospitals = await asyncio.gather(
        history_task, attractions_task, hotels_task, hospitals_task
    )

    if not history:
        history = (
            f"No encyclopedia entry was found for {name}. "
            "Check local tourism boards for its history."
        )

    return DestinationInfo(
        place=place,
        history=history,
        history_url=history_url,
        attractions=attractions,
        hotels=hotels,
        hospitals=hospitals,
        emergency_numbers=offline_data.emergency_numbers(place.country_code),
    )


@router.get("/geocode")
async def geocode(q: str) -> dict:
    place = await geo.geocode(q)
    if place is None:
        raise HTTPException(status_code=404, detail=f"Could not locate '{q}'.")
    return place.model_dump()
