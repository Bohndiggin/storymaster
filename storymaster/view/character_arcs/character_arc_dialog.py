"""Character Arc Add/Edit Dialog"""

from PyQt6.QtWidgets import QDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt
from .character_arc_dialog_ui import Ui_CharacterArcDialog
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_list_style,
    get_dialog_style,
    COLORS
)


class CharacterArcDialog(QDialog):
    """Dialog for adding or editing character arcs"""
    
    def __init__(self, model, storyline_id, setting_id, character_arc=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.storyline_id = storyline_id
        self.setting_id = setting_id
        self.character_arc = character_arc  # None for add, LitographyArc object for edit
        
        # Setup UI
        self.ui = Ui_CharacterArcDialog()
        self.ui.setupUi(self)
        
        # Apply theming
        self.setStyleSheet(get_dialog_style())
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Initialize UI components"""
        if self.character_arc:
            # Edit mode
            self.ui.titleLabel.setText("Edit Character Arc")
            self.ui.arcTitleEdit.setText(self.character_arc.title)
            self.ui.descriptionEdit.setPlainText(self.character_arc.description or "")
        else:
            # Add mode
            self.ui.titleLabel.setText("Add Character Arc")
            
        # Apply component theming
        self.ui.titleLabel.setStyleSheet(f"color: {COLORS['text_accent']};")
        self.ui.arcTitleEdit.setStyleSheet(get_input_style())
        self.ui.arcTypeComboBox.setStyleSheet(get_input_style())
        self.ui.charactersListWidget.setStyleSheet(get_list_style())
        self.ui.descriptionEdit.setStyleSheet(get_input_style())
        
        # Style button box
        ok_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok)
        cancel_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Cancel)
        if ok_button:
            ok_button.setStyleSheet(get_button_style('primary'))
        if cancel_button:
            cancel_button.setStyleSheet(get_button_style())
            
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
    def load_data(self):
        """Load arc types and characters"""
        self.load_arc_types()
        self.load_characters()
        
    def load_arc_types(self):
        """Load available arc types into the combo box"""
        try:
            self.ui.arcTypeComboBox.clear()
            arc_types = self.model.get_arc_types(self.setting_id)
            
            for arc_type in arc_types:
                self.ui.arcTypeComboBox.addItem(arc_type.name, arc_type.id)
                
            # Set current selection if editing
            if self.character_arc:
                for i in range(self.ui.arcTypeComboBox.count()):
                    if self.ui.arcTypeComboBox.itemData(i) == self.character_arc.arc_type_id:
                        self.ui.arcTypeComboBox.setCurrentIndex(i)
                        break
                        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc types: {e}")
            
    def load_characters(self):
        """Load available characters into the list widget"""
        try:
            self.ui.charactersListWidget.clear()
            actors = self.model.get_actors_for_setting(self.setting_id)
            
            selected_actor_ids = set()
            if self.character_arc:
                selected_actor_ids = {arc_to_actor.actor_id for arc_to_actor in self.character_arc.actors}
            
            for actor in actors:
                name = f"{actor.first_name or ''} {actor.last_name or ''}".strip()
                if not name:
                    name = f"Actor {actor.id}"
                    
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, actor.id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                
                # Set checked state if this actor is selected
                if actor.id in selected_actor_ids:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
                    
                self.ui.charactersListWidget.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load characters: {e}")
            
    def accept(self):
        """Handle OK button click"""
        title = self.ui.arcTitleEdit.text().strip()
        arc_type_id = self.ui.arcTypeComboBox.currentData()
        description = self.ui.descriptionEdit.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Validation Error", "Character arc title is required.")
            return
            
        if arc_type_id is None:
            QMessageBox.warning(self, "Validation Error", "Please select an arc type.")
            return
            
        # Get selected character IDs
        selected_actor_ids = []
        for i in range(self.ui.charactersListWidget.count()):
            item = self.ui.charactersListWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_actor_ids.append(item.data(Qt.ItemDataRole.UserRole))
                
        try:
            if self.character_arc:
                # Edit existing character arc
                self.model.update_character_arc(
                    self.character_arc.id,
                    title=title,
                    description=description if description else None,
                    arc_type_id=arc_type_id,
                    actor_ids=selected_actor_ids
                )
            else:
                # Create new character arc
                self.model.create_character_arc(
                    title=title,
                    description=description if description else None,
                    arc_type_id=arc_type_id,
                    storyline_id=self.storyline_id,
                    actor_ids=selected_actor_ids
                )
                
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save character arc: {e}")
            
    def get_result(self):
        """Get the dialog result data"""
        selected_actor_ids = []
        for i in range(self.ui.charactersListWidget.count()):
            item = self.ui.charactersListWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_actor_ids.append(item.data(Qt.ItemDataRole.UserRole))
                
        return {
            'title': self.ui.arcTitleEdit.text().strip(),
            'arc_type_id': self.ui.arcTypeComboBox.currentData(),
            'description': self.ui.descriptionEdit.toPlainText().strip(),
            'actor_ids': selected_actor_ids
        }