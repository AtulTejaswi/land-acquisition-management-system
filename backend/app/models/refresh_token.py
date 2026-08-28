import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    """Stores issued refresh tokens for server-side revocation and rotation.

    Each row tracks one issued refresh token. On use (rotation) the old row is
    marked ``revoked_at`` and a new row is inserted. Logout marks all active
    rows for the user as revoked.
    """

    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    jti = Column(String(36), nullable=False, unique=True, index=True)
    token_hash = Column(String(64), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_refresh_tokens_user_active", "user_id", "revoked_at"),
    )
