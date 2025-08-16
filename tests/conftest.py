"""
Simple test configuration for Storymaster tests
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock, MagicMock


# Handle headless environments (CI/CD)
def setup_headless_qt():
    """Configure Qt for headless operation"""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("DISPLAY", ":99")


# Set up headless mode before importing Qt
if "CI" in os.environ or "GITHUB_ACTIONS" in os.environ or "--headless" in sys.argv:
    setup_headless_qt()


# Mock problematic application modules before they're imported
def mock_application_modules():
    """Mock application modules that have Qt imports"""
    if not QT_AVAILABLE:
        # Mock the problematic application modules
        problematic_modules = [
            "storymaster.view.common.plot_manager_dialog",
            "storymaster.controller.common.main_page_controller",
            "storymaster.view.common.custom_widgets",
            "storymaster.view.common.spellcheck",
            "storymaster.view.common.new_user_dialog",
            "storymaster.view.common.new_setting_dialog",
            "storymaster.view.common.new_storyline_dialog",
            "storymaster.view.common.storyline_settings_dialog",
            "storymaster.view.common.spell_check_config",
        ]

        for module_name in problematic_modules:
            if module_name not in sys.modules:
                mock_module = MagicMock()
                # Add common attributes that tests might expect
                mock_module.PlotManagerDialog = MagicMock()
                mock_module.create_node_item = MagicMock()
                mock_module.TabNavigationTextEdit = MagicMock()
                mock_module.TabNavigationLineEdit = MagicMock()
                mock_module.TabNavigationComboBox = MagicMock()
                mock_module.enable_smart_tab_navigation = MagicMock()
                mock_module.SpellChecker = MagicMock()
                mock_module.SpellCheckTextEdit = MagicMock()
                mock_module.SpellCheckLineEdit = MagicMock()
                mock_module.SpellCheckHighlighter = MagicMock()
                mock_module.BasicWordList = MagicMock()
                mock_module.enable_spell_check = MagicMock()
                mock_module.get_spell_checker = MagicMock()
                mock_module.NewUserDialog = MagicMock()
                mock_module.NewSettingDialog = MagicMock()
                mock_module.NewStorylineDialog = MagicMock()
                mock_module.StorylineSettingsDialog = MagicMock()
                mock_module.SpellCheckConfigDialog = MagicMock()
                sys.modules[module_name] = mock_module


# Try to import Qt first to determine availability
try:
    from PySide6.QtWidgets import QApplication, QMessageBox

    QT_AVAILABLE = True
except ImportError as e:
    QT_AVAILABLE = False

# Now mock application modules if Qt is not available
mock_application_modules()

# Continue with Qt mocking if needed
if not QT_AVAILABLE:

    class MockQApplication:
        @staticmethod
        def instance():
            return None

        def __init__(self, *args):
            pass

    class MockQMessageBox:
        class StandardButton:
            Yes = "Yes"

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
            "question": Mock(return_value="Yes"),
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
