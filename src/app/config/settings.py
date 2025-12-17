"""
Application Configuration using Pydantic Settings.
Centralizes all environment variables and configuration.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Project Info
    PROJECT_NAME: str = "Future Work Readiness API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for the Future of Work Readiness Platform"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS - Origins that can access the API
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:5173",
        "https://fwr-front-end.vercel.app",
    ]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Use dependency injection in FastAPI routes.
    """
    return Settings()


# Global settings instance for direct import
settings = get_settings()

