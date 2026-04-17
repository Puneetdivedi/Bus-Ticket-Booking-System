"""Middleware for request/response size limits and validation."""
from typing import Callable

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.audit_logger import AuditLogger, AuditEventType
from app.logger import get_logger

logger = get_logger(__name__)

# Size limits (in bytes)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_BODY_SIZE_FOR_LOGGING = 1024  # 1 KB for logging


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request size limits."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size before processing."""
        try:
            # Get content length from headers
            content_length = request.headers.get("content-length")
            
            if content_length and int(content_length) > MAX_REQUEST_SIZE:
                request_id = request.headers.get("x-request-id", "unknown")
                logger.warning(
                    f"Request size limit exceeded: {content_length} bytes",
                    extra={
                        "request_id": request_id,
                        "content_length": content_length,
                        "max_size": MAX_REQUEST_SIZE,
                    },
                )
                
                # Log security event
                AuditLogger.log_security_breach_attempt(
                    attempt_type="REQUEST_SIZE_LIMIT_EXCEEDED",
                    details={
                        "content_length": int(content_length),
                        "max_size": MAX_REQUEST_SIZE,
                        "endpoint": request.url.path,
                    },
                    request_id=request_id,
                )
                
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": "Request body too large",
                        "error_code": "REQUEST_TOO_LARGE",
                        "max_size_bytes": MAX_REQUEST_SIZE,
                    },
                )
            
            response = await call_next(request)
            return response
            
        except ValueError:
            # Invalid content-length header
            logger.error("Invalid content-length header", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Invalid content-length header",
                    "error_code": "INVALID_HEADER",
                },
            )


class ResponseHeaderValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate and add security response headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate and enhance response headers."""
        response = await call_next(request)
        
        # Add timestamp header
        response.headers["X-Response-Time"] = str(request.headers.get("x-request-id", ""))
        
        # Add API version
        response.headers["X-API-Version"] = "1.1.2"
        
        # Add timestamp
        from datetime import datetime
        response.headers["X-Timestamp"] = datetime.utcnow().isoformat()
        
        return response


class EnvironmentValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate request environment and configuration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request environment."""
        request_id = request.headers.get("x-request-id", "unknown")
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-original-forwarded-for",
        ]
        
        forwarded_ips = []
        for header in suspicious_headers:
            if header in request.headers:
                forwarded_ips.append(request.headers.get(header))
        
        if forwarded_ips:
            logger.debug(
                f"Request forwarded through proxy",
                extra={
                    "request_id": request_id,
                    "forwarded_ips": forwarded_ips,
                },
            )
        
        response = await call_next(request)
        return response
