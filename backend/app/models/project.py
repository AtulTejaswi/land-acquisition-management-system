import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    ForeignKey,
    Enum as SAEnum,
    Text,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class ProjectPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    active = "active"
    delayed = "delayed"
    completed = "completed"


class MilestoneStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"


STAGES = [
    "project_proposal",
    "dpr_upload",
    "land_requirement",
    "state_review",
    "district_verification",
    "gis_mapping",
    "legal_notification",
    "objection_handling",
    "compensation_assessment",
    "award_declaration",
    "payment_disbursement",
    "physical_possession",
    "rehabilitation_resettlement",
    "project_completion",
]


class Ministry(Base):
    __tablename__ = "ministries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False)

    projects = relationship("Project", back_populates="ministry")


class ProjectCategory(Base):
    __tablename__ = "project_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)

    projects = relationship("Project", back_populates="category")


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    ministry_id = Column(
        UUID(as_uuid=True), ForeignKey("ministries.id"), nullable=False, index=True
    )
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("project_categories.id"), nullable=False, index=True
    )
    implementing_agency_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False, index=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    dpr_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    estimated_budget = Column(Numeric(18, 2), nullable=True)
    estimated_land_required_hectares = Column(Numeric(12, 3), nullable=True)
    priority = Column(
        SAEnum(ProjectPriority, name="project_priority_enum"),
        default=ProjectPriority.medium,
        nullable=False,
    )
    current_stage = Column(String(50), default="project_proposal", nullable=False, index=True)
    status = Column(
        SAEnum(ProjectStatus, name="project_status_enum"),
        default=ProjectStatus.draft,
        nullable=False,
        index=True,
    )
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    ministry = relationship("Ministry", back_populates="projects")
    category = relationship("ProjectCategory", back_populates="projects")
    state = relationship("State", back_populates="projects", foreign_keys=[state_id])
    district = relationship("District", back_populates="projects", foreign_keys=[district_id])
    milestones = relationship("Milestone", back_populates="project", lazy="selectin")
    parcels = relationship("LandParcel", back_populates="project", lazy="selectin")


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage = Column(String(50), nullable=False)
    title = Column(String(300), nullable=False)
    planned_date = Column(DateTime(timezone=True), nullable=True)
    actual_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        SAEnum(MilestoneStatus, name="milestone_status_enum"),
        default=MilestoneStatus.pending,
        nullable=False,
    )
    responsible_officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    remarks = Column(Text, nullable=True)

    project = relationship("Project", back_populates="milestones")
    responsible_officer = relationship("User", foreign_keys=[responsible_officer_id])
