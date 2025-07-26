"""
Simple test configuration for Storymaster tests
"""

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here as other tests might need it