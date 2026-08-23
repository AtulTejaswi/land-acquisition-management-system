import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    remarks = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)

    performer = relationship("User", foreign_keys=[performed_by])
