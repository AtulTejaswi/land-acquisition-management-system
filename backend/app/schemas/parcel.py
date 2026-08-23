from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
import uuid


class ParcelCreate(BaseModel):
    project_id: uuid.UUID
    survey_number: str
    village_id: uuid.UUID
    district_id: uuid.UUID
    state_id: uuid.UUID
    area_hectares: Optional[float] = None
    geom: Optional[Any] = None  # GeoJSON geometry
    land_type: str = "agricultural"
    ownership_status: str = "private"


class ParcelUpdate(BaseModel):
    survey_number: Optional[str] = None
    village_id: Optional[uuid.UUID] = None
    area_hectares: Optional[float] = None
    geom: Optional[Any] = None
    land_type: Optional[str] = None
    ownership_status: Optional[str] = None
    verification_status: Optional[str] = None


class ParcelResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    survey_number: str
    village_id: uuid.UUID
    district_id: uuid.UUID
    state_id: uuid.UUID
    area_hectares: Optional[float] = None
    land_type: str
    ownership_status: str
    verification_status: str
    created_at: datetime
    updated_at: datetime
    village_name: Optional[str] = None
    district_name: Optional[str] = None
    state_name: Optional[str] = None
    owners: List["LandOwnerResponse"] = []

    class Config:
        from_attributes = True


class LandOwnerCreate(BaseModel):
    parcel_id: uuid.UUID
    full_name: str
    aadhaar_masked: Optional[str] = None
    phone: str
    email: Optional[str] = None
    bank_account_masked: Optional[str] = None
    ifsc: Optional[str] = None
    share_percentage: Optional[float] = None
    user_id: Optional[uuid.UUID] = None


class LandOwnerResponse(BaseModel):
    id: uuid.UUID
    parcel_id: uuid.UUID
    full_name: str
    aadhaar_masked: Optional[str] = None
    phone: str
    email: Optional[str] = None
    bank_account_masked: Optional[str] = None
    ifsc: Optional[str] = None
    share_percentage: Optional[float] = None
    user_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedParcels(BaseModel):
    items: List[ParcelResponse]
    total: int
    page: int
    page_size: int


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[dict]


ParcelResponse.model_rebuild()
