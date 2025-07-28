"""
Shared Qt utilities for tests - handles headless environments
Import Qt components from this module instead of directly from PyQt6
"""

import os
import sys
from unittest.mock import Mock

# Handle headless environments (CI/CD)
def setup_headless_qt():
    """Configure Qt for headless operation"""
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    os.environ.setdefault('DISPLAY', ':99')

# Set up headless mode before importing Qt
if 'CI' in os.environ or 'GITHUB_ACTIONS' in os.environ or '--headless' in sys.argv:
    setup_headless_qt()

# Try to import Qt components
try:
    from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
    from PyQt6.QtWidgets import (
        QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
        QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QDialog,
        QListWidget, QListWidgetItem, QLabel, QPushButton, QComboBox
    )
    from PyQt6.QtGui import QPainter
    
    # Try to import additional classes that might be needed
    try:
        from PyQt6.QtGui import QKeyEvent, QMouseEvent, QContextMenuEvent
        from PyQt6.QtCore import QPoint
        EXTRA_QT_AVAILABLE = True
    except ImportError:
        EXTRA_QT_AVAILABLE = False
    QT_AVAILABLE = True
except ImportError as e:
    # Mock Qt classes when not available
    QT_AVAILABLE = False
    
    # Core classes
    class MockQPointF:
        def __init__(self, x=0, y=0):
            self._x = x
            self._y = y
        def x(self): return self._x
        def y(self): return self._y
    
    class MockQRectF:
        def __init__(self, x=0, y=0, w=0, h=0):
            self._x, self._y, self._w, self._h = x, y, w, h
        def x(self): return self._x
        def y(self): return self._y
        def width(self): return self._w
        def height(self): return self._h
    
    class MockQt:
        class AlignmentFlag:
            AlignCenter = 'AlignCenter'
        class Key:
            Key_Return = 'Key_Return'
            Key_Tab = 'Key_Tab'
    
    class MockQTimer:
        def __init__(self):
            pass
        def start(self, *args): pass
        def stop(self): pass
    
    # Widget classes
    class MockQApplication:
        @staticmethod
        def instance():
            return None
        def __init__(self, *args):
            pass
        def quit(self):
            pass
    
    class MockQGraphicsScene:
        def __init__(self):
            self._items = []
        def items(self):
            return self._items
        def addItem(self, item):
            self._items.append(item)
        def removeItem(self, item):
            if item in self._items:
                self._items.remove(item)
    
    class MockQGraphicsView:
        def __init__(self, *args):
            pass
        def setScene(self, scene):
            pass
    
    class MockQGraphicsItem:
        def __init__(self):
            pass
        def setPos(self, x, y):
            pass
    
    class MockQMessageBox:
        class StandardButton:
            Yes = 'Yes'
            No = 'No'
            Ok = 'Ok'
            Cancel = 'Cancel'
        
        @staticmethod
        def information(*args, **kwargs):
            return Mock()
        
        @staticmethod
        def warning(*args, **kwargs):
            return Mock()
            
        @staticmethod
        def critical(*args, **kwargs):
            return Mock()
            
        @staticmethod
        def question(*args, **kwargs):
            return MockQMessageBox.StandardButton.Yes
    
    class MockQWidget:
        def __init__(self, *args):
            pass
        def show(self):
            pass
        def hide(self):
            pass
    
    class MockQVBoxLayout:
        def __init__(self, *args):
            pass
        def addWidget(self, widget):
            pass
    
    class MockQTextEdit:
        def __init__(self, *args):
            pass
        def setText(self, text):
            pass
        def toPlainText(self):
            return ""
    
    class MockQLineEdit:
        def __init__(self, text="", *args):
            from unittest.mock import Mock
            self._text = text
            self._enabled = True
            self.textChanged = Mock()
        def setText(self, text):
            old_text = self._text
            self._text = text
            if old_text != text:
                self.textChanged.emit(text)
        def text(self):
            return self._text
        def isEnabled(self):
            return self._enabled
        def setEnabled(self, enabled):
            self._enabled = enabled
    
    class MockQDialog:
        def __init__(self, *args):
            pass
        def exec(self):
            return True
        def setWindowTitle(self, title):
            self._title = title
        def windowTitle(self):
            return getattr(self, '_title', '')
        def setModal(self, modal):
            self._modal = modal
        def isModal(self):
            return getattr(self, '_modal', False)
        def accept(self):
            pass
        def reject(self):
            pass
    
    class MockQListWidget:
        def __init__(self, *args):
            self._items = []
        def selectedItems(self):
            return []
        def addItem(self, item):
            self._items.append(item)
    
    class MockQListWidgetItem:
        def __init__(self, text="", *args):
            self._text = text
            self._data = None
        def text(self):
            return self._text
        def data(self, role=0):
            return self._data
        def setData(self, role, value):
            self._data = value
    
    # Assign mock classes
    QPointF = MockQPointF
    QRectF = MockQRectF
    Qt = MockQt
    QTimer = MockQTimer
    QApplication = MockQApplication
    QGraphicsView = MockQGraphicsView
    QGraphicsScene = MockQGraphicsScene
    QGraphicsItem = MockQGraphicsItem
    QMessageBox = MockQMessageBox
    QWidget = MockQWidget
    QVBoxLayout = MockQVBoxLayout
    QTextEdit = MockQTextEdit
    QLineEdit = MockQLineEdit
    QDialog = MockQDialog
    QListWidget = MockQListWidget
    QListWidgetItem = MockQListWidgetItem
    
    # Mock layout classes
    class MockQHBoxLayout:
        def __init__(self, *args):
            self._widgets = []
        def addWidget(self, widget):
            self._widgets.append(widget)
        def addLayout(self, layout):
            self._widgets.append(layout)
        def count(self):
            return len(self._widgets)
        def itemAt(self, index):
            class MockLayoutItem:
                def __init__(self, widget):
                    self._widget = widget
                def widget(self):
                    return self._widget
            if 0 <= index < len(self._widgets):
                return MockLayoutItem(self._widgets[index])
            return None
    
    # Mock widget classes
    class MockQLabel:
        def __init__(self, text="", *args):
            self._text = text
        def text(self):
            return self._text
        def setText(self, text):
            self._text = text
    
    class MockQPushButton:
        def __init__(self, text="", *args):
            from unittest.mock import Mock
            self._text = text
            self._enabled = True
            self.clicked = Mock()
        def text(self):
            return self._text
        def setText(self, text):
            self._text = text
        def isEnabled(self):
            return self._enabled
        def setEnabled(self, enabled):
            self._enabled = enabled
    
    class MockQComboBox:
        def __init__(self, *args):
            self._items = []
            self._current_index = 0
        def addItem(self, text, data=None):
            self._items.append({'text': text, 'data': data})
            if len(self._items) == 1:
                self._current_index = 0
        def count(self):
            return len(self._items)
        def currentText(self):
            if 0 <= self._current_index < len(self._items):
                return self._items[self._current_index]['text']
            return ""
        def currentData(self, role=0):
            if 0 <= self._current_index < len(self._items):
                return self._items[self._current_index]['data']
            return None
        def setCurrentIndex(self, index):
            if 0 <= index < len(self._items):
                self._current_index = index
        def currentIndex(self):
            return self._current_index
    
    # Mock additional classes
    class MockQPainter:
        def __init__(self, *args): pass
        def drawLine(self, *args): pass
        def setPen(self, *args): pass
    
    class MockQPoint:
        def __init__(self, x=0, y=0):
            self._x, self._y = x, y
        def x(self): return self._x
        def y(self): return self._y
    
    class MockQKeyEvent:
        def __init__(self, *args): pass
        def key(self): return 0
    
    class MockQMouseEvent:
        def __init__(self, *args): pass
        def pos(self): return MockQPoint()
    
    class MockQContextMenuEvent:
        def __init__(self, *args): pass
        def pos(self): return MockQPoint()
    
    QHBoxLayout = MockQHBoxLayout
    QLabel = MockQLabel
    QPushButton = MockQPushButton
    QComboBox = MockQComboBox
    QPainter = MockQPainter
    QPoint = MockQPoint  
    QKeyEvent = MockQKeyEvent
    QMouseEvent = MockQMouseEvent
    QContextMenuEvent = MockQContextMenuEvent

# Export commonly used classes
__all__ = [
    'QT_AVAILABLE',
    'QPointF', 'QRectF', 'Qt', 'QTimer',
    'QApplication', 'QGraphicsView', 'QGraphicsScene', 'QGraphicsItem',
    'QMessageBox', 'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QTextEdit', 'QLineEdit', 'QDialog',
    'QListWidget', 'QListWidgetItem', 'QLabel', 'QPushButton', 'QComboBox',
    'QPainter', 'QPoint', 'QKeyEvent', 'QMouseEvent', 'QContextMenuEvent'
]