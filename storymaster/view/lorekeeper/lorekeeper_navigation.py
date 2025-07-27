"""Navigation interface for user-friendly Lorekeeper"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QFrame,
    QSplitter,
    QStackedWidget,
)
from PyQt6.QtGui import QFont, QIcon

from storymaster.model.lorekeeper.entity_mappings import (
    ENTITY_MAPPINGS,
    MAIN_CATEGORIES,
    SUPPORTING_CATEGORIES,
    get_entity_mapping,
    get_entity_icon,
    get_plural_name,
)
from storymaster.view.common.theme import (
    COLORS, 
    DIMENSIONS, 
    FONTS,
    get_list_style,
    get_button_style,
    get_splitter_style
)



class EntityListWidget(QListWidget):
    """Enhanced list widget for displaying entities"""

    entity_selected = pyqtSignal(object)  # entity

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.setStyleSheet(get_list_style())

    def set_entities(self, entities: list, table_name: str):
        """Set the list of entities to display"""
        self.clear()
        mapping = get_entity_mapping(table_name)

        for entity in entities:
            # Create display text
            display_text = self.get_entity_display_text(entity, table_name)

            # Create item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, entity)

            # Add icon if available
            if mapping:
                item.setText(f"{mapping.icon} {display_text}")

            self.addItem(item)

    def get_entity_display_text(self, entity, table_name: str) -> str:
        """Generate display text for an entity"""
        # Character names
        if table_name == "actor":
            name_parts = []
            if hasattr(entity, "first_name") and entity.first_name:
                name_parts.append(entity.first_name)
            if hasattr(entity, "last_name") and entity.last_name:
                name_parts.append(entity.last_name)
            if name_parts:
                name = " ".join(name_parts)
                if hasattr(entity, "title") and entity.title:
                    full_name = f"{entity.title} {name}"
                    return self.truncate_text(full_name, 40)
                return self.truncate_text(name, 40)

        # Generic name field
        if hasattr(entity, "name") and entity.name:
            return self.truncate_text(entity.name, 40)

        # Title field (for plots, arcs, etc.)
        if hasattr(entity, "title") and entity.title:
            return self.truncate_text(entity.title, 40)

        # Fallback to ID
        return f"ID: {entity.id}"

    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text if it's too long"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double-click"""
        entity = item.data(Qt.ItemDataRole.UserRole)
        if entity:
            self.entity_selected.emit(entity)


class SearchBar(QWidget):
    """Search and filter bar"""

    search_changed = pyqtSignal(str)  # search_text
    filter_changed = pyqtSignal(str)  # filter_value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        self.search_field.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_field)

        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All", "")
        self.filter_combo.currentTextChanged.connect(self.filter_changed.emit)
        layout.addWidget(self.filter_combo)

        self.setLayout(layout)

    def set_filter_options(self, options: list):
        """Set the available filter options"""
        self.filter_combo.clear()
        self.filter_combo.addItem("All", "")
        for option in options:
            self.filter_combo.addItem(option, option)


class LorekeeperNavigation(QWidget):
    """Main navigation widget for Lorekeeper"""

    category_changed = pyqtSignal(str)  # table_name
    entity_selected = pyqtSignal(str, object)  # table_name, entity
    new_entity_requested = pyqtSignal(str)  # table_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.category_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)

        # Header
        header = QLabel("Lorekeeper")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {COLORS['text_accent']}; margin: {DIMENSIONS['margin_medium']} 0;")
        layout.addWidget(header)

        # Create vertical splitter for the two category sections
        categories_splitter = QSplitter(Qt.Orientation.Vertical)
        categories_splitter.setHandleWidth(2)
        categories_splitter.setStyleSheet(get_splitter_style())

        # Main categories section
        main_section = self.create_category_section("Main Categories", MAIN_CATEGORIES)
        main_section.setMinimumHeight(80)  # Minimum height for main categories
        categories_splitter.addWidget(main_section)

        # Supporting categories section
        supporting_section = self.create_category_section(
            "Supporting", SUPPORTING_CATEGORIES
        )
        supporting_section.setMinimumHeight(80)  # Minimum height for supporting categories
        categories_splitter.addWidget(supporting_section)

        # Set initial sizes for the category sections
        categories_splitter.setSizes([120, 100])  # Main gets slightly more space initially
        
        layout.addWidget(categories_splitter)
        self.setLayout(layout)

        # Select first category by default
        if MAIN_CATEGORIES:
            self.select_category(MAIN_CATEGORIES[0])

    def create_category_section(self, title: str, categories: list) -> QWidget:
        """Create a section of category list"""
        section = QFrame()
        section.setFrameStyle(QFrame.Shape.StyledPanel)
        section.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border_main']};
                border-radius: {DIMENSIONS['border_radius']};
                background-color: {COLORS['bg_main']};
                margin: {DIMENSIONS['margin_small']};
                padding: {DIMENSIONS['padding_small']};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(2, 2, 2, 2)

        # Section title
        title_label = QLabel(title)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; margin-bottom: {DIMENSIONS['margin_small']};")
        layout.addWidget(title_label)

        # Category list
        category_list = QListWidget()
        # Remove fixed height constraints to allow dynamic resizing
        category_list.setMinimumHeight(60)  # Minimum to show at least 2-3 items
        category_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                font-size: {FONTS['size_small']};
            }}
            QListWidget::item {{
                padding: {DIMENSIONS['margin_small']} {DIMENSIONS['padding_medium']};
                border: none;
                border-radius: {DIMENSIONS['border_radius_small']};
                margin: 0px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
        """)
        
        for table_name in categories:
            mapping = get_entity_mapping(table_name)
            if mapping:
                item_text = f"{mapping.icon} {mapping.plural_name}"
            else:
                item_text = table_name.replace("_", " ").title()
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, table_name)
            category_list.addItem(item)
        
        category_list.itemClicked.connect(self.on_category_item_clicked)
        layout.addWidget(category_list)
        
        # Set stretch factors: title doesn't stretch (0), list stretches (1)
        layout.setStretchFactor(title_label, 0)
        layout.setStretchFactor(category_list, 1)
        
        # Store reference for selection updates
        setattr(section, 'category_list', category_list)
        self.category_buttons[title] = category_list

        section.setLayout(layout)
        return section

    def on_category_item_clicked(self, item: QListWidgetItem):
        """Handle category item click"""
        table_name = item.data(Qt.ItemDataRole.UserRole)
        if table_name:
            self.select_category(table_name)

    def select_category(self, table_name: str):
        """Select a category and update the display"""
        if self.current_category == table_name:
            return

        self.current_category = table_name

        # Update list selections
        for section_title, list_widget in self.category_buttons.items():
            if isinstance(list_widget, QListWidget):
                # Clear previous selection
                list_widget.clearSelection()
                
                # Find and select the matching item
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == table_name:
                        item.setSelected(True)
                        break

        self.category_changed.emit(table_name)


class LorekeeperBrowser(QWidget):
    """Entity browser with list and search"""

    entity_selected = pyqtSignal(object)  # entity
    new_entity_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_entities = []
        self.current_table_name = ""
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with title and new button
        header_layout = QHBoxLayout()

        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.new_entity_requested.emit)
        self.new_button.setStyleSheet(get_button_style('primary'))
        header_layout.addWidget(self.new_button)

        layout.addLayout(header_layout)

        # Search bar
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.filter_entities)
        layout.addWidget(self.search_bar)

        # Entity list
        self.entity_list = EntityListWidget()
        self.entity_list.entity_selected.connect(self.entity_selected.emit)
        layout.addWidget(self.entity_list)

        self.setLayout(layout)

    def set_category(self, table_name: str):
        """Set the current category"""
        self.current_table_name = table_name
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
        self.entity_list.set_entities(entities, self.current_table_name)

    def filter_entities(self, search_text: str):
        """Filter entities based on search text"""
        if not search_text:
            self.entity_list.set_entities(
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

        self.entity_list.set_entities(filtered_entities, self.current_table_name)
