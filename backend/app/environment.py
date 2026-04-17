"""Environment validation and startup checks for production readiness."""
import sys
from typing import Any, Optional

from app.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


class EnvironmentValidator:
    """Validate environment configuration on startup."""

    def __init__(self):
        """Initialize validator."""
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def validate_all(self) -> bool:
        """
        Run all validations.
        
        Returns:
            True if all validations pass, False otherwise
        """
        self.validate_environment()
        self.validate_database_config()
        self.validate_security_settings()
        self.validate_logging_settings()
        
        self._report()
        
        return len(self.errors) == 0

    def validate_environment(self) -> None:
        """Validate environment configuration."""
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"API key enabled: {settings.API_KEY_ENABLED}")
        
        if settings.DEBUG and settings.ENVIRONMENT == "production":
            self.errors.append(
                "DEBUG=true in production environment - potential security risk"
            )
        
        if settings.ENVIRONMENT not in ["development", "staging", "production"]:
            self.warnings.append(f"Unknown environment: {settings.ENVIRONMENT}")

    def validate_database_config(self) -> None:
        """Validate database configuration."""
        if not settings.DATABASE_URL:
            self.errors.append("DATABASE_URL not configured")
            return
        
        logger.info(f"Database: {self._mask_connection_string(settings.DATABASE_URL)}")
        
        if "sqlite:///" in settings.DATABASE_URL and settings.ENVIRONMENT == "production":
            self.warnings.append(
                "SQLite database in production - consider using PostgreSQL"
            )

    def validate_security_settings(self) -> None:
        """Validate security-related settings."""
        if settings.API_KEY_ENABLED:
            if not settings.API_KEY or settings.API_KEY == "your-secret-key":
                self.errors.append("API_KEY_ENABLED but API_KEY is not set properly")
            else:
                logger.info("API key authentication: ENABLED")
        else:
            if settings.ENVIRONMENT == "production":
                self.warnings.append(
                    "API key authentication disabled in production"
                )
            logger.info("API key authentication: DISABLED")
        
        if not settings.CORS_ORIGINS_LIST:
            self.warnings.append("CORS_ORIGINS is empty - CORS requests will be blocked")

    def validate_logging_settings(self) -> None:
        """Validate logging configuration."""
        logger.info(f"Log level: {settings.LOG_LEVEL}")
        logger.info(f"Log format: {settings.LOG_FORMAT}")
        
        if settings.LOG_LEVEL == "DEBUG" and settings.ENVIRONMENT == "production":
            self.warnings.append("DEBUG log level in production may expose sensitive data")

    def _mask_connection_string(self, connection_string: str) -> str:
        """Mask sensitive information in connection string."""
        # Mask password
        if "@" in connection_string:
            parts = connection_string.split("@")
            if len(parts) == 2:
                auth_part = parts[0]
                host_part = parts[1]
                if ":" in auth_part:
                    user, _ = auth_part.rsplit(":", 1)
                    return f"{user}:***@{host_part}"
        return connection_string

    def _report(self) -> None:
        """Report validation results."""
        if self.errors:
            logger.error(f"Validation errors ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"  ✗ {error}")
        
        if self.warnings:
            logger.warning(f"Validation warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  ⚠ {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("✓ All environment validations passed")


def validate_environment_on_startup() -> bool:
    """
    Validate environment on application startup.
    
    Returns:
        True if validation passes, False otherwise
    """
    validator = EnvironmentValidator()
    return validator.validate_all()
