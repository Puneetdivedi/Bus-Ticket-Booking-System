"""Authentication and security utilities."""
from fastapi import Depends, Header

from app.exceptions import UnauthorizedException
from app.settings import settings


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Verify API key from request header."""
    if not settings.API_KEY_ENABLED:
        return "default"

    if not x_api_key:
        raise UnauthorizedException("API key is missing (X-API-Key header required)")

    if x_api_key != settings.API_KEY:
        raise UnauthorizedException("Invalid API key")

    return x_api_key


# Dependency injection for optional API key verification
async def optional_api_key(x_api_key: str = Header(None)) -> str | None:
    """Optional API key verification."""
    if not x_api_key:
        return None

    if settings.API_KEY_ENABLED and x_api_key != settings.API_KEY:
        raise UnauthorizedException("Invalid API key")

    return x_api_key
