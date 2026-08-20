"""Small offline dataset used when network providers are unavailable.

Keeps the whole flow demoable without any API key or internet access.
"""

from ..models import Place

PLACES: dict[str, Place] = {
    "taj mahal": Place(
        name="Taj Mahal",
        display_name="Taj Mahal, Agra, Uttar Pradesh, India",
        lat=27.1751,
        lon=78.0421,
        country="India",
        country_code="in",
        category="monument",
    ),
    "agra": Place(
        name="Agra",
        display_name="Agra, Uttar Pradesh, India",
        lat=27.1767,
        lon=78.0081,
        country="India",
        country_code="in",
        category="city",
    ),
    "chennai": Place(
        name="Chennai",
        display_name="Chennai, Tamil Nadu, India",
        lat=13.0827,
        lon=80.2707,
        country="India",
        country_code="in",
        category="city",
    ),
    "coimbatore": Place(
        name="Coimbatore",
        display_name="Coimbatore, Tamil Nadu, India",
        lat=11.0168,
        lon=76.9558,
        country="India",
        country_code="in",
        category="city",
    ),
    "goa": Place(
        name="Goa",
        display_name="Goa, India",
        lat=15.2993,
        lon=74.1240,
        country="India",
        country_code="in",
        category="state",
    ),
    "jaipur": Place(
        name="Jaipur",
        display_name="Jaipur, Rajasthan, India",
        lat=26.9124,
        lon=75.7873,
        country="India",
        country_code="in",
        category="city",
    ),
    "manali": Place(
        name="Manali",
        display_name="Manali, Himachal Pradesh, India",
        lat=32.2432,
        lon=77.1892,
        country="India",
        country_code="in",
        category="town",
    ),
    "paris": Place(
        name="Paris",
        display_name="Paris, Île-de-France, France",
        lat=48.8566,
        lon=2.3522,
        country="France",
        country_code="fr",
        category="city",
    ),
    "eiffel tower": Place(
        name="Eiffel Tower",
        display_name="Eiffel Tower, Paris, France",
        lat=48.8584,
        lon=2.2945,
        country="France",
        country_code="fr",
        category="monument",
    ),
}

# ISO country code -> emergency service numbers.
EMERGENCY_NUMBERS: dict[str, dict[str, str]] = {
    "in": {"All emergencies": "112", "Ambulance": "108", "Police": "100", "Fire": "101"},
    "fr": {"All emergencies": "112", "Ambulance": "15", "Police": "17", "Fire": "18"},
    "us": {"All emergencies": "911"},
    "gb": {"All emergencies": "999", "Non-emergency medical": "111"},
    "ae": {"Police": "999", "Ambulance": "998", "Fire": "997"},
    "sg": {"Police": "999", "Ambulance / Fire": "995"},
    "au": {"All emergencies": "000"},
    "jp": {"Police": "110", "Ambulance / Fire": "119"},
}

DEFAULT_EMERGENCY = {"All emergencies": "112"}


def lookup(query: str) -> Place | None:
    return PLACES.get(query.strip().lower())


def emergency_numbers(country_code: str | None) -> dict[str, str]:
    if not country_code:
        return DEFAULT_EMERGENCY
    return EMERGENCY_NUMBERS.get(country_code.lower(), DEFAULT_EMERGENCY)
