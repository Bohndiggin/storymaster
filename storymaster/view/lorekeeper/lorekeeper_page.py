"""New user-friendly Lorekeeper main page"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from storymaster.model.lorekeeper.entity_mappings import (
    get_entity_mapping,
    MAIN_CATEGORIES,
)
from storymaster.view.common.custom_widgets import enable_smart_tab_navigation
from storymaster.view.common.theme import (
    COLORS,
    FONTS,
    get_button_style,
    get_splitter_style,
)
from storymaster.view.lorekeeper.entity_page import EntityDetailPage
from storymaster.view.lorekeeper.lorekeeper_model_adapter import LorekeeperModelAdapter
from storymaster.view.lorekeeper.lorekeeper_navigation import LorekeeperNavigation


class LorekeeperPage(QWidget):
    """Main page for the user-friendly Lorekeeper interface"""

    # Signal emitted when an entity is saved (entity, entity_type)
    entity_saved_signal = Signal(object, str)

    def __init__(self, model, setting_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.model_adapter = LorekeeperModelAdapter(model, setting_id)
        self.current_table_name = ""
        self.current_entity = None
        self.current_entities = []  # Store current entities for filtering
        self.detail_pages = {}  # Cache detail pages by table name
        self.setup_ui()

        # Connect to model if available
        if hasattr(self.model, "entity_changed"):
            self.model.entity_changed.connect(self.on_entity_changed)

    def setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(get_splitter_style())

        # Left panel: Navigation and browser
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(200)  # Minimum width for navigation/browser
        splitter.addWidget(left_panel)

        # Right panel: Entity details
        right_panel = self.create_right_panel()
        right_panel.setMinimumWidth(300)  # Minimum width for detail panel
        splitter.addWidget(right_panel)

        # Set splitter proportions (left panel for navigation/browser, right panel for details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # Set initial sizes (left panel ~300px, right panel gets the rest)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)
        self.setLayout(layout)

        # Set up enhanced tab navigation
        enable_smart_tab_navigation(self)

        # Trigger initial category selection after all UI components are created
        if MAIN_CATEGORIES:
            self.navigation.select_category(MAIN_CATEGORIES[0])

    def create_left_panel(self) -> QWidget:
        """Create the left navigation and browser panel"""
        # Create vertical splitter for the entire left panel
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setHandleWidth(3)
        left_splitter.setStyleSheet(get_splitter_style())

        # Create container for top half (navigation + header/search)
        top_half_container = QWidget()
        top_half_layout = QVBoxLayout()
        top_half_layout.setContentsMargins(2, 2, 2, 2)
        top_half_layout.setSpacing(2)

        # Navigation widget (top of top half)
        self.navigation = LorekeeperNavigation()
        self.navigation.category_changed.connect(self.on_category_changed)
        self.navigation.setMinimumHeight(150)  # Minimum height for navigation
        top_half_layout.addWidget(self.navigation)

        # Browser header and search (bottom of top half)
        self.browser_header = self.create_browser_header()
        self.browser_search = self.create_browser_search()

        top_half_layout.addWidget(self.browser_header)
        top_half_layout.addWidget(self.browser_search)
        top_half_container.setLayout(top_half_layout)

        # Create container for bottom half (entity list)
        bottom_half_container = QWidget()
        bottom_half_layout = QVBoxLayout()
        bottom_half_layout.setContentsMargins(2, 2, 2, 2)
        bottom_half_layout.setSpacing(0)

        # Add entity list to bottom half
        self.entity_list = self.create_entity_list()
        bottom_half_layout.addWidget(self.entity_list)
        bottom_half_container.setLayout(bottom_half_layout)

        # Add both halves to the main splitter
        left_splitter.addWidget(top_half_container)
        left_splitter.addWidget(bottom_half_container)

        # Set proportions: top half and bottom half equal
        left_splitter.setStretchFactor(0, 1)  # Top half (nav + header + search)
        left_splitter.setStretchFactor(1, 1)  # Bottom half (list)
        left_splitter.setSizes([300, 300])  # Equal initial sizes

        return left_splitter

    def create_browser_header(self) -> QWidget:
        """Create the browser header with title and new button"""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.on_new_entity_requested)
        self.new_button.setStyleSheet(get_button_style("primary"))
        header_layout.addWidget(self.new_button)

        header_widget.setLayout(header_layout)
        return header_widget

    def create_browser_search(self) -> QWidget:
        """Create the browser search bar"""
        from storymaster.view.lorekeeper.lorekeeper_navigation import SearchBar

        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.filter_entities)
        return self.search_bar

    def create_entity_list(self) -> QWidget:
        """Create the entity list widget"""
        from storymaster.view.lorekeeper.lorekeeper_navigation import EntityListWidget

        self.entity_list_widget = EntityListWidget()
        self.entity_list_widget.entity_selected.connect(self.on_entity_selected)
        return self.entity_list_widget

    def set_category_display(self, table_name: str):
        """Set the current category display"""
        mapping = get_entity_mapping(table_name)

        if mapping:
            self.title_label.setText(f"{mapping.icon} {mapping.plural_name}")
            self.new_button.setText(f"New {mapping.display_name}")
        else:
            display_name = table_name.replace("_", " ").title()
            self.title_label.setText(display_name)
            self.new_button.setText(f"New {display_name}")

    def set_entities(self, entities: list):
        """Set the list of entities to display"""
        self.current_entities = entities
        self.entity_list_widget.set_entities(entities, self.current_table_name)

    def filter_entities(self, search_text: str):
        """Filter entities based on search text"""
        if not hasattr(self, "current_entities"):
            return

        if not search_text:
            self.entity_list_widget.set_entities(
                self.current_entities, self.current_table_name
            )
            return

        # Simple text search across entity fields
        filtered_entities = []
        search_lower = search_text.lower()

        for entity in self.current_entities:
            # Search in name fields
            if (
                hasattr(entity, "name")
                and entity.name
                and search_lower in entity.name.lower()
            ):
                filtered_entities.append(entity)
                continue

            # Search in character names
            if (
                hasattr(entity, "first_name")
                and entity.first_name
                and search_lower in entity.first_name.lower()
            ):
                filtered_entities.append(entity)
                continue

            if (
                hasattr(entity, "last_name")
                and entity.last_name
                and search_lower in entity.last_name.lower()
            ):
                filtered_entities.append(entity)
                continue

            # Search in title
            if (
                hasattr(entity, "title")
                and entity.title
                and search_lower in entity.title.lower()
            ):
                filtered_entities.append(entity)
                continue

            # Search in description
            if (
                hasattr(entity, "description")
                and entity.description
                and search_lower in entity.description.lower()
            ):
                filtered_entities.append(entity)
                continue

        self.entity_list_widget.set_entities(filtered_entities, self.current_table_name)

    def create_right_panel(self) -> QWidget:
        """Create the right entity details panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 4, 4)

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
        welcome_label = QLabel("Welcome to the Lorekeeper")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        welcome_label.setFont(font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet(f"color: {COLORS['text_accent']}; margin: 32px;")

        description = QLabel(
            "Create and manage the people, places, organizations, and events in your story world.\n\n"
            "• Select a category from the left to get started\n"
            "• Click 'New' to create a new entry\n"
            "• Double-click any item to view and edit details\n"
            "• Use the search bar to quickly find what you're looking for"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: {FONTS['size_large']}; line-height: 1.5;"
        )
        description.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(welcome_label)
        layout.addWidget(description)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def on_category_changed(self, table_name: str):
        """Handle category change"""
        # Auto-save the currently displayed entity before switching categories
        if (
            self.current_entity
            and self.current_table_name
            and self.current_table_name in self.detail_pages
            and self.current_table_name != table_name
        ):
            try:
                self.auto_save_current_entity()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    "Auto-save Warning",
                    f"Could not auto-save previous entity: {str(e)}\n\nPlease save manually if needed.",
                )

        self.current_table_name = table_name
        self.set_category_display(table_name)

        # Load entities for this category
        self.load_entities(table_name)

        # Show welcome page until an entity is selected
        self.detail_stack.setCurrentWidget(self.welcome_page)
        self.current_entity = None

    def on_entity_selected(self, entity):
        """Handle entity selection"""
        # Auto-save the currently displayed entity before switching
        if (
            self.current_entity
            and self.current_table_name in self.detail_pages
            and self.current_entity != entity
        ):
            try:
                self.auto_save_current_entity()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    "Auto-save Warning",
                    f"Could not auto-save previous entity: {str(e)}\n\nPlease save manually if needed.",
                )

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
            self.set_entities(entities)
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
            detail_page.autosave_requested.connect(self.auto_save_current_entity)
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

            # Refresh foreign key dropdowns on all detail pages
            # This ensures that if a new entity was created (like a new background),
            # it will appear in dropdowns on other entity pages (like Actor)
            for detail_page in self.detail_pages.values():
                if hasattr(detail_page, 'refresh_foreign_key_dropdowns'):
                    detail_page.refresh_foreign_key_dropdowns()

            # Emit signal to notify controller that entity was saved
            self.entity_saved_signal.emit(entity, self.current_table_name)

            # Success - no message needed, user can see the updated entity list

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

                # Refresh foreign key dropdowns on all detail pages
                # This ensures that deleted entities are removed from dropdowns
                for detail_page in self.detail_pages.values():
                    if hasattr(detail_page, 'refresh_foreign_key_dropdowns'):
                        detail_page.refresh_foreign_key_dropdowns()

                # Show welcome page
                self.detail_stack.setCurrentWidget(self.welcome_page)
                self.current_entity = None

                # Emit signal to notify controller that entity was deleted
                self.entity_saved_signal.emit(entity, self.current_table_name)

                # Success - no message needed, entity is removed from list

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

    def auto_save_current_entity(self):
        """Auto-save the currently displayed entity"""
        if not self.current_entity or self.current_table_name not in self.detail_pages:
            return

        detail_page = self.detail_pages[self.current_table_name]

        # Get the current data from the form
        all_data = {}
        for section_widget in detail_page.section_widgets.values():
            all_data.update(section_widget.get_field_data())

        # Update entity attributes with form data
        for field_name, value in all_data.items():
            if hasattr(self.current_entity, field_name):
                setattr(self.current_entity, field_name, value)

        # For locations, also save additional details
        if self.current_table_name == "location_" and self.model_adapter:
            self.model_adapter.save_location_details(self.current_entity, all_data)

        # Save the entity to the database
        self.save_entity_to_model(self.current_entity)

        # Refresh the entity list to show updated names/values
        self.load_entities(self.current_table_name)

        # Refresh foreign key dropdowns on all detail pages
        # This ensures that if a new entity was created or updated,
        # it will appear correctly in dropdowns on other entity pages
        for detail_page_instance in self.detail_pages.values():
            if hasattr(detail_page_instance, 'refresh_foreign_key_dropdowns'):
                detail_page_instance.refresh_foreign_key_dropdowns()

        # Emit signal to notify controller that entity was saved
        self.entity_saved_signal.emit(self.current_entity, self.current_table_name)

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

    def navigate_to_entity(self, table_name: str, entity_id: int):
        """
        Navigate to and display a specific entity.

        Args:
            table_name: The database table name (e.g., "actor", "location_", "faction")
            entity_id: The numeric entity ID
        """
        try:
            # Switch to the correct category
            self.on_category_changed(table_name)

            # Load entities for this table
            entities = self.get_entities_from_model(table_name)

            # Find the entity with the matching ID
            target_entity = None
            for entity in entities:
                if hasattr(entity, 'id') and entity.id == entity_id:
                    target_entity = entity
                    break

            if target_entity:
                # Select the entity
                self.on_entity_selected(target_entity)

                # Also select it in the browser if available
                if hasattr(self, 'browser'):
                    self.browser.select_entity_by_id(entity_id)

            else:
                QMessageBox.warning(
                    self,
                    "Entity Not Found",
                    f"Could not find entity with ID {entity_id} in {table_name}"
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Navigation Error",
                f"Failed to navigate to entity: {str(e)}"
            )
