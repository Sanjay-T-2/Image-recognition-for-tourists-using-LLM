import os
from functools import lru_cache
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_env_file(path: Path = ENV_FILE) -> None:
    """Load KEY=VALUE lines from backend/.env without overriding real env vars."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


class Settings:
    """Runtime configuration.

    Every external dependency is optional: when a key is missing the matching
    service degrades to a deterministic offline implementation so the app still
    runs end to end.
    """

    def __init__(self) -> None:
        load_env_file()
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url: str = os.getenv(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/")
        self.nominatim_url: str = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org")
        self.osrm_url: str = os.getenv("OSRM_URL", "https://router.project-osrm.org")
        self.overpass_url: str = os.getenv(
            "OVERPASS_URL", "https://overpass-api.de/api/interpreter"
        )
        self.wikipedia_url: str = os.getenv("WIKIPEDIA_URL", "https://en.wikipedia.org/api/rest_v1")
        self.user_agent: str = os.getenv(
            "HTTP_USER_AGENT", "ai-tourist-guide/1.0 (https://github.com)"
        )
        self.request_timeout: float = float(os.getenv("HTTP_TIMEOUT", "20"))
        self.vision_timeout: float = float(os.getenv("VISION_TIMEOUT", "90"))
        self.offline: bool = os.getenv("OFFLINE_MODE", "0") == "1"
        self.cache_ttl: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        self.cors_origins: list[str] = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ]

    @property
    def vision_enabled(self) -> bool:
        return bool(self.openai_api_key) and not self.offline


@lru_cache
def get_settings() -> Settings:
    return Settings()
