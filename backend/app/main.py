from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1 import (
    auth, projects, parcels, gis, compensation, documents,
    notifications, dashboard, reports, surveys, users, ai_routes,
    notifications_legal, objections,
)
import os

app = FastAPI(
    title="NLAMS — National Land Acquisition & Management System",
    description="e-Governance platform for India's land acquisition lifecycle",
    version="1.0.0",
)

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


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "NLAMS API", "version": "1.0.0"}
