"""
Simple test configuration for Storymaster tests
"""

import pytest
from unittest.mock import patch, Mock
from PyQt6.QtWidgets import QApplication, QMessageBox


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here as other tests might need it


@pytest.fixture(autouse=True)
def mock_message_boxes():
    """Automatically mock all QMessageBox dialogs to prevent them from appearing"""
    with patch.object(QMessageBox, 'information', return_value=Mock()) as mock_info, \
         patch.object(QMessageBox, 'warning', return_value=Mock()) as mock_warning, \
         patch.object(QMessageBox, 'critical', return_value=Mock()) as mock_critical, \
         patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes) as mock_question:
        yield {
            'information': mock_info,
            'warning': mock_warning, 
            'critical': mock_critical,
            'question': mock_question
        }