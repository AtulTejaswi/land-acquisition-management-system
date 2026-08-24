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
| 🏛️ State Authority | anil@maharashtra.gov.in | password123 |
| 📋 District Officer | suresh@nagpur.gov.in | password123 |
| 🏗️ Agency | agency@nhai.gov.in | password123 |
| 📱 Field Officer | rahul.f@nlams.gov.in | password123 |
| 👤 Citizen | ganesh@email.com | password123 |

## 📋 Demo Script (5-Minute Pitch)

### 1. Login as Super Admin (1 min)
- Click "🔑 Super Admin" quick login button
- Show **National Dashboard** with KPIs, charts, India heatmap
- Click on a state in the heatmap → drill into state view

### 2. Project Lifecycle (1.5 min)
- Navigate to Projects → Click "NH-44 Widening — Nagpur to Betul"
- Show the **14-stage lifecycle stepper** (completed stages in green, current pulsing)
- Scroll down to **Full Audit Trail Timeline** with timestamps and officer names
- Highlight the **AI Insights panel** (delay prediction, risk score, missing docs)

### 3. GIS Map (1 min)
- Navigate to GIS Map
- Show interactive MapLibre map with colored parcel polygons
- Click a parcel → side drawer with details
- Show verification status legend

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
│   ├── tests/             # pytest tests (28 passing)
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
│   │   │   ├── gis/       # GIS components (barrel)
│   │   │   ├── dashboard/ # Dashboard components (barrel)
│   │   │   ├── compensation/ # Compensation components (barrel)
│   │   │   ├── rr/        # R&R components (barrel)
│   │   │   ├── documents/ # Document components (barrel)
│   │   │   ├── notifications/ # Notification components (barrel)
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
│   │   └── lib/           # Utils, formatters
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
11. **MIS Report Export** — One-click CSV download
12. **Role-Switch Demo Mode** — Quick account switcher for demos
13. **Forgot Password** — Mock OTP flow (Sandbox/Demo Mode)

## 🏷️ Demo Mode

All external services (SMS, PFMS, DigiLocker, e-Sign) run in **Sandbox/Demo Mode** — clearly labeled in the UI. PFMS references are auto-generated mock IDs. This is intentional for the hackathon demo.
