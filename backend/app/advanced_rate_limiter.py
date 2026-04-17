"""Advanced rate limiting with multiple strategies and endpoints."""
from datetime import datetime, timedelta
from typing import Optional

from app.logger import get_logger

logger = get_logger(__name__)


class RateLimitEntry:
    """Track rate limit per client."""
    
    def __init__(self, limit: int, window_seconds: int):
        """Initialize rate limit entry."""
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: list[datetime] = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests outside window
        self.requests = [
            req_time for req_time in self.requests
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.requests) >= self.limit:
            return False
        
        # Record new request
        self.requests.append(now)
        return True
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window."""
        return max(0, self.limit - len(self.requests))
    
    def get_reset_time(self) -> datetime:
        """Get when limit resets."""
        if not self.requests:
            return datetime.utcnow()
        oldest = min(self.requests)
        return oldest + timedelta(seconds=self.window_seconds)


class AdvancedRateLimiter:
    """Advanced rate limiting with per-endpoint and per-client limits."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.clients: dict[str, dict[str, RateLimitEntry]] = {}
        
        # Default endpoint limits (requests per minute)
        self.endpoint_limits = {
            "GET /api/bookings": 60,
            "POST /api/bookings": 30,
            "GET /api/bookings/seat-map": 120,
            "GET /api/health": 300,
            "GET /api/metrics": 60,
        }
        
        self.default_limit = 30
        self.default_window = 60
    
    def is_allowed(
        self,
        client_id: str,
        endpoint: str,
        custom_limit: Optional[int] = None,
    ) -> tuple[bool, dict[str, int]]:
        """
        Check if client request is allowed.
        
        Returns:
            (allowed, headers_dict) tuple
        """
        # Get limit for endpoint
        limit = custom_limit or self.endpoint_limits.get(
            endpoint,
            self.default_limit,
        )
        window = self.default_window
        
        # Initialize client tracker
        if client_id not in self.clients:
            self.clients[client_id] = {}
        
        # Get or create entry for endpoint
        if endpoint not in self.clients[client_id]:
            self.clients[client_id][endpoint] = RateLimitEntry(limit, window)
        
        entry = self.clients[client_id][endpoint]
        allowed = entry.is_allowed()
        
        # Generate rate limit headers
        remaining = entry.get_remaining()
        reset_time = int(entry.get_reset_time().timestamp())
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id} on {endpoint}",
            )
        
        return allowed, headers
    
    def get_status(self, client_id: str) -> dict:
        """Get rate limit status for client."""
        if client_id not in self.clients:
            return {"status": "no_requests"}
        
        endpoints = {}
        for endpoint, entry in self.clients[client_id].items():
            endpoints[endpoint] = {
                "limit": entry.limit,
                "remaining": entry.get_remaining(),
                "requests_in_window": len(entry.requests),
                "reset_time": entry.get_reset_time().isoformat(),
            }
        
        return {
            "client_id": client_id,
            "endpoints": endpoints,
        }
    
    def reset_client(self, client_id: str) -> bool:
        """Reset rate limit for client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Rate limit reset for {client_id}")
            return True
        return False
    
    def cleanup_old_entries(self, older_than_minutes: int = 60) -> int:
        """Clean up old rate limit entries."""
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        removed_count = 0
        
        clients_to_remove = []
        for client_id, endpoints in self.clients.items():
            # If no requests in window, mark for removal
            if not any(
                entry.requests
                for entry in endpoints.values()
            ):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.clients[client_id]
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} inactive rate limit entries")
        
        return removed_count


# Global rate limiter instance
advanced_rate_limiter = AdvancedRateLimiter()


def get_rate_limiter() -> AdvancedRateLimiter:
    """Get global rate limiter."""
    return advanced_rate_limiter
