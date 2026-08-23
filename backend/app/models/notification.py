import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum


class NotificationType(str, enum.Enum):
    info = "info"
    success = "success"
    warning = "warning"
    alert = "alert"


class NotificationChannel(str, enum.Enum):
    in_app = "in_app"
    email = "email"
    sms = "sms"


class NotificationApp(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=True)
    type = Column(
        SAEnum(NotificationType, name="notification_type_enum"),
        default=NotificationType.info,
        nullable=False,
    )
    channel = Column(
        SAEnum(NotificationChannel, name="notification_channel_enum"),
        default=NotificationChannel.in_app,
        nullable=False,
    )
    is_read = Column(Boolean, default=False, nullable=False)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
