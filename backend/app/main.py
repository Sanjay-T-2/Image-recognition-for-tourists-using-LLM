from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import identify, info, travel

app = FastAPI(
    title="AI Tourist Guide API",
    version="1.0.0",
    description="Plan a trip from a place name or photo: distance, transport, cost and local info.",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identify.router, prefix="/api")
app.include_router(travel.router, prefix="/api")
app.include_router(info.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "vision_enabled": settings.vision_enabled,
        "offline": settings.offline,
    }
