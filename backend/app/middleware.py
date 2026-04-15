"""Middleware for logging, security, and monitoring."""
import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        request_id = request.headers.get("x-request-id", "unknown")
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Request failed: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(process_time * 1000, 2),
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(process_time * 1000, 2),
            },
        )

        # Add response headers
        response.headers["x-request-id"] = request_id
        response.headers["x-process-time"] = str(round(process_time * 1000, 2))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
