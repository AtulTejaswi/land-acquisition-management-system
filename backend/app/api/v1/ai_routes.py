from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.ai.insights import (
    compute_delay_prediction,
    compute_risk_score,
    estimate_compensation,
    detect_missing_documents,
)

router = APIRouter(prefix="/ai", tags=["ai-insights"])


@router.get("/delay-prediction/{project_id}")
async def delay_prediction(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await compute_delay_prediction(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.get("/risk-score/{project_id}")
async def risk_score(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await compute_risk_score(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.post("/compensation-estimate")
async def compensation_estimate(
    land_type: str,
    area_hectares: float,
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await estimate_compensation(db, land_type, area_hectares, state_id, district_id)


@router.get("/missing-documents/{project_id}")
async def missing_documents(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_missing_documents(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result
