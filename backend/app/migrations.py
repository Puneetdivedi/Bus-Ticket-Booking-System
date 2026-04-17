"""Database migration and schema versioning system."""
from datetime import datetime
from typing import Any, Callable, dict, list, Optional

from sqlalchemy import text

from app.database import SessionLocal, engine
from app.logger import get_logger

logger = get_logger(__name__)


class Migration:
    """Represent a database migration."""
    
    def __init__(
        self,
        version: str,
        name: str,
        up_sql: str,
        down_sql: str,
        description: str = "",
    ):
        """Initialize migration."""
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.description = description
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class MigrationManager:
    """Manage database migrations and versioning."""
    
    def __init__(self):
        """Initialize migration manager."""
        self.migrations: dict[str, Migration] = {}
        self.applied_migrations: list[str] = []
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self) -> None:
        """Ensure migrations tracking table exists."""
        try:
            session = SessionLocal()
            session.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            )
            session.commit()
            session.close()
            logger.info("Migrations table verified")
        except Exception as exc:
            logger.error(f"Failed to ensure migrations table: {exc}")
    
    def register_migration(self, migration: Migration) -> None:
        """Register a migration."""
        self.migrations[migration.version] = migration
        logger.info(f"Migration registered: {migration.version} - {migration.name}")
    
    def apply_migration(self, version: str) -> bool:
        """Apply a migration."""
        if version not in self.migrations:
            logger.error(f"Migration not found: {version}")
            return False
        
        migration = self.migrations[version]
        
        try:
            session = SessionLocal()
            
            # Execute migration SQL
            for statement in migration.up_sql.split(";"):
                if statement.strip():
                    session.execute(text(statement))
            
            # Record migration
            session.execute(
                text(
                    "INSERT INTO schema_migrations (version, name) VALUES (:version, :name)"
                ),
                {"version": version, "name": migration.name},
            )
            
            session.commit()
            session.close()
            
            self.applied_migrations.append(version)
            logger.info(f"Migration applied: {version}")
            return True
        
        except Exception as exc:
            logger.error(f"Migration failed: {exc}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a migration."""
        if version not in self.migrations:
            logger.error(f"Migration not found: {version}")
            return False
        
        migration = self.migrations[version]
        
        try:
            session = SessionLocal()
            
            # Execute rollback SQL
            for statement in migration.down_sql.split(";"):
                if statement.strip():
                    session.execute(text(statement))
            
            # Remove migration record
            session.execute(
                text("DELETE FROM schema_migrations WHERE version = :version"),
                {"version": version},
            )
            
            session.commit()
            session.close()
            
            self.applied_migrations.remove(version)
            logger.info(f"Migration rolled back: {version}")
            return True
        
        except Exception as exc:
            logger.error(f"Rollback failed: {exc}")
            return False
    
    def get_applied_migrations(self) -> list[str]:
        """Get list of applied migrations."""
        try:
            session = SessionLocal()
            result = session.execute(
                text("SELECT version FROM schema_migrations ORDER BY applied_at")
            )
            applied = [row[0] for row in result]
            session.close()
            return applied
        except Exception as exc:
            logger.error(f"Failed to get applied migrations: {exc}")
            return []
    
    def get_status(self) -> dict[str, Any]:
        """Get migration status."""
        applied = self.get_applied_migrations()
        pending = [v for v in self.migrations.keys() if v not in applied]
        
        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied": applied,
            "pending": pending,
        }


# Global migration manager
migration_manager = MigrationManager()


def get_migration_manager() -> MigrationManager:
    """Get global migration manager."""
    return migration_manager


def apply_pending_migrations() -> dict[str, Any]:
    """Apply all pending migrations."""
    manager = get_migration_manager()
    status = manager.get_status()
    
    applied_count = 0
    for version in sorted(status["pending"]):
        if manager.apply_migration(version):
            applied_count += 1
    
    return {
        "applied_migrations": applied_count,
        "pending_migrations": len(status["pending"]) - applied_count,
        "status": manager.get_status(),
    }
