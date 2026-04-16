"""Utilities for generating and managing request IDs."""
import uuid
from typing import Optional


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def extract_request_id(request_id: Optional[str]) -> str:
    """Extract or generate request ID from header."""
    if request_id and request_id.strip():
        return request_id.strip()
    return generate_request_id()
