"""Entity selection dialog for adding relationships"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QFont

from storymaster.model.lorekeeper.entity_mappings import get_entity_mapping


class EntitySelectionDialog(QDialog):
    """Dialog for selecting entities to add to relationships"""

    def __init__(self, relationship_type: str, model_adapter, parent=None):
        super().__init__(parent)
        self.relationship_type = relationship_type
        self.model_adapter = model_adapter
        self.selected_entity = None
        self.entities = []
        self.setup_ui()
        self.load_entities()

    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle(f"Add {self.relationship_type.replace('_', ' ').title()}")
        self.setModal(True)
        self.resize(400, 500)

        layout = QVBoxLayout()

        # Header
        header = QLabel(
            f"Select an entity to add to {self.relationship_type.replace('_', ' ')}"
        )
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search entities...")
        self.search_field.textChanged.connect(self.filter_entities)
        layout.addWidget(self.search_field)

        # Entity list
        self.entity_list = QListWidget()
        self.entity_list.itemDoubleClicked.connect(self.on_entity_double_clicked)
        layout.addWidget(self.entity_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.accept)
        self.select_button.setEnabled(False)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect selection change
        self.entity_list.itemSelectionChanged.connect(self.on_selection_changed)

    def load_entities(self):
        """Load all entities that can be added to this relationship"""
        # Determine which entity types can be added based on relationship type
        target_tables = self.get_target_tables_for_relationship()

        self.entities = []
        for table_name in target_tables:
            entities = self.model_adapter.get_entities(table_name)
            for entity in entities:
                # Add table info for display
                entity._table_name = table_name
                self.entities.append(entity)

        self.populate_list(self.entities)

    def get_target_tables_for_relationship(self) -> list:
        """Get the target entity types for this relationship"""
        # Mapping of relationship types to target entity types
        relationship_mappings = {
            "actor_a_on_b_relations": ["actor"],
            "faction_members": ["actor"],
            "residents": ["actor"],
            "actor_to_skills": ["skills"],
            "actor_to_race": ["race"],
            "actor_to_class": ["class"],
            "actor_to_stat": ["stat"],
            "object_to_owner": ["actor"],
            "history_actor": ["actor"],
            "history_location": ["location_"],
            "history_faction": ["faction"],
            "history_object": ["object_"],
            "history_world_data": ["world_data"],
            "arc_to_actor": ["actor"],
            "location_to_faction": ["faction"],
            "location_dungeon": ["location_"],
            "location_city": ["location_"],
            "location_city_districts": ["location_"],
            "location_flora_fauna": ["location_"],
        }

        # Default to all main entity types if relationship not mapped
        return relationship_mappings.get(
            self.relationship_type,
            ["actor", "faction", "location_", "object_", "history", "world_data"],
        )

    def populate_list(self, entities: list):
        """Populate the entity list"""
        self.entity_list.clear()

        for entity in entities:
            display_text = self.get_entity_display_text(entity)

            # Add entity type info
            table_name = getattr(entity, "_table_name", "unknown")
            mapping = get_entity_mapping(table_name)
            if mapping:
                display_text = f"{mapping.icon} {display_text} ({mapping.display_name})"
            else:
                display_text = f"{display_text} ({table_name})"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, entity)
            self.entity_list.addItem(item)

    def get_entity_display_text(self, entity) -> str:
        """Generate display text for an entity"""
        # Character names
        if hasattr(entity, "first_name") and entity.first_name:
            name_parts = [entity.first_name]
            if hasattr(entity, "last_name") and entity.last_name:
                name_parts.append(entity.last_name)
            return " ".join(name_parts)

        # Generic name field
        if hasattr(entity, "name") and entity.name:
            return entity.name

        # Title field
        if hasattr(entity, "title") and entity.title:
            return entity.title

        # Fallback to ID
        return f"ID: {entity.id}"

    def filter_entities(self, search_text: str):
        """Filter entities based on search text"""
        if not search_text:
            self.populate_list(self.entities)
            return

        search_lower = search_text.lower()
        filtered_entities = []

        for entity in self.entities:
            display_text = self.get_entity_display_text(entity).lower()
            if search_lower in display_text:
                filtered_entities.append(entity)

        self.populate_list(filtered_entities)

    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.entity_list.currentItem()
        self.select_button.setEnabled(current_item is not None)

        if current_item:
            self.selected_entity = current_item.data(Qt.ItemDataRole.UserRole)

    def on_entity_double_clicked(self, item: QListWidgetItem):
        """Handle entity double-click"""
        self.selected_entity = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def get_selected_entity(self):
        """Get the selected entity"""
        return self.selected_entity
