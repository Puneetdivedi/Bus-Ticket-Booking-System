"""Performance monitoring and profiling utilities."""
import time
import logging
from functools import wraps
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics."""

    @staticmethod
    def measure_time(operation_name: str) -> Callable:
        """Decorator to measure function execution time."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
                    logger.debug(
                        f"{operation_name} completed",
                        extra={
                            "operation": operation_name,
                            "duration_ms": round(elapsed_time, 2),
                        },
                    )
                    
                    # Log warning if slow
                    if elapsed_time > 1000:  # More than 1 second
                        logger.warning(
                            f"{operation_name} took {round(elapsed_time, 2)}ms (slow)",
                            extra={
                                "operation": operation_name,
                                "duration_ms": round(elapsed_time, 2),
                                "slow": True,
                            },
                        )
            return wrapper
        return decorator

    @staticmethod
    @contextmanager
    def timer(operation_name: str):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_time = (time.perf_counter() - start_time) * 1000
            logger.debug(
                f"{operation_name} completed in {round(elapsed_time, 2)}ms",
                extra={
                    "operation": operation_name,
                    "duration_ms": round(elapsed_time, 2),
                },
            )


class DatabasePerformance:
    """Database-specific performance monitoring."""

    @staticmethod
    def get_optimization_tips(query_time_ms: float) -> list[str]:
        """Get optimization suggestions based on query time."""
        tips = []
        
        if query_time_ms > 1000:
            tips.append("Query took >1s. Consider adding indexes.")
        if query_time_ms > 100:
            tips.append("Query took >100ms. Analyze query execution plan.")
        if query_time_ms > 10:
            tips.append("Query took >10ms. Consider caching results.")
        
        return tips

    @staticmethod
    def log_slow_query(query: str, duration_ms: float, threshold_ms: float = 100):
        """Log slow database queries."""
        if duration_ms > threshold_ms:
            logger.warning(
                "Slow database query detected",
                extra={
                    "query": query[:100],  # First 100 chars
                    "duration_ms": round(duration_ms, 2),
                    "threshold_ms": threshold_ms,
                },
            )


class CachePerformance:
    """Cache hit/miss tracking."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
    
    def record_hit(self):
        """Record cache hit."""
        self.hits += 1
    
    def record_miss(self):
        """Record cache miss."""
        self.misses += 1
    
    def get_hit_ratio(self) -> float:
        """Get cache hit ratio."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": self.hits + self.misses,
            "hit_ratio_percent": round(self.get_hit_ratio(), 2),
        }


# Global cache performance tracker
cache_stats = CachePerformance()


def get_cache_statistics() -> dict:
    """Get global cache statistics."""
    return cache_stats.get_stats()
