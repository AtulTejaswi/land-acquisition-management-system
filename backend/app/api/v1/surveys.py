from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.land import SurveyRecord, LandParcel
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.survey import SurveyCreate, SurveyResponse

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.get("", response_model=list[SurveyResponse])
async def list_surveys(
    parcel_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SurveyRecord)
    if parcel_id:
        query = query.where(SurveyRecord.parcel_id == parcel_id)
    if current_user.role.name == "field_officer":
        query = query.where(SurveyRecord.surveyed_by == current_user.id)
    result = await db.execute(query.order_by(SurveyRecord.created_at.desc()))
    return [SurveyResponse.model_validate(s) for s in result.scalars().all()]


@router.post("", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    data: SurveyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    survey = SurveyRecord(
        parcel_id=data.parcel_id,
        surveyed_by=current_user.id,
        survey_date=data.survey_date,
        geo_lat=data.geo_lat,
        geo_lng=data.geo_lng,
        condition_notes=data.condition_notes,
        status="completed",
    )
    db.add(survey)
    await db.commit()
    await db.refresh(survey)
    return SurveyResponse.model_validate(survey)
