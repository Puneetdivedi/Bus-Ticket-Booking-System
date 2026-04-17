"""Database health checks and connection pool monitoring."""
import time
from typing import Any, Optional

from sqlalchemy import text

from app.database import SessionLocal
from app.logger import get_logger

logger = get_logger(__name__)


class DatabaseHealth:
    """Monitor and report database health status."""
    
    def __init__(self):
        """Initialize database health monitor."""
        self.last_check_time: Optional[float] = None
        self.is_healthy = True
        self.last_error: Optional[str] = None
        self.connection_pool_size = 0
        self.connection_pool_overflow = 0
    
    def check_connection(self) -> bool:
        """Check if database is accessible."""
        try:
            session = SessionLocal()
            result = session.execute(text("SELECT 1"))
            session.close()
            
            self.is_healthy = True
            self.last_error = None
            self.last_check_time = time.time()
            logger.debug("Database health check: PASSED")
            return True
        except Exception as exc:
            self.is_healthy = False
            self.last_error = str(exc)
            self.last_check_time = time.time()
            logger.error(f"Database health check: FAILED - {exc}")
            return False
    
    def check_query_performance(self) -> dict[str, Any]:
        """Check database query performance."""
        try:
            session = SessionLocal()
            
            # Simple query performance check
            start = time.time()
            result = session.execute(
                text("SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table'")
            )
            execution_time = (time.time() - start) * 1000  # Convert to ms
            
            session.close()
            
            return {
                "status": "ok",
                "query_time_ms": round(execution_time, 2),
                "warning": execution_time > 100,
            }
        except Exception as exc:
            logger.error(f"Query performance check failed: {exc}")
            return {
                "status": "error",
                "error": str(exc),
                "query_time_ms": None,
            }
    
    def get_status(self) -> dict[str, Any]:
        """Get comprehensive database health status."""
        return {
            "is_healthy": self.is_healthy,
            "last_check_time": self.last_check_time,
            "last_error": self.last_error,
            "connection_pool_size": self.connection_pool_size,
            "connection_pool_overflow": self.connection_pool_overflow,
        }


# Global database health instance
db_health = DatabaseHealth()


def get_database_health() -> DatabaseHealth:
    """Get global database health monitor."""
    return db_health


def check_database_health() -> dict[str, Any]:
    """Quick database health check."""
    health = get_database_health()
    is_connected = health.check_connection()
    performance = health.check_query_performance()
    
    return {
        "connected": is_connected,
        "health": health.get_status(),
        "performance": performance,
    }
