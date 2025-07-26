"""
Dialog for managing notes linked to a litography node.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QSplitter, QTextEdit, QVBoxLayout)

from storymaster.model.database.schema.base import NoteType


class NodeNotesDialog(QDialog):
    """
    Dialog for viewing and managing notes linked to a specific node.
    """

    def __init__(self, node_data, controller, parent=None):
        super().__init__(parent)
        self.node_data = node_data
        self.controller = controller
        self.current_note = None

        self.setWindowTitle(
            f"Notes for Node (Type: {node_data.node_type.name.title()})"
        )
        self.setMinimumSize(600, 400)

        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout()

        # Node info section
        node_info_group = QGroupBox("Node Information")
        node_info_layout = QFormLayout()
        node_info_layout.addRow(
            "Node Type:", QLabel(self.node_data.node_type.name.title())
        )
        node_info_layout.addRow(
            "Node Height:", QLabel(f"{self.node_data.node_height:.2f}")
        )
        node_info_group.setLayout(node_info_layout)
        main_layout.addWidget(node_info_group)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Notes list
        left_widget = QGroupBox("Notes")
        left_layout = QVBoxLayout()

        self.notes_list = QListWidget()
        self.notes_list.itemSelectionChanged.connect(self.on_note_selected)
        left_layout.addWidget(self.notes_list)

        # List control buttons
        list_buttons_layout = QHBoxLayout()
        self.add_note_btn = QPushButton("Add Note")
        self.delete_note_btn = QPushButton("Delete Note")
        self.delete_note_btn.setEnabled(False)

        self.add_note_btn.clicked.connect(self.add_note)
        self.delete_note_btn.clicked.connect(self.delete_note)

        list_buttons_layout.addWidget(self.add_note_btn)
        list_buttons_layout.addWidget(self.delete_note_btn)
        left_layout.addLayout(list_buttons_layout)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right side - Note editor
        right_widget = QGroupBox("Note Editor")
        right_layout = QFormLayout()

        self.note_type_combo = QComboBox()
        for note_type in NoteType:
            self.note_type_combo.addItem(note_type.name.title(), note_type)

        self.note_title_edit = QLineEdit()
        self.note_description_edit = QTextEdit()

        right_layout.addRow("Note Type:", self.note_type_combo)
        right_layout.addRow("Title:", self.note_title_edit)
        right_layout.addRow("Description:", self.note_description_edit)

        # Lore associations section
        associations_group = QGroupBox("Lore Associations")
        associations_layout = QVBoxLayout()

        self.associations_list = QListWidget()
        self.associations_list.setMaximumHeight(100)
        associations_layout.addWidget(QLabel("Associated Lore Entities:"))
        associations_layout.addWidget(self.associations_list)

        # Association control buttons
        assoc_buttons_layout = QHBoxLayout()
        self.add_association_btn = QPushButton("Add Association")
        self.remove_association_btn = QPushButton("Remove Association")
        self.remove_association_btn.setEnabled(False)

        self.add_association_btn.clicked.connect(self.add_association)
        self.remove_association_btn.clicked.connect(self.remove_association)
        self.associations_list.itemSelectionChanged.connect(
            self.on_association_selected
        )

        assoc_buttons_layout.addWidget(self.add_association_btn)
        assoc_buttons_layout.addWidget(self.remove_association_btn)
        associations_layout.addLayout(assoc_buttons_layout)

        associations_group.setLayout(associations_layout)
        right_layout.addRow(associations_group)

        # Note editor buttons
        editor_buttons_layout = QHBoxLayout()
        self.save_note_btn = QPushButton("Save Note")
        self.cancel_edit_btn = QPushButton("Cancel")

        self.save_note_btn.clicked.connect(self.save_note)
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)

        editor_buttons_layout.addWidget(self.save_note_btn)
        editor_buttons_layout.addWidget(self.cancel_edit_btn)
        right_layout.addRow(editor_buttons_layout)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Disable editor initially
        self.set_editor_enabled(False)

        main_layout.addWidget(splitter)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def set_editor_enabled(self, enabled):
        """Enable or disable the note editor"""
        self.note_type_combo.setEnabled(enabled)
        self.note_title_edit.setEnabled(enabled)
        self.note_description_edit.setEnabled(enabled)
        self.save_note_btn.setEnabled(enabled)
        self.cancel_edit_btn.setEnabled(enabled)
        self.add_association_btn.setEnabled(enabled)
        if not enabled:
            self.remove_association_btn.setEnabled(False)

    def load_notes(self):
        """Load notes for the current node"""
        self.notes_list.clear()
        notes = self.controller.get_notes_for_node(self.node_data.id)

        for note in notes:
            item = QListWidgetItem(f"[{note.note_type.name}] {note.title}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

    def on_note_selected(self):
        """Handle note selection from the list"""
        current_item = self.notes_list.currentItem()
        if current_item:
            self.current_note = current_item.data(Qt.ItemDataRole.UserRole)
            self.load_note_to_editor(self.current_note)
            self.set_editor_enabled(True)
            self.delete_note_btn.setEnabled(True)
        else:
            self.current_note = None
            self.clear_editor()
            self.set_editor_enabled(False)
            self.delete_note_btn.setEnabled(False)

    def load_note_to_editor(self, note):
        """Load a note's data into the editor"""
        # Find the note type in the combo box
        for i in range(self.note_type_combo.count()):
            if self.note_type_combo.itemData(i) == note.note_type:
                self.note_type_combo.setCurrentIndex(i)
                break

        self.note_title_edit.setText(note.title)
        self.note_description_edit.setPlainText(note.description or "")
        self.load_associations(note.id)

    def clear_editor(self):
        """Clear the note editor"""
        self.note_type_combo.setCurrentIndex(0)
        self.note_title_edit.clear()
        self.note_description_edit.clear()
        self.associations_list.clear()

    def add_note(self):
        """Add a new note"""
        self.current_note = None
        self.clear_editor()
        self.set_editor_enabled(True)
        self.note_title_edit.setFocus()

    def save_note(self):
        """Save the current note"""
        title = self.note_title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Invalid Input", "Note title cannot be empty.")
            return

        note_type = self.note_type_combo.currentData()
        description = self.note_description_edit.toPlainText()

        try:
            if self.current_note:
                # Update existing note
                self.controller.update_note(
                    self.current_note.id,
                    title=title,
                    description=description,
                    note_type=note_type,
                )
            else:
                # Create new note
                self.controller.create_note(
                    node_id=self.node_data.id,
                    title=title,
                    description=description,
                    note_type=note_type,
                )

            self.load_notes()
            self.clear_editor()
            self.set_editor_enabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")

    def cancel_edit(self):
        """Cancel editing and clear the editor"""
        self.clear_editor()
        self.set_editor_enabled(False)
        self.current_note = None
        self.notes_list.clearSelection()

    def delete_note(self):
        """Delete the selected note"""
        if not self.current_note:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the note '{self.current_note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_note(self.current_note.id)
                self.load_notes()
                self.clear_editor()
                self.set_editor_enabled(False)
                self.current_note = None

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {str(e)}")

    def load_associations(self, note_id):
        """Load lore associations for the current note"""
        if not note_id:
            self.associations_list.clear()
            return

        try:
            associations = self.controller.get_note_associations(note_id)
            self.associations_list.clear()

            for entity_type, assoc_list in associations.items():
                for assoc in assoc_list:
                    if entity_type == "actors" and assoc.actor:
                        name = f"{assoc.actor.first_name or ''} {assoc.actor.last_name or ''}".strip()
                        if not name:
                            name = f"Actor #{assoc.actor.id}"
                        item_text = f"Actor: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("actor", assoc.actor_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "backgrounds" and assoc.background:
                        name = (
                            assoc.background.background_name
                            or f"Background #{assoc.background.id}"
                        )
                        item_text = f"Background: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            ("background", assoc.background_id),
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "classes" and assoc.class_:
                        name = assoc.class_.class_name or f"Class #{assoc.class_.id}"
                        item_text = f"Class: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("class", assoc.class_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "factions" and assoc.faction:
                        name = (
                            assoc.faction.faction_name or f"Faction #{assoc.faction.id}"
                        )
                        item_text = f"Faction: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("faction", assoc.faction_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "histories" and assoc.history:
                        name = (
                            assoc.history.event_name or f"History #{assoc.history.id}"
                        )
                        item_text = f"History: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("history", assoc.history_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "locations" and assoc.location:
                        name = (
                            assoc.location.location_name
                            or f"Location #{assoc.location.id}"
                        )
                        item_text = f"Location: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("location", assoc.location_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "objects" and assoc.object:
                        name = assoc.object.object_name or f"Object #{assoc.object.id}"
                        item_text = f"Object: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("object", assoc.object_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "races" and assoc.race:
                        name = assoc.race.race_name or f"Race #{assoc.race.id}"
                        item_text = f"Race: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, ("race", assoc.race_id))
                        self.associations_list.addItem(item)
                    elif entity_type == "skills" and assoc.skill:
                        name = assoc.skill.skill_name or f"Skill #{assoc.skill.id}"
                        item_text = f"Skill: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("skill", assoc.skill_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "sub_races" and assoc.sub_race:
                        name = (
                            assoc.sub_race.sub_race_name
                            or f"SubRace #{assoc.sub_race.id}"
                        )
                        item_text = f"Sub-Race: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole, ("sub_race", assoc.sub_race_id)
                        )
                        self.associations_list.addItem(item)
                    elif entity_type == "world_data" and assoc.world_data:
                        name = (
                            assoc.world_data.data_name
                            or f"World Data #{assoc.world_data.id}"
                        )
                        item_text = f"World Data: {name}"
                        item = QListWidgetItem(item_text)
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            ("world_data", assoc.world_data_id),
                        )
                        self.associations_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load associations: {str(e)}")

    def on_association_selected(self):
        """Handle association selection"""
        current_item = self.associations_list.currentItem()
        self.remove_association_btn.setEnabled(current_item is not None)

    def add_association(self):
        """Add a lore association to the current note"""
        if not self.current_note:
            QMessageBox.warning(
                self, "No Note", "Please select or create a note first."
            )
            return

        # Create a dialog to select lore entities
        dialog = LoreSelectionDialog(self.controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entity_type, entity_id = dialog.get_selected_entity()
            if entity_type and entity_id:
                try:
                    success = self.controller.create_note_association(
                        self.current_note.id, entity_type, entity_id
                    )
                    if success:
                        self.load_associations(self.current_note.id)
                    else:
                        QMessageBox.warning(
                            self, "Error", "Failed to create association."
                        )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Failed to create association: {str(e)}"
                    )

    def remove_association(self):
        """Remove the selected lore association"""
        current_item = self.associations_list.currentItem()
        if not current_item or not self.current_note:
            return

        entity_type, entity_id = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove association with {current_item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.controller.delete_note_association(
                    self.current_note.id, entity_type, entity_id
                )
                if success:
                    self.load_associations(self.current_note.id)
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove association.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to remove association: {str(e)}"
                )


class LoreSelectionDialog(QDialog):
    """Dialog for selecting lore entities to associate with notes"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_entity = (None, None)

        self.setWindowTitle("Select Lore Entity")
        self.setMinimumSize(400, 300)

        self.setup_ui()
        self.load_entities()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()

        # Entity type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Entity Type:"))

        self.entity_type_combo = QComboBox()
        self.entity_type_combo.addItems(
            [
                "Actors",
                "Backgrounds",
                "Classes",
                "Factions",
                "Histories",
                "Locations",
                "Objects",
                "Races",
                "Skills",
                "Sub-Races",
                "World Data",
            ]
        )
        self.entity_type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.entity_type_combo)
        layout.addLayout(type_layout)

        # Entity list
        layout.addWidget(QLabel("Select Entity:"))
        self.entity_list = QListWidget()
        self.entity_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.entity_list)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_entities(self):
        """Load entities for the current type"""
        # For now, we'll need to get the setting_id from somewhere
        # This is a simplified implementation
        self.entity_list.clear()

        try:
            # This would need the actual setting_id from the storyline
            # For now, we'll add a placeholder
            self.entity_list.addItem(
                "(Feature requires storyline setting configuration)"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load entities: {str(e)}")

    def on_type_changed(self):
        """Handle entity type change"""
        self.load_entities()

    def get_selected_entity(self):
        """Get the selected entity type and ID"""
        current_item = self.entity_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole) or (None, None)
        return (None, None)
