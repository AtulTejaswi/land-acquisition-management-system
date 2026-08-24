from pydantic_settings import BaseSettings
from typing import List
import os
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://nlams:nlams_secret_2024@localhost:5432/nlams_db"
    SYNC_DATABASE_URL: str = "postgresql://nlams:nlams_secret_2024@localhost:5432/nlams_db"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = os.environ.get(
        "UPLOAD_DIR",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "uploads",
        ),
    )
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def _validate_settings(settings: Settings) -> Settings:
    """Validate and enforce SECRET_KEY requirements."""
    if not settings.SECRET_KEY:
        if settings.ENVIRONMENT == "production":
            raise ValueError(
                "SECRET_KEY environment variable is required in production. "
                "Set it in your .env file or environment. "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(64))"'
            )
        else:
            # Dev-only: auto-generate an ephemeral key
            settings.SECRET_KEY = secrets.token_urlsafe(64)
            logger.warning(
                "⚠️  No SECRET_KEY set — auto-generating ephemeral dev key. "
                "Sessions will be invalidated on restart. "
                "Set SECRET_KEY in .env for persistent sessions."
            )
    return settings


settings = _validate_settings(Settings())
