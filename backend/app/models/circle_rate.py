import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class CircleRate(Base, TimestampMixin):
    __tablename__ = "circle_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=False, index=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=False, index=True)
    land_type = Column(String(30), nullable=False)
    rate_per_hectare = Column(Numeric(18, 2), nullable=False)
    financial_year = Column(String(10), nullable=False)

    state = relationship("State")
    district = relationship("District")
