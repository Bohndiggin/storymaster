"""Database and backup management dialog"""

import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storymaster.model.common.backup_manager import BackupManager
from storymaster.view.common.theme import (
    get_dialog_style,
    get_button_style,
    get_list_style,
    get_tab_style,
    get_checkbox_style,
    get_input_style,
)


class DatabaseManagerDialog(QDialog):
    """Dialog for managing database selection and backups"""

    database_changed = pyqtSignal(str)  # Emitted when user selects a different database

    def __init__(
        self,
        parent=None,
        current_db_path: str = None,
        backup_manager: BackupManager = None,
    ):
        super().__init__(parent)
        self.current_db_path = current_db_path or "storymaster.db"
        self.backup_manager = backup_manager
        self.selected_database = None

        self.setWindowTitle("Database & Backup Manager")
        self.setModal(True)
        self.resize(600, 500)
        
        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
            + get_tab_style()
            + get_checkbox_style()
            + get_input_style()
        )

        self.setup_ui()
        self.connect_signals()
        self.refresh_data()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Database selection tab
        self.setup_database_tab()

        # Backup management tab
        self.setup_backup_tab()

        # Settings tab
        self.setup_settings_tab()

        # Button box
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.switch_btn = QPushButton("Switch Database")
        self.switch_btn.setEnabled(False)
        self.close_btn = QPushButton("Close")

        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.switch_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def setup_database_tab(self):
        """Setup database selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Current database info
        current_group = QGroupBox("Current Database")
        current_layout = QVBoxLayout(current_group)

        self.current_db_label = QLabel()
        self.current_db_label.setFont(QFont("", weight=QFont.Weight.Bold))
        current_layout.addWidget(self.current_db_label)

        self.current_db_info = QLabel()
        current_layout.addWidget(self.current_db_info)

        layout.addWidget(current_group)

        # Available databases
        db_group = QGroupBox("Available Databases")
        db_layout = QVBoxLayout(db_group)

        self.database_list = QListWidget()
        self.database_list.itemSelectionChanged.connect(
            self.on_database_selection_changed
        )
        db_layout.addWidget(self.database_list)

        db_buttons = QHBoxLayout()
        self.browse_btn = QPushButton("Browse...")
        self.create_btn = QPushButton("Create New...")
        db_buttons.addWidget(self.browse_btn)
        db_buttons.addWidget(self.create_btn)
        db_buttons.addStretch()

        db_layout.addLayout(db_buttons)

        layout.addWidget(db_group)

        self.tab_widget.addTab(tab, "Database Selection")

    def setup_backup_tab(self):
        """Setup backup management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Backup controls
        controls_group = QGroupBox("Backup Controls")
        controls_layout = QHBoxLayout(controls_group)

        self.create_backup_btn = QPushButton("Create Backup Now")
        self.auto_backup_check = QCheckBox("Automatic Backups")

        controls_layout.addWidget(self.create_backup_btn)
        controls_layout.addWidget(self.auto_backup_check)
        controls_layout.addStretch()

        layout.addWidget(controls_group)

        # Available backups
        backup_group = QGroupBox("Available Backups")
        backup_layout = QVBoxLayout(backup_group)

        self.backup_list = QListWidget()
        self.backup_list.itemSelectionChanged.connect(self.on_backup_selection_changed)
        backup_layout.addWidget(self.backup_list)

        backup_buttons = QHBoxLayout()
        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.setEnabled(False)
        self.delete_backup_btn = QPushButton("Delete Selected")
        self.delete_backup_btn.setEnabled(False)

        backup_buttons.addWidget(self.restore_btn)
        backup_buttons.addWidget(self.delete_backup_btn)
        backup_buttons.addStretch()

        backup_layout.addLayout(backup_buttons)

        layout.addWidget(backup_group)

        # Status area
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_text)

        self.tab_widget.addTab(tab, "Backup Management")

    def setup_settings_tab(self):
        """Setup backup settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        settings_group = QGroupBox("Backup Settings")
        settings_layout = QGridLayout(settings_group)

        # Backup interval
        settings_layout.addWidget(QLabel("Backup Interval (minutes):"), 0, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        settings_layout.addWidget(self.interval_spin, 0, 1)

        # Max backups
        settings_layout.addWidget(QLabel("Maximum Backups:"), 1, 0)
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 20)
        self.max_backups_spin.setValue(3)
        settings_layout.addWidget(self.max_backups_spin, 1, 1)

        # Apply settings button
        self.apply_settings_btn = QPushButton("Apply Settings")
        settings_layout.addWidget(self.apply_settings_btn, 2, 0, 1, 2)

        layout.addWidget(settings_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Settings")

    def connect_signals(self):
        """Connect UI signals"""
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.switch_btn.clicked.connect(self.switch_database)
        self.close_btn.clicked.connect(self.accept)

        self.browse_btn.clicked.connect(self.browse_for_database)
        self.create_btn.clicked.connect(self.create_new_database)

        if self.backup_manager:
            self.create_backup_btn.clicked.connect(self.create_backup)
            self.auto_backup_check.toggled.connect(self.toggle_automatic_backups)
            self.restore_btn.clicked.connect(self.restore_backup)
            self.delete_backup_btn.clicked.connect(self.delete_backup)
            self.apply_settings_btn.clicked.connect(self.apply_settings)

            # Connect backup manager signals
            self.backup_manager.backup_created.connect(self.on_backup_created)
            self.backup_manager.backup_failed.connect(self.on_backup_failed)

    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_database_list()
        if self.backup_manager:
            self.refresh_backup_list()
            self.refresh_settings()

    def refresh_database_list(self):
        """Refresh the list of available databases"""
        self.database_list.clear()

        # Update current database info
        current_path = Path(self.current_db_path)
        self.current_db_label.setText(f"Current: {current_path.name}")

        if current_path.exists():
            stat = current_path.stat()
            size_mb = stat.st_size / (1024 * 1024)
            self.current_db_info.setText(f"Size: {size_mb:.2f} MB")
        else:
            self.current_db_info.setText("File not found")

        # Find database files in current directory
        current_dir = Path(self.current_db_path).parent
        for db_file in current_dir.glob("*.db"):
            if not db_file.name.startswith("test_"):  # Skip test databases
                item = QListWidgetItem(db_file.name)
                item.setData(Qt.ItemDataRole.UserRole, str(db_file))

                if db_file.samefile(current_path):
                    item.setText(f"{db_file.name} (Current)")
                    item.setFont(QFont("", weight=QFont.Weight.Bold))

                self.database_list.addItem(item)

    def refresh_backup_list(self):
        """Refresh the list of available backups"""
        if not self.backup_manager:
            return

        self.backup_list.clear()
        backups = self.backup_manager.get_available_backups()

        for backup in backups:
            size_mb = backup["size"] / (1024 * 1024)
            display_text = f"{backup['filename']} ({backup['created'].strftime('%Y-%m-%d %H:%M:%S')}, {size_mb:.2f} MB)"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, backup["path"])
            self.backup_list.addItem(item)

    def refresh_settings(self):
        """Refresh backup settings display"""
        if not self.backup_manager:
            return

        settings = self.backup_manager.get_backup_settings()
        self.interval_spin.setValue(settings["backup_interval_minutes"])
        self.max_backups_spin.setValue(settings["max_backups"])
        self.auto_backup_check.setChecked(settings["automatic_backups_active"])

    def on_database_selection_changed(self):
        """Handle database selection change"""
        current_item = self.database_list.currentItem()
        if current_item:
            self.selected_database = current_item.data(Qt.ItemDataRole.UserRole)
            self.switch_btn.setEnabled(True)
        else:
            self.selected_database = None
            self.switch_btn.setEnabled(False)

    def on_backup_selection_changed(self):
        """Handle backup selection change"""
        has_selection = self.backup_list.currentItem() is not None
        self.restore_btn.setEnabled(has_selection)
        self.delete_backup_btn.setEnabled(has_selection)

    def switch_database(self):
        """Switch to the selected database"""
        if not self.selected_database:
            return

        reply = QMessageBox.question(
            self,
            "Switch Database",
            f"Switch to database: {Path(self.selected_database).name}?\\n\\n"
            "This will close the current database and open the selected one.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.database_changed.emit(self.selected_database)
            self.accept()

    def browse_for_database(self):
        """Browse for an existing database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            str(Path(self.current_db_path).parent),
            "Database files (*.db);;All files (*.*)",
        )

        if file_path:
            self.selected_database = file_path
            self.refresh_database_list()

    def create_new_database(self):
        """Create a new database file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create New Database",
            str(Path(self.current_db_path).parent / "new_storymaster.db"),
            "Database files (*.db);;All files (*.*)",
        )

        if file_path:
            # The file will be created when the application initializes the database
            self.selected_database = file_path
            self.refresh_database_list()

    def create_backup(self):
        """Create a manual backup"""
        if self.backup_manager:
            backup_path = self.backup_manager.create_backup()
            if backup_path:
                self.refresh_backup_list()

    def toggle_automatic_backups(self, enabled: bool):
        """Toggle automatic backups"""
        if not self.backup_manager:
            return

        if enabled:
            self.backup_manager.start_automatic_backups()
            self.add_status_message("Automatic backups enabled")
        else:
            self.backup_manager.stop_automatic_backups()
            self.add_status_message("Automatic backups disabled")

    def restore_backup(self):
        """Restore from selected backup"""
        current_item = self.backup_list.currentItem()
        if not current_item or not self.backup_manager:
            return

        backup_path = current_item.data(Qt.ItemDataRole.UserRole)
        backup_name = Path(backup_path).name

        reply = QMessageBox.question(
            self,
            "Restore Backup",
            f"Restore from backup: {backup_name}?\\n\\n"
            "This will replace the current database. A backup of the current database will be created first.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.backup_manager.restore_from_backup(backup_path):
                # Emit signal to reload the application
                self.database_changed.emit(self.current_db_path)

    def delete_backup(self):
        """Delete selected backup"""
        current_item = self.backup_list.currentItem()
        if not current_item or not self.backup_manager:
            return

        backup_path = current_item.data(Qt.ItemDataRole.UserRole)
        backup_name = Path(backup_path).name

        reply = QMessageBox.question(
            self,
            "Delete Backup",
            f"Delete backup: {backup_name}?\\n\\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.backup_manager.delete_backup(backup_path):
                self.refresh_backup_list()
                self.add_status_message(f"Deleted backup: {backup_name}")

    def apply_settings(self):
        """Apply backup settings"""
        if not self.backup_manager:
            return

        interval = self.interval_spin.value()
        max_backups = self.max_backups_spin.value()

        self.backup_manager.update_backup_settings(interval, max_backups)
        self.add_status_message(
            f"Settings updated: {interval}min interval, {max_backups} max backups"
        )

    def on_backup_created(self, message: str):
        """Handle backup created signal"""
        self.add_status_message(f"✓ {message}")
        self.refresh_backup_list()

    def on_backup_failed(self, message: str):
        """Handle backup failed signal"""
        self.add_status_message(f"✗ {message}")

    def add_status_message(self, message: str):
        """Add a status message to the status text area"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
