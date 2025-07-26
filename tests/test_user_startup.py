"""
Test suite for user startup and guided setup functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from storymaster.controller.common.user_startup import (
    ensure_user_exists,
    create_first_user,
    get_startup_user_id
)
from storymaster.model.common.common_model import BaseModel
from storymaster.model.database.schema.base import User, Setting, Storyline, LitographyPlot


class TestEnsureUserExists:
    """Test the ensure_user_exists function"""

    def test_ensure_user_exists_with_existing_users(self):
        """Test ensure_user_exists when users already exist"""
        # Mock model with existing users
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "existing_user"
        mock_model.get_all_users.return_value = [mock_user]
        
        result = ensure_user_exists(mock_model)
        
        assert result == 1
        mock_model.get_all_users.assert_called_once()

    def test_ensure_user_exists_no_users_successful_creation(self):
        """Test ensure_user_exists when no users exist and creation succeeds"""
        # Mock model with no users initially, then one user after creation
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "new_user"
        
        # First call returns empty list, second call returns new user
        mock_model.get_all_users.side_effect = [[], [mock_user]]
        
        with patch('storymaster.controller.common.user_startup.create_first_user') as mock_create:
            mock_create.return_value = True
            
            result = ensure_user_exists(mock_model)
            
            assert result == 1
            assert mock_model.get_all_users.call_count == 2
            mock_create.assert_called_once_with(mock_model)

    def test_ensure_user_exists_no_users_failed_creation(self):
        """Test ensure_user_exists when no users exist and creation fails"""
        mock_model = Mock(spec=BaseModel)
        mock_model.get_all_users.return_value = []
        
        with patch('storymaster.controller.common.user_startup.create_first_user') as mock_create:
            mock_create.return_value = False
            
            with patch('PyQt6.QtWidgets.QApplication.quit') as mock_quit:
                with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                    result = ensure_user_exists(mock_model)
                    
                    assert result == 1  # Returns default even on failure
                    mock_create.assert_called_once_with(mock_model)
                    mock_critical.assert_called_once()
                    mock_quit.assert_called_once()

    def test_ensure_user_exists_database_error(self):
        """Test ensure_user_exists when database error occurs"""
        mock_model = Mock(spec=BaseModel)
        mock_model.get_all_users.side_effect = Exception("Database error")
        
        with patch('PyQt6.QtWidgets.QApplication.quit') as mock_quit:
            with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                result = ensure_user_exists(mock_model)
                
                assert result == 1  # Returns default on error
                mock_critical.assert_called_once()
                mock_quit.assert_called_once()


class TestCreateFirstUser:
    """Test the create_first_user function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock(spec=BaseModel)
        self.mock_user = Mock(spec=User)
        self.mock_user.id = 1
        self.mock_user.username = "test_user"

    def test_create_first_user_complete_success(self):
        """Test successful creation of user, setting, storyline, and plot"""
        # Mock successful user creation
        self.mock_model.create_user.return_value = self.mock_user
        
        # Mock successful entity creation
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        
        mock_storyline = Mock(spec=Storyline)
        mock_storyline.id = 1
        mock_storyline.name = "My First Story"
        
        self.mock_model.get_all_settings.return_value = [mock_setting]
        self.mock_model.get_all_storylines.return_value = [mock_storyline]
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                    with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                        # Configure dialog mocks
                        mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                        mock_setting_dialog.return_value.get_setting_data.return_value = {
                            "name": "My First World", 
                            "description": "Test description",
                            "user_id": 1
                        }
                        mock_storyline_dialog.return_value.get_storyline_data.return_value = {
                            "name": "My First Story",
                            "description": "Test description", 
                            "user_id": 1
                        }
                        
                        result = create_first_user(self.mock_model)
                        
                        assert result is True
                        self.mock_model.create_user.assert_called_once_with("test_user")
                        self.mock_model.add_row.assert_called()  # Should be called multiple times
                        assert mock_info.call_count >= 3  # Multiple success messages

    def test_create_first_user_user_creation_failure(self):
        """Test failure during user creation"""
        self.mock_model.create_user.side_effect = Exception("User creation failed")
        
        with patch('storymaster.view.common.new_user_dialog.NewUserDialog') as mock_dialog:
            with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                mock_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                
                result = create_first_user(self.mock_model)
                
                assert result is False
                mock_critical.assert_called_once()

    def test_create_first_user_user_cancellation(self):
        """Test when user cancels the user creation dialog"""
        with patch('storymaster.view.common.new_user_dialog.NewUserDialog') as mock_dialog:
            mock_dialog.return_value.get_user_data.return_value = None  # User cancelled
            
            result = create_first_user(self.mock_model)
            
            assert result is False

    def test_create_first_user_setting_cancellation(self):
        """Test when user cancels setting creation but user was created"""
        self.mock_model.create_user.return_value = self.mock_user
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                    mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                    mock_setting_dialog.return_value.get_setting_data.return_value = None  # User cancelled
                    
                    result = create_first_user(self.mock_model)
                    
                    assert result is True  # User was still created
                    self.mock_model.create_user.assert_called_once()
                    mock_info.assert_called()  # Should show incomplete setup message

    def test_create_first_user_storyline_cancellation(self):
        """Test when user cancels storyline creation but user and setting were created"""
        self.mock_model.create_user.return_value = self.mock_user
        
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        self.mock_model.get_all_settings.return_value = [mock_setting]
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                    with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                        mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                        mock_setting_dialog.return_value.get_setting_data.return_value = {
                            "name": "My First World", "description": "", "user_id": 1
                        }
                        mock_storyline_dialog.return_value.get_storyline_data.return_value = None  # Cancelled
                        
                        result = create_first_user(self.mock_model)
                        
                        assert result is True  # User and setting were created
                        mock_info.assert_called()  # Should show incomplete setup message

    def test_create_first_user_setting_creation_error(self):
        """Test error during setting creation"""
        self.mock_model.create_user.return_value = self.mock_user
        self.mock_model.add_row.side_effect = Exception("Setting creation failed")
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                    mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                    mock_setting_dialog.return_value.get_setting_data.return_value = {
                        "name": "My First World", "description": "", "user_id": 1
                    }
                    
                    result = create_first_user(self.mock_model)
                    
                    assert result is True  # User was still created
                    mock_critical.assert_called_once()

    def test_create_first_user_plot_creation_error(self):
        """Test error during plot creation (should still be considered success)"""
        self.mock_model.create_user.return_value = self.mock_user
        
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        
        mock_storyline = Mock(spec=Storyline)
        mock_storyline.id = 1
        mock_storyline.name = "My First Story"
        
        self.mock_model.get_all_settings.return_value = [mock_setting]
        self.mock_model.get_all_storylines.return_value = [mock_storyline]
        
        # Mock add_row to succeed for setting and storyline, fail for plot
        def add_row_side_effect(table_name, data):
            if table_name == "litography_plot":
                raise Exception("Plot creation failed")
            return Mock()
        
        self.mock_model.add_row.side_effect = add_row_side_effect
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                    with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                        mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                        mock_setting_dialog.return_value.get_setting_data.return_value = {
                            "name": "My First World", "description": "", "user_id": 1
                        }
                        mock_storyline_dialog.return_value.get_storyline_data.return_value = {
                            "name": "My First Story", "description": "", "user_id": 1
                        }
                        
                        result = create_first_user(self.mock_model)
                        
                        assert result is True  # Still successful
                        mock_info.assert_called()  # Should show "almost complete" message


class TestGuidedSetupIntegration:
    """Test integration aspects of guided setup"""

    def test_dialog_pre_configuration(self):
        """Test that dialogs are properly pre-configured during guided setup"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.BaseModel') as mock_base_model:
                    with patch('PyQt6.QtWidgets.QMessageBox.information'):
                        mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                        mock_setting_dialog.return_value.get_setting_data.return_value = None  # Cancel to avoid full flow
                        
                        mock_setting_instance = Mock()
                        mock_setting_dialog.return_value = mock_setting_instance
                        mock_base_model.return_value = mock_model
                        
                        create_first_user(mock_model)
                        
                        # Verify dialog was configured properly
                        mock_setting_instance.user_combo.setCurrentText.assert_called_with("test_user")
                        mock_setting_instance.user_combo.setEnabled.assert_called_with(False)
                        mock_setting_instance.name_line_edit.setText.assert_called_with("My First World")

    def test_entity_retrieval_after_creation(self):
        """Test that entities are properly retrieved after creation"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        
        # Mock setting retrieval
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        mock_model.get_all_settings.return_value = [mock_setting]
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('PyQt6.QtWidgets.QMessageBox.information'):
                    mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                    mock_setting_dialog.return_value.get_setting_data.return_value = {
                        "name": "My First World", "description": "", "user_id": 1
                    }
                    # Cancel storyline to avoid full flow
                    with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                        mock_storyline_dialog.return_value.get_storyline_data.return_value = None
                        
                        result = create_first_user(mock_model)
                        
                        assert result is True
                        mock_model.get_all_settings.assert_called_once()

    def test_relationship_creation(self):
        """Test that storyline-to-setting relationships are created"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        
        mock_storyline = Mock(spec=Storyline)
        mock_storyline.id = 1
        mock_storyline.name = "My First Story"
        
        mock_model.get_all_settings.return_value = [mock_setting]
        mock_model.get_all_storylines.return_value = [mock_storyline]
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                    with patch('PyQt6.QtWidgets.QMessageBox.information'):
                        mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                        mock_setting_dialog.return_value.get_setting_data.return_value = {
                            "name": "My First World", "description": "", "user_id": 1
                        }
                        mock_storyline_dialog.return_value.get_storyline_data.return_value = {
                            "name": "My First Story", "description": "", "user_id": 1
                        }
                        
                        create_first_user(mock_model)
                        
                        # Verify relationship creation was attempted
                        relationship_calls = [
                            call for call in mock_model.add_row.call_args_list
                            if call[0][0] == "storyline_to_setting"
                        ]
                        assert len(relationship_calls) == 1
                        relationship_data = relationship_calls[0][0][1]
                        assert relationship_data["storyline_id"] == 1
                        assert relationship_data["setting_id"] == 1


class TestGetStartupUserId:
    """Test the get_startup_user_id function"""

    def test_get_startup_user_id_delegates_correctly(self):
        """Test that get_startup_user_id properly delegates to ensure_user_exists"""
        with patch('storymaster.controller.common.user_startup.ensure_user_exists') as mock_ensure:
            mock_ensure.return_value = 42
            
            result = get_startup_user_id()
            
            assert result == 42
            mock_ensure.assert_called_once()


class TestGuidedSetupEdgeCases:
    """Test edge cases and error conditions in guided setup"""

    def test_setting_retrieval_failure(self):
        """Test handling when setting retrieval fails after creation"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        mock_model.get_all_settings.return_value = []  # Setting not found
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                mock_setting_dialog.return_value.get_setting_data.return_value = {
                    "name": "My First World", "description": "", "user_id": 1
                }
                
                with pytest.raises(ValueError, match="Failed to retrieve newly created setting"):
                    create_first_user(mock_model)

    def test_storyline_retrieval_failure(self):
        """Test handling when storyline retrieval fails after creation"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        
        mock_setting = Mock(spec=Setting)
        mock_setting.id = 1
        mock_setting.name = "My First World"
        mock_model.get_all_settings.return_value = [mock_setting]
        mock_model.get_all_storylines.return_value = []  # Storyline not found
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                with patch('storymaster.controller.common.user_startup.NewStorylineDialog') as mock_storyline_dialog:
                    mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                    mock_setting_dialog.return_value.get_setting_data.return_value = {
                        "name": "My First World", "description": "", "user_id": 1
                    }
                    mock_storyline_dialog.return_value.get_storyline_data.return_value = {
                        "name": "My First Story", "description": "", "user_id": 1
                    }
                    
                    with pytest.raises(ValueError, match="Failed to retrieve newly created storyline"):
                        create_first_user(mock_model)

    def test_base_model_creation_with_new_user_id(self):
        """Test that BaseModel is created with the new user ID"""
        mock_model = Mock(spec=BaseModel)
        mock_user = Mock(spec=User)
        mock_user.id = 42  # Specific ID to test
        mock_user.username = "test_user"
        mock_model.create_user.return_value = mock_user
        
        with patch('storymaster.controller.common.user_startup.NewUserDialog') as mock_user_dialog:
            with patch('storymaster.controller.common.user_startup.BaseModel') as mock_base_model_class:
                mock_user_dialog.return_value.get_user_data.return_value = {"username": "test_user"}
                
                # Mock the second model creation (for the user_model)
                mock_user_model = Mock(spec=BaseModel)
                mock_base_model_class.return_value = mock_user_model
                
                with patch('storymaster.controller.common.user_startup.NewSettingDialog') as mock_setting_dialog:
                    mock_setting_dialog.return_value.get_setting_data.return_value = None  # Cancel early
                    
                    create_first_user(mock_model)
                    
                    # Verify BaseModel was created with the correct user ID
                    mock_base_model_class.assert_called_once_with(42)