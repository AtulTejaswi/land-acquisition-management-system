from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: Optional[str] = None
    type: str
    channel: str
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedNotifications(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int


class LegalNotificationCreate(BaseModel):
    project_id: uuid.UUID
    section_type: str
    notification_number: Optional[str] = None


class LegalNotificationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    section_type: str
    notification_number: Optional[str] = None
    issued_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ObjectionCreate(BaseModel):
    parcel_id: uuid.UUID
    filer_name: str
    filer_contact: Optional[str] = None
    objection_text: str
    hearing_date: Optional[datetime] = None


class ObjectionUpdate(BaseModel):
    status: Optional[str] = None
    resolution_remarks: Optional[str] = None
    hearing_date: Optional[datetime] = None


class ObjectionResponse(BaseModel):
    id: uuid.UUID
    parcel_id: uuid.UUID
    filed_by: Optional[uuid.UUID] = None
    filer_name: str
    filer_contact: Optional[str] = None
    objection_text: str
    hearing_date: Optional[datetime] = None
    status: str
    resolution_remarks: Optional[str] = None
    resolved_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LegalNotificationUpdate(BaseModel):
    status: Optional[str] = None
    issued_date: Optional[datetime] = None
    notification_number: Optional[str] = None
    published_document_id: Optional[uuid.UUID] = None


class PaginatedLegalNotifications(BaseModel):
    items: List[LegalNotificationResponse]
    total: int
    page: int
    page_size: int


class PaginatedObjections(BaseModel):
    items: List[ObjectionResponse]
    total: int
    page: int
    page_size: int
