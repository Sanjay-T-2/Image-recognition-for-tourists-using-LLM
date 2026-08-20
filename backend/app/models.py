from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

TransportMode = Literal["flight", "train", "bus", "car", "ferry"]
Preference = Literal["low_cost", "high_comfort", "fewer_days", "more_days", "balanced"]


class Coordinates(BaseModel):
    lat: float
    lon: float


class Place(BaseModel):
    name: str
    display_name: str
    lat: float
    lon: float
    country: str | None = None
    country_code: str | None = None
    category: str | None = None


class IdentifyRequest(BaseModel):
    query: str | None = None
    image_base64: str | None = None
    origin: str | None = None
    origin_coords: Coordinates | None = None


class FollowUpQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    multi: bool = False


class IdentifyResponse(BaseModel):
    destination: Place
    origin: Place | None = None
    source: Literal["text", "image"]
    confidence: float
    summary: str
    questions: list[FollowUpQuestion]


class TransportHub(BaseModel):
    name: str
    kind: Literal["bus_station", "railway_station", "airport", "ferry_terminal"]
    lat: float
    lon: float
    distance_km: float
    side: Literal["origin", "destination"]


class BookingLink(BaseModel):
    provider: str
    url: str


class TransportOption(BaseModel):
    mode: TransportMode
    label: str
    distance_km: float
    duration_hours: float
    cost_min: float
    cost_max: float
    currency: str
    comfort: int = Field(ge=1, le=5)
    notes: str
    recommended: bool = False
    booking: list[BookingLink] = []


class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    origin_label: str | None = None
    destination_label: str | None = None
    preference: Preference = "balanced"
    currency: str = "INR"


class RouteResponse(BaseModel):
    straight_line_km: float
    road_km: float | None = None
    road_duration_hours: float | None = None
    preference: Preference
    options: list[TransportOption]
    hubs: list[TransportHub]


class CostLine(BaseModel):
    label: str
    amount: float
    detail: str


class StayEstimateRequest(BaseModel):
    destination: Coordinates
    destination_label: str
    days: int = Field(ge=1, le=60)
    travellers: int = Field(default=1, ge=1, le=20)
    start_date: date | None = None
    style: Literal["budget", "standard", "premium"] = "standard"
    transport_cost: float = 0
    currency: str = "INR"


class StayEstimateResponse(BaseModel):
    currency: str
    days: int
    travellers: int
    start_date: date | None
    end_date: date | None
    minimum_total: float
    comfortable_total: float
    per_day_minimum: float
    breakdown: list[CostLine]
    tips: list[str]


class Hospital(BaseModel):
    name: str
    lat: float
    lon: float
    distance_km: float
    phone: str | None = None
    emergency: bool = False


class Hotel(BaseModel):
    name: str
    lat: float
    lon: float
    distance_km: float
    stars: str | None = None
    price_band: str
    booking_url: str


class Attraction(BaseModel):
    name: str
    kind: str
    lat: float
    lon: float
    distance_km: float


class DestinationInfo(BaseModel):
    place: Place
    history: str
    history_url: str | None = None
    attractions: list[Attraction]
    hotels: list[Hotel]
    hospitals: list[Hospital]
    emergency_numbers: dict[str, str]
