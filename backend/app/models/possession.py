import uuid
from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class PossessionType(str, enum.Enum):
    physical = "physical"
    symbolic = "symbolic"


class Possession(Base, TimestampMixin):
    __tablename__ = "possession"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False, index=True
    )
    possession_date = Column(DateTime(timezone=True), nullable=True)
    taken_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    possession_type = Column(
        SAEnum(PossessionType, name="possession_type_enum"),
        default=PossessionType.physical,
        nullable=False,
    )
    remarks = Column(Text, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)

    parcel = relationship("LandParcel", foreign_keys=[parcel_id])
    officer = relationship("User", foreign_keys=[taken_by])
    document = relationship("Document", foreign_keys=[document_id])
