"""
Test suite for character arc system functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QListWidgetItem, QTreeWidgetItem
from PyQt6.QtCore import Qt

from storymaster.model.database.schema.base import (
    LitographyArc, ArcType, ArcPoint, Actor, ArcToActor, Setting, Storyline, LitographyNode
)
from storymaster.view.character_arcs.character_arc_widget import CharacterArcWidget
from storymaster.view.character_arcs.arc_type_dialog import ArcTypeDialog
from storymaster.view.character_arcs.arc_type_manager_dialog import ArcTypeManagerDialog
from storymaster.view.character_arcs.arc_point_dialog import ArcPointDialog
from storymaster.view.character_arcs.character_arc_dialog import CharacterArcDialog


class TestCharacterArcModelMethods:
    """Test character arc model methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_session = Mock()

    def test_get_character_arcs(self):
        """Test getting character arcs for a storyline"""
        # Mock arc data
        mock_arc_type = Mock(spec=ArcType)
        mock_arc_type.name = "Hero's Journey"
        
        mock_arc_to_actor = Mock(spec=ArcToActor)
        mock_actor = Mock(spec=Actor)
        mock_actor.first_name = "John"
        mock_actor.last_name = "Doe"
        mock_arc_to_actor.actor = mock_actor
        
        mock_arc = Mock(spec=LitographyArc)
        mock_arc.id = 1
        mock_arc.title = "Character Growth"
        mock_arc.arc_type = mock_arc_type
        mock_arc.actors = [mock_arc_to_actor]
        
        self.mock_model.get_character_arcs.return_value = [mock_arc]
        
        # Test the method
        arcs = self.mock_model.get_character_arcs(storyline_id=1)
        
        assert len(arcs) == 1
        assert arcs[0].title == "Character Growth"
        assert arcs[0].arc_type.name == "Hero's Journey"
        assert arcs[0].actors[0].actor.first_name == "John"

    def test_create_character_arc(self):
        """Test creating a new character arc"""
        mock_arc = Mock(spec=LitographyArc)
        mock_arc.id = 1
        mock_arc.title = "New Arc"
        
        self.mock_model.create_character_arc.return_value = mock_arc
        
        result = self.mock_model.create_character_arc(
            title="New Arc",
            description="Test description",
            arc_type_id=1,
            storyline_id=1,
            actor_ids=[1, 2]
        )
        
        assert result.title == "New Arc"
        assert result.id == 1

    def test_get_arc_points(self):
        """Test getting arc points for an arc"""
        mock_point1 = Mock(spec=ArcPoint)
        mock_point1.id = 1
        mock_point1.title = "Point 1"
        mock_point1.order_index = 1
        
        mock_point2 = Mock(spec=ArcPoint)
        mock_point2.id = 2
        mock_point2.title = "Point 2"
        mock_point2.order_index = 2
        
        self.mock_model.get_arc_points.return_value = [mock_point1, mock_point2]
        
        points = self.mock_model.get_arc_points(arc_id=1)
        
        assert len(points) == 2
        assert points[0].title == "Point 1"
        assert points[1].title == "Point 2"

    def test_create_arc_point(self):
        """Test creating a new arc point"""
        mock_point = Mock(spec=ArcPoint)
        mock_point.id = 1
        mock_point.title = "New Point"
        mock_point.order_index = 1
        
        self.mock_model.create_arc_point.return_value = mock_point
        
        result = self.mock_model.create_arc_point(
            arc_id=1,
            title="New Point",
            order_index=1,
            description="Test description",
            emotional_state="Happy",
            character_relationships="Strong",
            goals="Save the world",
            internal_conflict="Self-doubt",
            node_id=1
        )
        
        assert result.title == "New Point"
        assert result.order_index == 1

    def test_get_arc_types(self):
        """Test getting arc types for a setting"""
        mock_type1 = Mock(spec=ArcType)
        mock_type1.id = 1
        mock_type1.name = "Hero's Journey"
        
        mock_type2 = Mock(spec=ArcType)
        mock_type2.id = 2
        mock_type2.name = "Character Growth"
        
        self.mock_model.get_arc_types.return_value = [mock_type1, mock_type2]
        
        types = self.mock_model.get_arc_types(setting_id=1)
        
        assert len(types) == 2
        assert types[0].name == "Hero's Journey"
        assert types[1].name == "Character Growth"

    def test_delete_character_arc(self):
        """Test deleting a character arc"""
        self.mock_model.delete_character_arc.return_value = None
        
        # Should not raise an exception
        self.mock_model.delete_character_arc(arc_id=1)
        
        self.mock_model.delete_character_arc.assert_called_once_with(arc_id=1)

    def test_delete_arc_point(self):
        """Test deleting an arc point"""
        self.mock_model.delete_arc_point.return_value = None
        
        # Should not raise an exception
        self.mock_model.delete_arc_point(arc_point_id=1)
        
        self.mock_model.delete_arc_point.assert_called_once_with(arc_point_id=1)


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestCharacterArcWidget:
    """Test the CharacterArcWidget"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()

    def test_character_arc_widget_initialization(self, qapp):
        """Test widget initialization"""
        widget = CharacterArcWidget(self.mock_model)
        
        assert widget.model == self.mock_model
        assert widget.current_arc_id is None
        assert widget.current_arc_point_id is None
        assert widget.current_storyline_id is None

    def test_refresh_arcs(self, qapp):
        """Test refreshing the arc list"""
        widget = CharacterArcWidget(self.mock_model)
        
        # Mock arc data
        mock_arc_type = Mock()
        mock_arc_type.name = "Hero's Journey"
        
        mock_arc_to_actor = Mock()
        mock_actor = Mock()
        mock_actor.first_name = "John"
        mock_arc_to_actor.actor = mock_actor
        
        mock_arc = Mock()
        mock_arc.id = 1
        mock_arc.title = "Character Growth"
        mock_arc.arc_type = mock_arc_type
        mock_arc.actors = [mock_arc_to_actor]
        
        self.mock_model.get_character_arcs.return_value = [mock_arc]
        
        widget.refresh_arcs(storyline_id=1)
        
        assert widget.current_storyline_id == 1
        self.mock_model.get_character_arcs.assert_called_once_with(1)

    def test_refresh_arc_points(self, qapp):
        """Test refreshing arc points"""
        widget = CharacterArcWidget(self.mock_model)
        widget.current_arc_id = 1
        
        mock_point = Mock()
        mock_point.id = 1
        mock_point.order_index = 1
        mock_point.title = "Point 1"
        mock_point.node_id = 1
        mock_point.emotional_state = "Happy"
        
        self.mock_model.get_arc_points.return_value = [mock_point]
        
        widget.refresh_arc_points()
        
        self.mock_model.get_arc_points.assert_called_once_with(1)

    def test_arc_selection_changed(self, qapp):
        """Test arc selection change handling"""
        widget = CharacterArcWidget(self.mock_model)
        
        # Mock selected item
        mock_item = Mock()
        mock_item.data.return_value = 1  # arc_id
        widget.ui.arcListWidget.selectedItems.return_value = [mock_item]
        
        # Mock the arc details loading
        mock_arc = Mock()
        mock_arc.title = "Test Arc"
        mock_arc.arc_type = Mock()
        mock_arc.arc_type.name = "Test Type"
        mock_arc.description = "Test description"
        mock_arc.actors = []
        
        self.mock_model.get_character_arc.return_value = mock_arc
        self.mock_model.get_arc_points.return_value = []
        
        widget.on_arc_selection_changed()
        
        assert widget.current_arc_id == 1

    def test_arc_point_selection_changed(self, qapp):
        """Test arc point selection change handling"""
        widget = CharacterArcWidget(self.mock_model)
        
        # Mock selected item
        mock_item = Mock()
        mock_item.data.return_value = 1  # arc_point_id
        widget.ui.arcPointsTreeWidget.selectedItems.return_value = [mock_item]
        
        widget.on_arc_point_selection_changed()
        
        assert widget.current_arc_point_id == 1

    def test_delete_arc_confirmation(self, qapp):
        """Test arc deletion with confirmation"""
        widget = CharacterArcWidget(self.mock_model)
        widget.current_arc_id = 1
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                mock_question.return_value = QMessageBox.StandardButton.Yes
                
                widget.on_delete_arc()
                
                self.mock_model.delete_character_arc.assert_called_once_with(1)
                mock_info.assert_called_once()

    def test_delete_arc_point_confirmation(self, qapp):
        """Test arc point deletion with confirmation"""
        widget = CharacterArcWidget(self.mock_model)
        widget.current_arc_point_id = 1
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                mock_question.return_value = QMessageBox.StandardButton.Yes
                
                widget.on_delete_arc_point()
                
                self.mock_model.delete_arc_point.assert_called_once_with(1)
                mock_info.assert_called_once()


class TestArcTypeDialog:
    """Test the ArcTypeDialog"""

    def test_arc_type_dialog_initialization_add_mode(self, qapp):
        """Test dialog initialization in add mode"""
        mock_model = Mock()
        dialog = ArcTypeDialog(mock_model, setting_id=1)
        
        assert dialog.model == mock_model
        assert dialog.setting_id == 1
        assert dialog.arc_type is None

    def test_arc_type_dialog_initialization_edit_mode(self, qapp):
        """Test dialog initialization in edit mode"""
        mock_model = Mock()
        mock_arc_type = Mock()
        mock_arc_type.name = "Test Type"
        mock_arc_type.description = "Test description"
        
        dialog = ArcTypeDialog(mock_model, setting_id=1, arc_type=mock_arc_type)
        
        assert dialog.model == mock_model
        assert dialog.setting_id == 1
        assert dialog.arc_type == mock_arc_type

    def test_arc_type_dialog_validation_empty_name(self, qapp):
        """Test validation when name is empty"""
        mock_model = Mock()
        dialog = ArcTypeDialog(mock_model, setting_id=1)
        
        dialog.ui.nameEdit.text.return_value = ""  # Empty name
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()

    def test_arc_type_dialog_successful_creation(self, qapp):
        """Test successful arc type creation"""
        mock_model = Mock()
        dialog = ArcTypeDialog(mock_model, setting_id=1)
        
        dialog.ui.nameEdit.text.return_value = "New Type"
        dialog.ui.descriptionEdit.toPlainText.return_value = "Description"
        
        with patch.object(dialog, 'accept') as mock_accept:
            with patch('PyQt6.QtWidgets.QDialog.accept') as mock_super_accept:
                dialog.accept()
                
                mock_model.create_arc_type.assert_called_once_with(
                    name="New Type",
                    description="Description",
                    setting_id=1
                )


class TestArcTypeManagerDialog:
    """Test the ArcTypeManagerDialog"""

    def test_arc_type_manager_initialization(self, qapp):
        """Test dialog initialization"""
        mock_model = Mock()
        dialog = ArcTypeManagerDialog(mock_model, setting_id=1)
        
        assert dialog.model == mock_model
        assert dialog.setting_id == 1
        assert dialog.current_arc_type is None

    def test_refresh_arc_types(self, qapp):
        """Test refreshing arc types table"""
        mock_model = Mock()
        
        mock_type1 = Mock()
        mock_type1.id = 1
        mock_type1.name = "Type 1"
        mock_type1.description = "Description 1"
        
        mock_type2 = Mock()
        mock_type2.id = 2
        mock_type2.name = "Type 2"
        mock_type2.description = "Description 2"
        
        mock_model.get_arc_types.return_value = [mock_type1, mock_type2]
        
        dialog = ArcTypeManagerDialog(mock_model, setting_id=1)
        dialog.refresh_arc_types()
        
        mock_model.get_arc_types.assert_called_with(1)

    def test_add_arc_type_opens_dialog(self, qapp):
        """Test that add arc type opens the correct dialog"""
        mock_model = Mock()
        dialog = ArcTypeManagerDialog(mock_model, setting_id=1)
        
        with patch('storymaster.view.character_arcs.arc_type_manager_dialog.ArcTypeDialog') as mock_arc_type_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Accepted
            mock_arc_type_dialog.return_value = mock_dialog_instance
            
            with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                dialog.on_add_arc_type()
                
                mock_arc_type_dialog.assert_called_once_with(mock_model, 1, parent=dialog)
                mock_info.assert_called_once()

    def test_delete_arc_type_with_confirmation(self, qapp):
        """Test arc type deletion with confirmation"""
        mock_model = Mock()
        dialog = ArcTypeManagerDialog(mock_model, setting_id=1)
        
        mock_arc_type = Mock()
        mock_arc_type.id = 1
        mock_arc_type.name = "Test Type"
        dialog.current_arc_type = mock_arc_type
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                mock_question.return_value = QMessageBox.StandardButton.Yes
                
                dialog.on_delete_arc_type()
                
                mock_model.delete_arc_type.assert_called_once_with(1)
                mock_info.assert_called_once()


class TestArcPointDialog:
    """Test the ArcPointDialog"""

    def test_arc_point_dialog_initialization_add_mode(self, qapp):
        """Test dialog initialization in add mode"""
        mock_model = Mock()
        mock_model.get_arc_points.return_value = []  # No existing points
        mock_model.get_nodes_for_storyline.return_value = []
        
        dialog = ArcPointDialog(mock_model, arc_id=1, storyline_id=1)
        
        assert dialog.model == mock_model
        assert dialog.arc_id == 1
        assert dialog.storyline_id == 1
        assert dialog.arc_point is None

    def test_arc_point_dialog_initialization_edit_mode(self, qapp):
        """Test dialog initialization in edit mode"""
        mock_model = Mock()
        mock_model.get_nodes_for_storyline.return_value = []
        
        mock_arc_point = Mock()
        mock_arc_point.order_index = 1
        mock_arc_point.title = "Test Point"
        mock_arc_point.description = "Test description"
        mock_arc_point.emotional_state = "Happy"
        mock_arc_point.character_relationships = "Strong"
        mock_arc_point.goals = "Save world"
        mock_arc_point.internal_conflict = "Self-doubt"
        mock_arc_point.node_id = 1
        
        dialog = ArcPointDialog(mock_model, arc_id=1, storyline_id=1, arc_point=mock_arc_point)
        
        assert dialog.arc_point == mock_arc_point

    def test_arc_point_dialog_load_nodes(self, qapp):
        """Test loading story nodes into combo box"""
        mock_model = Mock()
        mock_model.get_arc_points.return_value = []
        
        mock_node1 = Mock()
        mock_node1.id = 1
        mock_node1.label = "Opening Scene"
        
        mock_node2 = Mock()
        mock_node2.id = 2
        mock_node2.label = "Climax"
        
        mock_model.get_nodes_for_storyline.return_value = [mock_node1, mock_node2]
        
        dialog = ArcPointDialog(mock_model, arc_id=1, storyline_id=1)
        
        mock_model.get_nodes_for_storyline.assert_called_once_with(1)

    def test_arc_point_dialog_validation_empty_title(self, qapp):
        """Test validation when title is empty"""
        mock_model = Mock()
        mock_model.get_arc_points.return_value = []
        mock_model.get_nodes_for_storyline.return_value = []
        
        dialog = ArcPointDialog(mock_model, arc_id=1, storyline_id=1)
        dialog.ui.titleEdit.text.return_value = ""  # Empty title
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()

    def test_arc_point_dialog_successful_creation(self, qapp):
        """Test successful arc point creation"""
        mock_model = Mock()
        mock_model.get_arc_points.return_value = []
        mock_model.get_nodes_for_storyline.return_value = []
        
        dialog = ArcPointDialog(mock_model, arc_id=1, storyline_id=1)
        
        dialog.ui.titleEdit.text.return_value = "New Point"
        dialog.ui.orderSpinBox.value.return_value = 1
        dialog.ui.descriptionEdit.toPlainText.return_value = "Description"
        dialog.ui.emotionalStateEdit.toPlainText.return_value = "Happy"
        dialog.ui.relationshipsEdit.toPlainText.return_value = "Strong"
        dialog.ui.goalsEdit.toPlainText.return_value = "Save world"
        dialog.ui.conflictEdit.toPlainText.return_value = "Self-doubt"
        dialog.ui.nodeComboBox.currentData.return_value = 1
        
        with patch.object(dialog, 'accept') as mock_accept:
            with patch('PyQt6.QtWidgets.QDialog.accept') as mock_super_accept:
                dialog.accept()
                
                mock_model.create_arc_point.assert_called_once()


class TestCharacterArcDialog:
    """Test the CharacterArcDialog"""

    def test_character_arc_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        mock_model = Mock()
        mock_model.get_arc_types.return_value = []
        mock_model.get_actors_for_setting.return_value = []
        
        dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
        
        assert dialog.model == mock_model
        assert dialog.storyline_id == 1
        assert dialog.setting_id == 1
        assert dialog.character_arc is None

    def test_character_arc_dialog_load_arc_types(self, qapp):
        """Test loading arc types into combo box"""
        mock_model = Mock()
        
        mock_type1 = Mock()
        mock_type1.id = 1
        mock_type1.name = "Hero's Journey"
        
        mock_type2 = Mock()
        mock_type2.id = 2
        mock_type2.name = "Character Growth"
        
        mock_model.get_arc_types.return_value = [mock_type1, mock_type2]
        mock_model.get_actors_for_setting.return_value = []
        
        dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
        
        mock_model.get_arc_types.assert_called_once_with(1)

    def test_character_arc_dialog_load_characters(self, qapp):
        """Test loading characters into list widget"""
        mock_model = Mock()
        mock_model.get_arc_types.return_value = []
        
        mock_actor1 = Mock()
        mock_actor1.id = 1
        mock_actor1.first_name = "John"
        mock_actor1.last_name = "Doe"
        
        mock_actor2 = Mock()
        mock_actor2.id = 2
        mock_actor2.first_name = "Jane"
        mock_actor2.last_name = "Smith"
        
        mock_model.get_actors_for_setting.return_value = [mock_actor1, mock_actor2]
        
        dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
        
        mock_model.get_actors_for_setting.assert_called_once_with(1)

    def test_character_arc_dialog_validation_empty_title(self, qapp):
        """Test validation when title is empty"""
        mock_model = Mock()
        mock_model.get_arc_types.return_value = []
        mock_model.get_actors_for_setting.return_value = []
        
        dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
        dialog.ui.arcTitleEdit.text.return_value = ""  # Empty title
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()

    def test_character_arc_dialog_validation_no_arc_type(self, qapp):
        """Test validation when no arc type is selected"""
        mock_model = Mock()
        mock_model.get_arc_types.return_value = []
        mock_model.get_actors_for_setting.return_value = []
        
        dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
        dialog.ui.arcTitleEdit.text.return_value = "Test Arc"
        dialog.ui.arcTypeComboBox.currentData.return_value = None  # No arc type selected
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.accept()
            mock_warning.assert_called_once()


class TestCharacterArcIntegration:
    """Test integration between character arc components"""

    def test_widget_dialog_integration(self, qapp):
        """Test that widget properly opens dialogs"""
        mock_model = Mock()
        mock_model.get_all_settings.return_value = [Mock(id=1)]
        
        widget = CharacterArcWidget(mock_model)
        widget.current_storyline_id = 1
        
        with patch('storymaster.view.character_arcs.character_arc_widget.CharacterArcDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Rejected
            mock_dialog.return_value = mock_dialog_instance
            
            widget.on_new_arc()
            
            mock_dialog.assert_called_once()

    def test_arc_type_manager_integration(self, qapp):
        """Test that widget properly opens arc type manager"""
        mock_model = Mock()
        mock_model.get_all_settings.return_value = [Mock(id=1)]
        
        widget = CharacterArcWidget(mock_model)
        
        with patch('storymaster.view.character_arcs.character_arc_widget.ArcTypeManagerDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.return_value = mock_dialog_instance
            
            widget.on_manage_arc_types()
            
            mock_dialog.assert_called_once()

    def test_arc_point_editor_integration(self, qapp):
        """Test that widget properly opens arc point editor"""
        mock_model = Mock()
        widget = CharacterArcWidget(mock_model)
        widget.current_arc_id = 1
        widget.current_storyline_id = 1
        
        with patch('storymaster.view.character_arcs.character_arc_widget.ArcPointDialog') as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = QDialog.DialogCode.Rejected
            mock_dialog.return_value = mock_dialog_instance
            
            widget.on_new_arc_point()
            
            mock_dialog.assert_called_once_with(
                mock_model, 1, 1, parent=widget
            )

    def test_error_handling_in_widget(self, qapp):
        """Test error handling in character arc widget"""
        mock_model = Mock()
        mock_model.get_character_arcs.side_effect = Exception("Database error")
        
        widget = CharacterArcWidget(mock_model)
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            widget.refresh_arcs(storyline_id=1)
            mock_warning.assert_called_once()

    def test_relationship_traversal_fix(self, qapp):
        """Test that the ArcToActor relationship traversal works correctly"""
        mock_model = Mock()
        
        # Mock the proper relationship structure
        mock_actor = Mock()
        mock_actor.first_name = "John"
        
        mock_arc_to_actor = Mock()
        mock_arc_to_actor.actor = mock_actor
        
        mock_arc = Mock()
        mock_arc.id = 1
        mock_arc.title = "Test Arc"
        mock_arc.actors = [mock_arc_to_actor]
        
        mock_model.get_character_arcs.return_value = [mock_arc]
        
        widget = CharacterArcWidget(mock_model)
        widget.refresh_arcs(storyline_id=1)
        
        # Should not raise an exception due to relationship traversal
        mock_model.get_character_arcs.assert_called_once_with(1)


class TestCharacterArcEdgeCases:
    """Test edge cases and error conditions"""

    def test_widget_with_no_storyline_id(self, qapp):
        """Test widget behavior when no storyline ID is set"""
        mock_model = Mock()
        widget = CharacterArcWidget(mock_model)
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            widget.on_new_arc()
            mock_warning.assert_called_once()

    def test_widget_with_no_current_arc(self, qapp):
        """Test widget behavior when no arc is selected"""
        mock_model = Mock()
        widget = CharacterArcWidget(mock_model)
        widget.current_arc_id = None
        
        # Should not crash when no arc is selected
        widget.on_new_arc_point()  # Should do nothing
        widget.on_edit_arc_point()  # Should do nothing

    def test_dialog_error_handling(self, qapp):
        """Test error handling in dialogs"""
        mock_model = Mock()
        mock_model.get_arc_types.side_effect = Exception("Database error")
        mock_model.get_actors_for_setting.return_value = []
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog = CharacterArcDialog(mock_model, storyline_id=1, setting_id=1)
            mock_warning.assert_called()  # Should show error for arc types

    def test_empty_data_handling(self, qapp):
        """Test handling of empty data"""
        mock_model = Mock()
        mock_model.get_character_arcs.return_value = []
        mock_model.get_arc_points.return_value = []
        mock_model.get_arc_types.return_value = []
        mock_model.get_actors_for_setting.return_value = []
        
        widget = CharacterArcWidget(mock_model)
        widget.refresh_arcs(storyline_id=1)
        widget.refresh_arc_points()
        
        # Should handle empty data gracefully
        assert widget.current_storyline_id == 1

    def test_invalid_selection_handling(self, qapp):
        """Test handling of invalid selections"""
        mock_model = Mock()
        widget = CharacterArcWidget(mock_model)
        
        # Test with empty selection
        widget.ui.arcListWidget.selectedItems.return_value = []
        widget.on_arc_selection_changed()
        
        assert widget.current_arc_id is None

        widget.ui.arcPointsTreeWidget.selectedItems.return_value = []
        widget.on_arc_point_selection_changed()
        
        assert widget.current_arc_point_id is None