from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class RRFamilyCreate(BaseModel):
    project_id: uuid.UUID
    family_head_name: str
    family_id_number: Optional[str] = None
    member_count: Optional[int] = None
    displaced_status: str = "not_displaced"
    housing_benefit_status: str = "not_started"
    employment_benefit_status: str = "not_started"
    monetary_benefit_amount: Optional[float] = None
    current_stage: str = "identification"
    progress_percentage: int = 0


class RRFamilyUpdate(BaseModel):
    family_head_name: Optional[str] = None
    member_count: Optional[int] = None
    displaced_status: Optional[str] = None
    housing_benefit_status: Optional[str] = None
    employment_benefit_status: Optional[str] = None
    monetary_benefit_amount: Optional[float] = None
    current_stage: Optional[str] = None
    progress_percentage: Optional[int] = None


class RRFamilyResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    family_head_name: str
    family_id_number: Optional[str] = None
    member_count: Optional[int] = None
    displaced_status: str
    housing_benefit_status: str
    employment_benefit_status: str
    monetary_benefit_amount: Optional[float] = None
    current_stage: str
    progress_percentage: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRRFamilies(BaseModel):
    items: List[RRFamilyResponse]
    total: int
    page: int
    page_size: int


class RRProjectSummary(BaseModel):
    project_id: uuid.UUID
    project_name: str
    total_families: int
    fully_displaced: int
    partially_displaced: int
    housing_provided: int
    employment_provided: int
    resettled: int
    avg_progress: float
