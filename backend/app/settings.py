"""Application settings and configuration management."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # App Configuration
    APP_NAME: str = "Bus Ticket Booking System API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./database/bus_booking.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Security Configuration
    API_KEY_ENABLED: bool = True
    API_KEY: str = "dev-api-key-change-in-production"
    API_RATE_LIMIT: str = "100/minute"

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: str | None = None

    # Feature Flags
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True

    # Business Logic
    MAX_SEATS_PER_BOOKING: int = 6
    TOTAL_SEATS: int = 60  # 4 columns × 15 rows

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()
