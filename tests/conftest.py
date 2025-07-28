"""
Simple test configuration for Storymaster tests
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock

# Handle headless environments (CI/CD)
def setup_headless_qt():
    """Configure Qt for headless operation"""
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    os.environ.setdefault('DISPLAY', ':99')

# Set up headless mode before importing Qt
if 'CI' in os.environ or 'GITHUB_ACTIONS' in os.environ or '--headless' in sys.argv:
    setup_headless_qt()

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    QT_AVAILABLE = True
except ImportError as e:
    # Mock Qt classes when not available
    QT_AVAILABLE = False
    
    class MockQApplication:
        @staticmethod
        def instance():
            return None
        def __init__(self, *args):
            pass
    
    class MockQMessageBox:
        class StandardButton:
            Yes = 'Yes'
        
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
    
    QApplication = MockQApplication
    QMessageBox = MockQMessageBox


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    if not QT_AVAILABLE:
        # Return mock app for headless environments
        return MockQApplication()
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here as other tests might need it


@pytest.fixture(autouse=True)
def mock_message_boxes():
    """Automatically mock all QMessageBox dialogs to prevent them from appearing"""
    if not QT_AVAILABLE:
        # Return mock objects when Qt is not available
        yield {
            "information": Mock(),
            "warning": Mock(),
            "critical": Mock(),
            "question": Mock(return_value='Yes'),
        }
        return
    
    with patch.object(
        QMessageBox, "information", return_value=Mock()
    ) as mock_info, patch.object(
        QMessageBox, "warning", return_value=Mock()
    ) as mock_warning, patch.object(
        QMessageBox, "critical", return_value=Mock()
    ) as mock_critical, patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
    ) as mock_question:
        yield {
            "information": mock_info,
            "warning": mock_warning,
            "critical": mock_critical,
            "question": mock_question,
        }
