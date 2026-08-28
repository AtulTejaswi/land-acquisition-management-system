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

### 3. State Dashboard (1 min)
- Navigate to State Dashboard (Odisha)
- See real charts: parcels by village (6 villages), area by village, ownership split
- Drill into district view for Khordha

### 4. Citizen Portal (30 sec)
- Logout → Login as Citizen
- Show Track Status page with parcels, compensation, payments

### 5. Field Officer Mobile (30 sec)
- Logout → Login as Field Officer
- Show mobile-first survey screen with GPS capture

### 6. Compensation Flow (30 sec)
- Login as District Officer
- Navigate to Compensation Desk
- Show compensation → payment chain with seeded data

## 📁 Project Structure

```
nlams/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/v1/        # API routes (thin wrappers)
│   │   ├── core/          # Config, security, deps
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLAlchemy models (20+ tables)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   │   ├── project_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── gis_service.py
│   │   ├── ai/            # AI insights (rule-based algorithms)
│   │   │   └── insights.py
│   │   ├── utils/         # Storage service, helpers
│   │   │   └── storage.py
│   │   └── main.py        # FastAPI app + router registration
│   ├── tests/             # pytest tests (70 passing)
│   ├── app/seed.py        # Database seeder (canonical)
│   └── requirements.txt
├── frontend/              # React frontend
│   ├── src/
│   │   ├── app/           # Router setup (App.tsx)
│   │   ├── components/
│   │   │   ├── ui/        # shadcn primitives
│   │   │   ├── layout/    # Sidebar, Topbar, RoleShell
│   │   │   ├── shared/    # DataTable, KPICard, StatusBadge, etc.
│   │   │   ├── project/   # StageStepper
│   │   │   ├── gis/       # ParcelLayer
│   │   │   ├── dashboard/ # TrendChart, HeatmapIndia
│   │   │   ├── rr/        # StageProgress, BenefitTracker
│   │   │   ├── documents/ # DocList
│   │   │   ├── notifications/ # NotificationItem
│   │   │   └── toast/     # Toast notification system
│   │   ├── pages/         # Page components by role (25+ pages)
│   │   │   ├── auth/      # Login, ForgotPassword
│   │   │   ├── public/    # Landing, About, Contact
│   │   │   ├── admin/     # NationalDashboard, ProjectList, etc.
│   │   │   ├── state/     # StateDashboard
│   │   │   ├── district/  # VerificationQueue, CompensationDesk, RRManagement
│   │   │   ├── agency/    # MyProjects, CreateProposal, MyDocuments
│   │   │   ├── citizen/   # TrackStatus, MyCompensation, MyRR, MyDocuments
│   │   │   └── field/     # MobileHome, MobileSurveys, MobileCamera, MobileProfile
│   │   ├── services/      # API client, auth service
│   │   ├── store/         # Auth context
│   │   ├── hooks/         # Custom hooks (useProjects, useParcels, useRoleGuard)
│   │   ├── types/         # TypeScript interfaces
│   │   ├── lib/           # Utils, formatters
│   │   ├── test/          # Test setup and utilities
│   │   └── __tests__/     # Integration tests (3 role flows)
│   ├── vitest.config.ts   # Vitest test configuration
│   └── package.json
├── docker-compose.yml
├── .github/workflows/     # CI/CD pipeline
└── DECISIONS.md           # Architectural decisions
```

## 🎯 Key Features

1. **6 Role-Based Dashboards** — Super Admin, State Authority, District Officer, Agency, Field Officer, Citizen
2. **14-Stage Lifecycle Tracking** — Full pipeline from proposal to completion with stage stepper
3. **GIS Map Integration** — Interactive MapLibre map with colored parcel polygons (PostGIS)
4. **AI Insights Panel** — Delay prediction, risk scoring (0-100), missing document detection, compensation estimation
5. **District Verification Queue** — Parcel verification workflow with approve/dispute actions
6. **Compensation Desk** — Full compensation → payment → possession chain with audit logging
7. **R&R Management** — Rehabilitation & Resettlement tracking with family-level benefit status
8. **Citizen Transparency Portal** — Track status, compensation, R&R, and documents
9. **Mobile Field Officer** — GPS capture, photo upload, bottom tab bar navigation
10. **Audit Trail** — Complete timeline of all stage changes with officer names and timestamps
11. **Report Exports** — One-click CSV download for Project MIS, Compensation, and GIS Parcel reports
12. **Role-Switch Demo Mode** — Quick account switcher for demos
13. **Forgot Password** — Mock OTP flow (Sandbox/Demo Mode)

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

Citizen-facing pages support English and Hindi. Toggle language via the topbar button when logged in as a citizen.

To add a new locale:
1. Create `frontend/src/i18n/locales/{lang}.json`
2. Add the locale to `frontend/src/i18n/index.ts` resources
3. Add `useTranslation()` calls to new pages
