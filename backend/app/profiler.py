"""Performance profiling and optimization utilities."""
import time
from functools import wraps
from typing import Any, Callable, Optional

from app.logger import get_logger
from app.metrics import get_metrics_collector

logger = get_logger(__name__)


class PerformanceProfile:
    """Store performance profile data."""
    
    def __init__(self, name: str):
        """Initialize profile."""
        self.name = name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
    
    def stop(self) -> float:
        """Stop profiling and return duration in ms."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        return self.duration_ms
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
        }


class Profiler:
    """Application profiler for performance analysis."""
    
    def __init__(self, name: str = "default"):
        """Initialize profiler."""
        self.name = name
        self.profiles: list[PerformanceProfile] = []
        self.slow_operation_threshold_ms = 1000
    
    def profile(self, operation_name: str):
        """Context manager for profiling operations."""
        class ProfileContext:
            def __init__(context_self, profiler: "Profiler", op_name: str):
                context_self.profiler = profiler
                context_self.op_name = op_name
                context_self.profile = PerformanceProfile(op_name)
            
            def __enter__(context_self):
                return context_self.profile
            
            def __exit__(context_self, exc_type, exc_val, exc_tb):
                duration = context_self.profile.stop()
                context_self.profiler.profiles.append(context_self.profile)
                
                if duration > context_self.profiler.slow_operation_threshold_ms:
                    logger.warning(
                        f"Slow operation detected: {context_self.op_name} "
                        f"({duration:.2f}ms)"
                    )
        
        return ProfileContext(self, operation_name)
    
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.profile(func.__name__) as prof:
                result = func(*args, **kwargs)
                duration = prof.duration_ms
                
                # Record to metrics
                collector = get_metrics_collector()
                collector.record_metric(
                    collector.Metric(
                        name=f"func_{func.__name__}",
                        value=duration,
                        unit="ms",
                        metric_type="PERFORMANCE",
                        tags={"function": func.__name__},
                    )
                )
                
                return result
        
        return wrapper
    
    def get_statistics(self) -> dict[str, Any]:
        """Get profiling statistics."""
        if not self.profiles:
            return {
                "total_profiles": 0,
                "slow_operations": 0,
            }
        
        durations = [p.duration_ms for p in self.profiles]
        slow_ops = sum(1 for d in durations if d > self.slow_operation_threshold_ms)
        
        return {
            "total_profiles": len(self.profiles),
            "slow_operations": slow_ops,
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "total_duration_ms": sum(durations),
        }
    
    def get_slowest_operations(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get slowest operations."""
        sorted_profiles = sorted(
            self.profiles,
            key=lambda p: p.duration_ms,
            reverse=True,
        )
        return [p.to_dict() for p in sorted_profiles[:limit]]
    
    def clear(self) -> None:
        """Clear profiling data."""
        self.profiles = []


# Global profiler instance
default_profiler = Profiler()


def get_profiler(name: str = "default") -> Profiler:
    """Get or create a profiler."""
    if name == "default":
        return default_profiler
    return Profiler(name)
