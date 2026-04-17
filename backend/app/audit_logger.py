"""Audit logging for compliance, security events, and critical operations."""
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from app.logger import get_logger
from app.utils import generate_request_id

audit_logger = get_logger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events for compliance tracking."""

    BOOKING_CREATED = "BOOKING_CREATED"
    BOOKING_UPDATED = "BOOKING_UPDATED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_EXPORTED = "BOOKING_EXPORTED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    API_KEY_VALIDATED = "API_KEY_VALIDATED"
    API_KEY_INVALID = "API_KEY_INVALID"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DATA_VALIDATION_FAILED = "DATA_VALIDATION_FAILED"
    SECURITY_BREACH_ATTEMPT = "SECURITY_BREACH_ATTEMPT"
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    ERROR_OCCURRED = "ERROR_OCCURRED"


class AuditEvent:
    """Structured audit event for compliance logging."""

    def __init__(
        self,
        event_type: AuditEventType,
        timestamp: Optional[datetime] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[dict[str, Any]] = None,
        severity: str = "INFO",
    ):
        """Initialize audit event."""
        self.event_id = generate_request_id()
        self.event_type = event_type
        self.timestamp = timestamp or datetime.utcnow()
        self.request_id = request_id
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.status = status
        self.details = details or {}
        self.severity = severity

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "request_id": str(self.request_id) if self.request_id else None,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "status": self.status,
            "severity": self.severity,
            "details": self.details,
        }

    def log(self) -> None:
        """Log the audit event."""
        log_level = getattr(logging, self.severity, logging.INFO)
        audit_logger.log(
            log_level,
            f"AUDIT: {self.event_type.value} - {self.action or self.resource_type}",
            extra={"audit_event": self.to_dict()},
        )


class AuditLogger:
    """High-level audit logging interface."""

    @staticmethod
    def log_booking_created(
        booking_id: str,
        mobile_number: str,
        seat_count: int,
        request_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log booking creation event."""
        event = AuditEvent(
            event_type=AuditEventType.BOOKING_CREATED,
            request_id=request_id,
            resource_type="Booking",
            resource_id=booking_id,
            action="CREATE",
            details={
                "mobile_number_hash": hash(mobile_number),
                "seat_count": seat_count,
                **(details or {}),
            },
        )
        event.log()

    @staticmethod
    def log_booking_cancelled(
        booking_id: str,
        reason: str,
        request_id: Optional[str] = None,
    ) -> None:
        """Log booking cancellation event."""
        event = AuditEvent(
            event_type=AuditEventType.BOOKING_CANCELLED,
            request_id=request_id,
            resource_type="Booking",
            resource_id=booking_id,
            action="CANCEL",
            details={"reason": reason},
        )
        event.log()

    @staticmethod
    def log_authentication_failure(
        error: str,
        request_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log authentication failure event."""
        event = AuditEvent(
            event_type=AuditEventType.AUTHENTICATION_FAILED,
            request_id=request_id,
            action="AUTHENTICATE",
            status="FAILED",
            severity="WARNING",
            details={"error": error, **(details or {})},
        )
        event.log()

    @staticmethod
    def log_rate_limit_exceeded(
        client_ip: str,
        endpoint: str,
        limit: int,
        request_id: Optional[str] = None,
    ) -> None:
        """Log rate limit exceeded event."""
        event = AuditEvent(
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            request_id=request_id,
            action="RATE_LIMIT_CHECK",
            status="FAILED",
            severity="WARNING",
            details={
                "client_ip": client_ip,
                "endpoint": endpoint,
                "limit": limit,
            },
        )
        event.log()

    @staticmethod
    def log_security_breach_attempt(
        attempt_type: str,
        details: dict[str, Any],
        request_id: Optional[str] = None,
    ) -> None:
        """Log potential security breach attempt."""
        event = AuditEvent(
            event_type=AuditEventType.SECURITY_BREACH_ATTEMPT,
            request_id=request_id,
            action="SECURITY_CHECK",
            status="FAILED",
            severity="CRITICAL",
            details={"attempt_type": attempt_type, **details},
        )
        event.log()

    @staticmethod
    def log_system_startup(environment: str, version: str) -> None:
        """Log system startup event."""
        event = AuditEvent(
            event_type=AuditEventType.SYSTEM_STARTUP,
            action="STARTUP",
            severity="INFO",
            details={"environment": environment, "version": version},
        )
        event.log()

    @staticmethod
    def log_error(
        error_type: str,
        error_message: str,
        request_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log error event."""
        event = AuditEvent(
            event_type=AuditEventType.ERROR_OCCURRED,
            request_id=request_id,
            action="ERROR",
            status="FAILED",
            severity="ERROR",
            details={
                "error_type": error_type,
                "error_message": error_message,
                **(details or {}),
            },
        )
        event.log()
