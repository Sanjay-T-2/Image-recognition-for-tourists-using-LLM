"""Heuristic trip planning: transport options and on-the-ground stay costs.

All money is modelled in INR and converted with static reference rates; the
numbers are deliberately presented as ranges because they are estimates, not
live fares.
"""

from datetime import timedelta

from ..models import (
    CostLine,
    Preference,
    StayEstimateRequest,
    StayEstimateResponse,
    TransportMode,
    TransportOption,
)
from . import booking

INR_PER_UNIT: dict[str, float] = {
    "INR": 1.0,
    "USD": 83.0,
    "EUR": 90.0,
    "GBP": 105.0,
    "AED": 22.6,
    "SGD": 61.0,
}

CURRENCY_BY_COUNTRY: dict[str, str] = {
    "in": "INR",
    "us": "USD",
    "fr": "EUR",
    "de": "EUR",
    "it": "EUR",
    "es": "EUR",
    "gb": "GBP",
    "ae": "AED",
    "sg": "SGD",
}

# Rough purchasing-power multiplier applied to the INR baseline.
COST_INDEX: dict[str, float] = {
    "in": 1.0,
    "np": 0.9,
    "lk": 1.0,
    "th": 1.4,
    "ae": 2.6,
    "sg": 3.0,
    "gb": 3.4,
    "us": 3.6,
    "fr": 3.2,
    "de": 3.0,
    "jp": 3.0,
    "au": 3.4,
}

STYLE_BASE_INR: dict[str, dict[str, float]] = {
    # per person per day, India baseline
    "budget": {"stay": 800, "food": 500, "local_transport": 250, "activities": 200},
    "standard": {"stay": 2200, "food": 1000, "local_transport": 500, "activities": 500},
    "premium": {"stay": 6000, "food": 2500, "local_transport": 1500, "activities": 1500},
}


def currency_for(country_code: str | None) -> str:
    return CURRENCY_BY_COUNTRY.get((country_code or "").lower(), "INR")


def convert_from_inr(amount_inr: float, currency: str) -> float:
    rate = INR_PER_UNIT.get(currency.upper(), 1.0)
    value = amount_inr / rate
    return round(value, 0 if currency.upper() == "INR" else 2)


def cost_index(country_code: str | None) -> float:
    return COST_INDEX.get((country_code or "").lower(), 1.6)


# mode -> (cost per km INR, avg speed km/h, fixed overhead hours, comfort)
MODE_PROFILE: dict[TransportMode, tuple[float, float, float, int]] = {
    "flight": (5.5, 700, 3.5, 4),
    "train": (1.1, 65, 1.2, 3),
    "bus": (1.4, 45, 0.7, 2),
    "car": (9.0, 55, 0.4, 4),
    "ferry": (3.0, 35, 1.5, 3),
}

MODE_NOTES: dict[TransportMode, str] = {
    "flight": "Fastest option; book 3-4 weeks ahead for the lower end of the range.",
    "train": "Best value for overnight journeys; sleeper vs AC changes the fare a lot.",
    "bus": "Cheapest for medium distances, but the slowest and least comfortable.",
    "car": "Full flexibility and stops on the way; cost shown is fuel plus tolls "
    "for the car, not per person.",
    "ferry": "Scenic water crossing, limited daily departures.",
}


def _available_modes(distance_km: float, has_road_route: bool) -> list[TransportMode]:
    modes: list[TransportMode] = []
    if distance_km >= 250:
        modes.append("flight")
    if has_road_route and distance_km <= 3000:
        modes.append("train")
    if has_road_route and distance_km <= 1200:
        modes.append("bus")
    if has_road_route and distance_km <= 2000:
        modes.append("car")
    if not has_road_route and distance_km <= 800:
        modes.append("ferry")
    if not modes:
        modes.append("flight")
    return modes


def _pick_recommended(
    options: list[TransportOption], preference: Preference
) -> TransportOption | None:
    if not options:
        return None
    if preference == "low_cost":
        return min(options, key=lambda o: o.cost_min)
    if preference == "high_comfort":
        return max(options, key=lambda o: (o.comfort, -o.duration_hours))
    if preference == "fewer_days":
        return min(options, key=lambda o: o.duration_hours)
    if preference == "more_days":
        scenic = [o for o in options if o.mode in ("train", "car", "ferry")]
        return max(scenic or options, key=lambda o: o.duration_hours)
    return min(options, key=lambda o: o.cost_min * 0.6 + o.duration_hours * 400)


def build_transport_options(
    straight_km: float,
    road_km: float | None,
    road_hours: float | None,
    origin_label: str,
    destination_label: str,
    preference: Preference,
    currency: str,
) -> list[TransportOption]:
    has_road_route = road_km is not None
    options: list[TransportOption] = []
    for mode in _available_modes(straight_km, has_road_route):
        per_km, speed, overhead, comfort = MODE_PROFILE[mode]
        if mode == "flight":
            distance = round(straight_km * 1.05, 1)
        else:
            distance = round(road_km or straight_km * 1.25, 1)
        if mode == "car" and road_hours:
            duration = round(road_hours + overhead, 2)
        else:
            duration = round(distance / speed + overhead, 2)
        base_inr = distance * per_km
        if mode == "flight":
            base_inr = max(base_inr, 2500)
        cost_min = convert_from_inr(base_inr * 0.8, currency)
        cost_max = convert_from_inr(base_inr * 1.6, currency)
        options.append(
            TransportOption(
                mode=mode,
                label=mode.capitalize(),
                distance_km=distance,
                duration_hours=duration,
                cost_min=cost_min,
                cost_max=cost_max,
                currency=currency,
                comfort=comfort,
                notes=MODE_NOTES[mode],
                booking=booking.links_for(mode, origin_label, destination_label),
            )
        )
    recommended = _pick_recommended(options, preference)
    if recommended is not None:
        recommended.recommended = True
    options.sort(key=lambda o: (not o.recommended, o.cost_min))
    return options


def estimate_stay(request: StayEstimateRequest, country_code: str | None) -> StayEstimateResponse:
    index = cost_index(country_code)
    base = STYLE_BASE_INR[request.style]
    days = request.days
    people = request.travellers
    nights = max(days - 1, 1)

    stay_inr = base["stay"] * index * nights * max(1, (people + 1) // 2)
    food_inr = base["food"] * index * days * people
    local_inr = base["local_transport"] * index * days * people
    activity_inr = base["activities"] * index * days * people
    buffer_inr = (stay_inr + food_inr + local_inr + activity_inr) * 0.1

    currency = request.currency
    breakdown = [
        CostLine(
            label="Accommodation",
            amount=convert_from_inr(stay_inr, currency),
            detail=f"{nights} night(s), {request.style} rooms for {people} traveller(s)",
        ),
        CostLine(
            label="Food",
            amount=convert_from_inr(food_inr, currency),
            detail=f"3 meals/day x {days} day(s) x {people} traveller(s)",
        ),
        CostLine(
            label="Local transport at destination",
            amount=convert_from_inr(local_inr, currency),
            detail="Autos, cabs and day trips around the destination",
        ),
        CostLine(
            label="Entry tickets & activities",
            amount=convert_from_inr(activity_inr, currency),
            detail="Monument entry, guides and experiences",
        ),
        CostLine(
            label="Buffer (10%)",
            amount=convert_from_inr(buffer_inr, currency),
            detail="Shopping, tips and unplanned expenses",
        ),
    ]
    on_ground_inr = stay_inr + food_inr + local_inr + activity_inr + buffer_inr
    transport_inr = request.transport_cost * INR_PER_UNIT.get(currency.upper(), 1.0)
    if request.transport_cost:
        breakdown.append(
            CostLine(
                label="Travel to and from destination",
                amount=round(request.transport_cost, 2),
                detail="Selected transport mode, round trip estimate",
            )
        )
        transport_inr *= 2

    minimum_inr = on_ground_inr + transport_inr
    end_date = request.start_date + timedelta(days=days - 1) if request.start_date else None
    return StayEstimateResponse(
        currency=currency,
        days=days,
        travellers=people,
        start_date=request.start_date,
        end_date=end_date,
        minimum_total=convert_from_inr(minimum_inr, currency),
        comfortable_total=convert_from_inr(minimum_inr * 1.45, currency),
        per_day_minimum=convert_from_inr(minimum_inr / days, currency),
        breakdown=breakdown,
        tips=[
            "Booking stays and long-distance tickets 3+ weeks ahead usually cuts "
            "20-30% off these numbers.",
            "Eating where locals eat instead of hotel restaurants typically halves the food line.",
            "Weekday travel is cheaper than weekends and public holidays at most destinations.",
        ],
    )
