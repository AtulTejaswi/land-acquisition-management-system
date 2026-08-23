import uuid
from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class NotificationLegalStatus(str, enum.Enum):
    draft = "draft"
    issued = "issued"
    challenged = "challenged"


class ObjectionStatus(str, enum.Enum):
    filed = "filed"
    under_review = "under_review"
    resolved = "resolved"
    rejected = "rejected"


class LegalNotification(Base, TimestampMixin):
    __tablename__ = "legal_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    section_type = Column(String(50), nullable=False)
    notification_number = Column(String(100), nullable=True)
    issued_date = Column(DateTime(timezone=True), nullable=True)
    published_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    status = Column(
        SAEnum(NotificationLegalStatus, name="legal_notification_status_enum"),
        default=NotificationLegalStatus.draft,
        nullable=False,
    )

    project = relationship("Project", foreign_keys=[project_id])
    published_document = relationship("Document", foreign_keys=[published_document_id])


class Objection(Base, TimestampMixin):
    __tablename__ = "objections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False, index=True
    )
    filed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    filer_name = Column(String(200), nullable=False)
    filer_contact = Column(String(15), nullable=True)
    objection_text = Column(Text, nullable=False)
    hearing_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        SAEnum(ObjectionStatus, name="objection_status_enum"),
        default=ObjectionStatus.filed,
        nullable=False,
    )
    resolution_remarks = Column(Text, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    parcel = relationship("LandParcel", foreign_keys=[parcel_id])
    filer = relationship("User", foreign_keys=[filed_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
