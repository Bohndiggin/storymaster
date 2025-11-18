"""Holds the common classes for views"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPoint, QPropertyAnimation
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

    def closeEvent(self, event):
        """Handle window close event to cleanup resources."""
        if self.controller and hasattr(self.controller, "cleanup"):
            self.controller.cleanup()
        event.accept()
