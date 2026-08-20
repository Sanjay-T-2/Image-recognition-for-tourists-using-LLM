import urllib.parse

from ..models import BookingLink, TransportMode

PROVIDERS: dict[TransportMode, list[tuple[str, str]]] = {
    "flight": [
        (
            "Google Flights",
            "https://www.google.com/travel/flights?q=Flights%20to%20{to}%20from%20{from}",
        ),
        ("Skyscanner", "https://www.skyscanner.net/transport/flights/?query={to}"),
        ("MakeMyTrip", "https://www.makemytrip.com/flights/"),
    ],
    "train": [
        ("IRCTC", "https://www.irctc.co.in/nget/train-search"),
        ("Trainline", "https://www.thetrainline.com/en/train-times/{from}-to-{to}"),
        ("RailYatri", "https://www.railyatri.in/trains-between-stations"),
    ],
    "bus": [
        ("RedBus", "https://www.redbus.in/search?fromCityName={from}&toCityName={to}"),
        ("AbhiBus", "https://www.abhibus.com/"),
        ("FlixBus", "https://www.flixbus.com/"),
    ],
    "car": [
        ("Zoomcar", "https://www.zoomcar.com/"),
        ("Google Maps route", "https://www.google.com/maps/dir/{from}/{to}"),
    ],
    "ferry": [
        ("Direct Ferries", "https://www.directferries.com/"),
        ("Google Maps route", "https://www.google.com/maps/dir/{from}/{to}"),
    ],
}


def links_for(mode: TransportMode, origin: str, destination: str) -> list[BookingLink]:
    quoted_from = urllib.parse.quote(origin)
    quoted_to = urllib.parse.quote(destination)
    return [
        BookingLink(
            provider=provider,
            url=template.replace("{from}", quoted_from).replace("{to}", quoted_to),
        )
        for provider, template in PROVIDERS.get(mode, [])
    ]
