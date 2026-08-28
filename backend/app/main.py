import time
import uuid
import json
import logging
import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1 import (
    auth,
    projects,
    parcels,
    gis,
    compensation,
    documents,
    notifications,
    dashboard,
    reports,
    surveys,
    users,
    ai_routes,
    notifications_legal,
    objections,
    rr,
    possession,
    ml_routes,
    datasets,
)

# ---------------------------------------------------------------------------
# Structured JSON logger
# ---------------------------------------------------------------------------
logger = logging.getLogger("nlams.access")


class StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Merge extra fields if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "path"):
            log_entry["path"] = record.path
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "latency_ms"):
            log_entry["latency_ms"] = record.latency_ms
        return json.dumps(log_entry, default=str)


_handler = logging.StreamHandler()
_handler.setFormatter(StructuredJSONFormatter())
logger.addHandler(_handler)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Sentry stub — only activates if SENTRY_DSN is set
# ---------------------------------------------------------------------------
if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=settings.ENVIRONMENT,
        )
        logger.info("Sentry error tracking enabled")
    except ImportError:
        logger.warning("SENTRY_DSN is set but sentry-sdk is not installed")

# ---------------------------------------------------------------------------
# Structured logging middleware
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NLAMS — National Land Acquisition & Management System",
    description="e-Governance platform for India's land acquisition lifecycle",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Prometheus metrics — scrape at /metrics
# Disabled if starlette version is incompatible
# ---------------------------------------------------------------------------
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
except (ImportError, TypeError) as exc:
    logger.warning(f"Prometheus metrics disabled: {exc}")


@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    # Extract user_id from access token cookie for logging
    user_id = None
    access_token = request.cookies.get("nlams_access_token")
    if access_token:
        try:
            from app.core.security import decode_token
            payload = decode_token(access_token)
            if payload:
                user_id = payload.get("sub")
        except Exception:
            pass
    # Also try Authorization header (backward compat)
    if not user_id:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                payload = decode_token(auth_header[7:])
                if payload:
                    user_id = payload.get("sub")
            except Exception:
                pass

    response = await call_next(request)

    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "user_id": user_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount upload directory (create if missing)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "documents"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(parcels.router, prefix="/api/v1")
app.include_router(gis.router, prefix="/api/v1")
app.include_router(compensation.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(surveys.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(ai_routes.router, prefix="/api/v1")
app.include_router(notifications_legal.router, prefix="/api/v1")
app.include_router(objections.router, prefix="/api/v1")
app.include_router(rr.router, prefix="/api/v1")
app.include_router(possession.router, prefix="/api/v1")
app.include_router(ml_routes.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")


@app.get("/api/health")
async def health_check():
    """Liveness check — returns 200 if the process is running."""
    return {"status": "ok", "service": "NLAMS API", "version": "1.0.0"}


@app.get("/api/health/ready")
async def readiness_check():
    """Readiness check — verifies database connectivity.

    Returns 200 when healthy, 503 when the database is unreachable.
    """
    from sqlalchemy import text
    from app.db.session import async_session_factory

    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return Response(
            content=json.dumps({"status": "degraded", "database": "disconnected", "error": str(e)}),
            status_code=503,
            media_type="application/json",
        )
