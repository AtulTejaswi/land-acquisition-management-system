import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class CompensationStatus(str, enum.Enum):
    draft = "draft"
    assessed = "assessed"
    approved = "approved"
    disputed = "disputed"


class BankVerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    failed = "failed"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    disbursed = "disbursed"
    failed = "failed"


class Compensation(Base, TimestampMixin):
    __tablename__ = "compensation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False, index=True
    )
    market_value = Column(Numeric(18, 2), nullable=True)
    solatium = Column(Numeric(18, 2), nullable=True)
    additional_compensation = Column(Numeric(18, 2), nullable=True)
    total_award = Column(Numeric(18, 2), nullable=True)
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assessment_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        SAEnum(CompensationStatus, name="compensation_status_enum"),
        default=CompensationStatus.draft,
        nullable=False,
    )

    parcel = relationship("LandParcel", foreign_keys=[parcel_id])
    assessor = relationship("User", foreign_keys=[assessed_by])
    payments = relationship("Payment", back_populates="compensation", lazy="selectin")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compensation_id = Column(
        UUID(as_uuid=True), ForeignKey("compensation.id"), nullable=False, index=True
    )
    land_owner_id = Column(
        UUID(as_uuid=True), ForeignKey("land_owners.id"), nullable=False, index=True
    )
    amount = Column(Numeric(18, 2), nullable=False)
    pfms_reference = Column(String(100), nullable=True)
    bank_verification_status = Column(
        SAEnum(BankVerificationStatus, name="bank_verification_status_enum"),
        default=BankVerificationStatus.pending,
        nullable=False,
    )
    payment_status = Column(
        SAEnum(PaymentStatus, name="payment_status_enum"),
        default=PaymentStatus.pending,
        nullable=False,
    )
    disbursed_date = Column(DateTime(timezone=True), nullable=True)

    compensation = relationship("Compensation", back_populates="payments")
    land_owner = relationship("LandOwner", foreign_keys=[land_owner_id])
