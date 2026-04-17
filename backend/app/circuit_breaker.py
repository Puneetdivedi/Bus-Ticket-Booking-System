"""Circuit breaker pattern for resilient database operations and external service calls."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from app.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Requests are blocked
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for handling cascading failures.
    
    Prevents cascading failures by stopping requests to failing services.
    Automatically retries when service recovers.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        expected_exception: type[Exception] = Exception,
        name: str = "CircuitBreaker",
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout_seconds: Time before attempting recovery
            expected_exception: Exception type to catch
            name: Circuit breaker identifier
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self.expected_exception = expected_exception
        self.name = name
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        
        logger.info(f"Circuit breaker '{name}' initialized")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"[{self.name}] Circuit breaker entering HALF_OPEN state")
            else:
                logger.warning(f"[{self.name}] Circuit breaker is OPEN - rejecting request")
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as exc:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return False
        return datetime.utcnow() >= self.last_failure_time + self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info(
                    f"[{self.name}] Circuit breaker recovered to CLOSED state"
                )
        
        logger.debug(f"[{self.name}] Call succeeded")

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        self.success_count = 0
        
        logger.warning(
            f"[{self.name}] Call failed ({self.failure_count}/{self.failure_threshold})"
        )
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"[{self.name}] Circuit breaker opened after {self.failure_count} failures"
            )

    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        logger.info(f"[{self.name}] Circuit breaker manually reset")

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat()
            if self.last_failure_time
            else None,
        }


# Pre-configured circuit breakers for critical services
database_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout_seconds=30,
    expected_exception=Exception,
    name="DatabaseCircuitBreaker",
)

booking_service_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout_seconds=60,
    expected_exception=Exception,
    name="BookingServiceCircuitBreaker",
)


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator to apply circuit breaker pattern to a function."""
    def decorator(func: F) -> F:
        async def async_wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        
        # Return appropriate wrapper
        if hasattr(func, "__await__"):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore
    
    return decorator
