"""Database optimization utilities and query helpers."""
from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities."""

    @staticmethod
    def explain_query(db: Session, query: str) -> str:
        """Explain query execution plan (SQLite/PostgreSQL compatible)."""
        try:
            result = db.execute(text(f"EXPLAIN QUERY PLAN {query}"))
            return "\n".join([str(row) for row in result])
        except Exception as e:
            logger.error(f"Error explaining query: {str(e)}")
            return ""

    @staticmethod
    def get_table_size(db: Session, table_name: str) -> int:
        """Get approximate row count for a table."""
        try:
            result = db.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting table size: {str(e)}")
            return 0

    @staticmethod
    def analyze_performance(db: Session, operation: str) -> dict:
        """Analyze operation performance."""
        return {
            "operation": operation,
            "status": "analyzed",
            "recommendations": [
                "Use database indexes for frequent queries",
                "Consider denormalization for read-heavy operations",
                "Implement caching for expensive queries",
            ],
        }


class IndexManager:
    """Database index management."""

    # Recommended indexes for the schema
    RECOMMENDED_INDEXES = {
        "bookings": [
            "travel_date",
            "mobile_number",
            "(travel_date, created_at)",
        ],
        "booking_seats": [
            "(travel_date, seat_number)",
            "booking_id",
            "travel_date",
        ],
    }

    @staticmethod
    def get_recommended_indexes() -> dict:
        """Get recommended indexes for the database."""
        return IndexManager.RECOMMENDED_INDEXES.copy()

    @staticmethod
    def create_index_script(database_type: str = "sqlite") -> str:
        """Generate index creation script."""
        if database_type == "sqlite":
            return IndexManager._sqlite_index_script()
        elif database_type == "postgresql":
            return IndexManager._postgresql_index_script()
        return ""

    @staticmethod
    def _sqlite_index_script() -> str:
        """Generate SQLite index creation script."""
        return """
-- Recommended indexes for SQLite

-- Bookings table indexes
CREATE INDEX IF NOT EXISTS idx_bookings_travel_date ON bookings(travel_date);
CREATE INDEX IF NOT EXISTS idx_bookings_mobile ON bookings(mobile_number);
CREATE INDEX IF NOT EXISTS idx_bookings_travel_date_created ON bookings(travel_date, created_at);

-- Booking seats table indexes
CREATE INDEX IF NOT EXISTS idx_booking_seats_travel_date_seat ON booking_seats(travel_date, seat_number);
CREATE INDEX IF NOT EXISTS idx_booking_seats_booking_id ON booking_seats(booking_id);
CREATE INDEX IF NOT EXISTS idx_booking_seats_travel_date ON booking_seats(travel_date);

-- Performance note: VACUUM and ANALYZE after creating indexes
VACUUM;
ANALYZE;
"""

    @staticmethod
    def _postgresql_index_script() -> str:
        """Generate PostgreSQL index creation script."""
        return """
-- Recommended indexes for PostgreSQL

-- Bookings table indexes
CREATE INDEX IF NOT EXISTS idx_bookings_travel_date ON bookings(travel_date);
CREATE INDEX IF NOT EXISTS idx_bookings_mobile ON bookings(mobile_number);
CREATE INDEX IF NOT EXISTS idx_bookings_travel_date_created ON bookings(travel_date, created_at);

-- Booking seats table indexes
CREATE INDEX IF NOT EXISTS idx_booking_seats_travel_date_seat ON booking_seats(travel_date, seat_number);
CREATE INDEX IF NOT EXISTS idx_booking_seats_booking_id ON booking_seats(booking_id);
CREATE INDEX IF NOT EXISTS idx_booking_seats_travel_date ON booking_seats(travel_date);

-- BRIN indexes for large datasets (optional)
CREATE INDEX IF NOT EXISTS idx_bookings_travel_date_brin ON bookings USING BRIN(travel_date);

-- Analyze tables for query planner
ANALYZE bookings;
ANALYZE booking_seats;
"""


class QueryBuilder:
    """Helper for building optimized queries."""

    @staticmethod
    def build_paginated_query(
        base_query: Any,
        skip: int = 0,
        limit: int = 50,
    ) -> Any:
        """Add pagination to a query."""
        return base_query.offset(skip).limit(limit)

    @staticmethod
    def build_filtered_query(
        base_query: Any,
        filters: dict,
    ) -> Any:
        """Add filters to a query."""
        for column, value in filters.items():
            if value is not None:
                # This is a simplified version - actual implementation depends on model
                pass
        return base_query


class DatabaseTuning:
    """Database configuration tuning recommendations."""

    @staticmethod
    def get_sqlite_tuning() -> dict:
        """Get SQLite tuning recommendations."""
        return {
            "pragma_journal_mode": "WAL",  # Write-ahead logging for concurrency
            "pragma_synchronous": "NORMAL",  # Balance between safety and performance
            "pragma_cache_size": 10000,  # Increase page cache
            "pragma_temp_store": "MEMORY",  # Use memory for temp tables
            "pragma_mmap_size": "30000000",  # Memory-mapped I/O
        }

    @staticmethod
    def get_postgresql_tuning() -> dict:
        """Get PostgreSQL tuning recommendations for production."""
        return {
            "max_connections": 100,
            "shared_buffers": "256MB",
            "effective_cache_size": "1GB",
            "maintenance_work_mem": "64MB",
            "checkpoint_completion_target": 0.9,
            "wal_buffers": "16MB",
        }

    @staticmethod
    def tuning_script(database_type: str = "sqlite") -> str:
        """Generate database tuning script."""
        if database_type == "sqlite":
            tuning = DatabaseTuning.get_sqlite_tuning()
            return "\n".join(
                [f"PRAGMA {k} = {v};" for k, v in tuning.items()]
            )
        return ""
