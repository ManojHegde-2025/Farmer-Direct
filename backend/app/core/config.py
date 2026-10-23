"""Application configuration loaded from environment variables."""

from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://farmerdirect:fd_dev_password_2026"
        "@localhost:5433/farmer_direct_db"
    )

    # JWT / Auth
    SECRET_KEY: str = "dev-secret-key-farmerdirect-2026-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # File uploads
    UPLOAD_DIR: str = "./uploads"

    # App metadata
    APP_NAME: str = "FarmerDirect API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @model_validator(mode="after")
    def normalize_database_url(self):
        url = self.DATABASE_URL.strip()

        if not url:
            raise ValueError("DATABASE_URL is missing or empty")

        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://"):]

        elif url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]

        self.DATABASE_URL = url
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()