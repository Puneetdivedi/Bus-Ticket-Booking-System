"""API response decorators and utilities."""
from functools import wraps
from typing import Any, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.utils import extract_request_id


def add_request_context(func: Callable) -> Callable:
    """Decorator to add request context to response headers."""

    @wraps(func)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Response:
        request_id = extract_request_id(request.headers.get("x-request-id"))
        response = await func(request, *args, **kwargs)

        if isinstance(response, Response):
            response.headers["x-request-id"] = request_id

        return response

    return wrapper
