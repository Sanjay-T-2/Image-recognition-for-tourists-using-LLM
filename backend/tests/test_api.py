import os

os.environ.setdefault("OFFLINE_MODE", "1")

from datetime import date  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.models import StayEstimateRequest  # noqa: E402
from app.services import geo, planner  # noqa: E402

client = TestClient(app)


def test_health_reports_offline_mode():
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["offline"] is True


def test_haversine_known_distance():
    # Chennai -> Coimbatore is roughly 430 km in a straight line.
    km = geo.haversine_km(13.0827, 80.2707, 11.0168, 76.9558)
    assert 400 < km < 460


def test_identify_from_text_returns_questions():
    response = client.post("/api/identify", json={"query": "Taj Mahal", "origin": "Chennai"})
    assert response.status_code == 200
    body = response.json()
    assert body["destination"]["name"] == "Taj Mahal"
    assert body["origin"]["name"] == "Chennai"
    assert {q["id"] for q in body["questions"]} == {"purpose", "travellers", "priority", "style"}


def test_identify_without_query_or_image_is_rejected():
    assert client.post("/api/identify", json={}).status_code == 422


def test_identify_image_without_vision_provider_needs_text():
    response = client.post("/api/identify", json={"image_base64": "Zm9v"})
    assert response.status_code == 422


def test_identify_image_with_typed_query_is_reported_as_text():
    response = client.post(
        "/api/identify", json={"image_base64": "Zm9v", "query": "Taj Mahal", "origin": "Agra"}
    )
    assert response.status_code == 200
    assert response.json()["source"] == "text"


def test_route_offers_modes_and_marks_recommendation():
    response = client.post(
        "/api/route",
        json={
            "origin": {"lat": 13.0827, "lon": 80.2707},
            "destination": {"lat": 27.1751, "lon": 78.0421},
            "origin_label": "Chennai",
            "destination_label": "Taj Mahal",
            "preference": "low_cost",
        },
    )
    body = response.json()
    assert body["straight_line_km"] > 1500
    modes = [option["mode"] for option in body["options"]]
    assert "flight" in modes
    recommended = [o for o in body["options"] if o["recommended"]]
    assert len(recommended) == 1
    assert recommended[0]["cost_min"] == min(o["cost_min"] for o in body["options"])
    assert recommended[0]["booking"]


def test_preference_changes_recommendation():
    payload = {
        "origin": {"lat": 13.0827, "lon": 80.2707},
        "destination": {"lat": 11.0168, "lon": 76.9558},
        "origin_label": "Chennai",
        "destination_label": "Coimbatore",
    }
    fastest = client.post("/api/route", json={**payload, "preference": "fewer_days"}).json()
    cheapest = client.post("/api/route", json={**payload, "preference": "low_cost"}).json()
    fastest_pick = next(o for o in fastest["options"] if o["recommended"])
    cheapest_pick = next(o for o in cheapest["options"] if o["recommended"])
    assert fastest_pick["duration_hours"] <= cheapest_pick["duration_hours"]
    assert cheapest_pick["cost_min"] <= fastest_pick["cost_min"]


def test_stay_estimate_scales_with_days_and_travellers():
    one = planner.estimate_stay(
        StayEstimateRequest(
            destination={"lat": 27.1751, "lon": 78.0421},
            destination_label="Taj Mahal",
            days=2,
            travellers=1,
            start_date=date(2026, 1, 5),
        ),
        "in",
    )
    two = planner.estimate_stay(
        StayEstimateRequest(
            destination={"lat": 27.1751, "lon": 78.0421},
            destination_label="Taj Mahal",
            days=4,
            travellers=2,
        ),
        "in",
    )
    assert two.minimum_total > one.minimum_total
    assert one.end_date == date(2026, 1, 6)
    assert one.comfortable_total > one.minimum_total
    assert {line.label for line in one.breakdown} >= {"Accommodation", "Food"}


def test_stay_estimate_endpoint_includes_transport_round_trip():
    payload = {
        "destination": {"lat": 27.1751, "lon": 78.0421},
        "destination_label": "Taj Mahal",
        "days": 3,
        "travellers": 2,
        "style": "budget",
        "currency": "INR",
    }
    without = client.post("/api/stay-estimate", json=payload).json()
    with_transport = client.post(
        "/api/stay-estimate", json={**payload, "transport_cost": 5000}
    ).json()
    assert with_transport["minimum_total"] == without["minimum_total"] + 10000


def test_destination_info_falls_back_offline():
    response = client.get(
        "/api/destination-info", params={"lat": 27.1751, "lon": 78.0421, "name": "Taj Mahal"}
    )
    body = response.json()
    assert body["place"]["name"] == "Taj Mahal"
    assert body["emergency_numbers"]["All emergencies"] == "112"


def test_currency_defaults_by_country():
    assert planner.currency_for("in") == "INR"
    assert planner.currency_for("fr") == "EUR"
    assert planner.currency_for(None) == "INR"
