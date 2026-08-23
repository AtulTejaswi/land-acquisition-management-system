from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class PossessionCreate(BaseModel):
    parcel_id: uuid.UUID
    possession_date: Optional[datetime] = None
    possession_type: str = "physical"
    remarks: Optional[str] = None


class PossessionResponse(BaseModel):
    id: uuid.UUID
    parcel_id: uuid.UUID
    possession_date: Optional[datetime] = None
    taken_by: Optional[uuid.UUID] = None
    possession_type: str
    remarks: Optional[str] = None
    document_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
