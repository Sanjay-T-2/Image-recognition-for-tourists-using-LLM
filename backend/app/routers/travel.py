from fastapi import APIRouter

from ..models import (
    Coordinates,
    RouteRequest,
    RouteResponse,
    StayEstimateRequest,
    StayEstimateResponse,
)
from ..services import geo, overpass, planner, routing

router = APIRouter(tags=["travel"])


@router.post("/route", response_model=RouteResponse)
async def route(request: RouteRequest) -> RouteResponse:
    """Distance, transport options with cost/time trade-offs and nearby hubs."""
    straight_km = round(
        geo.haversine_km(
            request.origin.lat,
            request.origin.lon,
            request.destination.lat,
            request.destination.lon,
        ),
        1,
    )
    road = await routing.road_route(request.origin, request.destination)
    road_km, road_hours = road if road else (None, None)

    options = planner.build_transport_options(
        straight_km=straight_km,
        road_km=road_km,
        road_hours=road_hours,
        origin_label=request.origin_label or "origin",
        destination_label=request.destination_label or "destination",
        preference=request.preference,
        currency=request.currency,
    )
    hubs = await overpass.nearby_hubs(request.origin, side="origin")
    hubs += await overpass.nearby_hubs(request.destination, side="destination")

    return RouteResponse(
        straight_line_km=straight_km,
        road_km=road_km,
        road_duration_hours=road_hours,
        preference=request.preference,
        options=options,
        hubs=hubs,
    )


@router.post("/stay-estimate", response_model=StayEstimateResponse)
async def stay_estimate(request: StayEstimateRequest) -> StayEstimateResponse:
    """Approximate minimum money needed on the ground for the chosen days."""
    place = await geo.reverse_geocode(request.destination.lat, request.destination.lon)
    return planner.estimate_stay(request, place.country_code if place else None)


@router.get("/currency")
async def currency(lat: float, lon: float) -> dict[str, str]:
    place = await geo.reverse_geocode(lat, lon)
    code = place.country_code if place else None
    return {"currency": planner.currency_for(code), "country_code": code or ""}


@router.get("/hubs")
async def hubs(lat: float, lon: float, side: str = "destination") -> dict:
    found = await overpass.nearby_hubs(Coordinates(lat=lat, lon=lon), side=side)
    return {"hubs": [hub.model_dump() for hub in found]}
