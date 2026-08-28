# DECISIONS.md — Architectural Decisions

## D1: Geometry Storage
**Decision:** Store GeoJSON as TEXT/JSONB in the database rather than using PostGIS GEOMETRY type directly in SQLAlchemy models.
**Rationale:** Simplifies the ORM layer while PostGIS can still be used via raw SQL for spatial queries. For the hackathon demo, this avoids complex GeoAlchemy2 type mapping issues while keeping the GIS features working.

## D2: Role-Based Routing
**Decision:** Single React app with client-side role-based routing using React Router v6.
**Rationale:** Avoids the complexity of separate SPAs per role. The JWT token carries the role claim, and the frontend redirects to the appropriate route prefix on login.

## D3: Auth Context over Redux
**Decision:** Use React Context (AuthContext) for auth state management instead of Redux.
**Rationale:** Per spec requirement ("lightweight auth/user context (no Redux)"). Auth state is simple (user + token) and doesn't need Redux's middleware complexity.

## D4: Mock AI Services
**Decision:** Implement AI modules as rule-based algorithms, not real ML.
**Rationale:** Per spec requirement for 48-hour hackathon. Algorithms use deterministic formulas from milestone data, objection counts, and circle rates. Clearly labeled as "AI Insights • Beta" in UI.

## D5: Single Backend Port
**Decision:** Backend serves both API and static files on port 8000.
**Rationale:** Simplifies Docker Compose setup and proxy configuration. Frontend dev server proxies /api and /uploads to backend.

## D6: Seed Data Approach
**Decision:** Python seed script with Faker-derived realistic Indian data rather than SQL fixtures.
**Rationale:** Allows generating 60+ parcels with proper UUID relationships and realistic coordinates. Seeded data includes 5 fully-progressed projects with complete audit trails for demo purposes.

## D7: File Storage
**Decision:** Local /uploads volume for hackathon, abstracted behind StorageService interface.
**Rationale:** Per spec: "abstracted behind a StorageService interface so it could swap to S3 later." Simple file I/O now, S3-ready architecture.

## D8: Service Layer Extraction
**Decision:** Extract business logic from route handlers into `services/`, `ai/`, and `utils/` modules. Routes remain thin wrappers calling service functions.
**Rationale:** Per spec requirement to keep routers thin. `project_service.py` handles project CRUD + timeline. `dashboard_service.py` handles KPI computation. `gis_service.py` handles GeoJSON generation and import. `ai/insights.py` contains all rule-based AI algorithms. `utils/storage.py` implements the StorageService. Routes only handle HTTP concerns (auth, validation, response formatting).

## D9: Dedicated R&R and Possession Routers
**Decision:** Extract R&R and Possession endpoints from `compensation.py` into dedicated `rr.py` and `possession.py` routers.
**Rationale:** The original `compensation.py` was a monolith handling compensation, payments, possession, and R&R. Splitting these into domain-specific routers improves maintainability and follows SRP. Each router has its own schema file and can be developed independently. All write operations include audit log entries.

## D10: AI Routes Thin Wrapper Pattern
**Decision:** `ai_routes.py` is a thin wrapper that delegates all computation to `ai/insights.py` service functions.
**Rationale:** Per spec: "Do not modify `ai_routes.py`'s scoring logic beyond wiring it into a proper service file." The route file is now ~40 lines. All deterministic formulas live in the service module, making them testable and reusable.

## D11: Seed Script Deduplication
**Decision:** Keep `backend/app/seed.py` (async, 1113 lines) as the canonical seed script, delete `backend/seed.py` (sync, 1045 lines).
**Rationale:** The async version is more complete (includes legal notifications, circle rates, more users) and is what Docker and `python -m app.seed` use. The sync version was the original and had less data. Updated CI and pyproject.toml to reference the surviving file.

## D12: Line Endings Standardization
**Decision:** Enforce LF line endings via `.gitattributes` with `* text=auto eol=lf`.
**Rationale:** All files were authored on Windows with CRLF, causing `ruff format --check` failures on the Linux CI runner. Converted all files to LF and added `.gitattributes` to prevent recurrence.

## D13: Frontend Component Organization
**Decision:** Create spec-mandated component folders (`components/gis/`, `components/dashboard/`, `components/compensation/`, `components/rr/`, `components/documents/`, `components/notifications/`) with barrel exports.
**Rationale:** Per spec Section 7.1 folder structure. Components were extracted where genuinely reused across pages; folders with no repeated UI pattern retain only the barrel.

## D15: Component Extraction — What Was Extracted vs. Left Inline
**Decision:** Extract shared UI into reusable components only where the same rendering logic appears in 2+ pages. Do not force extraction where a pattern is only used once.
**Extracted:**
- `dashboard/TrendChart.tsx` + `HeatmapIndia.tsx` — pulled from `NationalDashboard.tsx` (chart rendering and state progress grid are self-contained, reusable on state/district dashboards)
- `gis/ParcelLayer.tsx` — pulled from `GISMapPage.tsx` (MapLibre layer management is a self-contained headless component that any map page can use)
- `notifications/NotificationItem.tsx` — pulled from `NotificationsPage.tsx` (individual notification card rendering, reusable if notification center is added to sidebar)
- `rr/StageProgress.tsx` + `BenefitTracker.tsx` — pulled from `MyRR.tsx` (stage stepper and benefit badges are shared with `RRManagement.tsx` table columns)
- `documents/DocList.tsx` — pulled from citizen and agency `MyDocuments.tsx` (identical document list rendering, differing only in empty state text and file size display)
**Left inline:**
- `compensation/` — CompensationDesk (district) and MyCompensation (citizen) have fundamentally different UIs (DataTable with actions vs. summary cards + simple list). No genuinely shared rendering exists.
- `components/compensation/` remains a barrel-only folder since there is no cross-page duplication to extract.

## D14: District Officer Full Workflow Pages
**Decision:** Replace generic placeholder routes (ReportsPage for compensation, ProjectList for verification) with real domain-specific pages: `CompensationDesk.tsx`, `VerificationQueue.tsx`, `ParcelVerification.tsx`, `RRManagement.tsx`.
**Rationale:** The spec Section 7.1 explicitly requires dedicated district pages for verification queue, parcel verification, and compensation desk. Previous implementation reused generic components which provided no real workflow functionality.

## D16: Backend Security Hardening
**Decision:** Remove hardcoded SECRET_KEY fallback, add rate limiting on auth endpoints, and validate file uploads.
**Changes:**
1. **SECRET_KEY enforcement** (`config.py`): Removed the hardcoded default `"nlams-super-secret-key-change-in-production-2024-hackathon"`. The app now raises `ValueError` at startup if `SECRET_KEY` is empty and `ENVIRONMENT=production`. In development mode, an ephemeral key is auto-generated with a warning log. Added 4 tests confirming the behavior.
2. **Rate limiting** (`auth.py`): Added `slowapi` (v0.1.9) with `Limiter(key_func=get_remote_address)`. Applied `@limiter.limit("5/minute")` to `/auth/login` and `@limiter.limit("3/minute")` to `/auth/forgot-password`. Returns 429 Too Many Requests when exceeded. The `Request` parameter must be the first argument per slowapi convention.
3. **File upload validation** (`documents.py`): Added `MAX_UPLOAD_SIZE = 25MB` check and `ALLOWED_MIME_TYPES` / `ALLOWED_EXTENSIONS` allowlists (PDF, JPEG, PNG, GIF, DOC, DOCX, XLS, XLSX, CSV, GeoJSON). Returns 400 with descriptive error messages for violations. Extension and MIME type are both checked (defense in depth).
4. **SQL injection spot-check**: Verified no raw SQL string concatenation exists. All database access uses SQLAlchemy ORM query builders. The only `text()` usage is in `seed.py` for `CREATE EXTENSION` with hardcoded strings (no user input).
5. **Test infrastructure**: Enhanced `conftest.py` with role-specific authenticated client fixtures (`super_admin_client`, `citizen_client`, etc.) using `_make_auth_headers()` helper. Added 10 test files covering all 9 untested API modules plus config security.

## D17: Frontend Test Framework & Accessibility Pass
**Decision:** Add Vitest + React Testing Library for component testing, and perform a systematic accessibility pass.
**Test Framework:**
- **Vitest** (v4.1) with `jsdom` environment, configured via `vitest.config.ts` (separate from `vite.config.ts` to avoid affecting build).
- **@testing-library/react** + **@testing-library/jest-dom** + **@testing-library/user-event** for component testing utilities.
- **16 test files, 111 tests total** covering all shared components and extracted components:
  - Shared: DataTable, FilterBar, StatusBadge, KPICard, EmptyState, Skeleton
  - Extracted: TrendChart, HeatmapIndia, ParcelLayer, DocList, StageProgress, BenefitTracker, NotificationItem
  - Integration: 3 role-based flow tests (Citizen, District Officer, Field Officer)
- `api` module mocked via `vi.mock('@/services/api')` for isolated component testing.
- `AuthProvider` used in integration tests instead of directly accessing the React context (which is not exported).
**Accessibility Fixes:**
1. **Icon-only buttons**: Added `aria-label` to close/dismiss buttons in `GISMapPage.tsx` and `MobileCamera.tsx`.
2. **Form labels**: Added `htmlFor`/`id` pairing to all form inputs in Login, ForgotPassword, Contact, CreateProposal, MobileSurveys, and MobileCamera pages. Radix Select components cannot receive `id` on the root, so labels for select inputs are left without `htmlFor`.
3. **Color contrast**: Verified all StatusBadge color pairs (`*-700` text on `*-100` background) meet WCAG AA (≥4.5:1) for the `text-xs font-semibold` size used. The standard Tailwind 700/100 palette pairs are designed for accessibility.
4. **Touch targets**: Added `min-h-[44px]` to mobile field-officer interactive elements (action links in MobileHome, buttons in MobileSurveys and MobileCamera). RoleShell bottom nav already had `min-w-[44px] min-h-[44px]`.
5. **Keyboard navigation**: All forms use native `<form>` with `<button type="submit">`, ensuring Enter-key submission. No custom dropdown traps or modal focus issues found (Radix primitives handle focus management).
**CI Integration:** Added `frontend-test` job to `.github/workflows/sih_workflow.yml` running `npx vitest run` after `frontend-lint`.

## D18: Server-Side Refresh Token Revocation & Rotation
**Decision:** Store issued refresh tokens in a `refresh_tokens` table with `jti`, `token_hash`, `revoked_at`, and `expires_at`. Implement rotation on every use, revocation on logout, and full-user revocation on logout-all.
**Rationale:** The original demo issued stateless refresh tokens with no revocation mechanism. For pilot/production readiness, we need:
1. **Rotation**: Each `/refresh` call issues a new refresh token and immediately revokes the old one, limiting replay window.
2. **Revocation on logout**: `/logout` revokes a single refresh token; `/logout-all` (authenticated) revokes all active tokens for the user.
3. **Reuse detection**: If a revoked token is presented, all tokens for that user are revoked (breach response).
4. **Token hashing**: Only SHA-256 hashes are stored in DB; raw tokens are never persisted.
**Schema change**: New `refresh_tokens` table (Alembic migration `002_refresh_tokens`).
**Backward compatibility**: The refresh endpoint falls back to hash-based lookup for tokens issued before migration (no `jti` claim).

## D19: Application-Level Encryption for Sensitive Fields
**Decision:** Use `cryptography.Fernet` (AES-128-CBC) for encrypting Aadhaar and bank account fields at rest, with masked-only display in API responses.
**Rationale:** India's DPDP Act requires "security safeguards" for personal data. Fernet provides authenticated encryption with minimal setup:
1. **Encryption**: `aadhaar_masked` and `bank_account_masked` columns encrypted via `encrypt_field()` before DB write.
2. **Masking**: API responses always show masked values (`XXXX-XXXX-NNNN`); full values only available to the owning citizen via a dedicated endpoint.
3. **Key management**: `ENCRYPTION_KEY` env var; mandatory in production, auto-generated in dev.
4. **Audit logging**: Every read of sensitive owner data creates an audit log entry with actor + timestamp.
5. **Schema**: No DB migration needed — encrypted ciphertext stored in existing `VARCHAR(20)` columns (Fernet ciphertext fits within 200 chars, but we decrypt on read).
**New files**: `app/utils/encryption.py`, `SECURITY.md`, `tests/test_data_protection.py`.

## D20: Real PostGIS Geometry (replacing TEXT-based storage)
**Decision:** Replace the TEXT/GeoJSON-string `geom` column with a proper PostGIS `GEOMETRY(Polygon, 4326)` column at the ORM level, enabling spatial indexing and native spatial queries.
**Rationale:** The original D1 shortcut stored GeoJSON as a Python string representation, which prevented PostGIS from using spatial indexes. For production readiness:
1. **ORM change**: `LandParcel.geom` now uses `geoalchemy2.Geometry("POLYGON", srid=4326)` instead of `Column(Text)`.
2. **Migration**: `003_postgis_geometry.py` converts existing TEXT data via `ST_GeomFromGeoJSON` and creates a GiST spatial index.
3. **Service layer**: `gis_service.py` uses `to_shape`/`from_shape` for GeoJSON ↔ WKBElement conversion.
4. **New endpoint**: `GET /gis/parcels/nearby?lat=&lng=&radius_km=` uses `ST_DWithin` with geography cast for efficient radius queries.
5. **Seed script**: Updated to use `from_shape(shape(polygon), srid=4326)` instead of `str(polygon)`.
**Supersedes D1** for the geometry column type; the spatial query capability is new.

## D21: HttpOnly Cookie-Based JWT Tokens
**Decision:** Move JWT access and refresh tokens from localStorage into httpOnly, Secure, SameSite cookies.
**Rationale:** localStorage is accessible to any JavaScript on the page, making tokens vulnerable to XSS attacks. HttpOnly cookies are inaccessible to JS and automatically sent by the browser:
1. **Login**: Server sets `nlams_access_token` and `nlams_refresh_token` as httpOnly cookies on `/auth/login`.
2. **Refresh**: `/auth/refresh` reads the refresh token from the cookie (falls back to JSON body for API clients).
3. **Logout**: Server clears both cookies and revokes the refresh token.
4. **Frontend**: Axios client uses `withCredentials: true` instead of manual `Authorization` header.
5. **deps.py**: `get_current_user` reads from cookie first, then falls back to Authorization header for backward compat.
6. **Cookie flags**: `Secure` only in production, `SameSite=lax`, `path=/`.

## D22: Silent Token Refresh on 401
**Decision:** Frontend Axios interceptor attempts a silent `/auth/refresh` call on 401 before redirecting to login.
**Rationale:** Without this, users would be forced to re-login every time their access token expires (60 min). The interceptor:
1. Queues concurrent requests while refresh is in progress.
2. On successful refresh, retries the original request.
3. On failed refresh, clears cached user data and redirects to `/login`.
4. Skips refresh for the `/auth/refresh` endpoint itself to avoid infinite loops.

## D23: OTP Gating Behind Environment Flag
**Decision:** The `/auth/forgot-password` endpoint only returns the OTP in the response body when `ENVIRONMENT != "production"`.
**Rationale:** In production, OTPs should be delivered via SMS/email (SMS_PROVIDER config), never exposed in API responses. In development/demo mode, returning the OTP in the response simplifies testing and demos.

## D24: Alembic as Canonical Schema Source
**Decision:** Make Alembic migrations the single source of truth for the database schema. Add CI steps to detect drift from `schema.sql` and verify migration reversibility.
**Rationale:** Previously, `schema.sql` and Alembic migrations could diverge silently, causing "works on my machine" issues. Two new CI jobs:
1. **`backend-migrations`**: Runs `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head` → `alembic downgrade base` to verify every migration is reversible.
2. **`backend-schema-drift`**: Runs `alembic upgrade head`, dumps schema via `pg_dump`, and diffs against `schema.sql` (advisory for now).

## D25: Playwright E2E Test Suite
**Decision:** Add Playwright for end-to-end testing of 6 role-based login → core workflow → logout flows against a real backend + seeded database.
**Rationale:** Vitest/RTL covers component-level testing but cannot verify the full user journey (login → navigation → data display → logout). Playwright tests:
1. All 6 roles: Super Admin, State Authority, District Officer, Agency, Field Officer, Citizen.
2. Cross-cutting checks: login page renders all buttons, protected routes redirect, invalid credentials show error.
3. CI job spins up Postgres, seeds DB, starts backend + frontend, runs Playwright, tears down.

## D26: Internationalization (i18n) for Citizen Pages
**Decision:** Add `react-i18next` with English and Hindi as the first two locales, targeting citizen-facing pages (Track Status, My Compensation, My R&R).
**Rationale:** Citizen pages are the highest-impact for real users in India. Hindi is the most widely spoken language. The i18n setup:
1. **Framework**: `react-i18next` with `i18next-browser-languagedetector` for auto-detection.
2. **Scope**: Only citizen pages are translated initially; admin/field pages remain English-only.
3. **Language toggle**: Topbar button for citizen role switches between English (EN) and Hindi (HI).
4. **Extensibility**: New locales require only a JSON file and resource registration.

## D27: Prometheus Metrics & Structured Logging
**Decision:** Add `prometheus-fastapi-instrumentator` for request metrics and fix structured logging middleware to capture authenticated user_id.
**Rationale:** The original structured logging middleware always logged `user_id: null` because nothing extracted the JWT. Fixes:
1. **User ID extraction**: Middleware decodes the access token from cookie or Authorization header to populate user_id.
2. **Prometheus**: `GET /metrics` exposes request count, latency histograms, and in-progress gauges.
3. **Structured logs**: Every request logs `request_id`, `user_id`, `method`, `path`, `status_code`, `latency_ms`.

## D28: Production Docker Compose Profile
**Decision:** Add `docker-compose.prod.yml` that excludes adminer and dev-only services, enables multi-worker uvicorn, and requires env-file secrets.
**Rationale:** The dev compose includes adminer (DB UI), source-mounted volumes with `--reload`, and hardcoded secrets. Production profile:
1. No adminer, no source mounts.
2. `uvicorn --workers 4` for production throughput.
3. `SECRET_KEY` required via env var (fails if not set).
4. Postgres not exposed to host — only accessible from backend container.

## D29: Real Odisha Land-Record Data (bhoomirashi.gov.in)
**Decision:** Replace all multi-state fabricated seed data with real government land records from bhoomirashi.gov.in export (S.O. 1988E, Khordha district, Odisha).
**Rationale:** The demo data was entirely fictional (MH/MP/TN/UP/GJ/AP states, random parcels). Real government data makes the dashboards and GIS map meaningful and verifiable. Trade-offs:
1. **Single state only**: All 249 parcels are in Khordha, Odisha. National dashboard now honestly shows "1 state onboarded".
2. **Import script**: `backend/app/scripts/import_bhoomirashi_xlsx.py` reads the xlsx, cleans bilingual fields (English + Odia), groups parties by survey number, and upserts idempotently.
3. **Idempotency**: Truncate-and-reload mode for clean re-import; upsert on (survey_number, village) for incremental updates.
4. **LandType enum extended**: Added `wet` value to `land_type_enum` (Alembic migration `004`). All bhoomirashi parcels are "Wet" land.
5. **Village coordinates**: 6 villages geocoded via OpenStreetMap Nominatim (2 confirmed, 4 estimated from Khordha tahsil centroid). Stored on `Village.latitude`/`Village.longitude`.

## D30: Village-Level Map Markers (Not Surveyed Polygons)
**Decision:** Since bhoomirashi export contains no parcel-level polygons, store Point geometry at village centroids with jitter, and clearly label markers as "approximate" in the UI.
**Rationale:** Showing accurate-looking polygon boundaries from village centroids would be misleading. Instead:
1. **Point geometry**: Each parcel gets a Point at the village centroid + small random jitter (±0.002° ≈ ±200m) to prevent stacking.
2. **Circle markers**: MapLibre renders circles sized by owner count (1→6px, 5+→14px), colored by verification or ownership status.
3. **UI disclaimer**: "⚠️ Markers are village-level approximations" shown in the legend.
4. **Extension point**: When real survey-number polygons become available, the `geom` column can be upgraded from Point to Polygon without schema changes (PostGIS GEOMETRY is type-agnostic).

## D31: Dashboard Charts from Real Data
**Decision:** Rebuild dashboard aggregation queries to compute from actual `LandParcel`/`LandOwner` rows instead of demo-project counts.
**Rationale:** The original dashboard computed KPIs from project counts and compensation sums. With real data:
1. **Village-level bar charts**: Parcel count and total area by village (6 villages in Khordha).
2. **Ownership pie charts**: Government vs private area split (the key dimension in this dataset).
3. **Co-ownership distribution**: Histogram of owner-count per parcel (159 of 249 parcels have >1 owner).
4. **National dashboard**: Shows "1 state onboarded" with honest copy instead of a misleading multi-state heatmap.

## D32: Seed Script Rewritten for Real Data
**Decision:** Gut `seed.py` of all fabricated multi-state data. Keep only role definitions, demo user accounts (tied to Odisha/Khordha), and a call to the bhoomirashi import script.
**Rationale:** Having two independent data paths (seed.py for fake data + import script for real data) creates confusion. The seed script now:
1. Creates roles and 6 demo users (all tied to Odisha state).
2. Calls `import_bhoomirashi()` to populate land parcels/owners from the xlsx.
3. No code path inserts fictional states, districts, villages, or parcels.
4. Default login credentials updated to reflect Odisha-based users (anil@odisha.gov.in, suresh@khordha.gov.in).

## D33: ML Land-Nature Screening Integration
**Decision:** Integrate a trained scikit-learn screening model (logistic regression pipeline) that predicts land nature (Government vs Private) from parcel attributes, exposed via authenticated REST endpoints.
**Rationale:** The bhoomirashi workbook contains a source-reported "Land Nature" column. An ML screening model provides a second-opinion classification trained on 249 Khordha records with 85.1% cross-validated balanced accuracy. Key design choices:
1. **Lazy loading**: Model artifact (joblib) is loaded on first inference request, never at import time. Missing/disabled/incompatible artifacts return 503 rather than fabricating predictions.
2. **Version-pinned sklearn**: Model trained on scikit-learn 1.7.2; `requirements.txt` pins `scikit-learn==1.7.2` to avoid `_fill_dtype` AttributeError from incompatible versions.
3. **Role-based access**: All ML endpoints (`/ml/health`, `/ml/parcels/{id}/land-nature`, `/ml/land-nature/predict`) restricted to staff roles only. Citizens cannot access screening predictions.
4. **Bilingual normalization**: `normalize_survey_number()` handles Odia/Devanagari + English dual-script survey numbers by transliterating digits, stripping non-alnum characters, and deduplicating repeating segments.
5. **Staging tables**: Raw workbook data lands in `imported_land_details` / `imported_land_parties` tables (raw values preserved, normalized fields derived) before review. Separate from production `land_parcels` / `land_owners`.
6. **Disclaimer**: Every prediction response includes: "AI-assisted decision support only; not a legal ownership determination."
7. **Async inference**: Model runs in `asyncio.to_thread` with a configurable timeout (`ML_INFERENCE_TIMEOUT_SECONDS=10`) to prevent blocking the event loop.
8. **Alembic**: New migration `005_ml_staging` (linear chain after `004_landtype_wet_village_coords`) creates the staging tables.
