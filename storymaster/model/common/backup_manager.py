"""Database backup management system with rolling backups"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class BackupManager(QObject):
    """Manages automatic database backups with rolling backup functionality"""

    backup_created = pyqtSignal(str)  # Signal emitted when backup is created
    backup_failed = pyqtSignal(str)  # Signal emitted when backup fails

    def __init__(
        self, database_path: str, backup_interval_minutes: int = 5, max_backups: int = 3
    ):
        super().__init__()
        self.database_path = Path(database_path)
        self.backup_interval_minutes = backup_interval_minutes
        self.max_backups = max_backups
        self.backup_dir = self.database_path.parent / "backups"

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(exist_ok=True)

        # Setup timer for automatic backups
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.create_backup)
        self.backup_timer.setInterval(
            backup_interval_minutes * 60 * 1000
        )  # Convert to milliseconds

    def start_automatic_backups(self):
        """Start the automatic backup timer"""
        if not self.backup_timer.isActive():
            self.backup_timer.start()

    def stop_automatic_backups(self):
        """Stop the automatic backup timer"""
        if self.backup_timer.isActive():
            self.backup_timer.stop()

    def create_backup(self) -> Optional[str]:
        """Create a backup of the current database"""
        try:
            if not self.database_path.exists():
                error_msg = f"Database file not found: {self.database_path}"
                self.backup_failed.emit(error_msg)
                return None

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self.database_path.stem}_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename

            # Copy the database file
            shutil.copy2(self.database_path, backup_path)

            # Clean up old backups
            self._cleanup_old_backups()

            success_msg = f"Backup created: {backup_filename}"
            self.backup_created.emit(success_msg)
            return str(backup_path)

        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            self.backup_failed.emit(error_msg)
            return None

    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent max_backups files"""
        try:
            # Get all backup files for this database
            pattern = f"{self.database_path.stem}_backup_*.db"
            backup_files = list(self.backup_dir.glob(pattern))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove excess backups
            for backup_file in backup_files[self.max_backups :]:
                backup_file.unlink()

        except Exception as e:
            print(f"Warning: Failed to cleanup old backups: {e}")

    def get_available_backups(self) -> List[dict]:
        """Get list of available backup files with metadata"""
        backup_files = []
        try:
            pattern = f"{self.database_path.stem}_backup_*.db"
            for backup_path in self.backup_dir.glob(pattern):
                stat = backup_path.stat()
                backup_info = {
                    "path": str(backup_path),
                    "filename": backup_path.name,
                    "created": datetime.fromtimestamp(stat.st_mtime),
                    "size": stat.st_size,
                }
                backup_files.append(backup_info)

            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x["created"], reverse=True)

        except Exception as e:
            print(f"Error getting backup list: {e}")

        return backup_files

    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore database from a backup file"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                self.backup_failed.emit(f"Backup file not found: {backup_path}")
                return False

            # Create a backup of current database before restoring
            if self.database_path.exists():
                current_backup = (
                    f"{self.database_path.stem}_pre_restore_{int(time.time())}.db"
                )
                current_backup_path = self.backup_dir / current_backup
                shutil.copy2(self.database_path, current_backup_path)

            # Restore from backup
            shutil.copy2(backup_file, self.database_path)

            self.backup_created.emit(f"Database restored from: {backup_file.name}")
            return True

        except Exception as e:
            error_msg = f"Failed to restore from backup: {str(e)}"
            self.backup_failed.emit(error_msg)
            return False

    def delete_backup(self, backup_path: str) -> bool:
        """Delete a specific backup file"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False

    def get_backup_settings(self) -> dict:
        """Get current backup settings"""
        return {
            "database_path": str(self.database_path),
            "backup_interval_minutes": self.backup_interval_minutes,
            "max_backups": self.max_backups,
            "backup_dir": str(self.backup_dir),
            "automatic_backups_active": self.backup_timer.isActive(),
        }

    def update_backup_settings(
        self, interval_minutes: int = None, max_backups: int = None
    ):
        """Update backup settings"""
        if interval_minutes is not None:
            self.backup_interval_minutes = interval_minutes
            if self.backup_timer.isActive():
                self.backup_timer.setInterval(interval_minutes * 60 * 1000)

        if max_backups is not None:
            self.max_backups = max_backups
            # Clean up excess backups if needed
            self._cleanup_old_backups()
