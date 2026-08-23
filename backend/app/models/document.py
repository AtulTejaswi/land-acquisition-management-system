import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SAEnum, Text

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class DocType(str, enum.Enum):
    dpr = "dpr"
    survey_report = "survey_report"
    notification = "notification"
    award = "award"
    geojson = "geojson"
    photo = "photo"
    other = "other"


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    parcel_id = Column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=True, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    doc_type = Column(SAEnum(DocType, name="doc_type_enum"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    version = Column(Integer, default=1)
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    digital_signature_placeholder = Column(Text, nullable=True)

    project = relationship("Project", foreign_keys=[project_id])
    parcel = relationship("LandParcel", foreign_keys=[parcel_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    parent = relationship("Document", remote_side=[id], foreign_keys=[parent_document_id])
