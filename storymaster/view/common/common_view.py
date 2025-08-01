"""Holds the common classes for views"""

from PyQt6.QtCore import QPoint, QPropertyAnimation
from PyQt6.QtWidgets import (
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
