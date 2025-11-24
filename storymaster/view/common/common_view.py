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
        # Create Tools menu (or add to existing File menu)
        tools_menu = self.ui.menubar.addMenu("Tools")

        # Create Sync Settings action
        sync_action = QAction("📱 Mobile Sync Settings", self)
        sync_action.setStatusTip("Manage mobile device synchronization")
        sync_action.triggered.connect(self.show_sync_dialog)

        tools_menu.addAction(sync_action)

    def show_sync_dialog(self):
        """Show the sync management dialog"""
        from storymaster.view.common.sync_dialog import SyncDialog

        dialog = SyncDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """Handle window close event to cleanup resources."""
        if self.controller and hasattr(self.controller, "cleanup"):
            self.controller.cleanup()
        event.accept()
