"""Holds the common classes for views"""

from PyQt5.QtCore import QPoint, QPropertyAnimation
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMainWindow
)

from storymaster.view.main_page import Ui_MainWindow


class BaseView(QMainWindow):
    """Base views"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Story Master")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
