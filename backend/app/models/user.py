import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    phone = Column(String(15), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, index=True)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True, index=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True, index=True)
    agency_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    role = relationship("Role", back_populates="users")
    state = relationship("State", back_populates="users")
    district = relationship("District", back_populates="users")

    @property
    def role_name(self) -> str:
        return self.role.name if self.role else ""
