from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class SurveyCreate(BaseModel):
    parcel_id: uuid.UUID
    survey_date: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    condition_notes: Optional[str] = None


class SurveyResponse(BaseModel):
    id: uuid.UUID
    parcel_id: uuid.UUID
    surveyed_by: uuid.UUID
    survey_date: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    condition_notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
