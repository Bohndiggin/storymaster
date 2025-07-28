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
        QMessageBox, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QDialog,
        QListWidget, QListWidgetItem
    )
    from PyQt6.QtGui import QPainter
    
    # Try to import additional classes that might be needed
    try:
        from PyQt6.QtWidgets import QContextMenuEvent, QKeyEvent, QMouseEvent
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
        def __init__(self, *args):
            pass
        def setText(self, text):
            pass
        def text(self):
            return ""
    
    class MockQDialog:
        def __init__(self, *args):
            pass
        def exec(self):
            return True
    
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
    'QMessageBox', 'QWidget', 'QVBoxLayout', 'QTextEdit', 'QLineEdit', 'QDialog',
    'QListWidget', 'QListWidgetItem', 'QPainter', 'QPoint', 'QKeyEvent', 
    'QMouseEvent', 'QContextMenuEvent'
]