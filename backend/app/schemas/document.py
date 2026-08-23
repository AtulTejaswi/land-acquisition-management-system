from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class DocumentResponse(BaseModel):
    id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    parcel_id: Optional[uuid.UUID] = None
    uploaded_by: uuid.UUID
    doc_type: str
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    version: int
    parent_document_id: Optional[uuid.UUID] = None
    digital_signature_placeholder: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedDocuments(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
