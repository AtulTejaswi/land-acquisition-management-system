import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class State(Base, TimestampMixin):
    __tablename__ = "states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)
    region = Column(String(50), nullable=True)

    districts = relationship("District", back_populates="state", lazy="selectin")
    users = relationship("User", back_populates="state", lazy="selectin")


class District(Base, TimestampMixin):
    __tablename__ = "districts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)

    state = relationship("State", back_populates="districts")
    villages = relationship("Village", back_populates="district", lazy="selectin")
    users = relationship("User", back_populates="district", lazy="selectin")

    __table_args__ = (UniqueConstraint("state_id", "name", name="uq_district_state_name"),)


class Village(Base, TimestampMixin):
    __tablename__ = "villages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=False, index=True)
    tehsil = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)

    district = relationship("District", back_populates="villages")
