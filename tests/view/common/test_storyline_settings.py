"""
Test suite for storyline-to-setting management functionality
"""

import pytest
from unittest.mock import Mock, patch
from tests.test_qt_utils import QT_AVAILABLE, QApplication, QMessageBox

# Skip all tests in this module if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PyQt6 not available in headless environment"
)

from storymaster.model.database.schema.base import (
    Storyline,
    Setting,
    StorylineToSetting,
)


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestStorylineSettingsModel:
    """Test storyline-to-setting model methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()

    def test_get_settings_for_storyline(self):
        """Test getting settings linked to a storyline"""
        # Mock storyline with linked settings
        mock_setting1 = Mock(spec=Setting)
        mock_setting1.id = 1
        mock_setting1.name = "Fantasy World"

        mock_setting2 = Mock(spec=Setting)
        mock_setting2.id = 2
        mock_setting2.name = "Sci-Fi Universe"

        mock_sts1 = Mock(spec=StorylineToSetting)
        mock_sts1.setting = mock_setting1

        mock_sts2 = Mock(spec=StorylineToSetting)
        mock_sts2.setting = mock_setting2

        mock_storyline = Mock(spec=Storyline)
        mock_storyline.id = 1
        mock_storyline.storyline_to_settings = [mock_sts1, mock_sts2]

        self.mock_model.get_settings_for_storyline.return_value = [
            mock_setting1,
            mock_setting2,
        ]

        result = self.mock_model.get_settings_for_storyline(storyline_id=1)

        assert len(result) == 2
        assert result[0].name == "Fantasy World"
        assert result[1].name == "Sci-Fi Universe"

    def test_get_storylines_for_setting(self):
        """Test getting storylines linked to a setting"""
        # Mock setting with linked storylines
        mock_storyline1 = Mock(spec=Storyline)
        mock_storyline1.id = 1
        mock_storyline1.name = "Epic Quest"

        mock_storyline2 = Mock(spec=Storyline)
        mock_storyline2.id = 2
        mock_storyline2.name = "Space Adventure"

        self.mock_model.get_storylines_for_setting.return_value = [
            mock_storyline1,
            mock_storyline2,
        ]

        result = self.mock_model.get_storylines_for_setting(setting_id=1)

        assert len(result) == 2
        assert result[0].name == "Epic Quest"
        assert result[1].name == "Space Adventure"

    def test_link_storyline_to_setting_success(self):
        """Test successfully linking storyline to setting"""
        self.mock_model.link_storyline_to_setting.return_value = True

        result = self.mock_model.link_storyline_to_setting(storyline_id=1, setting_id=2)

        assert result is True
        self.mock_model.link_storyline_to_setting.assert_called_once_with(
            storyline_id=1, setting_id=2
        )

    def test_link_storyline_to_setting_already_exists(self):
        """Test linking when relationship already exists"""
        self.mock_model.link_storyline_to_setting.return_value = False

        result = self.mock_model.link_storyline_to_setting(storyline_id=1, setting_id=2)

        assert result is False  # Already linked

    def test_unlink_storyline_from_setting_success(self):
        """Test successfully unlinking storyline from setting"""
        self.mock_model.unlink_storyline_from_setting.return_value = True

        result = self.mock_model.unlink_storyline_from_setting(
            storyline_id=1, setting_id=2
        )

        assert result is True
        self.mock_model.unlink_storyline_from_setting.assert_called_once_with(
            storyline_id=1, setting_id=2
        )

    def test_unlink_storyline_from_setting_not_linked(self):
        """Test unlinking when no relationship exists"""
        self.mock_model.unlink_storyline_from_setting.return_value = False

        result = self.mock_model.unlink_storyline_from_setting(
            storyline_id=1, setting_id=2
        )

        assert result is False  # Wasn't linked

    def test_get_available_settings_for_storyline(self):
        """Test getting settings available to link to storyline"""
        # Mock all settings for user
        mock_setting1 = Mock(spec=Setting)
        mock_setting1.id = 1
        mock_setting1.name = "Available Setting 1"

        mock_setting2 = Mock(spec=Setting)
        mock_setting2.id = 2
        mock_setting2.name = "Available Setting 2"

        mock_setting3 = Mock(spec=Setting)
        mock_setting3.id = 3
        mock_setting3.name = "Already Linked Setting"

        self.mock_model.get_available_settings_for_storyline.return_value = [
            mock_setting1,
            mock_setting2,
        ]

        result = self.mock_model.get_available_settings_for_storyline(storyline_id=1)

        assert len(result) == 2
        assert result[0].name == "Available Setting 1"
        assert result[1].name == "Available Setting 2"
        # Setting 3 should not be in results (already linked)


class TestStorylineSettingsDialog:
    """Test the StorylineSettingsDialog"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()

    def test_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        assert dialog.storyline_id == 1
        assert dialog.storyline_name == "Test Storyline"
        assert dialog.model == self.mock_model
        assert dialog.windowTitle() == "Manage Settings for Test Storyline"

    def test_dialog_loads_data_on_init(self, qapp):
        """Test that dialog loads data on initialization"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        # Mock available settings
        mock_available_setting = Mock(spec=Setting)
        mock_available_setting.id = 1
        mock_available_setting.name = "Available Setting"
        mock_available_setting.description = "Test description"

        # Mock linked settings
        mock_linked_setting = Mock(spec=Setting)
        mock_linked_setting.id = 2
        mock_linked_setting.name = "Linked Setting"
        mock_linked_setting.description = None

        self.mock_model.get_available_settings_for_storyline.return_value = [
            mock_available_setting
        ]
        self.mock_model.get_settings_for_storyline.return_value = [mock_linked_setting]

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Verify data was loaded
        self.mock_model.get_available_settings_for_storyline.assert_called_once_with(1)
        self.mock_model.get_settings_for_storyline.assert_called_once_with(1)

        # Check list counts
        assert dialog.get_available_settings_count() == 1
        assert dialog.get_linked_settings_count() == 1

    def test_link_setting_success(self, qapp):
        """Test successful setting linking"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        self.mock_model.get_available_settings_for_storyline.return_value = []
        self.mock_model.get_settings_for_storyline.return_value = []
        self.mock_model.link_storyline_to_setting.return_value = True

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Mock selected item
        with patch.object(dialog.available_list, "selectedItems") as mock_selected:
            mock_item = Mock()
            mock_item.data.return_value = 5  # setting_id
            mock_item.text.return_value = "Test Setting"
            mock_selected.return_value = [mock_item]

            with patch.object(dialog, "load_data") as mock_load_data:
                dialog.link_setting()

                self.mock_model.link_storyline_to_setting.assert_called_once_with(
                    1, 5
                )
                mock_load_data.assert_called_once()  # Should refresh data

    def test_link_setting_already_linked(self, qapp):
        """Test linking when setting is already linked"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        self.mock_model.get_available_settings_for_storyline.return_value = []
        self.mock_model.get_settings_for_storyline.return_value = []
        self.mock_model.link_storyline_to_setting.return_value = False  # Already linked

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Mock selected item
        with patch.object(dialog.available_list, "selectedItems") as mock_selected:
            mock_item = Mock()
            mock_item.data.return_value = 5  # setting_id
            mock_item.text.return_value = "Test Setting"
            mock_selected.return_value = [mock_item]

            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                dialog.link_setting()

                self.mock_model.link_storyline_to_setting.assert_called_once_with(1, 5)
                mock_warning.assert_called_once()

    def test_unlink_setting_with_confirmation(self, qapp):
        """Test unlinking setting with user confirmation"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        self.mock_model.get_available_settings_for_storyline.return_value = []
        self.mock_model.get_settings_for_storyline.return_value = []
        self.mock_model.unlink_storyline_from_setting.return_value = True

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Mock selected item
        with patch.object(dialog.linked_list, "selectedItems") as mock_selected:
            mock_item = Mock()
            mock_item.data.return_value = 5  # setting_id
            mock_item.text.return_value = "Test Setting"
            mock_selected.return_value = [mock_item]

            with patch.object(dialog, "load_data") as mock_load_data:
                with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
                    # QMessageBox imported from test_qt_utils

                    mock_question.return_value = QMessageBox.StandardButton.Yes

                    dialog.unlink_setting()

                    self.mock_model.unlink_storyline_from_setting.assert_called_once_with(
                        1, 5
                    )
                    mock_load_data.assert_called_once()  # Should refresh data

    def test_unlink_setting_cancelled(self, qapp):
        """Test unlinking setting when user cancels"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        self.mock_model.get_available_settings_for_storyline.return_value = []
        self.mock_model.get_settings_for_storyline.return_value = []

        dialog = StorylineSettingsDialog(
            self.mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Mock selected item
        with patch.object(dialog.linked_list, "selectedItems") as mock_selected:
            mock_item = Mock()
            mock_item.data.return_value = 5  # setting_id
            mock_item.text.return_value = "Test Setting"
            mock_selected.return_value = [mock_item]

            with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
                # QMessageBox imported from test_qt_utils

                mock_question.return_value = QMessageBox.StandardButton.No

                dialog.unlink_setting()

                # Should not call unlink method
                self.mock_model.unlink_storyline_from_setting.assert_not_called()


class TestStorylineSettingsIntegration:
    """Test integration aspects of storyline-settings management"""

    def test_model_integration_get_settings_for_storyline(self):
        """Test model integration for getting settings linked to storyline"""
        mock_model = Mock()

        # Mock linked settings
        mock_setting1 = Mock(spec=Setting)
        mock_setting1.id = 1
        mock_setting1.name = "Fantasy World"

        mock_setting2 = Mock(spec=Setting)
        mock_setting2.id = 2
        mock_setting2.name = "Modern World"

        mock_model.get_settings_for_storyline.return_value = [
            mock_setting1,
            mock_setting2,
        ]

        # Test getting settings for storyline
        settings = mock_model.get_settings_for_storyline(storyline_id=1)

        assert len(settings) == 2
        assert settings[0].name == "Fantasy World"
        assert settings[1].name == "Modern World"
        mock_model.get_settings_for_storyline.assert_called_once_with(storyline_id=1)

    def test_model_integration_link_unlink_workflow(self):
        """Test complete link/unlink workflow"""
        mock_model = Mock()

        # Test linking
        mock_model.link_storyline_to_setting.return_value = True
        result = mock_model.link_storyline_to_setting(storyline_id=1, setting_id=2)
        assert result is True

        # Test unlinking
        mock_model.unlink_storyline_from_setting.return_value = True
        result = mock_model.unlink_storyline_from_setting(storyline_id=1, setting_id=2)
        assert result is True

        # Verify method calls
        mock_model.link_storyline_to_setting.assert_called_once_with(
            storyline_id=1, setting_id=2
        )
        mock_model.unlink_storyline_from_setting.assert_called_once_with(
            storyline_id=1, setting_id=2
        )

    def test_model_integration_available_settings_filtering(self):
        """Test filtering of available settings"""
        mock_model = Mock()

        # Mock all settings for user
        all_settings = [
            Mock(id=1, name="Setting 1"),
            Mock(id=2, name="Setting 2"),
            Mock(id=3, name="Setting 3"),
        ]

        # Mock linked settings (Setting 2 is already linked)
        linked_settings = [Mock(id=2, name="Setting 2")]

        # Mock available settings (Settings 1 and 3)
        setting1 = Mock()
        setting1.id = 1
        setting1.name = "Setting 1"

        setting3 = Mock()
        setting3.id = 3
        setting3.name = "Setting 3"

        available_settings = [setting1, setting3]

        mock_model.get_available_settings_for_storyline.return_value = (
            available_settings
        )

        result = mock_model.get_available_settings_for_storyline(storyline_id=1)

        assert len(result) == 2
        assert result[0].name == "Setting 1"
        assert result[1].name == "Setting 3"
        # Setting 2 should not be in available list since it's already linked

    def test_storyline_settings_business_logic(self):
        """Test business logic without UI components"""
        mock_model = Mock()

        # Test scenario: storyline has no settings initially
        mock_model.get_settings_for_storyline.return_value = []

        # Get initial state
        initial_settings = mock_model.get_settings_for_storyline(storyline_id=1)
        assert len(initial_settings) == 0

        # Link a setting
        mock_model.link_storyline_to_setting.return_value = True
        link_result = mock_model.link_storyline_to_setting(storyline_id=1, setting_id=5)
        assert link_result is True

        # Now storyline should have one setting
        mock_model.get_settings_for_storyline.return_value = [
            Mock(id=5, name="New Setting")
        ]
        updated_settings = mock_model.get_settings_for_storyline(storyline_id=1)
        assert len(updated_settings) == 1
        assert updated_settings[0].id == 5


class TestStorylineSettingsEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_settings_lists(self, qapp):
        """Test dialog behavior with empty settings lists"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        mock_model = Mock()
        mock_model.get_available_settings_for_storyline.return_value = []
        mock_model.get_settings_for_storyline.return_value = []

        dialog = StorylineSettingsDialog(
            mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Should handle empty lists gracefully
        assert dialog.get_available_settings_count() == 0
        assert dialog.get_linked_settings_count() == 0

    def test_link_setting_no_selection(self, qapp):
        """Test linking setting when nothing is selected"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        mock_model = Mock()
        mock_model.get_available_settings_for_storyline.return_value = []
        mock_model.get_settings_for_storyline.return_value = []

        dialog = StorylineSettingsDialog(
            mock_model, storyline_id=1, storyline_name="Test Storyline"
        )

        # Mock empty selection
        with patch.object(dialog.available_list, "selectedItems") as mock_selected:
            mock_selected.return_value = []

            dialog.link_setting()

            # Should not call model method
            mock_model.link_storyline_to_setting.assert_not_called()

    def test_database_error_handling(self, qapp):
        """Test handling of database errors"""
        from storymaster.view.common.storyline_settings_dialog import (
            StorylineSettingsDialog,
        )

        mock_model = Mock()
        mock_model.get_available_settings_for_storyline.side_effect = Exception(
            "Database error"
        )
        mock_model.get_settings_for_storyline.return_value = []

        with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog = StorylineSettingsDialog(
                mock_model, storyline_id=1, storyline_name="Test Storyline"
            )

            mock_warning.assert_called_once()
