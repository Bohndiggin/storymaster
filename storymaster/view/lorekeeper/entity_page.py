"""Entity detail page component for user-friendly Lorekeeper interface"""

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from storymaster.model.lorekeeper.entity_mappings import (
    EntityMapping,
    FieldSection,
    get_entity_mapping,
)
from storymaster.view.common.custom_widgets import (
    TabNavigationComboBox,
    TabNavigationLineEdit,
    TabNavigationTextEdit,
    enable_smart_tab_navigation,
)
from storymaster.view.common.theme import (
    COLORS,
    FONTS,
    get_button_style,
    get_group_box_style,
    get_input_style,
    get_label_style,
    get_splitter_style,
)
from storymaster.view.common.tooltips import (
    LOREKEEPER_TOOLTIPS,
    apply_general_tooltips,
    apply_lorekeeper_tooltips,
)


class SectionWidget(QGroupBox):
    """Widget for displaying a logical section of entity fields"""

    # Signal emitted when a checkbox changes (field_name, checked)
    checkbox_changed = Signal(str, bool)
    # Signal emitted when any field changes (for autosave)
    field_changed = Signal()

    def __init__(self, section: FieldSection, model_adapter=None, table_name=None, parent=None):
        super().__init__(section.display_name, parent)
        self.section = section
        self.model_adapter = model_adapter
        self.table_name = table_name
        self.field_widgets = {}
        self.setStyleSheet(get_group_box_style())
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        # Add description if available
        if self.section.description:
            desc_label = QLabel(self.section.description)
            desc_label.setStyleSheet(get_label_style("muted"))
            desc_label.setWordWrap(True)
            layout.addRow(desc_label)

        # Create field widgets
        for field_name in self.section.fields:
            widget = self.create_field_widget(field_name)
            self.field_widgets[field_name] = widget

            # Create user-friendly label with proper styling
            label_text = self.get_field_display_name(field_name)
            label = QLabel(label_text)
            label.setStyleSheet(get_label_style())
            layout.addRow(label, widget)

        self.setLayout(layout)

    def create_field_widget(self, field_name: str) -> QWidget:
        """Create appropriate widget based on field type"""
        # Check if field is an enum type
        enum_class = self.get_enum_class_for_field(field_name)
        if enum_class:
            widget = TabNavigationComboBox()
            widget.setStyleSheet(get_input_style())
            # Populate with enum values
            for enum_value in enum_class:
                widget.addItem(enum_value.value.title(), enum_value.value)
            return widget

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
            "flora_fauna_description",
            "district_description",
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

        # Boolean fields that need checkboxes
        boolean_fields = [
            "is_dungeon",
            "is_city",
        ]

        if field_name in boolean_fields:
            widget = QCheckBox()
            # Connect checkbox changes to signal if this is a checkbox section
            if self.section.is_checkbox_section:
                widget.stateChanged.connect(
                    lambda state, field=field_name: self.checkbox_changed.emit(
                        field, state == Qt.CheckState.Checked.value
                    )
                )
        elif field_name in multiline_fields:
            widget = TabNavigationTextEdit()
            widget.setMaximumHeight(120)
            widget.setAcceptRichText(False)
            widget.setStyleSheet(get_input_style())
        elif field_name in foreign_key_fields:
            widget = TabNavigationComboBox()
            widget.setEditable(True)
            widget.setStyleSheet(get_input_style())
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
            widget = TabNavigationLineEdit()
            widget.setPlaceholderText("Enter a number")
            widget.setStyleSheet(get_input_style())
        else:
            widget = TabNavigationLineEdit()
            widget.setStyleSheet(get_input_style())

        # Apply tooltips based on field name
        self.apply_field_tooltip(widget, field_name)

        # Connect widget changes to trigger autosave
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.field_changed.emit)
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(self.field_changed.emit)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(self.field_changed.emit)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(self.field_changed.emit)

        return widget

    def get_enum_class_for_field(self, field_name: str):
        """Get the enum class for a field if it's an enum type"""
        if not self.table_name or not self.model_adapter:
            return None

        try:
            from sqlalchemy import inspect as sqla_inspect
            from sqlalchemy.sql.sqltypes import Enum as SQLAlchemyEnum
            import enum

            table_class = self.model_adapter.table_classes.get(self.table_name)
            if not table_class:
                return None

            mapper = sqla_inspect(table_class)

            # Get the column - need to check if it exists first
            if field_name not in mapper.columns:
                return None

            column = mapper.columns[field_name]
            column_type = column.type

            # Check if it's a SQLAlchemy Enum type
            if isinstance(column_type, SQLAlchemyEnum):
                # The enum_class attribute contains the Python enum
                if hasattr(column_type, 'enum_class') and column_type.enum_class is not None:
                    return column_type.enum_class

        except Exception as e:
            # Silently ignore errors - field is not an enum
            pass

        return None

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
            "is_dungeon": "Dungeon",
            "is_city": "City",
            "dangers": "Dangers",
            "traps": "Traps",
            "secrets": "Secrets",
            "government": "Government Type",
        }

        return field_mappings.get(field_name, field_name.replace("_", " ").title())

    def populate_foreign_key_dropdown(self, widget: QComboBox, field_name: str):
        """Populate a foreign key dropdown with available options"""
        try:
            options = self.model_adapter.get_foreign_key_options(
                "", field_name
            )  # table_name not needed for this call

            # Add empty option
            widget.addItem("-- Select --", None)

            # Add all available options
            for entity_id, display_name in options:
                widget.addItem(display_name, entity_id)

        except Exception as e:
            print(f"Error populating dropdown for {field_name}: {e}")

    def refresh_foreign_key_dropdowns(self):
        """Refresh all foreign key dropdowns in this section"""
        # List of foreign key fields that need dropdowns
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

        for field_name, widget in self.field_widgets.items():
            if field_name in foreign_key_fields and isinstance(widget, QComboBox):
                # Save current selection
                current_value = widget.currentData()

                # Clear and repopulate
                widget.clear()
                if self.model_adapter:
                    self.populate_foreign_key_dropdown(widget, field_name)

                    # Restore selection if still valid
                    if current_value is not None:
                        index = widget.findData(current_value)
                        if index >= 0:
                            widget.setCurrentIndex(index)

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
            elif isinstance(widget, QCheckBox):
                data[field_name] = widget.isChecked()
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
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(value) if value is not None else False)

    def apply_field_tooltip(self, widget, field_name: str):
        """Apply appropriate tooltip to a field widget"""
        # Create tooltip key by combining entity type context with field name
        entity_context = getattr(self, "entity_type", "")

        # Try specific field combinations first
        tooltip_keys = [
            f"{entity_context}_{field_name}",  # e.g., "actor_first_name"
            field_name,  # e.g., "first_name"
        ]

        tooltip_text = None
        for key in tooltip_keys:
            if key in LOREKEEPER_TOOLTIPS:
                tooltip_text = LOREKEEPER_TOOLTIPS[key]
                break

        # If no specific tooltip found, create a helpful generic one
        if not tooltip_text:
            display_name = self.get_field_display_name(field_name)
            tooltip_text = f"Enter the {display_name.lower()} for this item. This information helps build your story world."

        widget.setToolTip(tooltip_text)


class RelationshipWidget(QGroupBox):
    """Widget for displaying and managing entity relationships"""

    relationship_selected = Signal(str, object)  # relationship_type, related_entity
    add_relationship_requested = Signal(str)  # relationship_type
    remove_relationship_requested = Signal(str, object)  # relationship_type, entity
    edit_relationship_requested = Signal(str, object)  # relationship_type, entity

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

    entity_saved = Signal(object)  # entity
    entity_deleted = Signal(object)  # entity
    autosave_requested = Signal()  # Signal to trigger autosave

    def __init__(self, table_name: str, model_adapter=None, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.model_adapter = model_adapter
        self.entity_mapping = get_entity_mapping(table_name)
        self.current_entity = None
        self.section_widgets = {}
        self.relationship_widgets = {}

        # Set up autosave timer (triggers 2 seconds after last change)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(2000)  # 2 second delay
        self.autosave_timer.timeout.connect(self.on_autosave_timer)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(get_splitter_style())

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

        # Set up enhanced tab navigation for all form fields
        enable_smart_tab_navigation(self)

    def create_details_panel(self) -> QWidget:
        """Create the entity details panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header with entity name and actions
        header_layout = QHBoxLayout()

        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(get_button_style("danger"))
        apply_general_tooltips(self.delete_button, "delete_button")

        self.delete_button.clicked.connect(self.delete_entity)

        header_layout.addWidget(self.delete_button)

        layout.addLayout(header_layout)

        # Scrollable area for sections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        sections_widget = QWidget()
        sections_layout = QVBoxLayout()
        sections_layout.setContentsMargins(8, 8, 8, 8)
        sections_layout.setSpacing(10)

        # Create section widgets
        if self.entity_mapping:
            for section in self.entity_mapping.sections:
                section_widget = SectionWidget(section, self.model_adapter, self.table_name)
                self.section_widgets[section.name] = section_widget

                # Connect checkbox signals for conditional sections
                if section.is_checkbox_section:
                    section_widget.checkbox_changed.connect(self.on_checkbox_changed)

                # Connect field change signals for autosave
                section_widget.field_changed.connect(self.on_field_changed)

                # Hide conditional sections initially
                if section.conditional_field:
                    section_widget.setVisible(False)

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
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

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
        relationships_layout.setContentsMargins(8, 8, 8, 8)
        relationships_layout.setSpacing(8)

        # Create relationship widgets
        if self.entity_mapping:
            for rel_table, rel_display in self.entity_mapping.relationships.items():
                rel_widget = RelationshipWidget(rel_table, rel_display)
                rel_widget.relationship_selected.connect(self.on_relationship_selected)
                rel_widget.add_relationship_requested.connect(self.on_add_relationship)
                rel_widget.remove_relationship_requested.connect(
                    self.on_remove_relationship
                )
                rel_widget.edit_relationship_requested.connect(
                    self.on_edit_relationship
                )
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

        # For locations, also get additional details
        if self.table_name == "location_" and self.model_adapter:
            location_details = self.model_adapter.get_location_details(
                self.current_entity
            )
            entity_dict.update(location_details)

        for section_name, section_widget in self.section_widgets.items():
            section_widget.set_field_data(entity_dict)

        # Update conditional section visibility
        self.update_conditional_sections()

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

        # For locations, also save additional details
        if self.table_name == "location_" and self.model_adapter:
            self.model_adapter.save_location_details(self.current_entity, all_data)

        self.entity_saved.emit(self.current_entity)

    def delete_entity(self):
        """Delete the current entity"""
        if self.current_entity:
            self.entity_deleted.emit(self.current_entity)

    def refresh_foreign_key_dropdowns(self):
        """Refresh all foreign key dropdowns in all sections"""
        for section_widget in self.section_widgets.values():
            if hasattr(section_widget, 'refresh_foreign_key_dropdowns'):
                section_widget.refresh_foreign_key_dropdowns()

    def on_field_changed(self):
        """Handle any field change - restart autosave timer"""
        # Restart the timer - this debounces rapid typing
        self.autosave_timer.stop()
        self.autosave_timer.start()

    def on_autosave_timer(self):
        """Called when autosave timer expires"""
        # Emit signal to parent to trigger autosave
        self.autosave_requested.emit()

    def on_relationship_selected(self, relationship_type: str, related_entity):
        """Handle relationship selection"""
        # This would navigate to the related entity
        # Implementation depends on the overall navigation system
        pass

    def on_add_relationship(self, relationship_type: str):
        """Handle adding a new relationship"""
        from PySide6.QtWidgets import QDialog, QMessageBox

        from storymaster.view.lorekeeper.entity_selection_dialog import (
            EntitySelectionDialog,
        )

        if not self.model_adapter:
            QMessageBox.warning(
                self, "Error", "Model adapter not available. Cannot add relationships."
            )
            return

        # Show entity selection dialog
        dialog = EntitySelectionDialog(
            relationship_type, self.model_adapter, self.current_entity, self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_entity = dialog.get_selected_entity()
            if selected_entity:
                entity_name = self.get_entity_display_name(selected_entity)

                # Actually create the relationship
                success = self.model_adapter.add_relationship(
                    self.current_entity, relationship_type, selected_entity
                )

                if success:
                    # Refresh the relationship display (no popup)
                    self.refresh_relationship_display(relationship_type)
                else:
                    QMessageBox.warning(
                        self,
                        "Relationship Exists",
                        f"A relationship with '{entity_name}' already exists in {relationship_type.replace('_', ' ')}",
                    )

    def on_remove_relationship(self, relationship_type: str, related_entity):
        """Handle removing a relationship"""
        from PySide6.QtWidgets import QMessageBox

        entity_name = self.get_entity_display_name(related_entity)
        reply = QMessageBox.question(
            self,
            "Remove Relationship",
            f"Are you sure you want to remove '{entity_name}' from {relationship_type.replace('_', ' ')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Actually remove the relationship
            success = self.model_adapter.remove_relationship(
                self.current_entity, relationship_type, related_entity
            )

            if success:
                # Refresh the relationship display (no popup)
                self.refresh_relationship_display(relationship_type)
            else:
                QMessageBox.warning(
                    self, "Error", f"Failed to remove relationship with '{entity_name}'"
                )

    def on_edit_relationship(self, relationship_type: str, related_entity):
        """Handle editing a relationship"""
        from PySide6.QtWidgets import QDialog, QMessageBox

        from storymaster.view.lorekeeper.relationship_details_dialog import (
            RelationshipDetailsDialog,
        )

        if not self.model_adapter:
            QMessageBox.warning(
                self, "Error", "Model adapter not available. Cannot edit relationships."
            )
            return

        # Open relationship details dialog
        dialog = RelationshipDetailsDialog(
            relationship_type,
            self.current_entity,
            related_entity,
            self.model_adapter,
            self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            relationship_data = dialog.get_relationship_data()
            entity_name = self.get_entity_display_name(related_entity)

            # Actually update the relationship in the database
            success = self.model_adapter.update_relationship(
                self.current_entity,
                relationship_type,
                related_entity,
                relationship_data,
            )

            if success:
                # Refresh the relationship display (no popup)
                self.refresh_relationship_display(relationship_type)
            else:
                QMessageBox.warning(
                    self, "Error", f"Failed to update relationship with '{entity_name}'"
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
        relationship_types = (
            [relationship_type]
            if relationship_type
            else self.relationship_widgets.keys()
        )

        for rel_type in relationship_types:
            if rel_type in self.relationship_widgets:
                related_entities = self.model_adapter.get_relationship_entities(
                    self.current_entity, rel_type
                )
                self.relationship_widgets[rel_type].set_related_entities(
                    related_entities
                )

    def load_relationships(self):
        """Load and display all relationships for the current entity"""
        if not self.current_entity or not self.model_adapter:
            return

        for rel_type, rel_widget in self.relationship_widgets.items():
            related_entities = self.model_adapter.get_relationship_entities(
                self.current_entity, rel_type
            )
            rel_widget.set_related_entities(related_entities)

    def on_checkbox_changed(self, field_name: str, checked: bool):
        """Handle checkbox changes for conditional sections"""
        if not self.entity_mapping:
            return

        # Find sections that depend on this field
        for section in self.entity_mapping.sections:
            if section.conditional_field == field_name:
                section_widget = self.section_widgets.get(section.name)
                if section_widget:
                    section_widget.setVisible(checked)

    def update_conditional_sections(self):
        """Update visibility of conditional sections based on current data"""
        if not self.current_entity or not self.entity_mapping:
            return

        entity_dict = self.current_entity.as_dict()

        for section in self.entity_mapping.sections:
            if section.conditional_field:
                # Check if the controlling field is true
                field_value = entity_dict.get(section.conditional_field, False)
                section_widget = self.section_widgets.get(section.name)
                if section_widget:
                    section_widget.setVisible(bool(field_value))
