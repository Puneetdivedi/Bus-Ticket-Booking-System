"""API metrics collection and monitoring for performance tracking."""
import time
from datetime import datetime, timedelta
from typing import Any, Optional

from app.logger import get_logger

logger = get_logger(__name__)


class MetricType:
    """Metric types for tracking."""
    
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"
    PERFORMANCE = "PERFORMANCE"
    DATABASE = "DATABASE"
    CACHE = "CACHE"


class Metric:
    """Individual metric data point."""
    
    def __init__(
        self,
        name: str,
        value: float,
        unit: str = "ms",
        metric_type: str = MetricType.PERFORMANCE,
        tags: Optional[dict[str, str]] = None,
    ):
        """Initialize metric."""
        self.name = name
        self.value = value
        self.unit = unit
        self.metric_type = metric_type
        self.tags = tags or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "type": self.metric_type,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsCollector:
    """Collect and aggregate application metrics."""
    
    def __init__(self, max_metrics: int = 10000):
        """Initialize metrics collector."""
        self.metrics: list[Metric] = []
        self.max_metrics = max_metrics
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._start_time = datetime.utcnow()
    
    def record_metric(self, metric: Metric) -> None:
        """Record a metric."""
        self.metrics.append(metric)
        
        # Keep only recent metrics (FIFO when limit exceeded)
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
    ) -> None:
        """Record request metric."""
        self._request_count += 1
        if status_code >= 400:
            self._error_count += 1
        self._total_response_time += response_time_ms
        
        metric = Metric(
            name=f"http_{method}_{endpoint}",
            value=response_time_ms,
            unit="ms",
            metric_type=MetricType.REQUEST,
            tags={
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code),
            },
        )
        self.record_metric(metric)
    
    def record_database_query(
        self,
        query_type: str,
        query_time_ms: float,
        rows_affected: int = 0,
    ) -> None:
        """Record database query metric."""
        metric = Metric(
            name=f"db_{query_type}",
            value=query_time_ms,
            unit="ms",
            metric_type=MetricType.DATABASE,
            tags={
                "query_type": query_type,
                "rows_affected": str(rows_affected),
            },
        )
        self.record_metric(metric)
    
    def record_cache_operation(
        self,
        operation: str,
        hit: bool,
        operation_time_ms: float,
    ) -> None:
        """Record cache operation metric."""
        metric = Metric(
            name=f"cache_{operation}",
            value=operation_time_ms,
            unit="ms",
            metric_type=MetricType.CACHE,
            tags={
                "operation": operation,
                "hit": str(hit),
            },
        )
        self.record_metric(metric)
    
    def record_error(
        self,
        error_type: str,
        endpoint: str,
        status_code: int,
    ) -> None:
        """Record error metric."""
        metric = Metric(
            name=f"error_{error_type}",
            value=1.0,
            unit="count",
            metric_type=MetricType.ERROR,
            tags={
                "error_type": error_type,
                "endpoint": endpoint,
                "status_code": str(status_code),
            },
        )
        self.record_metric(metric)
    
    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
        avg_response_time = (
            self._total_response_time / self._request_count
            if self._request_count > 0
            else 0
        )
        error_rate = (
            (self._error_count / self._request_count * 100)
            if self._request_count > 0
            else 0
        )
        
        return {
            "uptime_seconds": uptime_seconds,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate_percent": round(error_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "metrics_recorded": len(self.metrics),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_recent_metrics(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent metrics."""
        return [m.to_dict() for m in self.metrics[-limit:]]
    
    def get_metrics_by_type(self, metric_type: str) -> list[dict[str, Any]]:
        """Get metrics by type."""
        return [
            m.to_dict()
            for m in self.metrics
            if m.metric_type == metric_type
        ]
    
    def clear_old_metrics(self, older_than_minutes: int = 60) -> int:
        """Clear metrics older than specified minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        initial_count = len(self.metrics)
        
        self.metrics = [
            m for m in self.metrics
            if m.timestamp > cutoff_time
        ]
        
        removed = initial_count - len(self.metrics)
        if removed > 0:
            logger.info(f"Cleared {removed} old metrics")
        
        return removed


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return metrics_collector
