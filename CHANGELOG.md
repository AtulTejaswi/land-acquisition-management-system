# Changelog

All notable changes to NLAMS are documented here.

## Phase 2 — Hardening, Testing & Production Readiness (2026-08-25)

### Added

#### Auth Hardening (D18)
- **Refresh token revocation**: New `refresh_tokens` table with `jti`, `token_hash`, `revoked_at`, `expires_at` columns
- **Token rotation**: Each `/auth/refresh` call issues a new refresh token and immediately revokes the old one
- **Logout endpoint**: `POST /auth/logout` — revokes a single refresh token
- **Logout-all endpoint**: `POST /auth/logout-all` — revokes all active refresh tokens for the authenticated user
- **Reuse detection**: If a revoked token is reused, all tokens for that user are revoked (breach response)
- **Alembic migration**: `002_refresh_tokens.py`

#### Data Protection (D19)
- **Fernet encryption**: `app/utils/encryption.py` — symmetric encryption for Aadhaar and bank account fields
- **ENCRYPTION_KEY config**: Added to Settings, mandatory in production, auto-generated in dev
- **Audit logging for reads**: Sensitive owner data access (bank/Aadhaar) is now logged in `audit_logs`
- **SECURITY.md**: Documents encryption, masking, access control, and DPDP Act compliance mapping
- **Tests**: 6 unit tests for encryption roundtrip, None handling, Unicode, etc.

#### PostGIS Geometry (D20)
- **Real GEOMETRY column**: `LandParcel.geom` changed from `Text` to `Geometry("POLYGON", srid=4326)`
- **Spatial index**: GiST index on the new geometry column
- **Nearby parcels endpoint**: `GET /gis/parcels/nearby?lat=&lng=&radius_km=` using `ST_DWithin`
- **Alembic migration**: `003_postgis_geometry.py` — converts existing TEXT data to PostGIS geometry
- **Seed script updated**: Uses `from_shape()` for proper GeoJSON storage

#### Observability (Phase 6)
- **Structured JSON logging**: Middleware logs request_id, user_id, method, path, status_code, latency_ms
- **Readiness check**: `GET /api/health/ready` — verifies database connectivity
- **Sentry stub**: Activates when `SENTRY_DSN` env var is set

#### SMS Provider (Phase 7)
- **SMS interface**: `app/services/sms.py` with `SMSProvider` abstract class
- **Mock adapter**: Default `SMS_PROVIDER=mock` — logs messages instead of sending
- **MSG91 adapter**: Real provider behind `SMS_PROVIDER=msg91` + `MSG91_API_KEY`
- **Tests**: 6 tests for provider factory and interface contract

#### CI Security Scanning (Phase 4)
- **Backend security job**: `pip-audit --strict` (non-blocking initially)
- **Frontend security job**: `npm audit --audit-level=high` (non-blocking initially)
- **Blocking mypy**: Removed `continue-on-error: true` from the mypy step

#### Documentation (Phase 8)
- **LICENSE**: MIT License
- **CONTRIBUTING.md**: Setup instructions, branch naming, PR checklist
- **CHANGELOG.md**: This file

### Changed
- `auth.py`: Refresh tokens now stored in DB; login issues refresh token row; rotation on refresh
- `security.py`: `create_refresh_token()` returns `(raw_token, jti, expires_at)` tuple; added `hash_token()`
- `gis_service.py`: Uses `to_shape`/`from_shape` for GeoJSON ↔ PostGIS conversion
- `gis.py`: Updated single parcel endpoint; added `/parcels/nearby` spatial query
- `seed.py`: Uses `from_shape(shape(polygon), srid=4326)` for geometry storage
- `config.py`: Added `ENCRYPTION_KEY`, `SENTRY_DSN`, `SMS_PROVIDER`, `MSG91_API_KEY` settings
- `conftest.py`: Engine fixture handles missing DB gracefully; `db_session` skips when unavailable

### Files Added
- `backend/app/models/refresh_token.py`
- `backend/app/utils/encryption.py`
- `backend/app/utils/geo.py`
- `backend/app/services/sms.py`
- `backend/alembic/versions/002_refresh_tokens.py`
- `backend/alembic/versions/003_postgis_geometry.py`
- `backend/tests/test_auth_token_revocation.py`
- `backend/tests/test_data_protection.py`
- `backend/tests/test_sms_service.py`
- `SECURITY.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CHANGELOG.md`

---

## Phase 1 — Hackathon Demo (2026-08-23)

Initial feature-complete implementation with 70+ backend tests, 111 frontend tests, and CI passing.
