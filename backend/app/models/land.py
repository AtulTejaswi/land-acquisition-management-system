import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, Enum as SAEnum, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class LandType(str, enum.Enum):
    agricultural = "agricultural"
    residential = "residential"
    commercial = "commercial"
    forest = "forest"
    govt = "govt"
    other = "other"


class OwnershipStatus(str, enum.Enum):
    private = "private"
    govt = "govt"
    disputed = "disputed"
    common = "common"


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    disputed = "disputed"
    acquired = "acquired"


class SurveyStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    flagged = "flagged"


class LandParcel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "land_parcels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    survey_number = Column(String(50), nullable=False)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=False, index=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=False, index=True)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False, index=True)
    area_hectares = Column(Numeric(12, 4), nullable=True)
    geom = Column(
        Text, nullable=True
    )  # Will store GeoJSON geometry as text; PostGIS GEOMETRY handled at DB level
    land_type = Column(
        SAEnum(LandType, name="land_type_enum"), default=LandType.agricultural, nullable=False
    )
    ownership_status = Column(
        SAEnum(OwnershipStatus, name="ownership_status_enum"),
        default=OwnershipStatus.private,
        nullable=False,
    )
    verification_status = Column(
        SAEnum(VerificationStatus, name="verification_status_enum"),
        default=VerificationStatus.pending,
        nullable=False,
    )

    project = relationship("Project", back_populates="parcels")
    village = relationship("Village")
    district = relationship("District")
    state = relationship("State")
    owners = relationship("LandOwner", back_populates="parcel", lazy="selectin")
    surveys = relationship("SurveyRecord", back_populates="parcel", lazy="selectin")


class LandOwner(Base, TimestampMixin):
    __tablename__ = "land_owners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False, index=True
    )
    full_name = Column(String(200), nullable=False)
    aadhaar_masked = Column(String(20), nullable=True)
    phone = Column(String(15), nullable=False)
    email = Column(String(200), nullable=True)
    bank_account_masked = Column(String(20), nullable=True)
    ifsc = Column(String(20), nullable=True)
    share_percentage = Column(Numeric(5, 2), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    parcel = relationship("LandParcel", back_populates="owners")
    user = relationship("User", foreign_keys=[user_id])


class SurveyRecord(Base, TimestampMixin):
    __tablename__ = "survey_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False, index=True
    )
    surveyed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    survey_date = Column(String(30), nullable=True)
    geo_lat = Column(Numeric(10, 7), nullable=True)
    geo_lng = Column(Numeric(10, 7), nullable=True)
    condition_notes = Column(Text, nullable=True)
    status = Column(
        SAEnum(SurveyStatus, name="survey_status_enum"),
        default=SurveyStatus.scheduled,
        nullable=False,
    )

    parcel = relationship("LandParcel", back_populates="surveys")
    surveyor = relationship("User", foreign_keys=[surveyed_by])
