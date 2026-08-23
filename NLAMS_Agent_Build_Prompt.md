# MASTER BUILD PROMPT — National Land Acquisition & Management System (NLAMS)
### Paste this entire document as the system/first prompt to your coding agent (Claude Code, Cursor, etc.)

---

## 0. HOW TO USE THIS PROMPT

Give this whole file to your agent as one instruction. Tell the agent:
> "Read this entire spec before writing any code. Build in the phase order given in Section 14. After each phase, run the app and confirm it works before moving to the next phase. Do not skip the database schema — build it first."

If your agent supports splitting work into multiple sessions, feed it one numbered section at a time (in order) rather than the whole file, to avoid context overflow.

---

## 1. ROLE & MINDSET FOR THE AGENT

You are acting as a **Lead Solution Architect + Senior Full-Stack Engineer + Database Architect** for a national e-Governance platform commissioned by a state Digital India cell. You are building this for a **48-hour Smart India Hackathon (SIH) demo**, so:

- Prioritize **visual polish, working demo flows, and seeded realistic data** over exhaustive edge-case handling.
- Every screen must look like a real government analytics product (think Vercel Dashboard + NIC Portal), never a bare CRUD scaffold.
- Every module must have **at least one working end-to-end flow** with real data — judges click through screens, they don't read code.
- Prefer **mocked-but-realistic** integrations (SMS, PFMS, DigiLocker, e-Sign) over broken real ones. Clearly label mocked services as "Sandbox/Demo Mode" in the UI so it looks intentional, not incomplete.
- Do not ask me clarifying questions before starting — make reasonable assumptions, document them in a `DECISIONS.md` file as you go, and keep building.

---

## 2. PROJECT SUMMARY (for your context — do not repeat this back, just build)

**NLAMS** digitizes India's land acquisition lifecycle end-to-end: Project Proposal → DPR Upload → Land Requirement → State Review → District Verification → GIS Mapping → Legal Notification → Objection Handling → Compensation Assessment → Award Declaration → Payment Disbursement → Physical Possession → Rehabilitation & Resettlement (R&R) → Project Completion.

Six roles use the platform: **Super Admin (Central Ministry)**, **State Authority**, **District Collector/LAO**, **Project Implementing Agency**, **Field Officer (mobile-first)**, **Citizen/Land Owner**.

---

## 3. TECH STACK (mandatory — do not substitute)

**Frontend:** React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui + React Router v6 + TanStack React Query + Recharts + Framer Motion + MapLibre GL JS (OpenStreetMap tiles, no Google Maps key needed) + Zod for form validation + react-hook-form.

**Backend:** FastAPI (Python 3.11+) + SQLAlchemy 2.0 (async) + Alembic migrations + Pydantic v2 schemas + PostgreSQL 15+ with **PostGIS** extension + JWT auth (access + refresh tokens) + Passlib/bcrypt + python-jose.

**Infra/dev:** Docker Compose (postgres+postgis, backend, frontend, adminer/pgweb), `.env` based config, seed script with Faker for realistic Indian data (states, districts, villages, names).

**File storage:** Local `/uploads` volume for the hackathon (structured like an S3 bucket — `documents/{project_id}/{stage}/{filename}`), abstracted behind a `StorageService` interface so it could swap to S3 later.

Do not introduce Next.js, Redux, GraphQL, MongoDB, or Firebase — the stack above is fixed.

---

## 4. NON-NEGOTIABLE QUALITY BAR

1. Every list page has: search, at least 2 filters, sort, pagination, skeleton loading state, and an empty state illustration/message.
2. Every dashboard has: KPI cards with trend indicators, at least 2 chart types, a date-range filter.
3. Every workflow stage change writes an **audit log row** (who, when, from-status, to-status, remarks).
4. Every role has a visually distinct dashboard shell (different sidebar nav, different accent usage) while sharing the same design tokens.
5. GIS module must render actual polygons on a real map (MapLibre + OSM raster/vector tiles), not a static image.
6. Mobile Field Officer screens must be tested at 375px width and work with touch targets ≥44px.
7. No lorem-ipsum in the final demo — seed data must use real Indian state/district/village names, realistic project names (e.g., "NH-44 Widening — Nagpur to Betul", "Bhogapuram International Airport Land Pooling"), and realistic rupee figures.

---

## 5. DATABASE — BUILD THIS FIRST

Use PostgreSQL + PostGIS. All primary keys are UUIDv4. Every table has `created_at`, `updated_at` (trigger-based `updated_at`), and soft-delete via `is_deleted boolean default false` where deletion matters (users, projects, parcels).

### 5.1 Core tables (minimum set — expand as needed but do not reduce)

```
states(id, name, code, region, created_at, updated_at)
districts(id, state_id FK, name, code, created_at, updated_at)
villages(id, district_id FK, tehsil, name, code, created_at, updated_at)

roles(id, name UNIQUE, description)                 -- super_admin, state_authority, district_officer, agency, field_officer, citizen
users(id, full_name, email UNIQUE, phone UNIQUE, password_hash, role_id FK,
      state_id FK NULL, district_id FK NULL, agency_name NULL,
      is_active, last_login_at, created_at, updated_at)

ministries(id, name, code)
project_categories(id, name)  -- Highway, Railway, Irrigation, Industrial Corridor, Renewable Energy, Smart City, Airport, Defence, Welfare

projects(id, name, ministry_id FK, category_id FK, implementing_agency_id FK(users),
         state_id FK, district_id FK, description, dpr_document_id FK(documents) NULL,
         estimated_budget NUMERIC(18,2), estimated_land_required_hectares NUMERIC(12,3),
         priority ENUM(low,medium,high,critical), current_stage ENUM(...14 stages...),
         status ENUM(draft, submitted, under_review, approved, rejected, active, delayed, completed),
         start_date, target_completion_date, created_by FK(users), created_at, updated_at, is_deleted)

milestones(id, project_id FK, stage ENUM(...14 stages...), title, planned_date, actual_date,
           status ENUM(pending,in_progress,completed,delayed), responsible_officer_id FK(users),
           remarks, created_at, updated_at)

land_parcels(id, project_id FK, survey_number, village_id FK, district_id FK, state_id FK,
             area_hectares NUMERIC(12,4), geom GEOMETRY(Polygon, 4326)  -- PostGIS
             land_type ENUM(agricultural,residential,commercial,forest,govt,other),
             ownership_status ENUM(private,govt,disputed,common),
             verification_status ENUM(pending,verified,disputed,acquired),
             created_at, updated_at, is_deleted)

land_owners(id, parcel_id FK, full_name, aadhaar_masked, phone, email NULL,
            bank_account_masked, ifsc, share_percentage NUMERIC(5,2),
            user_id FK(users) NULL, created_at, updated_at)

survey_records(id, parcel_id FK, surveyed_by FK(users), survey_date,
               geo_lat, geo_lng, photo_document_ids UUID[] / join table,
               condition_notes, status ENUM(scheduled,completed,flagged), created_at, updated_at)

legal_notifications(id, project_id FK, section_type (e.g. "Section 11", "Section 19"),
                    notification_number, issued_date, published_document_id FK(documents),
                    status ENUM(draft,issued,challenged), created_at, updated_at)

objections(id, parcel_id FK, filed_by FK(users) NULL, filer_name, filer_contact,
           objection_text, hearing_date, status ENUM(filed,under_review,resolved,rejected),
           resolution_remarks, resolved_by FK(users), created_at, updated_at)

compensation(id, parcel_id FK, market_value NUMERIC(18,2), solatium NUMERIC(18,2),
             additional_compensation NUMERIC(18,2), total_award NUMERIC(18,2) GENERATED,
             assessed_by FK(users), assessment_date,
             status ENUM(draft,assessed,approved,disputed), created_at, updated_at)

payments(id, compensation_id FK, land_owner_id FK, amount NUMERIC(18,2),
         pfms_reference, bank_verification_status ENUM(pending,verified,failed),
         payment_status ENUM(pending,processing,disbursed,failed),
         disbursed_date, created_at, updated_at)

possession(id, parcel_id FK, possession_date, taken_by FK(users),
           possession_type ENUM(physical,symbolic), remarks,
           document_id FK(documents) NULL, created_at, updated_at)

rehabilitation_families(id, project_id FK, family_head_name, family_id_number,
         member_count, displaced_status ENUM(not_displaced,partially,fully),
         housing_benefit_status ENUM(not_started,in_progress,provided),
         employment_benefit_status ENUM(not_started,in_progress,provided),
         monetary_benefit_amount NUMERIC(18,2),
         current_stage ENUM(identification,verification,benefit_disbursement,resettled),
         progress_percentage INT, created_at, updated_at)

documents(id, project_id FK NULL, parcel_id FK NULL, uploaded_by FK(users),
          doc_type ENUM(dpr,survey_report,notification,award,geojson,photo,other),
          file_name, file_path, file_size, mime_type, version INT DEFAULT 1,
          parent_document_id FK(documents) NULL,  -- version chain
          digital_signature_placeholder TEXT NULL,
          created_at, updated_at)

audit_logs(id, entity_type, entity_id, action, performed_by FK(users),
           old_value JSONB, new_value JSONB, remarks, ip_address, created_at)

notifications(id, user_id FK, title, body, type ENUM(info,success,warning,alert),
              channel ENUM(in_app,email,sms), is_read, related_entity_type, related_entity_id,
              created_at)
```

### 5.2 Required indexes
- B-tree on every FK column.
- GiST index on `land_parcels.geom` (`USING GIST`).
- Composite index on `projects(state_id, district_id, status)`.
- Composite index on `milestones(project_id, stage)`.
- Full-text (`GIN` + `pg_trgm`) index on `projects.name` and `land_owners.full_name` for search.

### 5.3 Constraints
- `CHECK` constraints on all percentage/status enums via native Postgres ENUM types.
- `share_percentage` per parcel across `land_owners` must sum to ≤100 (enforce at application layer + a periodic validation query, not a DB trigger, to keep it simple).
- `ON DELETE RESTRICT` for FK from transactional tables into `states/districts/villages`; `ON DELETE CASCADE` from `milestones`/`documents` into `projects`.

### 5.4 Deliverable
Write this as actual Alembic migration files (`001_initial_schema.py`, etc.) plus a raw `schema.sql` reference file, plus a `seed.py` that populates: 5 ministries, 10 states with real districts/villages, 40+ users across all 6 roles, 15 realistic projects at various stages, 60+ land parcels with real polygon coordinates (use approximate real-world lat/lng boxes, e.g. around NH-44 route or a real district), compensation + payment + R&R records for at least 5 fully-progressed projects, and an audit trail history for one flagship project so its full timeline can be demoed.

---

## 6. BACKEND — API ARCHITECTURE (FastAPI)

### 6.1 Folder structure
```
backend/
  app/
    core/           # config.py, security.py (JWT), deps.py (role-based guards)
    db/             # session.py, base.py
    models/         # SQLAlchemy models, one file per domain
    schemas/        # Pydantic request/response schemas
    api/
      v1/
        auth.py
        projects.py
        parcels.py
        gis.py
        compensation.py
        rr.py            # rehabilitation & resettlement
        documents.py
        notifications.py
        dashboard.py
        reports.py
        users.py
    services/       # business logic layer (keep routers thin)
    ai/             # delay_prediction.py, risk_score.py, compensation_estimator.py, doc_checker.py
    utils/
    main.py
  alembic/
  tests/
  seed.py
  Dockerfile
```

### 6.2 Auth
- `POST /api/v1/auth/login` (email/phone + password) → access + refresh JWT, payload includes `role`, `state_id`, `district_id`.
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/forgot-password` (mock OTP flow — generate + log OTP to console/response in demo mode)
- Role-based dependency `require_role(["super_admin","state_authority"])` used on every protected route. Row-level scoping: state_authority only sees their state_id, district_officer only their district_id, citizen only their own records (via `user_id` linkage on `land_owners`).

### 6.3 Key endpoints (build all, return real paginated JSON `{items, total, page, page_size}`)

```
/auth/*                         login, refresh, me, forgot-password
/dashboard/national             KPIs + charts for super admin
/dashboard/state/{state_id}     state-scoped KPIs
/dashboard/district/{district_id}
/projects                       GET(list+filters), POST(create)
/projects/{id}                  GET, PATCH, DELETE(soft)
/projects/{id}/milestones       GET, POST, PATCH
/projects/{id}/timeline         full stage-by-stage audit history
/parcels                        GET(list+filters incl. bbox), POST
/parcels/{id}                   GET, PATCH
/parcels/{id}/owners            GET, POST
/gis/parcels/geojson            GET — returns FeatureCollection for map layer, filterable by project/district/state
/gis/parcels/{id}/geojson       single parcel geometry
/gis/import-geojson             POST — bulk import parcels from uploaded GeoJSON
/surveys                        GET, POST (field officer submissions incl. lat/lng + photos)
/notifications-legal            GET, POST (Section 11/19 style legal notices) — namespaced to avoid clashing with /notifications (in-app alerts)
/objections                     GET, POST, PATCH (resolve)
/compensation                   GET, POST, PATCH
/payments                       GET, POST, PATCH (mock PFMS reference generator)
/possession                     GET, POST
/rr/families                    GET, POST, PATCH
/documents                      GET, POST (multipart upload), GET /{id}/versions
/notifications                  GET (per user), PATCH /{id}/read
/reports/mis                    GET — generates downloadable MIS report (CSV/PDF) with filters
/ai/delay-prediction/{project_id}
/ai/risk-score/{project_id}
/ai/compensation-estimate       POST — input parcel attrs, returns estimated range
/ai/missing-documents/{project_id}
/users                          admin-only CRUD for user management
```

All list endpoints accept `?page=&page_size=&search=&sort_by=&sort_dir=&status=&state_id=&district_id=&from_date=&to_date=`.

### 6.4 AI modules (rule-based, framed as "AI" for demo — do not attempt real ML training in 48 hrs)
- **Delay prediction:** compare `milestones.planned_date` vs today vs historical average stage duration → output risk label (On Track / At Risk / Delayed) + estimated delay in days.
- **Compensation estimator:** simple regression-like formula from land_type, area, circle-rate lookup table (seed a `circle_rates` table) + solatium multiplier (100% per LARR Act 2013) → return a range.
- **Risk score:** weighted score from (# open objections, days since last milestone update, budget variance, parcel dispute %) → 0-100 score with color band.
- **Missing document detector:** checklist per stage (e.g., Award stage requires: award_document, compensation_approval, notification) vs what's actually uploaded → list gaps.
Label all of these clearly in UI as "AI Insights" cards with a small "beta" badge — judges love seeing AI reasoning surfaced, not hidden.

---

## 7. FRONTEND — STRUCTURE & PAGES

### 7.1 Folder structure
```
frontend/src/
  app/                 # router setup, route guards per role
  components/
    ui/                # shadcn primitives
    layout/            # Sidebar, Topbar, RoleShell
    dashboard/         # KPICard, TrendChart, HeatmapIndia, TimelineGraph
    gis/                # MapView, ParcelLayer, DrawControl, ParcelSearch
    project/            # ProjectCard, MilestoneTracker, StageStepper
    compensation/
    rr/
    documents/          # FileUpload, VersionHistory, DocPreview
    notifications/
    shared/             # DataTable, FilterBar, EmptyState, Skeletons, StatusBadge
  pages/
    public/             Landing, About, Contact
    auth/               Login, ForgotPassword
    admin/              NationalDashboard, UserManagement, Reports, Settings
    state/              StateDashboard, DistrictMonitoring
    district/           VerificationQueue, ParcelVerification, CompensationDesk
    agency/             MyProjects, CreateProposal, ProjectDetail
    citizen/            TrackStatus, MyCompensation, MyDocuments
    field/              MobileInspection, MySurveys
  hooks/                # useAuth, useRoleGuard, useProjects, useParcels...
  services/             # axios/fetch API client, one file per module matching backend routers
  store/                # lightweight auth/user context (no Redux)
  types/                # TS interfaces mirroring Pydantic schemas
  lib/                  # utils, formatters (currency in ₹ lakh/crore, date)
  styles/               # tailwind.css, design tokens
```

### 7.2 Role-based routing
Wrap routes in a `<RoleShell role="state_authority">` that renders the correct sidebar + restricts nav items. Redirect based on `role` claim in JWT immediately after login (`/admin`, `/state`, `/district`, `/agency`, `/citizen`, `/field`).

---

## 8. DESIGN SYSTEM

- **Colors:** Primary `#1E40AF` (deep blue), Secondary Emerald `#059669`, Accent Orange `#F97316`, Background `#F8FAFC`/Slate, Success `#16A34A`, Warning `#D97706`, Danger `#DC2626`. Define all as Tailwind CSS variables/theme extension, never hardcode hex in components.
- **Typography:** Inter or "Manrope" for UI, tabular-nums for all financial/numeric figures.
- **Cards:** subtle border (`border-slate-200`), soft shadow on hover, rounded-xl. Use glassmorphism (`backdrop-blur-md bg-white/70`) only on the Topbar and modal overlays — not everywhere.
- **Tables:** sticky header, zebra-free (use hover row highlight instead), inline status badges with color-coded pills, row-level actions in a kebab menu.
- **Status stepper:** horizontal stepper component for the 14-stage lifecycle, used on Project Detail page — completed (emerald filled), current (blue pulsing dot), pending (slate outline), delayed (orange/red).
- **Empty states:** simple line-art SVG + one-line message + primary CTA.
- **Loading:** skeleton shimmer matching final layout shape, never a spinner-only screen for data-heavy pages.

---

## 9. GIS MODULE — SPECIFIC BUILD NOTES

- Use `maplibre-gl` + free OSM raster tiles (e.g. `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, respecting usage policy — for demo/local dev this is fine) or MapTiler free tier if a key is available; fall back to raster OSM if not.
- Base layers toggle: Street / Satellite (use Esri World Imagery free tile endpoint as the "satellite" layer for demo).
- Render parcels as GeoJSON polygon layer, colored by `verification_status` (pending=slate, verified=emerald, disputed=orange, acquired=blue).
- Click a parcel → side drawer with survey number, village/tehsil/district, area, owners, linked project, and a "View Documents" tab.
- Draw tool (mapbox-gl-draw or maplibre equivalent) for creating a new parcel polygon manually, auto-calculating area via `@turf/area` and writing it back to the form.
- "Import GeoJSON" button on the GIS page → uploads a `.geojson` file, previews parcels on map before confirming import.
- Parcel search bar with autocomplete by survey number / village name, flying the map to the result (`map.flyTo`).

---

## 10. MOBILE FIELD OFFICER SCREEN — SPECIFIC BUILD NOTES

- Single-column, large touch targets, bottom tab bar (Home / My Surveys / Camera / Profile).
- "New Inspection" flow: select parcel (searchable list) → capture GPS (use browser `navigator.geolocation`) → mock "geo-tagged photo" capture (file input with camera capture attribute) → notes field → submit → optimistic UI update with success toast.
- Show a small map thumbnail confirming captured coordinates fall inside/near the parcel boundary (basic point-in-polygon check via turf.js) — flag with a warning banner if outside expected boundary (this is a nice AI/validation touch judges notice).

---

## 11. ANIMATION GUIDANCE (Framer Motion)

- Page transitions: fade + slight y-translate (`initial={{opacity:0,y:8}}`, 200ms).
- KPI cards: staggered entrance on dashboard load (`staggerChildren: 0.05`).
- Stage stepper: animate the "current stage" dot with a pulsing scale loop.
- Charts: animate on mount, not on every re-render (guard with `key` stability).
- Modal/drawer: spring transition, backdrop fade.
- Toasts: slide-in from top-right, auto-dismiss.
- Do not animate table row updates on every poll/refetch — only on genuine create/delete to avoid jank.

---

## 12. SIH JUDGING — MAKE THESE VISIBLE, NOT JUST FUNCTIONAL

Explicitly build these because judges score on differentiation:
1. **Live India heatmap** on National Dashboard, state shaded by acquisition progress %, clickable to drill into state dashboard.
2. **AI Insights panel** on Project Detail (delay prediction + risk score + missing docs) with clear "AI" badge.
3. **GIS polygon-based parcel map** (most teams fake this with a static image — you should not).
4. **Full 14-stage audit trail timeline** with officer name, timestamp, remarks, and attached doc per stage on one flagship demo project.
5. **Citizen transparency portal** — a real citizen login showing their own compensation/payment status end-to-end (judges resonate with citizen-centric impact).
6. **One-click MIS report export** (PDF/CSV) from the Reports page.
7. A **role-switch demo mode** (optional, dev-only): a quick account switcher so you can show all 6 dashboards fast during the pitch without repeated logins.

---

## 13. ENVIRONMENT & RUN INSTRUCTIONS TO GENERATE

The agent should produce:
- `docker-compose.yml` bringing up: `postgres` (postgis/postgis image), `backend`, `frontend`, `pgadmin` or `adminer`.
- `.env.example` for both frontend and backend.
- Root `README.md` with: setup steps, seed command, default login credentials for all 6 roles (clearly listed table: role / email / password), and a "Demo Script" section listing the exact click-path to show each USP feature in a 5-minute pitch.

---

## 14. BUILD ORDER (48-HOUR HACKATHON PHASING — FOLLOW STRICTLY)

**Phase 1 (Hours 0–6): Foundation**
DB schema + migrations + seed script working end to end. Docker Compose boots all services. Auth (login/JWT/role guard) working for all 6 roles against seeded users.

**Phase 2 (Hours 6–16): Core CRUD + Layout**
Project CRUD + milestone tracker. Role-based dashboard shells and sidebars (empty charts OK for now). Document upload working (local storage) linked to projects/parcels.

**Phase 3 (Hours 16–26): GIS Module**
MapLibre map rendering seeded parcel polygons, click-to-inspect drawer, parcel search, draw tool for new parcel, GeoJSON import.

**Phase 4 (Hours 26–34): Compensation, Payments, R&R**
Full compensation → payment → possession → R&R chain wired to real seeded data for at least 5 projects, visible on District and Citizen dashboards.

**Phase 5 (Hours 34–40): Dashboards & Analytics**
National dashboard with India heatmap, charts, KPI cards, filters. State and district dashboards. Reports/MIS export.

**Phase 6 (Hours 40–44): AI Insight Cards + Notifications**
Delay prediction, risk score, missing-doc detector, compensation estimator wired into Project Detail and Dashboard. In-app notification center.

**Phase 7 (Hours 44–48): Field Officer Mobile Flow + Polish**
Mobile inspection screen, animations pass (Framer Motion), empty/loading states pass, final seed data enrichment for the flagship demo project, README + demo script, final QA pass on all 6 role logins.

**At the end of every phase**, the agent must: run the app, take a mental note of what's broken, fix blocking issues, and only then proceed — never leave a phase with the app in a non-running state.

---

## 15. FINAL INSTRUCTION TO THE AGENT

Build this as if it will actually be judged in front of a panel evaluating national-scale governance software. Favor a **smaller number of modules that work flawlessly and look outstanding** over a large number of half-built modules. If you must cut scope under time pressure, cut in this order (last cut first): Field Officer mobile flow → AI modules → Objection handling → Document versioning → GIS draw tool (keep GIS *viewing*, cut only *drawing* if truly out of time). Never cut: Auth/RBAC, Project lifecycle, GIS parcel viewing, National Dashboard, Citizen tracking view — these five are the ones judges will always click into first.

Begin with Section 5 (Database) now.
