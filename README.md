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
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Config, security, deps
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── seed.py            # Database seeder
│   └── requirements.txt
├── frontend/              # React frontend
│   ├── src/
│   │   ├── app/           # Router setup
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components by role
│   │   ├── services/      # API client
│   │   └── store/         # Auth context
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🎯 Key Features

1. **6 Role-Based Dashboards** — Super Admin, State Authority, District Officer, Agency, Field Officer, Citizen
2. **14-Stage Lifecycle Tracking** — Full pipeline from proposal to completion
3. **GIS Map Integration** — Interactive MapLibre map with parcel polygons (PostGIS)
4. **AI Insights Panel** — Delay prediction, risk scoring, missing document detection
5. **Citizen Transparency Portal** — Real-time compensation/payment tracking
6. **Mobile Field Officer** — GPS capture, photo upload, point-in-polygon validation
7. **Audit Trail** — Complete timeline of all stage changes
8. **MIS Report Export** — One-click CSV download

## 🏷️ Demo Mode

All external services (SMS, PFMS, DigiLocker, e-Sign) run in **Sandbox/Demo Mode** — clearly labeled in the UI. PFMS references are auto-generated mock IDs. This is intentional for the hackathon demo.
