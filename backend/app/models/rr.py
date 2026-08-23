import uuid
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class DisplacedStatus(str, enum.Enum):
    not_displaced = "not_displaced"
    partially = "partially"
    fully = "fully"


class BenefitStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    provided = "provided"


class RRStage(str, enum.Enum):
    identification = "identification"
    verification = "verification"
    benefit_disbursement = "benefit_disbursement"
    resettled = "resettled"


class RehabilitationFamily(Base, TimestampMixin):
    __tablename__ = "rehabilitation_families"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    family_head_name = Column(String(200), nullable=False)
    family_id_number = Column(String(50), nullable=True)
    member_count = Column(Integer, nullable=True)
    displaced_status = Column(
        SAEnum(DisplacedStatus, name="displaced_status_enum"),
        default=DisplacedStatus.not_displaced,
        nullable=False,
    )
    housing_benefit_status = Column(
        SAEnum(BenefitStatus, name="rr_housing_benefit_enum"),
        default=BenefitStatus.not_started,
        nullable=False,
    )
    employment_benefit_status = Column(
        SAEnum(BenefitStatus, name="rr_employment_benefit_enum"),
        default=BenefitStatus.not_started,
        nullable=False,
    )
    monetary_benefit_amount = Column(Numeric(18, 2), nullable=True)
    current_stage = Column(
        SAEnum(RRStage, name="rr_stage_enum"), default=RRStage.identification, nullable=False
    )
    progress_percentage = Column(Integer, default=0)

    project = relationship("Project", foreign_keys=[project_id])
