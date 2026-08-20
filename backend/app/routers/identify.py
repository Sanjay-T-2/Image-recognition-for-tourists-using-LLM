from fastapi import APIRouter, HTTPException

from ..models import FollowUpQuestion, IdentifyRequest, IdentifyResponse, Place
from ..services import geo, vision, wiki

router = APIRouter(tags=["identify"])


def _questions(destination: Place) -> list[FollowUpQuestion]:
    return [
        FollowUpQuestion(
            id="purpose",
            question=f"What kind of trip to {destination.name} are you planning?",
            options=["Sightseeing", "Pilgrimage", "Adventure", "Family holiday", "Work + leisure"],
        ),
        FollowUpQuestion(
            id="travellers",
            question="Who is travelling?",
            options=["Solo", "Couple", "Family with kids", "Friends group"],
        ),
        FollowUpQuestion(
            id="priority",
            question="What matters most for getting there?",
            options=[
                "Lowest cost",
                "Fastest route",
                "Most comfortable",
                "Scenic / more days on the way",
            ],
        ),
        FollowUpQuestion(
            id="style",
            question="What is your spending style at the destination?",
            options=["Budget", "Standard", "Premium"],
        ),
    ]


@router.post("/identify", response_model=IdentifyResponse)
async def identify(request: IdentifyRequest) -> IdentifyResponse:
    """Resolve a destination from a place name or a photo, then ask follow-ups."""
    source: str = "text"
    confidence = 0.9
    summary = ""
    query = (request.query or "").strip()

    # A typed place name is an explicit choice, so it wins over an attached photo.
    if request.image_base64 and not query:
        result = await vision.identify_image(request.image_base64)
        if result is None:
            raise HTTPException(
                status_code=422,
                detail="Photo analysis is unavailable right now. Type the place name instead.",
            )
        source = "image"
        query = result.place
        confidence = result.confidence
        summary = result.summary

    if not query:
        raise HTTPException(status_code=422, detail="Provide a place name or a photo.")

    destination = await geo.geocode(query)
    if destination is None:
        raise HTTPException(status_code=404, detail=f"Could not locate '{query}'.")

    origin: Place | None = None
    if request.origin_coords:
        origin = await geo.reverse_geocode(
            request.origin_coords.lat, request.origin_coords.lon
        ) or Place(
            name="Your location",
            display_name="Your location",
            lat=request.origin_coords.lat,
            lon=request.origin_coords.lon,
        )
    elif request.origin:
        origin = await geo.geocode(request.origin)

    if not summary:
        summary, _ = await wiki.summary(destination.name)
    if not summary:
        summary = f"{destination.display_name} is your selected destination."

    return IdentifyResponse(
        destination=destination,
        origin=origin,
        source=source,  # type: ignore[arg-type]
        confidence=confidence,
        summary=summary,
        questions=_questions(destination),
    )
