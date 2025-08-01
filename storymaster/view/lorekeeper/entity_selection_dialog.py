"""Entity selection dialog for adding relationships"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from storymaster.model.lorekeeper.entity_mappings import get_entity_mapping
from storymaster.view.common.theme import (
    get_button_style,
    get_dialog_style,
    get_input_style,
    get_label_style,
    get_list_style,
)


class EntitySelectionDialog(QDialog):
    """Dialog for selecting entities to add to relationships"""

    def __init__(
        self, relationship_type: str, model_adapter, current_entity=None, parent=None
    ):
        super().__init__(parent)
        self.relationship_type = relationship_type
        self.model_adapter = model_adapter
        self.current_entity = current_entity
        self.selected_entity = None
        self.entities = []
        self.setup_ui()
        self.load_entities()

    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle(f"Add {self.relationship_type.replace('_', ' ').title()}")
        self.setModal(True)
        self.resize(400, 500)

        # Apply comprehensive theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
            + get_input_style()
        )

        layout = QVBoxLayout()

        # Header
        header = QLabel(
            f"Select an entity to add to {self.relationship_type.replace('_', ' ')}"
        )
        header.setStyleSheet(get_label_style("header"))
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
        """Get the target entity types for this relationship based on current entity"""
        if not self.current_entity:
            # Fallback to old static mapping if no current entity
            return self._get_static_target_tables()

        current_entity_type = self.current_entity.__class__.__name__

        # Dynamic mapping based on current entity type and relationship
        if self.relationship_type == "actor_a_on_b_relations":
            return ["actor"]  # Always show other actors
        elif self.relationship_type == "faction_members":
            if current_entity_type == "Actor":
                return ["faction"]  # Character joining organizations
            elif current_entity_type == "Faction":
                return ["actor"]  # Organization gaining members
        elif self.relationship_type == "residents":
            if current_entity_type == "Actor":
                return ["location_"]  # Character living in places
            elif current_entity_type == "Location":
                return ["actor"]  # Location gaining residents
        elif self.relationship_type == "object_to_owner":
            if current_entity_type == "Actor":
                return ["object_"]  # Character owning objects
            elif current_entity_type == "Object_":
                return ["actor"]  # Object being owned by characters
        elif self.relationship_type == "location_to_faction":
            if current_entity_type == "Location":
                return ["faction"]  # Location controlled by factions
            elif current_entity_type == "Faction":
                return ["location_"]  # Faction controlling locations
        elif self.relationship_type == "actor_to_skills":
            if current_entity_type == "Actor":
                return ["skills"]  # Character learning skills
            elif current_entity_type == "Skills":
                return ["actor"]  # Skill known by characters
        elif self.relationship_type == "actor_to_race":
            if current_entity_type == "Actor":
                return ["race"]  # Character having heritage
            elif current_entity_type == "Race":
                return ["actor"]  # Heritage belonging to characters
        elif self.relationship_type == "actor_to_class":
            if current_entity_type == "Actor":
                return ["class"]  # Character having professions
            elif current_entity_type == "Class_":
                return ["actor"]  # Profession practiced by characters
        elif self.relationship_type == "actor_to_stat":
            if current_entity_type == "Actor":
                return ["stat"]  # Character having stats
            elif current_entity_type == "Stat":
                return ["actor"]  # Stat belonging to characters
        elif self.relationship_type == "history_actor":
            if current_entity_type == "Actor":
                return ["history"]  # Character involved in events
            elif current_entity_type == "History":
                return ["actor"]  # Event involving characters
        elif self.relationship_type == "history_location":
            if current_entity_type == "Location":
                return ["history"]  # Location involved in events
            elif current_entity_type == "History":
                return ["location_"]  # Event involving locations
        elif self.relationship_type == "history_faction":
            if current_entity_type == "Faction":
                return ["history"]  # Faction involved in events
            elif current_entity_type == "History":
                return ["faction"]  # Event involving factions
        elif self.relationship_type == "history_object":
            if current_entity_type == "Object_":
                return ["history"]  # Object involved in events
            elif current_entity_type == "History":
                return ["object_"]  # Event involving objects
        elif self.relationship_type == "history_world_data":
            if current_entity_type == "WorldData":
                return ["history"]  # Lore connected to events
            elif current_entity_type == "History":
                return ["world_data"]  # Event connected to lore
        elif self.relationship_type == "location_a_on_b_relations":
            return ["location_"]  # Locations relating to other locations
        elif self.relationship_type == "location_geographic_relations":
            return ["location_"]  # Geographic connections between locations
        elif self.relationship_type == "location_political_relations":
            return ["location_"]  # Political relationships between locations
        elif self.relationship_type == "location_economic_relations":
            return ["location_"]  # Economic relationships between locations
        elif self.relationship_type == "location_hierarchy":
            return ["location_"]  # Hierarchical relationships between locations

        # Fallback to static mapping
        return self._get_static_target_tables()

    def _get_static_target_tables(self) -> list:
        """Static fallback mapping (old behavior)"""
        relationship_mappings = {
            "actor_a_on_b_relations": ["actor"],
            "faction_members": ["faction"],
            "residents": ["location_"],
            "actor_to_skills": ["skills"],
            "actor_to_race": ["race"],
            "actor_to_class": ["class"],
            "actor_to_stat": ["stat"],
            "arc_to_actor": ["actor"],
            "faction_a_on_b_relations": ["faction"],
            "location_to_faction": ["faction"],
            "location_dungeon": ["location_"],
            "location_city": ["location_"],
            "location_city_districts": ["location_"],
            "location_flora_fauna": ["location_"],
            "object_to_owner": ["object_"],
            "history_actor": ["history"],
            "history_location": ["history"],
            "history_faction": ["history"],
            "history_object": ["history"],
            "history_world_data": ["history"],
            "location_a_on_b_relations": ["location_"],
            "location_geographic_relations": ["location_"],
            "location_political_relations": ["location_"],
            "location_economic_relations": ["location_"],
            "location_hierarchy": ["location_"],
        }

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
