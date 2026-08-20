# AI Tourist Guide

Plan a trip from a **place name or a photo of a tourist spot**. The app identifies the place,
asks a few questions about your plan, then walks you through distance → transport → budget →
booking, with local history, attractions, hotels and emergency info alongside.

## What it does

1. **Identify** – type a destination or upload a photo. Photos are analysed by an LLM vision model
   when `OPENAI_API_KEY` is set; otherwise the app asks for the place name.
2. **Ask** – short follow-up questions (trip purpose, who is travelling, priority, spending style)
   that seed the rest of the plan.
3. **Distance** – straight-line and road distance from your location (typed city or browser
   geolocation) to the destination.
4. **Transport** – flight / train / bus / car / ferry options with cost range, duration, comfort and
   a recommendation that changes with the chosen trade-off: *low cost, high comfort, fewer days,
   more days / scenic*. Nearby bus stands, railway stations, airports and ferry terminals are listed
   for both ends of the journey.
5. **Budget** – pick days, dates, travellers and spending style to get an approximate **minimum**
   amount needed: accommodation, food, local transport at the destination, entry tickets, buffer and
   round-trip travel. Everything is editable and recalculates live.
6. **Book** – deep-links into the booking site for the selected mode (Google Flights, Skyscanner,
   MakeMyTrip, IRCTC, Trainline, RedBus, Zoomcar, Direct Ferries …) prefilled with your route.
7. **Know before you go** – history of the place, best places to visit, hotels with booking links,
   nearby hospitals with phone numbers and country emergency numbers.

## Data sources

No API key is required to run the app:

| Capability | Provider | Key needed |
| --- | --- | --- |
| Geocoding / reverse geocoding | OpenStreetMap Nominatim | no |
| Road distance & driving time | OSRM | no |
| Stations, airports, hospitals, hotels, attractions | Overpass API | no |
| History / summaries | Wikipedia REST | no |
| Photo → place identification | any OpenAI-compatible vision model | `OPENAI_API_KEY` (optional) |

If a provider is unreachable the app degrades gracefully; with `OFFLINE_MODE=1` it uses a small
built-in dataset so the whole flow still works without internet.

Fares and stay costs are **heuristic estimates** (a per-km/per-day model with a country cost index),
not live prices — the booking providers show the real numbers.

## Run it

```bash
# backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, proxies /api to the backend
```

## Configuration

Copy `backend/.env.example` and export what you need:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | – | enables photo identification |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | any OpenAI-compatible API (e.g. `https://openrouter.ai/api/v1`) |
| `OPENAI_MODEL` | `gpt-4o-mini` | vision model (e.g. `google/gemma-4-26b-a4b-it:free` on OpenRouter) |
| `VISION_TIMEOUT` | `90` | seconds to wait for the vision model |
| `OFFLINE_MODE` | `0` | `1` skips all network calls |
| `CORS_ORIGINS` | `http://localhost:5173` | comma-separated allowed origins |
| `CACHE_TTL_SECONDS` | `3600` | in-process response cache TTL |
| `NOMINATIM_URL` / `OSRM_URL` / `OVERPASS_URL` | public endpoints | self-hosted alternatives |

## Tests and checks

```bash
cd backend && OFFLINE_MODE=1 .venv/bin/python -m pytest -q
cd backend && .venv/bin/ruff check . && .venv/bin/mypy app
cd frontend && npm run typecheck && npm run lint && npm run build
```

## Layout

```
backend/app/routers   identify, travel (route + stay estimate), info endpoints
backend/app/services  geocoding, routing, overpass, wikipedia, vision, planner, booking links
frontend/src          step-by-step React UI (input → questions → plan → booking)
```
