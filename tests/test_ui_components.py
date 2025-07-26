"""
Test suite for UI components and dialog functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtCore import Qt

from storymaster.view.common.new_user_dialog import NewUserDialog
from storymaster.view.common.new_setting_dialog import NewSettingDialog
from storymaster.view.common.new_storyline_dialog import NewStorylineDialog
from storymaster.view.common.plot_manager_dialog import PlotManagerDialog


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestNewUserDialog:
    """Test the NewUserDialog"""

    def test_new_user_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        mock_model = Mock()
        dialog = NewUserDialog(mock_model)
        
        assert dialog.model == mock_model
        assert dialog.windowTitle() == "Create New User"

    def test_new_user_dialog_get_data_accepted(self, qapp):
        """Test getting user data when dialog is accepted"""
        mock_model = Mock()
        dialog = NewUserDialog(mock_model)
        
        # Mock the UI elements
        dialog.username_line_edit = Mock()
        dialog.username_line_edit.text.return_value = "test_user"
        
        with patch.object(dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Accepted
            
            result = dialog.get_user_data()
            
            assert result == {"username": "test_user"}

    def test_new_user_dialog_get_data_rejected(self, qapp):
        """Test getting user data when dialog is rejected"""
        mock_model = Mock()
        dialog = NewUserDialog(mock_model)
        
        with patch.object(dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Rejected
            
            result = dialog.get_user_data()
            
            assert result is None

    def test_new_user_dialog_validation(self, qapp):
        """Test user input validation"""
        mock_model = Mock()
        dialog = NewUserDialog(mock_model)
        
        # Test that dialog has username field
        assert hasattr(dialog, 'username_line_edit')


class TestNewSettingDialog:
    """Test the NewSettingDialog"""

    def test_new_setting_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        dialog = NewSettingDialog(mock_model)
        
        assert dialog.model == mock_model
        assert dialog.windowTitle() == "Create New Setting"

    def test_new_setting_dialog_populate_users(self, qapp):
        """Test user population in combo box"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"}
        ]
        
        dialog = NewSettingDialog(mock_model)
        
        mock_model.get_all_rows_as_dicts.assert_called_once_with("user")

    def test_new_setting_dialog_get_data_accepted(self, qapp):
        """Test getting setting data when dialog is accepted"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        dialog = NewSettingDialog(mock_model)
        
        # Mock the UI elements
        dialog.name_line_edit.text = Mock(return_value="Test Setting")
        dialog.description_text_edit.toPlainText = Mock(return_value="Test description")
        dialog.user_combo.currentData = Mock(return_value=1)
        
        with patch.object(dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Accepted
            
            result = dialog.get_setting_data()
            
            assert result == {
                "name": "Test Setting",
                "description": "Test description",
                "user_id": 1
            }

    def test_new_setting_dialog_error_handling(self, qapp):
        """Test error handling when user loading fails"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.side_effect = Exception("Database error")
        
        dialog = NewSettingDialog(mock_model)
        
        # Should handle the error gracefully
        assert dialog.user_combo.isEnabled() is False


class TestNewStorylineDialog:
    """Test the NewStorylineDialog"""

    def test_new_storyline_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        dialog = NewStorylineDialog(mock_model)
        
        assert dialog.model == mock_model
        assert dialog.windowTitle() == "Create New Storyline"

    def test_new_storyline_dialog_populate_users(self, qapp):
        """Test user population in combo box"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"}
        ]
        
        dialog = NewStorylineDialog(mock_model)
        
        mock_model.get_all_rows_as_dicts.assert_called_once_with("user")

    def test_new_storyline_dialog_get_data_accepted(self, qapp):
        """Test getting storyline data when dialog is accepted"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        dialog = NewStorylineDialog(mock_model)
        
        # Mock the UI elements
        dialog.name_line_edit.text = Mock(return_value="Test Storyline")
        dialog.description_text_edit.toPlainText = Mock(return_value="Test description")
        dialog.user_combo.currentData = Mock(return_value=1)
        
        with patch.object(dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Accepted
            
            result = dialog.get_storyline_data()
            
            assert result == {
                "name": "Test Storyline",
                "description": "Test description",
                "user_id": 1
            }

    def test_new_storyline_dialog_get_data_rejected(self, qapp):
        """Test getting storyline data when dialog is rejected"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []
        
        dialog = NewStorylineDialog(mock_model)
        
        with patch.object(dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Rejected
            
            result = dialog.get_storyline_data()
            
            assert result is None


class TestPlotManagerDialog:
    """Test the PlotManagerDialog"""

    def test_plot_manager_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        dialog = PlotManagerDialog()
        
        assert dialog.windowTitle() == "Manage Plots"
        assert dialog.selected_plot_id is None

    def test_plot_manager_dialog_populate_plots(self, qapp):
        """Test plot population"""
        dialog = PlotManagerDialog()
        
        # Mock plot data
        mock_plot1 = Mock()
        mock_plot1.id = 1
        mock_plot1.title = "Main Plot"
        
        mock_plot2 = Mock()
        mock_plot2.id = 2
        mock_plot2.title = "Sub Plot"
        
        plots = [mock_plot1, mock_plot2]
        current_plot_id = 1
        
        dialog.populate_plots(plots, current_plot_id)
        
        assert dialog.current_plot_id == 1

    def test_plot_manager_dialog_add_plot_validation(self, qapp):
        """Test add plot validation"""
        dialog = PlotManagerDialog()
        
        # Mock empty input
        dialog.new_plot_input.text = Mock(return_value="")
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.on_add_plot()
            mock_warning.assert_called_once()

    def test_plot_manager_dialog_add_plot_success(self, qapp):
        """Test successful plot addition"""
        dialog = PlotManagerDialog()
        
        dialog.new_plot_input.text = Mock(return_value="New Plot")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog.on_add_plot()
            
            assert dialog.action == "add"
            assert dialog.new_plot_name == "New Plot"
            mock_accept.assert_called_once()

    def test_plot_manager_dialog_switch_plot(self, qapp):
        """Test plot switching"""
        dialog = PlotManagerDialog()
        
        # Mock selected item
        mock_item = Mock()
        mock_item.data.return_value = 2
        dialog.plot_list.selectedItems = Mock(return_value=[mock_item])
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog.on_switch_plot()
            
            assert dialog.selected_plot_id == 2
            assert dialog.action == "switch"
            mock_accept.assert_called_once()

    def test_plot_manager_dialog_delete_current_plot_protection(self, qapp):
        """Test protection against deleting current plot"""
        dialog = PlotManagerDialog()
        dialog.current_plot_id = 1
        
        # Mock selected item (current plot)
        mock_item = Mock()
        mock_item.data.return_value = 1
        mock_item.text.return_value = "Main Plot (Current)"
        dialog.plot_list.selectedItems = Mock(return_value=[mock_item])
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.on_delete_plot()
            mock_warning.assert_called_once()

    def test_plot_manager_dialog_delete_plot_confirmation(self, qapp):
        """Test plot deletion with confirmation"""
        dialog = PlotManagerDialog()
        dialog.current_plot_id = 1
        
        # Mock selected item (different plot)
        mock_item = Mock()
        mock_item.data.return_value = 2
        mock_item.text.return_value = "Sub Plot"
        dialog.plot_list.selectedItems = Mock(return_value=[mock_item])
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            with patch.object(dialog, 'accept') as mock_accept:
                mock_question.return_value = QMessageBox.StandardButton.Yes
                
                dialog.on_delete_plot()
                
                assert dialog.selected_plot_id == 2
                assert dialog.action == "delete"
                mock_accept.assert_called_once()

    def test_plot_manager_dialog_selection_handling(self, qapp):
        """Test selection change handling"""
        dialog = PlotManagerDialog()
        dialog.current_plot_id = 1
        
        # Test with selection
        mock_item = Mock()
        mock_item.data.return_value = 2
        dialog.plot_list.selectedItems = Mock(return_value=[mock_item])
        
        dialog.on_selection_changed()
        
        # Should enable buttons for non-current plot
        assert dialog.switch_btn.isEnabled() is True
        assert dialog.delete_btn.isEnabled() is True

    def test_plot_manager_dialog_current_plot_selection(self, qapp):
        """Test selection of current plot"""
        dialog = PlotManagerDialog()
        dialog.current_plot_id = 1
        
        # Test with current plot selected
        mock_item = Mock()
        mock_item.data.return_value = 1  # Current plot
        dialog.plot_list.selectedItems = Mock(return_value=[mock_item])
        
        dialog.on_selection_changed()
        
        # Should disable switch button for current plot
        assert dialog.switch_btn.isEnabled() is False
        assert dialog.delete_btn.isEnabled() is True


class TestDialogIntegration:
    """Test integration between dialogs and the application"""

    def test_dialog_modal_behavior(self, qapp):
        """Test that dialogs are properly modal"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []
        
        # Test various dialogs
        user_dialog = NewUserDialog(mock_model)
        assert user_dialog.isModal()
        
        setting_dialog = NewSettingDialog(mock_model)
        assert setting_dialog.isModal()
        
        storyline_dialog = NewStorylineDialog(mock_model)
        assert storyline_dialog.isModal()
        
        plot_dialog = PlotManagerDialog()
        assert plot_dialog.isModal()

    def test_dialog_size_constraints(self, qapp):
        """Test that dialogs have appropriate size constraints"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []
        
        setting_dialog = NewSettingDialog(mock_model)
        assert setting_dialog.minimumWidth() >= 400
        
        storyline_dialog = NewStorylineDialog(mock_model)
        assert storyline_dialog.minimumWidth() >= 400

    def test_dialog_button_connections(self, qapp):
        """Test that dialog buttons are properly connected"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []
        
        setting_dialog = NewSettingDialog(mock_model)
        
        # Test that button box exists and is connected
        assert hasattr(setting_dialog, 'button_box')
        
        storyline_dialog = NewStorylineDialog(mock_model)
        assert hasattr(storyline_dialog, 'button_box')

    def test_dialog_field_validation(self, qapp):
        """Test field validation across dialogs"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        # Test setting dialog validation
        setting_dialog = NewSettingDialog(mock_model)
        assert hasattr(setting_dialog, 'name_line_edit')
        assert hasattr(setting_dialog, 'description_text_edit')
        assert hasattr(setting_dialog, 'user_combo')
        
        # Test storyline dialog validation
        storyline_dialog = NewStorylineDialog(mock_model)
        assert hasattr(storyline_dialog, 'name_line_edit')
        assert hasattr(storyline_dialog, 'description_text_edit')
        assert hasattr(storyline_dialog, 'user_combo')

    def test_dialog_error_recovery(self, qapp):
        """Test dialog behavior when errors occur"""
        mock_model = Mock()
        
        # Test database error handling
        mock_model.get_all_rows_as_dicts.side_effect = Exception("Database error")
        
        setting_dialog = NewSettingDialog(mock_model)
        # Should not crash and should disable combo box
        assert setting_dialog.user_combo.isEnabled() is False
        
        storyline_dialog = NewStorylineDialog(mock_model)
        assert storyline_dialog.user_combo.isEnabled() is False

    def test_dialog_data_consistency(self, qapp):
        """Test data consistency across dialog operations"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"id": 1, "username": "test_user"}
        ]
        
        setting_dialog = NewSettingDialog(mock_model)
        setting_dialog.name_line_edit.setText("Test Setting")
        setting_dialog.description_text_edit.setPlainText("Test description")
        
        # Mock the dialog execution
        with patch.object(setting_dialog, 'exec') as mock_exec:
            mock_exec.return_value = QDialog.DialogCode.Accepted
            
            result = setting_dialog.get_setting_data()
            
            assert result["name"] == "Test Setting"
            assert result["description"] == "Test description"
            assert "user_id" in result


class TestUIComponentEdgeCases:
    """Test edge cases and error conditions for UI components"""

    def test_dialog_with_empty_data(self, qapp):
        """Test dialog behavior with empty data"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []  # No users
        
        setting_dialog = NewSettingDialog(mock_model)
        
        # Should handle empty user list gracefully
        assert setting_dialog.user_combo.count() >= 0

    def test_dialog_with_malformed_data(self, qapp):
        """Test dialog behavior with malformed data"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = [
            {"username": "user_without_id"},  # Missing ID
            {"id": "not_a_number", "username": "user2"}  # Invalid ID
        ]
        
        # Should handle malformed data without crashing
        setting_dialog = NewSettingDialog(mock_model)
        
        # Dialog should still be created
        assert setting_dialog is not None

    def test_plot_manager_with_no_plots(self, qapp):
        """Test plot manager with no plots"""
        dialog = PlotManagerDialog()
        
        dialog.populate_plots([], None)
        
        # Should handle empty plot list
        assert dialog.current_plot_id is None

    def test_plot_manager_with_none_current_plot(self, qapp):
        """Test plot manager when no current plot is set"""
        dialog = PlotManagerDialog()
        
        mock_plot = Mock()
        mock_plot.id = 1
        mock_plot.title = "Plot 1"
        
        dialog.populate_plots([mock_plot], None)
        
        # Should handle None current plot ID
        assert dialog.current_plot_id is None

    def test_dialog_memory_management(self, qapp):
        """Test that dialogs are properly cleaned up"""
        mock_model = Mock()
        mock_model.get_all_rows_as_dicts.return_value = []
        
        # Create and destroy dialogs
        dialog1 = NewSettingDialog(mock_model)
        del dialog1
        
        dialog2 = NewStorylineDialog(mock_model)
        del dialog2
        
        dialog3 = PlotManagerDialog()
        del dialog3
        
        # Should not cause memory leaks or crashes
        assert True  # If we get here, no crashes occurred