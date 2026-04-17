"""Rate limiting and throttling configuration."""
from typing import Dict, Tuple
from enum import Enum


class RateLimitTier(str, Enum):
    """Rate limiting tiers."""
    
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RateLimitConfig:
    """Rate limit configuration for different tiers."""
    
    # Requests per minute per IP
    LIMITS: Dict[RateLimitTier, int] = {
        RateLimitTier.FREE: 10,
        RateLimitTier.BASIC: 60,
        RateLimitTier.PREMIUM: 300,
        RateLimitTier.ENTERPRISE: 1000,
    }
    
    # Burst allowance (requests per second)
    BURST_SIZE: Dict[RateLimitTier, int] = {
        RateLimitTier.FREE: 2,
        RateLimitTier.BASIC: 5,
        RateLimitTier.PREMIUM: 20,
        RateLimitTier.ENTERPRISE: 50,
    }
    
    # Time window in seconds
    TIME_WINDOW = 60


class EndpointRateLimits:
    """Rate limits for specific endpoints."""
    
    # Format: "endpoint_path": (requests_per_minute, burst_size)
    ENDPOINT_LIMITS = {
        "/api/bookings": (100, 5),
        "/api/bookings/seat-map": (200, 10),
        "/api/bookings/boarding-sequence": (100, 5),
        "/api/bookings/export/csv": (50, 2),
        "/api/health": (1000, 50),  # Health checks can be frequent
    }

    @staticmethod
    def get_limit(endpoint: str) -> Tuple[int, int]:
        """Get rate limit for endpoint."""
        return EndpointRateLimits.ENDPOINT_LIMITS.get(
            endpoint,
            (100, 5),  # Default limit
        )


class ThrottleStrategies:
    """Different throttling strategies."""
    
    @staticmethod
    def fixed_window(
        current_count: int,
        limit: int,
        window_start: float,
        window_size: float,
    ) -> Tuple[bool, Dict[str, int]]:
        """Fixed window throttling strategy."""
        import time
        
        current_time = time.time()
        if current_time - window_start > window_size:
            # New window
            return True, {
                "remaining": limit - 1,
                "reset_in": int(window_size),
                "limit": limit,
            }
        
        if current_count >= limit:
            # Limit exceeded
            return False, {
                "remaining": 0,
                "reset_in": int(window_size - (current_time - window_start)),
                "limit": limit,
            }
        
        # Within limit
        return True, {
            "remaining": limit - current_count - 1,
            "reset_in": int(window_size - (current_time - window_start)),
            "limit": limit,
        }

    @staticmethod
    def token_bucket(
        tokens: float,
        capacity: float,
        refill_rate: float,
        last_refill: float,
    ) -> Tuple[bool, Dict[str, float]]:
        """Token bucket throttling strategy."""
        import time
        
        current_time = time.time()
        time_passed = current_time - last_refill
        
        # Refill tokens
        new_tokens = min(
            capacity,
            tokens + (refill_rate * time_passed),
        )
        
        if new_tokens >= 1:
            # Request allowed
            return True, {
                "tokens_remaining": new_tokens - 1,
                "capacity": capacity,
                "refill_rate": refill_rate,
            }
        
        # Request denied
        return False, {
            "tokens_remaining": 0,
            "capacity": capacity,
            "wait_seconds": (1 - new_tokens) / refill_rate,
        }


class RateLimitResponse:
    """Standard rate limit response headers."""
    
    @staticmethod
    def get_headers(
        limit: int,
        remaining: int,
        reset_in: int,
    ) -> Dict[str, str]:
        """Get standard rate limit headers."""
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(reset_in),
        }


# Default configuration
DEFAULT_RATE_LIMIT = 100  # requests per minute
DEFAULT_BURST_SIZE = 5    # requests per second
DEFAULT_STRATEGY = "fixed_window"  # or "token_bucket"
