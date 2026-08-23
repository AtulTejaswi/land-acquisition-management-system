from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class CompensationCreate(BaseModel):
    parcel_id: uuid.UUID
    market_value: Optional[float] = None
    solatium: Optional[float] = None
    additional_compensation: Optional[float] = None


class CompensationUpdate(BaseModel):
    market_value: Optional[float] = None
    solatium: Optional[float] = None
    additional_compensation: Optional[float] = None
    status: Optional[str] = None


class CompensationResponse(BaseModel):
    id: uuid.UUID
    parcel_id: uuid.UUID
    market_value: Optional[float] = None
    solatium: Optional[float] = None
    additional_compensation: Optional[float] = None
    total_award: Optional[float] = None
    assessed_by: Optional[uuid.UUID] = None
    assessment_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    compensation_id: uuid.UUID
    land_owner_id: uuid.UUID
    amount: float


class PaymentUpdate(BaseModel):
    bank_verification_status: Optional[str] = None
    payment_status: Optional[str] = None
    disbursed_date: Optional[datetime] = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    compensation_id: uuid.UUID
    land_owner_id: uuid.UUID
    amount: float
    pfms_reference: Optional[str] = None
    bank_verification_status: str
    payment_status: str
    disbursed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedCompensations(BaseModel):
    items: List[CompensationResponse]
    total: int
    page: int
    page_size: int


class PaginatedPayments(BaseModel):
    items: List[PaymentResponse]
    total: int
    page: int
    page_size: int


class RRFamilyCreate(BaseModel):
    project_id: uuid.UUID
    family_head_name: str
    family_id_number: Optional[str] = None
    member_count: Optional[int] = None
    displaced_status: str = "not_displaced"
    housing_benefit_status: str = "not_started"
    employment_benefit_status: str = "not_started"
    monetary_benefit_amount: Optional[float] = None
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
