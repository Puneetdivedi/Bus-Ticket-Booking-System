"""Custom exception classes and error handlers."""
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "APP_ERROR",
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception."""
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize validation exception."""
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: Any):
        """Initialize not found exception."""
        super().__init__(
            message=f"{resource} with id {identifier} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictException(AppException):
    """Resource conflict exception (e.g., duplicate booking)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize conflict exception."""
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details,
        )


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized"):
        """Initialize unauthorized exception."""
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, message: str = "Forbidden"):
        """Initialize forbidden exception."""
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class RateLimitException(AppException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded"):
        """Initialize rate limit exception."""
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException and return JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions and return JSON response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_ERROR",
                "details": {},
            }
        },
    )
