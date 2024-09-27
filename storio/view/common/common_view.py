"""Holds the common classes for views"""

from PyQt6.QtCore import QPoint, QPropertyAnimation
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BaseView(QWidget):
    """Base views"""
