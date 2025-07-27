"""New user-friendly Lorekeeper main page"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QStackedWidget,
    QLabel,
    QMessageBox,
)
from PyQt6.QtGui import QFont

from storymaster.view.lorekeeper.lorekeeper_navigation import (
    LorekeeperNavigation,
    LorekeeperBrowser,
)
from storymaster.view.lorekeeper.entity_page import EntityDetailPage
from storymaster.view.lorekeeper.lorekeeper_model_adapter import LorekeeperModelAdapter
from storymaster.model.lorekeeper.entity_mappings import get_entity_mapping


class NewLorekeeperPage(QWidget):
    """Main page for the new user-friendly Lorekeeper interface"""

    def __init__(self, model, setting_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.model_adapter = LorekeeperModelAdapter(model, setting_id)
        self.current_table_name = ""
        self.current_entity = None
        self.detail_pages = {}  # Cache detail pages by table name
        self.setup_ui()

        # Connect to model if available
        if hasattr(self.model, "entity_changed"):
            self.model.entity_changed.connect(self.on_entity_changed)

    def setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Navigation and browser
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel: Entity details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (navigation smaller, details larger)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def create_left_panel(self) -> QWidget:
        """Create the left navigation and browser panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 4, 8)

        # Navigation
        self.navigation = LorekeeperNavigation()
        self.navigation.category_changed.connect(self.on_category_changed)
        layout.addWidget(self.navigation)

        # Browser
        self.browser = LorekeeperBrowser()
        self.browser.entity_selected.connect(self.on_entity_selected)
        self.browser.new_entity_requested.connect(self.on_new_entity_requested)
        layout.addWidget(self.browser)

        # Set proportions (navigation smaller, browser larger)
        layout.setStretchFactor(self.navigation, 0)
        layout.setStretchFactor(self.browser, 1)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right entity details panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 8, 8, 8)

        # Stacked widget for different entity detail pages
        self.detail_stack = QStackedWidget()

        # Welcome page (shown when no entity is selected)
        self.welcome_page = self.create_welcome_page()
        self.detail_stack.addWidget(self.welcome_page)

        layout.addWidget(self.detail_stack)
        panel.setLayout(layout)
        return panel

    def create_welcome_page(self) -> QWidget:
        """Create the welcome page shown when no entity is selected"""
        page = QWidget()
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel("Welcome to the World Builder")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        welcome_label.setFont(font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: #0d7d7e; margin: 32px;")

        description = QLabel(
            "Create and manage the people, places, organizations, and events in your story world.\n\n"
            "• Select a category from the left to get started\n"
            "• Click 'New' to create a new entry\n"
            "• Double-click any item to view and edit details\n"
            "• Use the search bar to quickly find what you're looking for"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #ccc; font-size: 14px; line-height: 1.5;")
        description.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(welcome_label)
        layout.addWidget(description)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def on_category_changed(self, table_name: str):
        """Handle category change"""
        self.current_table_name = table_name
        self.browser.set_category(table_name)

        # Load entities for this category
        self.load_entities(table_name)

        # Show welcome page until an entity is selected
        self.detail_stack.setCurrentWidget(self.welcome_page)
        self.current_entity = None

    def on_entity_selected(self, entity):
        """Handle entity selection"""
        self.current_entity = entity
        self.show_entity_details(entity)

    def on_new_entity_requested(self):
        """Handle request to create new entity"""
        if not self.current_table_name:
            return

        # Create new entity instance
        new_entity = self.create_new_entity(self.current_table_name)
        if new_entity:
            self.current_entity = new_entity
            self.show_entity_details(new_entity)

    def load_entities(self, table_name: str):
        """Load entities for the given table"""
        try:
            # Get entities from model
            entities = self.get_entities_from_model(table_name)
            self.browser.set_entities(entities)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load {table_name}: {str(e)}")

    def get_entities_from_model(self, table_name: str) -> list:
        """Get entities from the model"""
        return self.model_adapter.get_entities(table_name)

    def create_new_entity(self, table_name: str):
        """Create a new entity instance"""
        return self.model_adapter.create_entity(table_name)

    def show_entity_details(self, entity):
        """Show entity details in the right panel"""
        if not entity or not self.current_table_name:
            return

        # Get or create detail page for this table type
        if self.current_table_name not in self.detail_pages:
            detail_page = EntityDetailPage(self.current_table_name, self.model_adapter)
            detail_page.entity_saved.connect(self.on_entity_saved)
            detail_page.entity_deleted.connect(self.on_entity_deleted)
            self.detail_pages[self.current_table_name] = detail_page
            self.detail_stack.addWidget(detail_page)

        detail_page = self.detail_pages[self.current_table_name]
        detail_page.set_entity(entity)
        self.detail_stack.setCurrentWidget(detail_page)

    def on_entity_saved(self, entity):
        """Handle entity save"""
        try:
            # Save entity through model
            self.save_entity_to_model(entity)

            # Refresh the entity list
            self.load_entities(self.current_table_name)

            # Show success message
            mapping = get_entity_mapping(self.current_table_name)
            entity_type = mapping.display_name if mapping else "Entity"
            QMessageBox.information(
                self, "Success", f"{entity_type} saved successfully!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save entity: {str(e)}")

    def on_entity_deleted(self, entity):
        """Handle entity deletion"""
        # Confirm deletion
        mapping = get_entity_mapping(self.current_table_name)
        entity_type = mapping.display_name if mapping else "entity"

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete this {entity_type}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete entity through model
                self.delete_entity_from_model(entity)

                # Refresh the entity list
                self.load_entities(self.current_table_name)

                # Show welcome page
                self.detail_stack.setCurrentWidget(self.welcome_page)
                self.current_entity = None

                # Show success message
                QMessageBox.information(
                    self, "Success", f"{entity_type.title()} deleted successfully!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete entity: {str(e)}"
                )

    def save_entity_to_model(self, entity):
        """Save entity to model"""
        return self.model_adapter.update_entity(entity)

    def delete_entity_from_model(self, entity):
        """Delete entity from model"""
        return self.model_adapter.delete_entity(entity)

    def on_entity_changed(self, entity):
        """Handle entity change from model"""
        # Update display if this is the currently shown entity
        if (
            self.current_entity
            and hasattr(entity, "id")
            and hasattr(self.current_entity, "id")
        ):
            if entity.id == self.current_entity.id:
                self.current_entity = entity
                if self.current_table_name in self.detail_pages:
                    self.detail_pages[self.current_table_name].set_entity(entity)
