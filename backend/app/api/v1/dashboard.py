from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.services.dashboard_service import (
    get_national_dashboard,
    get_state_dashboard,
    get_district_dashboard,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/national")
async def national_dashboard(
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    return await get_national_dashboard(db)


@router.get("/state/{state_id}")
async def state_dashboard(
    state_id: uuid.UUID,
    current_user: User = Depends(require_role(["super_admin", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    return await get_state_dashboard(db, state_id)


@router.get("/district/{district_id}")
async def district_dashboard(
    district_id: uuid.UUID,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_district_dashboard(db, district_id)
