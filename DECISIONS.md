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
