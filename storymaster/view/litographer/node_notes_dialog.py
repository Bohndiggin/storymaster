"""
Dialog for managing notes linked to a litography node.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from storymaster.model.database.schema.base import NoteType
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_group_box_style,
    get_splitter_style,
    get_list_style,
    get_dialog_style,
    get_checkbox_style,
    get_tab_style,
)
from storymaster.view.common.tooltips import (
    apply_notes_tooltips,
    apply_general_tooltips,
)
from storymaster.view.common.custom_widgets import enable_smart_tab_navigation


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
            f"Notes for {node_data.name} ({node_data.node_type.name.title()})"
        )
        self.setMinimumSize(600, 400)
        
        # Apply comprehensive theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_input_style()
            + get_list_style()
            + get_group_box_style()
            + get_splitter_style()
            + get_checkbox_style()
            + get_tab_style()
        )

        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout()

        # Node info section
        node_info_group = QGroupBox("Node Information")
        node_info_layout = QFormLayout()
        node_type_label = QLabel(self.node_data.node_type.name.title())
        node_type_label.setStyleSheet("background-color: transparent; color: #ffffff;")
        node_info_layout.addRow("Node Type:", node_type_label)
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
        self.add_note_btn.setStyleSheet(get_button_style("primary"))
        self.delete_note_btn = QPushButton("Delete Note")
        self.delete_note_btn.setStyleSheet(get_button_style("danger"))
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
        self.note_type_combo.setStyleSheet(get_input_style())
        apply_notes_tooltips(self.note_type_combo, "note_type")
        for note_type in NoteType:
            self.note_type_combo.addItem(note_type.name.title(), note_type)

        self.note_title_edit = QLineEdit()
        self.note_title_edit.setStyleSheet(get_input_style())
        apply_notes_tooltips(self.note_title_edit, "note_title")

        self.note_description_edit = QTextEdit()
        self.note_description_edit.setStyleSheet(get_input_style())
        apply_notes_tooltips(self.note_description_edit, "note_description")

        right_layout.addRow("Note Type:", self.note_type_combo)
        right_layout.addRow("Title:", self.note_title_edit)
        right_layout.addRow("Description:", self.note_description_edit)

        # Lore associations section
        associations_group = QGroupBox("Lore Associations")
        associations_layout = QVBoxLayout()

        self.associations_list = QListWidget()
        self.associations_list.setMaximumHeight(100)
        entities_label = QLabel("Associated Lore Entities:")
        entities_label.setStyleSheet("background-color: transparent; color: #ffffff;")
        associations_layout.addWidget(entities_label)
        associations_layout.addWidget(self.associations_list)

        # Association control buttons
        assoc_buttons_layout = QHBoxLayout()
        self.add_association_btn = QPushButton("Add Association")
        apply_notes_tooltips(self.add_association_btn, "add_association")

        self.remove_association_btn = QPushButton("Remove Association")
        self.remove_association_btn.setStyleSheet(get_button_style("danger"))
        self.remove_association_btn.setEnabled(False)
        apply_notes_tooltips(self.remove_association_btn, "remove_association")

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
        self.save_note_btn.setStyleSheet(get_button_style("primary"))
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

        # Set up enhanced tab navigation
        enable_smart_tab_navigation(self)

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
            # Get setting_id and create model adapter
            setting_id = getattr(self.controller, "current_setting_id", None)
            if not setting_id:
                self.associations_list.clear()
                return

            from storymaster.view.lorekeeper.lorekeeper_model_adapter import (
                LorekeeperModelAdapter,
            )

            adapter = LorekeeperModelAdapter(self.controller.model, setting_id)

            # Get the current note entity
            note_entity = adapter.get_entity_by_id("litography_notes", note_id)
            if not note_entity:
                self.associations_list.clear()
                return

            self.associations_list.clear()

            # Define relationship types to check
            relationship_types = [
                ("litography_note_to_world_data", "World Data"),
                ("litography_note_to_actor", "Actor"),
                ("litography_note_to_location", "Location"),
                ("litography_note_to_object", "Object"),
                ("litography_note_to_faction", "Faction"),
            ]

            for relationship_name, display_type in relationship_types:
                try:
                    related_entities = adapter.get_relationship_entities(
                        note_entity, relationship_name
                    )
                    for entity in related_entities:
                        if entity:
                            # Create display name based on entity type
                            if hasattr(entity, "name") and entity.name:
                                display_name = entity.name
                            elif hasattr(entity, "first_name") and entity.first_name:
                                name_parts = [entity.first_name]
                                if hasattr(entity, "last_name") and entity.last_name:
                                    name_parts.append(entity.last_name)
                                display_name = " ".join(name_parts)
                            elif hasattr(entity, "title") and entity.title:
                                display_name = entity.title
                            else:
                                display_name = f"ID: {entity.id}"

                            item_text = f"{display_type}: {display_name}"
                            item = QListWidgetItem(item_text)

                            # Map relationship back to entity type
                            entity_type_mapping = {
                                "litography_note_to_world_data": "world_data",
                                "litography_note_to_actor": "actor",
                                "litography_note_to_location": "location",
                                "litography_note_to_object": "object",
                                "litography_note_to_faction": "faction",
                            }
                            entity_type = entity_type_mapping.get(relationship_name)
                            item.setData(
                                Qt.ItemDataRole.UserRole, (entity_type, entity.id)
                            )
                            self.associations_list.addItem(item)
                except Exception as rel_e:
                    print(f"Error loading {relationship_name}: {rel_e}")
                    continue

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
                    # Get setting_id and create model adapter
                    setting_id = getattr(self.controller, "current_setting_id", None)
                    if not setting_id:
                        QMessageBox.warning(self, "Error", "No setting configured")
                        return

                    from storymaster.view.lorekeeper.lorekeeper_model_adapter import (
                        LorekeeperModelAdapter,
                    )

                    adapter = LorekeeperModelAdapter(self.controller.model, setting_id)

                    # Get the note and related entity
                    note_entity = adapter.get_entity_by_id(
                        "litography_notes", self.current_note.id
                    )
                    related_entity = adapter.get_entity_by_id(entity_type, entity_id)

                    if not note_entity or not related_entity:
                        QMessageBox.warning(
                            self, "Error", "Could not find note or entity"
                        )
                        return

                    # Map entity type to relationship name
                    type_to_relationship = {
                        "world_data": "litography_note_to_world_data",
                        "actor": "litography_note_to_actor",
                        "location_": "litography_note_to_location",
                        "location": "litography_note_to_location",
                        "object_": "litography_note_to_object",
                        "object": "litography_note_to_object",
                        "faction": "litography_note_to_faction",
                    }

                    relationship_name = type_to_relationship.get(entity_type)
                    if not relationship_name:
                        QMessageBox.warning(
                            self, "Error", f"Unsupported entity type: {entity_type}"
                        )
                        return

                    # Add the relationship
                    success = adapter.add_relationship(
                        note_entity, relationship_name, related_entity
                    )
                    if success:
                        self.load_associations(self.current_note.id)
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "Association already exists or failed to create.",
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
                # Get setting_id and create model adapter
                setting_id = getattr(self.controller, "current_setting_id", None)
                if not setting_id:
                    QMessageBox.warning(self, "Error", "No setting configured")
                    return

                from storymaster.view.lorekeeper.lorekeeper_model_adapter import (
                    LorekeeperModelAdapter,
                )

                adapter = LorekeeperModelAdapter(self.controller.model, setting_id)

                # Get the note and related entity
                note_entity = adapter.get_entity_by_id(
                    "litography_notes", self.current_note.id
                )
                related_entity = adapter.get_entity_by_id(entity_type, entity_id)

                if not note_entity or not related_entity:
                    QMessageBox.warning(self, "Error", "Could not find note or entity")
                    return

                # Map entity type to relationship name
                type_to_relationship = {
                    "world_data": "litography_note_to_world_data",
                    "actor": "litography_note_to_actor",
                    "location_": "litography_note_to_location",
                    "location": "litography_note_to_location",
                    "object_": "litography_note_to_object",
                    "object": "litography_note_to_object",
                    "faction": "litography_note_to_faction",
                }

                relationship_name = type_to_relationship.get(entity_type)
                if not relationship_name:
                    QMessageBox.warning(
                        self, "Error", f"Unsupported entity type: {entity_type}"
                    )
                    return

                # Remove the relationship
                success = adapter.remove_relationship(
                    note_entity, relationship_name, related_entity
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
        entity_type_label = QLabel("Entity Type:")
        entity_type_label.setStyleSheet("background-color: transparent; color: #ffffff;")
        type_layout.addWidget(entity_type_label)

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
        select_entity_label = QLabel("Select Entity:")
        select_entity_label.setStyleSheet("background-color: transparent; color: #ffffff;")
        layout.addWidget(select_entity_label)
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
        self.entity_list.clear()

        try:
            # Get setting_id from controller
            setting_id = getattr(self.controller, "current_setting_id", None)
            if not setting_id:
                self.entity_list.addItem("(No setting configured)")
                return

            # Create Lorekeeper model adapter
            from storymaster.view.lorekeeper.lorekeeper_model_adapter import (
                LorekeeperModelAdapter,
            )

            adapter = LorekeeperModelAdapter(self.controller.model, setting_id)

            # Map UI types to table names
            type_mapping = {
                "Actors": "actor",
                "Backgrounds": "background",
                "Classes": "class",
                "Factions": "faction",
                "Histories": "history",
                "Locations": "location_",
                "Objects": "object_",
                "Races": "race",
                "Skills": "skills",
                "Sub-Races": "sub_race",
                "World Data": "world_data",
            }

            current_type = self.entity_type_combo.currentText()
            table_name = type_mapping.get(current_type)

            if table_name:
                entities = adapter.get_entities(table_name)
                for entity in entities:
                    # Create display name based on entity type
                    if hasattr(entity, "name") and entity.name:
                        display_name = entity.name
                    elif hasattr(entity, "first_name") and entity.first_name:
                        name_parts = [entity.first_name]
                        if hasattr(entity, "last_name") and entity.last_name:
                            name_parts.append(entity.last_name)
                        display_name = " ".join(name_parts)
                    elif hasattr(entity, "title") and entity.title:
                        display_name = entity.title
                    else:
                        display_name = f"ID: {entity.id}"

                    item = QListWidgetItem(display_name)
                    # Store entity type and ID for selection
                    item.setData(Qt.ItemDataRole.UserRole, (table_name, entity.id))
                    self.entity_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load entities: {str(e)}")

    def on_type_changed(self):
        """Handle entity type change"""
        self.load_entities()

    def get_selected_entity(self):
        """Get the selected entity type and ID"""
        current_item = self.entity_list.currentItem()
        if current_item and current_item.data(Qt.ItemDataRole.UserRole):
            table_name, entity_id = current_item.data(Qt.ItemDataRole.UserRole)
            # Convert table name back to the format expected by the controller
            table_to_type_mapping = {
                "actor": "actor",
                "background": "background",
                "class": "class",
                "faction": "faction",
                "history": "history",
                "location_": "location",
                "object_": "object",
                "race": "race",
                "skills": "skill",
                "sub_race": "sub_race",
                "world_data": "world_data",
            }
            entity_type = table_to_type_mapping.get(table_name, table_name)
            return (entity_type, entity_id)
        return (None, None)
