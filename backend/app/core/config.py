from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://nlams:nlams_secret_2024@localhost:5432/nlams_db"
    SYNC_DATABASE_URL: str = "postgresql://nlams:nlams_secret_2024@localhost:5432/nlams_db"
    SECRET_KEY: str = "nlams-super-secret-key-change-in-production-2024-hackathon"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = os.environ.get(
        "UPLOAD_DIR",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads"
        ),
    )
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
