"""Request validation and schema enforcement for API contracts."""
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from app.logger import get_logger

logger = get_logger(__name__)


class APIRequest(BaseModel):
    """Base API request model with validation."""
    
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[str] = Field(None, description="Request timestamp")
    
    class Config:
        """Pydantic config."""
        str_strip_whitespace = True
        validate_assignment = True


class HealthCheckRequest(APIRequest):
    """Health check request validation."""
    
    include_details: bool = Field(
        default=False,
        description="Include detailed health information",
    )


class MetricsRequest(APIRequest):
    """Metrics request validation."""
    
    metric_type: Optional[str] = Field(
        None,
        description="Filter by metric type",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Number of metrics to retrieve",
    )
    minutes: int = Field(
        default=60,
        ge=1,
        le=10080,
        description="Historical window in minutes",
    )


class BookingExportRequest(APIRequest):
    """Booking export request validation."""
    
    format: str = Field(
        default="csv",
        regex="^(csv|json|xml)$",
        description="Export format",
    )
    include_cancelled: bool = Field(
        default=False,
        description="Include cancelled bookings",
    )
    date_from: Optional[str] = Field(
        None,
        description="Export from date (YYYY-MM-DD)",
    )
    date_to: Optional[str] = Field(
        None,
        description="Export to date (YYYY-MM-DD)",
    )


class PaginationRequest(BaseModel):
    """Pagination parameters."""
    
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Number of records to return",
    )
    sort_by: Optional[str] = Field(
        default="created_at",
        description="Field to sort by",
    )
    sort_order: str = Field(
        default="desc",
        regex="^(asc|desc)$",
        description="Sort order",
    )


class APIResponse(BaseModel):
    """Standard API response model."""
    
    success: bool = Field(..., description="Request success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    timestamp: str = Field(..., description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation successful",
                "data": {},
                "timestamp": "2026-04-18T10:30:00",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class ErrorResponse(APIResponse):
    """Error response model."""
    
    success: bool = False
    details: Optional[dict[str, Any]] = Field(
        None,
        description="Additional error details",
    )


class ValidatedRequest:
    """Request validator utility."""
    
    @staticmethod
    def validate_pagination(skip: int, limit: int) -> tuple[int, int]:
        """Validate pagination parameters."""
        skip = max(0, skip)
        limit = max(1, min(1000, limit))
        return skip, limit
    
    @staticmethod
    def validate_export_format(format_str: str) -> str:
        """Validate export format."""
        valid_formats = ["csv", "json", "xml"]
        if format_str.lower() not in valid_formats:
            raise ValueError(f"Invalid format: {format_str}. Must be one of {valid_formats}")
        return format_str.lower()
    
    @staticmethod
    def validate_sort_order(sort_order: str) -> str:
        """Validate sort order."""
        order = sort_order.lower()
        if order not in ["asc", "desc"]:
            raise ValueError(f"Invalid sort order: {sort_order}. Must be 'asc' or 'desc'")
        return order
