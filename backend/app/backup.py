"""Backup and recovery utilities for data protection."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import text

from app.database import SessionLocal
from app.logger import get_logger

logger = get_logger(__name__)


class BackupManager:
    """Manage database backups and recovery."""
    
    def __init__(self, backup_dir: str = "backups"):
        """Initialize backup manager."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        logger.info(f"Backup directory: {self.backup_dir.absolute()}")
    
    def create_backup(self, backup_name: Optional[str] = None) -> dict[str, Any]:
        """Create a database backup."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"backup_{timestamp}"
            backup_path = self.backup_dir / f"{backup_name}.json"
            
            session = SessionLocal()
            
            # Export all bookings
            bookings_query = text(
                """
                SELECT 
                    b.booking_id, 
                    b.travel_date, 
                    b.mobile_number, 
                    b.num_seats,
                    b.created_at,
                    GROUP_CONCAT(bs.seat_number) as seats
                FROM bookings b
                LEFT JOIN booking_seats bs ON b.booking_id = bs.booking_id
                GROUP BY b.booking_id
                """
            )
            
            result = session.execute(bookings_query)
            bookings = []
            for row in result:
                bookings.append({
                    "booking_id": row[0],
                    "travel_date": row[1],
                    "mobile_number": row[2],
                    "num_seats": row[3],
                    "created_at": row[4],
                    "seats": row[5].split(",") if row[5] else [],
                })
            
            session.close()
            
            # Create backup file
            backup_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "backup_version": "1.0",
                "bookings_count": len(bookings),
                "bookings": bookings,
            }
            
            with open(backup_path, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Backup created: {backup_path} ({len(bookings)} bookings)")
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "timestamp": datetime.utcnow().isoformat(),
                "bookings_backed_up": len(bookings),
            }
        
        except Exception as exc:
            logger.error(f"Backup creation failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
            }
    
    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.json"), reverse=True):
            try:
                stat = backup_file.stat()
                with open(backup_file, "r") as f:
                    data = json.load(f)
                
                backups.append({
                    "name": backup_file.stem,
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "bookings_count": data.get("bookings_count", 0),
                })
            except Exception as exc:
                logger.warning(f"Failed to read backup {backup_file}: {exc}")
        
        return backups
    
    def restore_backup(self, backup_name: str) -> dict[str, Any]:
        """Restore from a backup."""
        try:
            backup_path = self.backup_dir / f"{backup_name}.json"
            
            if not backup_path.exists():
                return {
                    "success": False,
                    "error": f"Backup not found: {backup_name}",
                }
            
            with open(backup_path, "r") as f:
                backup_data = json.load(f)
            
            # Verify backup integrity
            if "bookings" not in backup_data:
                return {
                    "success": False,
                    "error": "Invalid backup format",
                }
            
            logger.info(
                f"Restore from backup: {backup_name} "
                f"({backup_data.get('bookings_count', 0)} bookings)"
            )
            
            return {
                "success": True,
                "backup_name": backup_name,
                "bookings_count": len(backup_data.get("bookings", [])),
                "backup_timestamp": backup_data.get("timestamp"),
                "message": "Backup data loaded successfully. Manual import required.",
            }
        
        except Exception as exc:
            logger.error(f"Restore failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
            }
    
    def delete_backup(self, backup_name: str) -> dict[str, Any]:
        """Delete a backup."""
        try:
            backup_path = self.backup_dir / f"{backup_name}.json"
            
            if not backup_path.exists():
                return {
                    "success": False,
                    "error": f"Backup not found: {backup_name}",
                }
            
            backup_path.unlink()
            logger.info(f"Backup deleted: {backup_name}")
            
            return {
                "success": True,
                "message": f"Backup {backup_name} deleted",
            }
        
        except Exception as exc:
            logger.error(f"Delete backup failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
            }
    
    def cleanup_old_backups(self, keep_count: int = 5) -> dict[str, Any]:
        """Remove old backups keeping only recent ones."""
        try:
            backups = sorted(
                self.backup_dir.glob("*.json"),
                key=lambda p: p.stat().st_ctime,
                reverse=True,
            )
            
            deleted_count = 0
            for backup_file in backups[keep_count:]:
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup_file.name}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "remaining_backups": len(backups[:keep_count]),
            }
        
        except Exception as exc:
            logger.error(f"Cleanup failed: {exc}")
            return {
                "success": False,
                "error": str(exc),
            }


# Global backup manager instance
backup_manager = BackupManager()


def get_backup_manager() -> BackupManager:
    """Get global backup manager."""
    return backup_manager
