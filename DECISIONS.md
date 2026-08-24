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
**Rationale:** Per spec Section 7.1 folder structure. Currently placeholder barrels — the actual components are still inline in pages. This establishes the directory structure for future extraction as the codebase grows.

## D14: District Officer Full Workflow Pages
**Decision:** Replace generic placeholder routes (ReportsPage for compensation, ProjectList for verification) with real domain-specific pages: `CompensationDesk.tsx`, `VerificationQueue.tsx`, `ParcelVerification.tsx`, `RRManagement.tsx`.
**Rationale:** The spec Section 7.1 explicitly requires dedicated district pages for verification queue, parcel verification, and compensation desk. Previous implementation reused generic components which provided no real workflow functionality.
