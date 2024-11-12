"""Holds the common classes for views"""

from PyQt5.QtCore import QPoint, QPropertyAnimation
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BaseView(QWidget):
    """Base views"""
