# 🇮🇳 NLAMS — National Land Acquisition & Management System

> e-Governance platform digitizing India's land acquisition lifecycle end-to-end
> Built for **Smart India Hackathon (SIH)** — 48-hour demo

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui + Recharts + MapLibre GL JS + Framer Motion |
| Backend | FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 + JWT Auth |
| Database | PostgreSQL 15 + PostGIS |
| Infra | Docker Compose |

## ⚡ Quick Start

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set up PostgreSQL with PostGIS extension
# Update DATABASE_URL in .env

python -m app.seed  # Seed database
uvicorn app.main:app --reload  # Start on port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Start on port 5173
```

## 🔐 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| 🔑 Super Admin | rajesh@nlams.gov.in | password123 |
| 🏛️ State Authority | anil@odisha.gov.in | password123 |
| 📋 District Officer | suresh@khordha.gov.in | password123 |
| 🏗️ Agency | agency@nhai.gov.in | password123 |
| 📱 Field Officer | rahul.f@nlams.gov.in | password123 |
| 👤 Citizen | ganesh@email.com | password123 |

## 📋 Demo Script (5-Minute Pitch)

### 1. Login as Super Admin (1 min)
- Click "🔑 Super Admin" quick login button
- Show **National Dashboard** with real KPIs from Odisha (Khordha) data
- See parcel counts, area breakdown, ownership split, co-ownership distribution
- Shows "1 state onboarded" with real bhoomirashi land-record data

### 2. GIS Map (1 min)
- Navigate to GIS Map
- Show interactive MapLibre map centered on Khordha, Odisha
- Village-level markers with parcel counts (toggle verification/ownership colors)
- Click a marker → side drawer with survey number, area, ownership, owner list
- Note: markers are village-level approximations, not surveyed boundaries

### 3. BhoomiRashi Data Portal (1 min)
- Navigate to BhoomiRashi Portal
- Show ingestion summary KPIs (parsed parcels, owners, area)
- Browse staging schedule table with bilingual survey numbers
- Click "View Parties →" to inspect owner names and addresses
- Click "Reload Datasheet" to trigger bhoomirashi Excel re-ingestion

### 4. ML Land-Nature Screening (30 sec)
- Open API docs at http://localhost:8000/docs
- Try `POST /ml/land-nature/predict` with village="Kanjiama", area=0.15
- Show confidence score (99.39% private) and explanation factors
- Note: citizen role gets 403 — ML is staff-only

### 5. Dataset Browser (30 sec)
- Navigate to Dataset Browser
- Show 14 table selector cards with live row counts
- Click "Land Parcels" → 249 records with dynamic columns
- Click "Users" → 6 users with role and last login

### 6. Citizen Portal (30 sec)
- Logout → Login as Citizen
- Show Track Status page with parcels, compensation, payments
- Toggle Hindi/English language

### 7. Field Officer Mobile (30 sec)
- Logout → Login as Field Officer
- Show mobile-first survey screen with GPS capture

## 📁 Project Structure

```
nlams/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/v1/        # API routes (17 modules)
│   │   │   ├── auth.py          # Login, register, refresh, logout
│   │   │   ├── datasets.py      # Dataset browser (14 tables)
│   │   │   ├── ml_routes.py     # ML inference + staging endpoints
│   │   │   ├── gis.py           # GeoJSON import + map data
│   │   │   └── ...              # parcels, compensation, dashboard, etc.
│   │   ├── core/          # Config, security (JWT cookies), deps
│   │   ├── db/            # Async SQLAlchemy session
│   │   ├── models/        # SQLAlchemy models (20+ tables)
│   │   ├── schemas/       # Pydantic v2 request/response schemas
│   │   ├── services/      # Business logic (dashboard, GIS, SMS)
│   │   ├── ml/            # ML pipeline
│   │   │   ├── normalize.py     # Bilingual text normalization
│   │   │   ├── features.py      # Feature engineering
│   │   │   ├── ingest.py        # Bhoomirashi workbook ingestion
│   │   │   ├── train.py         # Model training
│   │   │   ├── service.py       # Inference service
│   │   │   └── artifacts/       # Trained model + metrics
│   │   ├── scripts/       # Data import scripts
│   │   ├── utils/         # Encryption, geo, storage
│   │   └── main.py        # FastAPI app + middleware + routers
│   ├── tests/             # pytest tests
│   ├── alembic/           # Database migrations (5 versions)
│   ├── seed.py            # Database seeder (bhoomirashi data)
│   └── requirements.txt
├── frontend/              # React 18 + Vite + TypeScript
│   ├── src/
│   │   ├── app/           # Router (App.tsx)
│   │   ├── components/    # Shared components
│   │   │   ├── ui/        # shadcn primitives (card, button, etc.)
│   │   │   ├── layout/    # RoleShell, Sidebar
│   │   │   ├── shared/    # KPICard, StatusBadge, DataTable
│   │   │   └── gis/       # ParcelLayer (MapLibre)
│   │   ├── pages/         # 28 page components by role
│   │   │   ├── admin/     # NationalDashboard, BhoomiRashiPortal,
│   │   │   │              # CompensationReportPage, DatasetPage,
│   │   │   │              # GISMapPage, ProjectList, etc.
│   │   │   ├── citizen/   # TrackStatus, MyCompensation, MyRR
│   │   │   ├── district/  # VerificationQueue, CompensationDesk
│   │   │   └── field/     # MobileHome, MobileSurveys, MobileCamera
│   │   ├── i18n/          # react-i18next (English + Hindi)
│   │   ├── services/      # Axios client, auth service
│   │   ├── store/         # AuthContext (httpOnly cookies)
│   │   └── __tests__/     # Vitest integration tests
│   ├── e2e/               # Playwright E2E tests (14 tests)
│   └── vitest.config.ts
├── docker-compose.yml     # Dev environment
├── docker-compose.prod.yml # Production (no adminer)
├── .github/workflows/     # CI: lint, test, build, E2E, Docker smoke
└── DECISIONS.md           # Architectural decisions log
```

## 🎯 Key Features

1. **6 Role-Based Dashboards** — Super Admin, State Authority, District Officer, Agency, Field Officer, Citizen
2. **14-Stage Lifecycle Tracking** — Full pipeline from proposal to completion with stage stepper
3. **GIS Map Integration** — Interactive MapLibre map with OpenFreeMap vector tiles and PostGIS parcel markers
4. **ML Land-Nature Screening** — Logistic regression model predicting private vs government land ownership with explanation factors
5. **BhoomiRashi Data Portal** — Ingest, browse, and promote gazette land records into active acquisition projects
6. **Compensation Report** — KPIs, pie/bar charts, and detailed breakdown under RFCTLARR Act 2013
7. **Dataset Browser** — Raw data grid for all 14 database tables with search and pagination
8. **District Verification Queue** — Parcel verification workflow with approve/dispute actions
9. **Compensation Desk** — Full compensation → payment → possession chain with audit logging
10. **R&R Management** — Rehabilitation & Resettlement tracking with family-level benefit status
11. **Citizen Transparency Portal** — Track status, compensation, R&R, and documents (English + Hindi)
12. **Mobile Field Officer** — GPS capture, photo upload, bottom tab bar navigation
13. **Audit Trail** — Complete timeline of all stage changes with officer names and timestamps
14. **Report Exports** — One-click CSV download for Project MIS, Compensation, and GIS Parcel reports
15. **Role-Switch Demo Mode** — Quick account switcher for demos

## 🤖 ML Endpoints

The backend includes a trained logistic regression model for **land-nature screening** — predicting whether a parcel is private or government-owned based on village, area, survey number patterns, and party count.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/ml/health` | GET | Staff | Model status and metadata |
| `/api/v1/ml/land-nature/predict` | POST | Staff | Predict land nature from manual input |
| `/api/v1/ml/parcels/{id}/land-nature` | GET | Staff | Predict for an existing parcel |
| `/api/v1/ml/staging/summary` | GET | Staff | Staging record counts and villages |
| `/api/v1/ml/staging/parcels` | GET | Staff | Paginated staging parcels with filters |
| `/api/v1/ml/staging/parcels/{id}/parties` | GET | Staff | Parties for a staging parcel |
| `/api/v1/ml/staging/promote` | POST | Admin | Promote staging parcels into a project |
| `/api/v1/ml/ingest` | POST | Admin | Trigger bhoomirashi workbook ingestion |

### Example: Predict land nature

```bash
curl -X POST http://localhost:8000/api/v1/ml/land-nature/predict \
  -H "Content-Type: application/json" \
  -d '{
    "village": "Kanjiama",
    "area_hectares": 0.15,
    "survey_number": "242",
    "party_count": 3,
    "land_type": "wet"
  }'
```

Response:
```json
{
  "prediction": "private",
  "confidence": 0.9939,
  "explanation": {
    "factors": [
      {"name": "village", "value": "Kanjiama"},
      {"name": "area_hectares", "value": 0.15},
      {"name": "survey_number_head", "value": "242"},
      {"name": "party_count", "value": 3}
    ]
  },
  "disclaimer": "This is a decision-support aid. Final determination requires field verification."
}
```

## 📦 Dataset Browser API

Browse all 14 raw database tables via a single paginated endpoint:

```bash
# List all parcels (page 1, 25 per page)
curl -b cookies.txt "http://localhost:8000/api/v1/datasets?table=parcels&page=1&page_size=25"

# Get row counts for all tables
curl -b cookies.txt http://localhost:8000/api/v1/datasets/summary
```

Available tables: `projects`, `parcels`, `users`, `compensations`, `payments`, `states`, `districts`, `villages`, `ministries`, `categories`, `documents`, `land_owners`, `rr_families`, `roles`

## 📊 New Dashboards

### BhoomiRashi Portal (`/admin/bhoomirashi`)

Staging hub for ingesting official gazette land records (MoRTH S.O. 1988E) into the acquisition pipeline:
- **4 KPI cards**: Parsed parcels, identified owners, private/government split, total area in hectares + acres
- **Data table**: 9-column staging schedule with bilingual survey numbers, village/sub-district, area, land type, land nature, owner count
- **Filters**: Village dropdown, land nature (Private/Government), text search
- **Party inspector**: Click "View Parties →" to see owner names, addresses, and indicated shares in a modal
- **Ingest trigger**: "Reload Datasheet" button re-parses the bhoomirashi Excel workbook
- **Promote workflow**: Select staging parcels → choose target project → promote into active LandParcel + LandOwner records

### Compensation Report (`/admin/compensation-report`)

Comprehensive compensation analysis under RFCTLARR Act, 2013:
- **4 KPI cards**: Total assessments, total market value, total award value, total disbursed
- **3 charts**: Status distribution (pie), Top 5 awards (horizontal bar), Payment disbursement status (pie)
- **Detailed breakdown table**: Parcel, market value, solatium (100%), additional compensation, total award, status badge, disbursed amount
- **Legal framework reference**: Section 26 market value, Section 30(1) solatium, Section 30(3) additional 12% p.a.

### Dataset Browser (`/admin/datasets`)

Raw data explorer for all 14 NLAMS database tables:
- **14 table selector cards**: Click any table to view its data — shows icon, label, and live row count
- **Dynamic data grid**: Auto-generates columns from the table schema with smart formatting (dates, currency, percentages, booleans)
- **Search**: Text search on name/email/survey-number fields
- **Pagination**: Page navigation with prev/next and numbered page buttons
- **Currently loaded data**: 1 project, 249 parcels, 6 users, 961 land owners, 6 villages, 1 state, 1 district

## 🏷️ Demo Mode

All external services (SMS, PFMS, DigiLocker, e-Sign) run in **Sandbox/Demo Mode** — clearly labeled in the UI. PFMS references are auto-generated mock IDs. This is intentional for the hackathon demo.

Toggle SMS provider via `SMS_PROVIDER` env var: `mock` (default) or `msg91`.

## 🚢 Production Deployment

```bash
# Copy and edit environment file
cp .env.example .env.production
# Edit .env.production with real secrets (SECRET_KEY, ENCRYPTION_KEY, POSTGRES_PASSWORD)

# Deploy
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

Production mode excludes adminer, enables structured JSON logging, Sentry error tracking, and Prometheus metrics.

## 🗄️ Database Backup & Restore

```bash
# Backup
docker compose exec postgres pg_dump -U nlams nlams_db > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20240101.sql | docker compose exec -T postgres psql -U nlams nlams_db

# Point-in-time recovery requires WAL archiving (see PostgreSQL docs)
```

## 📊 Monitoring

- **Structured JSON logs**: Every request logs `request_id`, `user_id`, `method`, `path`, `status_code`, `latency_ms`
- **Health checks**: `GET /api/health` (liveness), `GET /api/health/ready` (readiness with DB check)
- **Prometheus metrics**: Scrape `GET /metrics` for request count, latency histograms, and error rates
- **Sentry**: Set `SENTRY_DSN` env var to enable error tracking (off by default)

## 🌐 Internationalization

Citizen-facing pages support English and Hindi via react-i18next. Toggle language via the topbar button when logged in as a citizen.

To add a new locale:
1. Create `frontend/src/i18n/locales/{lang}.json`
2. Add the locale to `frontend/src/i18n/index.ts` resources
3. Add `useTranslation()` calls to new pages

## 🧪 Testing

| Layer | Tool | Count |
|-------|------|-------|
| Backend unit tests | pytest + pytest-asyncio | 19 (15 pass, 4 skip w/o DB) |
| Frontend unit tests | Vitest | 111 |
| E2E tests | Playwright | 14 |
| **Total** | | **144** |

### Running tests locally
```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend
cd frontend && npx vitest run

# E2E (requires backend + frontend running)
cd frontend && npx playwright test
```

### CI Pipeline
The GitHub Actions workflow (`.github/workflows/sih_workflow.yml`) runs on every PR:
1. **Backend lint** — ruff check + format + mypy
2. **Backend test** — pytest against PostGIS service container
3. **Backend build** — Docker image build
4. **Frontend lint** — TypeScript + ESLint
5. **Frontend test** — Vitest
6. **Frontend build** — Vite production build
7. **E2E tests** — Playwright against real backend + seeded DB
8. **Migration reversibility** — alembic upgrade/downgrade cycle
9. **Schema drift check** — diff alembic state vs schema.sql
10. **Docker Compose smoke test** — full stack startup

## 🔒 Security

- **JWT in httpOnly cookies** (not localStorage) with Secure + SameSite=Strict
- **Token revocation** — server-side denylist for logout + refresh token rotation
- **Rate limiting** — slowapi on login, register, forgot-password, and refresh endpoints
- **CORS** — explicit origin allowlist with credentials
- **Structured logging** — every request logs request_id, user_id, latency
- **Dependency audit** — npm audit (0 vulnerabilities) + pip-audit (1 accepted risk: ecdsa side-channel)
