# CleanAir Companion 🍃

> **GenAI-powered assistant for families navigating severe winter smog and urban air pollution**  
> Primary region: Maharashtra, India (Pune / Mulshi) · Generalises to any city

---

## ✨ What it does

| Feature | Details |
|---|---|
| **Live AQI** | Fetches PM2.5, PM10, NO2, temperature inversion hints from OpenAQ / Open-Meteo (cached, fresh-labelled) |
| **Daily Plan** | AI-generated personalised plan: best outdoor windows, low-emission routines, indoor hacks |
| **Impact Cards** | Deterministic Python module computes PM2.5 exposure reduction (µg/m³·h) and CO2e avoided (kg) — LLM only explains, never invents |
| **Chat Assistant** | RAG-grounded Q&A on WHO/CPCB guidelines; refuses if ungrounded; escalates severe symptoms |
| **Community Mode** | Neighbourhood groups, collective impact dashboard, weekly challenges |
| **Alerts** | Push / WhatsApp / SMS abstraction for AQI threshold crossings and best-window reminders |
| **PWA / Offline** | Service worker caches last-known plan — works on 2G/3G |
| **i18n** | English, Hindi, Marathi (extensible) |
| **A11y** | WCAG AA — large-text mode, aria labels, keyboard navigation, voice input hook |

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy (async) · Alembic · Pydantic v2 |
| AI | Google Gemini API (Gemini 1.5 Pro / Flash, structured JSON outputs, function calling) · Google text-embedding-004 · Anthropic Claude (alternative provider) |
| RAG | pgvector HNSW index · cosine similarity |
| Frontend | Angular 18 · Angular Material · PWA / ngsw |
| DB | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis 7 · Celery |
| Auth | JWT (HS256) + anonymous mode |
| Infra | Docker Compose · Nginx |

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop ≥ 25
- API keys: Anthropic, OpenAI, OpenAQ (free tier)

### 1. Clone & configure
```bash
git clone https://github.com/your-org/cleanair-companion.git
cd cleanair-companion
cp .env.example .env
# Edit .env — fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, SECRET_KEY
```

### 2. Start services
```bash
docker compose up -d
```

### 3. Run migrations
```bash
docker compose exec backend alembic upgrade head
```

### 4. Seed knowledge base
```bash
# Place source documents in backend/knowledge_base/raw/ (see manifest in ingest.py)
docker compose exec backend python -m knowledge_base.scripts.ingest \
  --source-dir knowledge_base/raw
```

### 5. Open the app
- **Frontend PWA**: http://localhost:4200
- **API docs** (dev mode): http://localhost:8000/api/docs
- **Nginx proxy**: http://localhost:80

---

## 📂 Project Structure

```
cleanair-companion/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST endpoints: aqi, plan, chat, impact, community, alerts
│   │   ├── services/           # Business logic: AQI, impact, plan, RAG, chat, community, alert
│   │   │   └── impact/         # ⭐ Deterministic calculator — all numbers cited & unit-tested
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── schemas/            # Pydantic v2
│   │   └── prompts/            # LLM prompt templates with JSON output schemas
│   ├── alembic/versions/       # DB migrations incl. pgvector HNSW index
│   ├── knowledge_base/         # RAG source documents + ingestion pipeline
│   └── tests/                  # unit/ + integration/
├── frontend/
│   └── src/app/
│       ├── features/           # onboarding, dashboard, daily-plan, chat, community, alerts, settings
│       ├── core/               # services, guards, interceptors
│       └── shared/             # AQI badge, pipes, directives
├── infra/                      # Nginx, Redis config, Prometheus
└── docker-compose.yml
```

---

## 🔑 Key Design Decisions

### Safety & Guardrails
- **No LLM-invented numbers** — all PM2.5, CO2e, and health values are computed by the deterministic `ImpactCalculator` Python module; the LLM only writes explanatory text referencing these values
- **RAG refusal** — chat refuses to answer if no passage has similarity ≥ 0.72
- **Medical escalation** — severe symptom keywords trigger an immediate "see a doctor" response
- **Prompt injection protection** — `sanitizer.py` strips injection patterns from all user input and retrieved documents
- **Privacy by design** — location stored at ±1 km precision (2 decimal places)
- **Non-medical disclaimer** — injected on every response

### Emission Factors (all cited)
| Source | Used for |
|---|---|
| IPCC AR6 WG3 Table A.III.2 | Transport CO2e per km |
| ARAI India Vehicle EF 2019 | City-cycle PM2.5/NO2 per km |
| Chafe et al. 2015 (Lancet) | Cooking fuel PM2.5 emission rates |
| BEE India 2021 | Cooking sector CO2e |
| WHO AQG 2021 | Breathing rates, dose-response |
| CPCB AQI 2014/2021 | AQI categories and health tiers |

---

## 🧪 Running Tests

```bash
# Backend unit + integration tests
docker compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

# Run only impact calculator tests (fast, no DB needed)
docker compose exec backend pytest tests/unit/test_impact_calculator.py -v

# Run sanitizer tests
docker compose exec backend pytest tests/unit/test_sanitizer.py -v
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health/` | Health check |
| `POST` | `/api/v1/auth/register` | Register (email + password) |
| `POST` | `/api/v1/auth/login` | Login → JWT |
| `POST` | `/api/v1/auth/anonymous` | Anonymous session |
| `GET/POST/PATCH` | `/api/v1/profile/` | User lifestyle profile |
| `GET` | `/api/v1/aqi/?lat=&lon=` | Live AQI for location |
| `GET` | `/api/v1/aqi/category?aqi=` | CPCB AQI category |
| `GET` | `/api/v1/plan/today` | Generate today's plan |
| `POST` | `/api/v1/impact/commute` | Commute switch impact |
| `POST` | `/api/v1/impact/cooking` | Cooking fuel switch impact |
| `POST` | `/api/v1/impact/purifier` | Air purifier impact |
| `POST` | `/api/v1/chat/` | RAG-grounded chat |
| `GET/POST` | `/api/v1/community/` | Community groups |
| `GET/PATCH` | `/api/v1/alerts/` | Alert preferences |

---

## 🗄 Database Schema (summary)

```
users ──< user_profiles          (lifestyle, location, household)
users ──< daily_plans            (persisted plan snapshots)
         knowledge_chunks        (pgvector HNSW — RAG store)
         aqi_readings            (cached pollutant data)
users ──< community_members >── communities ──< challenges
users ──< alert_subscriptions ──< alert_deliveries
```

---

## 🔧 Environment Variables

See [`.env.example`](.env.example) for the full list. Minimum required:

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
SECRET_KEY=<64-char hex>
POSTGRES_PASSWORD=<strong-password>
```

---

## 📦 Knowledge Base

Place source documents in `backend/knowledge_base/raw/`. See the manifest in  
`backend/knowledge_base/scripts/ingest.py` for the expected filenames and metadata.

Recommended sources to obtain and place:
- `who_aqg_2021_summary.md` — WHO AQG 2021 key guidance
- `cpcb_aqi_categories.md` — CPCB AQI health categories
- `indoor_air_quality_guide.md` — WHO household guidelines
- `cooking_fuels_health.md` — Household cooking and health
- `mask_selection_guide.md` — N95/P100 mask guidance
- `maharashtra_smog_advisory.md` — Local winter advisory

Run ingestion:
```bash
python -m knowledge_base.scripts.ingest --source-dir knowledge_base/raw
```

---

## 🌍 Extending to Other Cities

1. Set user profile `city`, `state`, `country`
2. The AQI service uses GPS coordinates → automatically finds nearest OpenAQ station
3. Add local knowledge base documents to `knowledge_base/raw/` with `source_type: "local"`
4. The impact calculator uses generic emission factors — city-specific factors can be added to `emission_factors.py`

---

## 📋 Roadmap

- [ ] Voice input (Web Speech API integration)
- [ ] CPCB Sameer App API direct integration
- [ ] iOS / Android native wrapper (Capacitor)
- [ ] Hyperlocal AQI interpolation (kriging)
- [ ] Personalised emission factor calibration from commute telemetry
- [ ] Multi-language LLM responses (Claude natively supports Hindi/Marathi)

---

## ⚠️ Disclaimer

This application provides **general air quality guidance only**. It is **not a substitute for professional medical advice**. Always consult a qualified doctor for health concerns. Data is sourced from public APIs and may not reflect real-time conditions at your exact location.

---

## 📄 License

MIT License — see LICENSE file.

