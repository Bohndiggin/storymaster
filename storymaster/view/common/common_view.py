"""Holds the common classes for views"""

from PyQt6.QtCore import QPoint, QPropertyAnimation
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMainWindow
)

from storymaster.view.common.main_page import Ui_MainWindow


class BaseView(QMainWindow):
    """Base views"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Story Master")


class MainView(BaseView):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
