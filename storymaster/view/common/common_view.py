"""Holds the common classes for views"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPoint, QPropertyAnimation
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from storymaster.view.common.storymaster_main import Ui_StorymasterMainWindow
from storymaster.view.common.theme import get_main_window_style

if TYPE_CHECKING:
    from storymaster.controller.common.main_page_controller import MainWindowController


class BaseView(QMainWindow):
    """Base views"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Story Master")


class MainView(BaseView):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_StorymasterMainWindow()
        self.ui.setupUi(self)

        # Override the generated stylesheet with our theme system
        self.setStyleSheet(get_main_window_style())

        # Controller reference (set by controller after initialization)
        self.controller: Optional["MainWindowController"] = None

        # Add Sync menu item
        self._setup_sync_menu()

    def _setup_sync_menu(self):
        """Add Sync menu to menubar"""
        tools_menu = self.ui.menubar.addMenu("Tools")

        sync_action = QAction("Mobile Sync Settings", self)
        sync_action.setStatusTip("Manage mobile device synchronization")
        sync_action.triggered.connect(self.show_sync_dialog)
        tools_menu.addAction(sync_action)

        remote_action = QAction("Configure Remote Sync...", self)
        remote_action.setStatusTip("Pair this desktop with a self-hosted sync server")
        remote_action.triggered.connect(self.show_remote_sync_dialog)
        tools_menu.addAction(remote_action)

        tools_menu.addSeparator()

        sync_now_action = QAction("Sync Now", self)
        sync_now_action.setStatusTip("Push local changes and pull remote changes")
        sync_now_action.triggered.connect(self.run_sync_now)
        tools_menu.addAction(sync_now_action)

    def show_sync_dialog(self):
        """Show the sync management dialog"""
        from storymaster.view.common.sync_dialog import SyncDialog

        dialog = SyncDialog(self)
        dialog.exec()

    def show_remote_sync_dialog(self):
        from storymaster.view.common.remote_sync_dialog import RemoteSyncDialog

        dialog = RemoteSyncDialog(self)
        dialog.exec()

    def run_sync_now(self):
        from PySide6.QtWidgets import QMessageBox

        from storymaster.sync_client.client import SyncClient, SyncError

        client = SyncClient()
        if not client.is_configured():
            QMessageBox.information(
                self,
                "Sync not configured",
                "Configure a remote sync server first via Tools → Configure Remote Sync.",
            )
            return
        try:
            result = client.sync_now()
        except SyncError as e:
            QMessageBox.warning(self, "Sync failed", str(e))
            return
        QMessageBox.information(
            self,
            "Sync complete",
            f"Pushed: {result['push']['sent']} sent, "
            f"{result['push']['accepted']} accepted, "
            f"{result['push']['conflicts']} conflicts.\n"
            f"Pulled: {result['pull']['accepted']} applied, "
            f"{result['pull']['conflicts']} conflicts.",
        )

    def closeEvent(self, event):
        """Handle window close event to cleanup resources."""
        if self.controller and hasattr(self.controller, "cleanup"):
            self.controller.cleanup()
        event.accept()
