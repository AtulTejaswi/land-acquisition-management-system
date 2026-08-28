# ML Integration Audit — NLAMS

Date: 2026-08-28. All facts below were verified against the repository source; documentation claims (README) were cross-checked against actual files.

## 1. Frontend

- **Stack** (verified in `frontend/package.json`): React 18.3, TypeScript 5.6, Vite 6, react-router-dom 6.28, @tanstack/react-query 5.59, axios, Tailwind CSS 3.4, Radix UI primitives (shadcn-style `src/components/ui/`), framer-motion, recharts, maplibre-gl, react-hook-form + zod, lucide-react.
- **Entry**: `frontend/src/main.tsx` → `frontend/src/app/App.tsx` (all routes declared there).
- **Route guards**: `ProtectedRoute` (App.tsx:53), `RoleRedirect` (App.tsx:60), role shells in `frontend/src/components/layout/RoleShell.tsx`, role logic in `frontend/src/hooks/useRoleGuard.ts` (`ROLE_HIERARCHY`, `hasMinRole`, `isStateScoped`, `isDistrictScoped`). Role branches: `/admin`, `/state`, `/district`, `/agency`, `/field`, `/citizen`.
- **API client**: `frontend/src/services/api.ts` — axios, `baseURL: '/api/v1'`, Bearer token from `localStorage['nlams_access_token']`, 401 interceptor clears storage. Auth service `frontend/src/services/auth.ts`; auth state `frontend/src/store/AuthContext.tsx`. Data fetching mixes react-query hooks (`useProjects.ts`, `useParcels.ts`) and inline `useQuery` in pages.
- **Types**: `frontend/src/types/index.ts` mirrors backend Pydantic schemas.
- **Existing AI UI**: only in `frontend/src/pages/admin/ProjectDetail.tsx` — react-query keys `['ai-delay', id]` (line 34), `['ai-risk', id]` (line 43), `['ai-missing-docs', id]` (line 52) calling `/ai/*`; "🤖 AI Insights" panel at line 144.
- **Candidate integration surfaces**: ProjectDetail.tsx (AI Insights panel), GISMapPage.tsx (parcel drawer), CompensationDesk.tsx, dashboard pages (NationalDashboard/StateDashboard/DistrictDashboard with KPICard/HeatmapIndia/TrendChart).
- **Tests**: Vitest + Testing Library (jsdom); setup `src/test/setup.ts`; colocated `*.test.tsx` plus 3 role-flow integration tests in `src/__tests__/`. Commands: `npm run test` (vitest run), `npm run lint`, `npm run typecheck`, `npm run build` (tsc --noEmit && vite build).

## 2. Backend

- **Entry**: `backend/app/main.py` (line 30) — FastAPI, slowapi rate limiting (line 28), CORS (line 38), `/uploads` static mount (line 49), `GET /api/health` (line 70).
- **Routers** registered at main.py:52–67 under `/api/v1`: auth, projects, parcels, gis, compensation, documents, notifications, dashboard, reports, surveys, users, **ai_routes**, notifications_legal, objections, rr, possession.
- **Config**: `backend/app/core/config.py` — pydantic-settings `Settings` (DATABASE_URL asyncpg, SYNC_DATABASE_URL, SECRET_KEY, ALGORITHM=HS256, token expiry, UPLOAD_DIR, CORS_ORIGINS, ENVIRONMENT).
- **Auth/RBAC**: JWT via python-jose — `backend/app/core/security.py` (`create_access_token`:18, `decode_token`:34); `backend/app/core/deps.py` (`get_current_user`:14, `require_role(allowed_roles)`:41, `get_current_active_user`:53).
- **Models** (`backend/app/models/`, UUID PKs, TimestampMixin/SoftDeleteMixin): User/Role (user.py), State/District/Village (state.py; Village has tehsil), Ministry/ProjectCategory/Project/Milestone (project.py), LandParcel/LandOwner/SurveyRecord + enums LandType/OwnershipStatus/VerificationStatus (land.py; LandParcel has survey_number, area_hectares, GeoAlchemy2 `geom`, verification_status), Compensation/Payment, CircleRate (land_type, rate_per_hectare, financial_year), Document, LegalNotification/Objection, Possession, RehabilitationFamily, NotificationApp, AuditLog.
- **Migrations**: one alembic revision — `backend/alembic/versions/001_initial_schema.py`. Seed: `backend/app/seed.py` (`python -m app.seed`, run automatically in docker-compose).
- **Existing "AI"**: `backend/app/api/v1/ai_routes.py` (router `/ai`) — `GET /ai/delay-prediction/{project_id}`:19, `GET /ai/risk-score/{project_id}`:31, `POST /ai/compensation-estimate`:43, `GET /ai/missing-documents/{project_id}`:55; all behind `get_current_user`. Service `backend/app/ai/insights.py` — deterministic formulas; its own docstring says "not real ML". UI labels it "AI Insights • Beta".
- **Errors**: per-route `HTTPException`; no global handlers beyond slowapi.
- **Tests**: pytest + pytest-asyncio + httpx ASGITransport; `conftest.py` needs a Postgres test DB (`DATABASE_URL` env or `postgresql+asyncpg://nlams_test:nlams_test@localhost:5432/nlams_test`). 132 test functions across 20 files, including `tests/test_ai_routes.py` (10 tests).
- **Deps** (`requirements.txt`): fastapi 0.115, sqlalchemy[asyncio] 2.0.35, asyncpg, alembic, pydantic 2.10, python-jose, passlib/bcrypt, faker, geoalchemy2, shapely, pyproj, aiofiles, httpx, pgvector, slowapi. **No pandas / scikit-learn / openpyxl / joblib anywhere.**

## 3. Docker

`docker-compose.yml`: postgres (postgis/postgis:15-3.4, 5432, healthcheck), backend (8000, `python -m app.seed && uvicorn app.main:app --reload`, upload volume + bind mount), frontend (5173, VITE_API_URL=http://localhost:8000), nginx (80), adminer (8080). `.env.example` files at root, `backend/`, `frontend/`.

## 4. ML model status — BLOCKER

**No ML model was supplied with the prompt.** Searches across the repository, Downloads, and paste attachments found no model artifact (`.pkl/.joblib/.h5/.onnx/.sav`), no model source directory, and no training/inference scripts. The repository contains zero ML code (only the rule-based `app/ai/insights.py`). The master prompt's rule 9 explicitly forbids inventing an endpoint, input schema, model format, or output label before inspecting the supplied model code; therefore no inference contract or integration can be honestly built until the model is provided or an alternative is authorized (e.g., training a documented model offline on the ingested workbook data).

## 5. Workbook (input spec)

`[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features.xlsx` (in ~/Downloads), verified:
- **Document Information** (3×2): Title = `Details of Survey Numbers for "S.O. 1988`, Tentative Publish Date = 22/06/2020.
- **Land Details** (250×11): S.No, District, Sub District, Village, Survey Number, Area, Description, Land Type, Land Nature, Land Category, Additional Details. Confirmed irregularities: bilingual survey numbers (`242\n२४२`), compound references (`244\n/789 & 244\n/955`), area strings with embedded `Hectares`, quoted enum values (`"Wet"`, `"Government"`, `"Rural"`), multiline Description.
- **Land Parties** (479×6): Source S.No, Land Parties, Name, Address, Type, Area — bilingual names/addresses, `Owner` type, one-to-many parcel→party linkage via Source S.No.

## 6. Risks and smallest safe design

- The existing `/ai/*` rule-based endpoints and their UI/tests must be preserved; ML output must be clearly separated and never labeled as the same thing.
- `LandParcel.survey_number` exists but has no normalized companion column; ingestion should keep raw values and add normalized fields (staging/import approach preferred over mutating transactional tables directly — one alembic migration max).
- `LandType`/`OwnershipStatus` enums must not be silently coerced from workbook `Land Type`/`Land Nature` values; unmapped values should be preserved as source metadata.
- Backend has no pandas/openpyxl yet — ingestion dependencies must be added to requirements.txt.
- Tests require a live Postgres; the CI workflow (`sih_workflow.yml`) runs `pytest`, `ruff check/format --check`, `mypy app/ --ignore-missing-imports`, frontend `tsc --noEmit`, eslint, vitest, and docker builds.
