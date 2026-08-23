from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class ProjectCreate(BaseModel):
    name: str
    ministry_id: uuid.UUID
    category_id: uuid.UUID
    implementing_agency_id: Optional[uuid.UUID] = None
    state_id: uuid.UUID
    district_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    estimated_budget: Optional[float] = None
    estimated_land_required_hectares: Optional[float] = None
    priority: str = "medium"
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    ministry_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    implementing_agency_id: Optional[uuid.UUID] = None
    state_id: Optional[uuid.UUID] = None
    district_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    estimated_budget: Optional[float] = None
    estimated_land_required_hectares: Optional[float] = None
    priority: Optional[str] = None
    current_stage: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    ministry_id: uuid.UUID
    category_id: uuid.UUID
    implementing_agency_id: Optional[uuid.UUID] = None
    state_id: uuid.UUID
    district_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    estimated_budget: Optional[float] = None
    estimated_land_required_hectares: Optional[float] = None
    priority: str
    current_stage: str
    status: str
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    created_by: uuid.UUID
    dpr_document_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    ministry_name: Optional[str] = None
    category_name: Optional[str] = None
    state_name: Optional[str] = None
    district_name: Optional[str] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedProjects(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int


class MilestoneCreate(BaseModel):
    stage: str
    title: str
    planned_date: Optional[datetime] = None
    status: str = "pending"
    responsible_officer_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class MilestoneUpdate(BaseModel):
    stage: Optional[str] = None
    title: Optional[str] = None
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: Optional[str] = None
    responsible_officer_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    stage: str
    title: str
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: str
    responsible_officer_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MinistryResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
