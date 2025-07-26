"""Character Arc Add/Edit Dialog"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt


class CharacterArcDialog(QDialog):
    """Dialog for adding or editing character arcs"""
    
    def __init__(self, model, storyline_id, setting_id, character_arc=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.storyline_id = storyline_id
        self.setting_id = setting_id
        self.character_arc = character_arc  # None for add, LitographyArc object for edit
        
        # Load UI
        ui_path = os.path.join(os.path.dirname(__file__), "character_arc_dialog.ui")
        uic.loadUi(ui_path, self)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Initialize UI components"""
        if self.character_arc:
            # Edit mode
            self.titleLabel.setText("Edit Character Arc")
            self.arcTitleEdit.setText(self.character_arc.title)
            self.descriptionEdit.setPlainText(self.character_arc.description or "")
        else:
            # Add mode
            self.titleLabel.setText("Add Character Arc")
            
        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
    def load_data(self):
        """Load arc types and characters"""
        self.load_arc_types()
        self.load_characters()
        
    def load_arc_types(self):
        """Load available arc types into the combo box"""
        try:
            self.arcTypeComboBox.clear()
            arc_types = self.model.get_arc_types(self.setting_id)
            
            for arc_type in arc_types:
                self.arcTypeComboBox.addItem(arc_type.name, arc_type.id)
                
            # Set current selection if editing
            if self.character_arc:
                for i in range(self.arcTypeComboBox.count()):
                    if self.arcTypeComboBox.itemData(i) == self.character_arc.arc_type_id:
                        self.arcTypeComboBox.setCurrentIndex(i)
                        break
                        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc types: {e}")
            
    def load_characters(self):
        """Load available characters into the list widget"""
        try:
            self.charactersListWidget.clear()
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
                    
                self.charactersListWidget.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load characters: {e}")
            
    def accept(self):
        """Handle OK button click"""
        title = self.arcTitleEdit.text().strip()
        arc_type_id = self.arcTypeComboBox.currentData()
        description = self.descriptionEdit.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Validation Error", "Character arc title is required.")
            return
            
        if arc_type_id is None:
            QMessageBox.warning(self, "Validation Error", "Please select an arc type.")
            return
            
        # Get selected character IDs
        selected_actor_ids = []
        for i in range(self.charactersListWidget.count()):
            item = self.charactersListWidget.item(i)
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
        for i in range(self.charactersListWidget.count()):
            item = self.charactersListWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_actor_ids.append(item.data(Qt.ItemDataRole.UserRole))
                
        return {
            'title': self.arcTitleEdit.text().strip(),
            'arc_type_id': self.arcTypeComboBox.currentData(),
            'description': self.descriptionEdit.toPlainText().strip(),
            'actor_ids': selected_actor_ids
        }