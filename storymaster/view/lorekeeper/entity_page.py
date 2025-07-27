"""Entity detail page component for user-friendly Lorekeeper interface"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QScrollArea,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSplitter,
)
from PyQt6.QtGui import QFont, QPalette

from storymaster.model.lorekeeper.entity_mappings import (
    EntityMapping,
    FieldSection,
    get_entity_mapping,
)


class SectionWidget(QGroupBox):
    """Widget for displaying a logical section of entity fields"""

    def __init__(self, section: FieldSection, model_adapter=None, parent=None):
        super().__init__(section.display_name, parent)
        self.section = section
        self.model_adapter = model_adapter
        self.field_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(8)

        # Add description if available
        if self.section.description:
            desc_label = QLabel(self.section.description)
            desc_label.setStyleSheet(
                "color: #888; font-style: italic; margin-bottom: 8px;"
            )
            desc_label.setWordWrap(True)
            layout.addRow(desc_label)

        # Create field widgets
        for field_name in self.section.fields:
            widget = self.create_field_widget(field_name)
            self.field_widgets[field_name] = widget

            # Create user-friendly label
            label_text = self.get_field_display_name(field_name)
            layout.addRow(label_text, widget)

        self.setLayout(layout)

    def create_field_widget(self, field_name: str) -> QWidget:
        """Create appropriate widget based on field type"""
        # Text fields that should be multi-line
        multiline_fields = [
            "description",
            "notes",
            "appearance",
            "strengths",
            "weaknesses",
            "ideal",
            "bond",
            "flaw",
            "goals",
            "faction_values",
            "faction_income_sources",
            "faction_expenses",
            "sights",
            "smells",
            "sounds",
            "feels",
            "tastes",
            "dangers",
            "traps",
            "secrets",
            "government",
        ]

        # Foreign key fields that need dropdowns
        foreign_key_fields = [
            "background_id",
            "alignment_id",
            "race_id",
            "class_id",
            "faction_id",
            "location_id",
            "actor_id",
            "skill_id",
            "object_id",
        ]

        if field_name in multiline_fields:
            widget = QTextEdit()
            widget.setMaximumHeight(100)
            widget.setAcceptRichText(False)
        elif field_name in foreign_key_fields:
            widget = QComboBox()
            widget.setEditable(True)
            # Populate foreign key dropdown if model adapter is available
            if self.model_adapter:
                self.populate_foreign_key_dropdown(widget, field_name)
        elif field_name in [
            "actor_age",
            "event_year",
            "object_value",
            "level",
            "skill_level",
            "stat_value",
        ]:
            widget = QLineEdit()
            widget.setPlaceholderText("Enter a number")
        else:
            widget = QLineEdit()

        return widget

    def get_field_display_name(self, field_name: str) -> str:
        """Convert database field names to user-friendly labels"""
        field_mappings = {
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "last_name": "Last Name",
            "actor_age": "Age",
            "background_id": "Background",
            "actor_role": "Role in Story",
            "alignment_id": "Alignment",
            "faction_values": "Values & Beliefs",
            "faction_income_sources": "Income Sources",
            "faction_expenses": "Major Expenses",
            "location_type": "Type of Place",
            "object_value": "Value",
            "event_year": "Year",
            "world_data": "Lore Category",
        }

        return field_mappings.get(field_name, field_name.replace("_", " ").title())

    def populate_foreign_key_dropdown(self, widget: QComboBox, field_name: str):
        """Populate a foreign key dropdown with available options"""
        try:
            options = self.model_adapter.get_foreign_key_options("", field_name)  # table_name not needed for this call
            
            # Add empty option
            widget.addItem("-- Select --", None)
            
            # Add all available options
            for entity_id, display_name in options:
                widget.addItem(display_name, entity_id)
                
        except Exception as e:
            print(f"Error populating dropdown for {field_name}: {e}")

    def get_field_data(self) -> dict:
        """Get all field data from this section"""
        data = {}
        for field_name, widget in self.field_widgets.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text()
            elif isinstance(widget, QTextEdit):
                data[field_name] = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentData()
        return data

    def set_field_data(self, data: dict):
        """Set field data in this section"""
        for field_name, value in data.items():
            if field_name in self.field_widgets:
                widget = self.field_widgets[field_name]
                if isinstance(widget, QLineEdit):
                    widget.setText(str(value) if value is not None else "")
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(value) if value is not None else "")
                elif isinstance(widget, QComboBox):
                    # Set combobox selection based on value
                    index = widget.findData(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)


class RelationshipWidget(QGroupBox):
    """Widget for displaying and managing entity relationships"""

    relationship_selected = pyqtSignal(str, object)  # relationship_type, related_entity
    add_relationship_requested = pyqtSignal(str)  # relationship_type
    remove_relationship_requested = pyqtSignal(str, object)  # relationship_type, entity
    edit_relationship_requested = pyqtSignal(str, object)  # relationship_type, entity

    def __init__(
        self, relationship_name: str, relationship_display_name: str, parent=None
    ):
        super().__init__(relationship_display_name, parent)
        self.relationship_name = relationship_name
        self.related_entities = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # List of related entities
        self.entity_list = QListWidget()
        self.entity_list.itemDoubleClicked.connect(self.on_entity_selected)
        layout.addWidget(self.entity_list)

        # Buttons for managing relationships
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        self.edit_button = QPushButton("Edit")

        # Connect button signals
        self.add_button.clicked.connect(self.on_add_clicked)
        self.remove_button.clicked.connect(self.on_remove_clicked)
        self.edit_button.clicked.connect(self.on_edit_clicked)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Enable/disable buttons based on selection
        self.entity_list.itemSelectionChanged.connect(self.update_button_states)
        self.update_button_states()

    def update_button_states(self):
        """Enable/disable buttons based on selection"""
        has_selection = bool(self.entity_list.currentItem())
        self.edit_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)

    def on_entity_selected(self, item: QListWidgetItem):
        """Handle entity selection"""
        entity_data = item.data(Qt.ItemDataRole.UserRole)
        self.relationship_selected.emit(self.relationship_name, entity_data)

    def set_related_entities(self, entities: list):
        """Set the list of related entities"""
        self.related_entities = entities
        self.entity_list.clear()

        for entity in entities:
            # Create display text based on entity type
            display_text = self.get_entity_display_text(entity)
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, entity)
            self.entity_list.addItem(item)

    def get_entity_display_text(self, entity) -> str:
        """Generate display text for an entity"""
        # Try to get a meaningful name for the entity
        if hasattr(entity, "name") and entity.name:
            return entity.name
        elif hasattr(entity, "first_name") and entity.first_name:
            name_parts = [entity.first_name]
            if hasattr(entity, "last_name") and entity.last_name:
                name_parts.append(entity.last_name)
            return " ".join(name_parts)
        elif hasattr(entity, "title") and entity.title:
            return entity.title
        else:
            return f"ID: {entity.id}"

    def on_add_clicked(self):
        """Handle add button click"""
        self.add_relationship_requested.emit(self.relationship_name)

    def on_remove_clicked(self):
        """Handle remove button click"""
        current_item = self.entity_list.currentItem()
        if current_item:
            entity = current_item.data(Qt.ItemDataRole.UserRole)
            self.remove_relationship_requested.emit(self.relationship_name, entity)

    def on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.entity_list.currentItem()
        if current_item:
            entity = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_relationship_requested.emit(self.relationship_name, entity)


class EntityDetailPage(QWidget):
    """Main page for viewing/editing entity details"""

    entity_saved = pyqtSignal(object)  # entity
    entity_deleted = pyqtSignal(object)  # entity

    def __init__(self, table_name: str, model_adapter=None, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.model_adapter = model_adapter
        self.entity_mapping = get_entity_mapping(table_name)
        self.current_entity = None
        self.section_widgets = {}
        self.relationship_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout()

        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Entity details
        left_panel = self.create_details_panel()
        splitter.addWidget(left_panel)

        # Right panel: Relationships
        right_panel = self.create_relationships_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setStretchFactor(0, 2)  # Details panel takes more space
        splitter.setStretchFactor(1, 1)  # Relationships panel smaller

        layout.addWidget(splitter)
        self.setLayout(layout)

    def create_details_panel(self) -> QWidget:
        """Create the entity details panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Header with entity name and actions
        header_layout = QHBoxLayout()

        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.delete_button = QPushButton("Delete")
        self.save_button.clicked.connect(self.save_entity)
        self.delete_button.clicked.connect(self.delete_entity)

        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.delete_button)

        layout.addLayout(header_layout)

        # Scrollable area for sections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        sections_widget = QWidget()
        sections_layout = QVBoxLayout()

        # Create section widgets
        if self.entity_mapping:
            for section in self.entity_mapping.sections:
                section_widget = SectionWidget(section, self.model_adapter)
                self.section_widgets[section.name] = section_widget
                sections_layout.addWidget(section_widget)

        sections_layout.addStretch()
        sections_widget.setLayout(sections_layout)
        scroll_area.setWidget(sections_widget)

        layout.addWidget(scroll_area)
        panel.setLayout(layout)
        return panel

    def create_relationships_panel(self) -> QWidget:
        """Create the relationships panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Header
        header = QLabel("Relationships")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Scrollable area for relationships
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        relationships_widget = QWidget()
        relationships_layout = QVBoxLayout()

        # Create relationship widgets
        if self.entity_mapping:
            for rel_table, rel_display in self.entity_mapping.relationships.items():
                rel_widget = RelationshipWidget(rel_table, rel_display)
                rel_widget.relationship_selected.connect(self.on_relationship_selected)
                rel_widget.add_relationship_requested.connect(self.on_add_relationship)
                rel_widget.remove_relationship_requested.connect(self.on_remove_relationship)
                rel_widget.edit_relationship_requested.connect(self.on_edit_relationship)
                self.relationship_widgets[rel_table] = rel_widget
                relationships_layout.addWidget(rel_widget)

        relationships_layout.addStretch()
        relationships_widget.setLayout(relationships_layout)
        scroll_area.setWidget(relationships_widget)

        layout.addWidget(scroll_area)
        panel.setLayout(layout)
        return panel

    def set_entity(self, entity):
        """Set the entity to display/edit"""
        self.current_entity = entity
        self.update_display()

    def update_display(self):
        """Update the display with current entity data"""
        if not self.current_entity or not self.entity_mapping:
            return

        # Update title
        title = self.get_entity_title()
        self.title_label.setText(title)

        # Update section data
        entity_dict = self.current_entity.as_dict()
        for section_name, section_widget in self.section_widgets.items():
            section_widget.set_field_data(entity_dict)
        
        # Load relationships
        self.load_relationships()

    def get_entity_title(self) -> str:
        """Get display title for the current entity"""
        if not self.current_entity:
            return f"New {self.entity_mapping.display_name}"

        # Try to find a meaningful name
        if hasattr(self.current_entity, "name") and self.current_entity.name:
            return self.current_entity.name
        elif hasattr(self.current_entity, "first_name"):
            name_parts = []
            if self.current_entity.first_name:
                name_parts.append(self.current_entity.first_name)
            if (
                hasattr(self.current_entity, "last_name")
                and self.current_entity.last_name
            ):
                name_parts.append(self.current_entity.last_name)
            if name_parts:
                return " ".join(name_parts)
        elif hasattr(self.current_entity, "title") and self.current_entity.title:
            return self.current_entity.title

        return f"{self.entity_mapping.display_name} #{self.current_entity.id}"

    def save_entity(self):
        """Save the current entity"""
        if not self.current_entity:
            return

        # Collect data from all sections
        all_data = {}
        for section_widget in self.section_widgets.values():
            all_data.update(section_widget.get_field_data())

        # Update entity attributes
        for field_name, value in all_data.items():
            if hasattr(self.current_entity, field_name):
                setattr(self.current_entity, field_name, value)

        self.entity_saved.emit(self.current_entity)

    def delete_entity(self):
        """Delete the current entity"""
        if self.current_entity:
            self.entity_deleted.emit(self.current_entity)

    def on_relationship_selected(self, relationship_type: str, related_entity):
        """Handle relationship selection"""
        # This would navigate to the related entity
        # Implementation depends on the overall navigation system
        pass

    def on_add_relationship(self, relationship_type: str):
        """Handle adding a new relationship"""
        from PyQt6.QtWidgets import QMessageBox, QDialog
        from storymaster.view.lorekeeper.entity_selection_dialog import EntitySelectionDialog
        
        if not self.model_adapter:
            QMessageBox.warning(
                self, 
                "Error", 
                "Model adapter not available. Cannot add relationships."
            )
            return
        
        # Show entity selection dialog
        dialog = EntitySelectionDialog(relationship_type, self.model_adapter, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_entity = dialog.get_selected_entity()
            if selected_entity:
                entity_name = self.get_entity_display_name(selected_entity)
                
                # Actually create the relationship
                success = self.model_adapter.add_relationship(
                    self.current_entity, 
                    relationship_type, 
                    selected_entity
                )
                
                if success:
                    QMessageBox.information(
                        self, 
                        "Relationship Added", 
                        f"Successfully added '{entity_name}' to {relationship_type.replace('_', ' ')}"
                    )
                    # Refresh the relationship display
                    self.refresh_relationship_display(relationship_type)
                else:
                    QMessageBox.warning(
                        self, 
                        "Relationship Exists", 
                        f"A relationship with '{entity_name}' already exists in {relationship_type.replace('_', ' ')}"
                    )

    def on_remove_relationship(self, relationship_type: str, related_entity):
        """Handle removing a relationship"""
        from PyQt6.QtWidgets import QMessageBox
        
        entity_name = self.get_entity_display_name(related_entity)
        reply = QMessageBox.question(
            self,
            "Remove Relationship",
            f"Are you sure you want to remove '{entity_name}' from {relationship_type.replace('_', ' ')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Actually remove the relationship
            success = self.model_adapter.remove_relationship(
                self.current_entity,
                relationship_type,
                related_entity
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Relationship Removed", 
                    f"Successfully removed '{entity_name}' from {relationship_type.replace('_', ' ')}"
                )
                # Refresh the relationship display
                self.refresh_relationship_display(relationship_type)
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to remove relationship with '{entity_name}'"
                )

    def on_edit_relationship(self, relationship_type: str, related_entity):
        """Handle editing a relationship"""
        from PyQt6.QtWidgets import QMessageBox, QDialog
        from storymaster.view.lorekeeper.relationship_details_dialog import RelationshipDetailsDialog
        
        if not self.model_adapter:
            QMessageBox.warning(
                self, 
                "Error", 
                "Model adapter not available. Cannot edit relationships."
            )
            return
        
        # Open relationship details dialog
        dialog = RelationshipDetailsDialog(
            relationship_type, 
            self.current_entity, 
            related_entity, 
            self.model_adapter, 
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            relationship_data = dialog.get_relationship_data()
            entity_name = self.get_entity_display_name(related_entity)
            
            # Actually update the relationship in the database
            success = self.model_adapter.update_relationship(
                self.current_entity,
                relationship_type,
                related_entity,
                relationship_data
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Relationship Updated",
                    f"Successfully updated relationship with '{entity_name}'\n\nDetails: {len(relationship_data)} fields modified"
                )
                # Refresh the relationship display
                self.refresh_relationship_display(relationship_type)
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to update relationship with '{entity_name}'"
                )

    def get_entity_display_name(self, entity) -> str:
        """Get display name for an entity"""
        if hasattr(entity, "name") and entity.name:
            return entity.name
        elif hasattr(entity, "first_name") and entity.first_name:
            name_parts = [entity.first_name]
            if hasattr(entity, "last_name") and entity.last_name:
                name_parts.append(entity.last_name)
            return " ".join(name_parts)
        elif hasattr(entity, "title") and entity.title:
            return entity.title
        else:
            return f"ID: {getattr(entity, 'id', 'Unknown')}"

    def refresh_relationship_display(self, relationship_type: str = None):
        """Refresh the display of relationships"""
        if not self.current_entity or not self.model_adapter:
            return
        
        # Refresh specific relationship type or all relationships
        relationship_types = [relationship_type] if relationship_type else self.relationship_widgets.keys()
        
        for rel_type in relationship_types:
            if rel_type in self.relationship_widgets:
                related_entities = self.model_adapter.get_relationship_entities(
                    self.current_entity, 
                    rel_type
                )
                self.relationship_widgets[rel_type].set_related_entities(related_entities)

    def load_relationships(self):
        """Load and display all relationships for the current entity"""
        if not self.current_entity or not self.model_adapter:
            return
        
        for rel_type, rel_widget in self.relationship_widgets.items():
            related_entities = self.model_adapter.get_relationship_entities(
                self.current_entity, 
                rel_type
            )
            rel_widget.set_related_entities(related_entities)
