"""
Test suite for the backup manager system
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from storymaster.model.common.backup_manager import BackupManager


@pytest.fixture
def temp_database_file():
    """Create a temporary database file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        temp_file.write(b"test database content")
        temp_path = Path(temp_file.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()

    # Cleanup backup directory
    backup_dir = temp_path.parent / "backups"
    if backup_dir.exists():
        for backup_file in backup_dir.glob("*"):
            backup_file.unlink()
        backup_dir.rmdir()


@pytest.fixture
def backup_manager(qapp, temp_database_file):
    """Create a BackupManager instance for testing"""
    manager = BackupManager(
        database_path=str(temp_database_file),
        backup_interval_minutes=1,  # Short interval for testing
        max_backups=3,
    )
    yield manager

    # Cleanup
    manager.stop_automatic_backups()


class TestBackupManagerInitialization:
    """Test BackupManager initialization and setup"""

    def test_backup_manager_creation(self, qapp, temp_database_file):
        """Test that BackupManager can be created with valid parameters"""
        manager = BackupManager(
            database_path=str(temp_database_file),
            backup_interval_minutes=5,
            max_backups=3,
        )

        assert manager.database_path == temp_database_file
        assert manager.backup_interval_minutes == 5
        assert manager.max_backups == 3
        assert manager.backup_dir == temp_database_file.parent / "backups"

    def test_backup_directory_creation(self, qapp, temp_database_file):
        """Test that backup directory is created on initialization"""
        manager = BackupManager(str(temp_database_file))
        backup_dir = temp_database_file.parent / "backups"

        assert backup_dir.exists()
        assert backup_dir.is_dir()

    def test_timer_initialization(self, qapp, temp_database_file):
        """Test that backup timer is properly initialized"""
        manager = BackupManager(
            database_path=str(temp_database_file), backup_interval_minutes=5
        )

        assert isinstance(manager.backup_timer, QTimer)
        assert (
            manager.backup_timer.interval() == 5 * 60 * 1000
        )  # 5 minutes in milliseconds
        assert not manager.backup_timer.isActive()  # Should not be active initially

    def test_signal_setup(self, qapp, temp_database_file):
        """Test that PyQt signals are properly set up"""
        manager = BackupManager(str(temp_database_file))

        # Test that signals exist
        assert hasattr(manager, "backup_created")
        assert hasattr(manager, "backup_failed")


class TestBackupManagerOperations:
    """Test backup creation and management operations"""

    def test_manual_backup_creation(self, backup_manager):
        """Test manual backup creation"""
        # Create a backup
        backup_path = backup_manager.create_backup()

        assert backup_path is not None
        assert Path(backup_path).exists()
        assert Path(backup_path).parent == backup_manager.backup_dir

    def test_backup_file_naming(self, backup_manager):
        """Test that backup files are named correctly"""
        backup_path = backup_manager.create_backup()
        backup_file = Path(backup_path)

        # Should follow format: original_name_YYYYMMDD_HHMMSS.db
        assert backup_file.suffix == ".db"
        assert backup_manager.database_path.stem in backup_file.name

    def test_backup_content_integrity(self, backup_manager):
        """Test that backup contains the same content as original"""
        original_content = backup_manager.database_path.read_bytes()
        backup_path = backup_manager.create_backup()
        backup_content = Path(backup_path).read_bytes()

        assert original_content == backup_content

    def test_multiple_backups(self, backup_manager):
        """Test creation of multiple backups"""
        backup1 = backup_manager.create_backup()

        # Add delay to ensure different timestamps
        import time

        time.sleep(1.1)

        backup2 = backup_manager.create_backup()

        assert backup1 != backup2
        assert Path(backup1).exists()
        assert Path(backup2).exists()

    def test_max_backups_enforcement(self, backup_manager):
        """Test that old backups are removed when max_backups is exceeded"""
        # Set max_backups to 2 for easier testing
        backup_manager.max_backups = 2

        # Create 4 backups
        backups = []
        for i in range(4):
            backup_path = backup_manager.create_backup()
            backups.append(backup_path)
            # Small delay to ensure different timestamps
            import time

            time.sleep(0.1)

        # Should only have 2 backups remaining
        existing_backups = list(backup_manager.backup_dir.glob("*.db"))
        assert len(existing_backups) <= backup_manager.max_backups

    def test_backup_failure_handling(self, backup_manager):
        """Test handling of backup failures"""
        # Remove the original database file to simulate failure
        backup_manager.database_path.unlink()

        backup_path = backup_manager.create_backup()
        assert backup_path is None


class TestBackupManagerAutomation:
    """Test automatic backup functionality"""

    def test_start_automatic_backups(self, backup_manager):
        """Test starting automatic backups"""
        backup_manager.start_automatic_backups()

        assert backup_manager.backup_timer.isActive()

    def test_stop_automatic_backups(self, backup_manager):
        """Test stopping automatic backups"""
        backup_manager.start_automatic_backups()
        backup_manager.stop_automatic_backups()

        assert not backup_manager.backup_timer.isActive()

    def test_timer_interval_configuration(self, qapp, temp_database_file):
        """Test that timer interval is configured correctly"""
        manager = BackupManager(
            database_path=str(temp_database_file), backup_interval_minutes=10
        )

        expected_interval = 10 * 60 * 1000  # 10 minutes in milliseconds
        assert manager.backup_timer.interval() == expected_interval

    def test_automatic_backup_prevention_when_already_active(self, backup_manager):
        """Test that starting automatic backups when already active doesn't duplicate"""
        backup_manager.start_automatic_backups()
        initial_timer = backup_manager.backup_timer

        backup_manager.start_automatic_backups()  # Try to start again

        assert backup_manager.backup_timer is initial_timer
        assert backup_manager.backup_timer.isActive()


class TestBackupManagerUtilities:
    """Test utility methods of BackupManager"""

    def test_get_backup_list(self, backup_manager):
        """Test getting list of existing backups"""
        # Create some backups
        backup_manager.create_backup()

        import time

        time.sleep(1.1)

        backup_manager.create_backup()

        backups = backup_manager.get_available_backups()

        assert len(backups) >= 2
        for backup_info in backups:
            assert "path" in backup_info
            assert Path(backup_info["path"]).exists()
            assert Path(backup_info["path"]).suffix == ".db"

    def test_cleanup_old_backups(self, backup_manager):
        """Test cleanup of old backups"""
        # Set max_backups to 1
        backup_manager.max_backups = 1

        # Create multiple backups with delays to ensure different timestamps
        backup_manager.create_backup()

        import time

        time.sleep(1.1)
        backup_manager.create_backup()

        time.sleep(0.1)
        backup_manager.create_backup()

        # Trigger cleanup using the private method
        backup_manager._cleanup_old_backups()

        # Should only have 1 backup remaining
        existing_backups = list(backup_manager.backup_dir.glob("*.db"))
        assert len(existing_backups) <= 1

    def test_restore_from_backup(self, backup_manager, temp_database_file):
        """Test restoring database from backup"""
        # Create original content
        original_content = b"original database content"
        temp_database_file.write_bytes(original_content)

        # Create backup
        backup_path = backup_manager.create_backup()

        # Modify original
        modified_content = b"modified database content"
        temp_database_file.write_bytes(modified_content)

        # Restore from backup
        success = backup_manager.restore_from_backup(backup_path)

        assert success
        assert temp_database_file.read_bytes() == original_content


class TestBackupManagerSignals:
    """Test PyQt signal emission"""

    def test_backup_created_signal(self, backup_manager):
        """Test that backup_created signal is emitted"""
        signal_received = Mock()
        backup_manager.backup_created.connect(signal_received)

        backup_manager.create_backup()

        signal_received.assert_called_once()

    def test_backup_failed_signal(self, backup_manager):
        """Test that backup_failed signal is emitted on failure"""
        signal_received = Mock()
        backup_manager.backup_failed.connect(signal_received)

        # Remove database file to cause failure
        backup_manager.database_path.unlink()
        backup_manager.create_backup()

        signal_received.assert_called_once()

    def test_signal_parameters(self, backup_manager):
        """Test that signals are emitted with correct parameters"""
        created_messages = []
        failed_messages = []

        def on_backup_created(message):
            created_messages.append(message)

        def on_backup_failed(message):
            failed_messages.append(message)

        backup_manager.backup_created.connect(on_backup_created)
        backup_manager.backup_failed.connect(on_backup_failed)

        # Test successful backup
        backup_manager.create_backup()
        assert len(created_messages) == 1
        assert "Backup created:" in created_messages[0]
        assert ".db" in created_messages[0]

        # Test failed backup
        backup_manager.database_path.unlink()
        backup_manager.create_backup()
        assert len(failed_messages) == 1
        assert isinstance(failed_messages[0], str)
