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
    QToolButton,
    QButtonGroup,
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


class CategoryButton(QToolButton):
    """Custom button for entity categories"""

    def __init__(self, table_name: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        mapping = get_entity_mapping(table_name)

        if mapping:
            self.setText(f"{mapping.icon} {mapping.plural_name}")
            self.setToolTip(mapping.description)
        else:
            self.setText(table_name.replace("_", " ").title())

        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setMinimumHeight(40)
        self.setStyleSheet(
            """
            QToolButton {
                text-align: left;
                padding: 8px 16px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
                color: white;
            }
            QToolButton:checked {
                background-color: #0d7d7e;
                border-color: #0d7d7e;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
                border-color: #777;
            }
            QToolButton:checked:hover {
                background-color: #0e8d8e;
            }
        """
        )


class EntityListWidget(QListWidget):
    """Enhanced list widget for displaying entities"""

    entity_selected = pyqtSignal(object)  # entity

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
                color: white;
                alternate-background-color: #323232;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #0d7d7e;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """
        )

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
                    return f"{entity.title} {name}"
                return name

        # Generic name field
        if hasattr(entity, "name") and entity.name:
            return entity.name

        # Title field (for plots, arcs, etc.)
        if hasattr(entity, "title") and entity.title:
            return entity.title

        # Fallback to ID
        return f"ID: {entity.id}"

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
        self.button_group = QButtonGroup()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("World Builder")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #0d7d7e; margin: 16px 0;")
        layout.addWidget(header)

        # Main categories section
        main_section = self.create_category_section("Main Categories", MAIN_CATEGORIES)
        layout.addWidget(main_section)

        # Supporting categories section
        supporting_section = self.create_category_section(
            "Supporting", SUPPORTING_CATEGORIES
        )
        layout.addWidget(supporting_section)

        layout.addStretch()
        self.setLayout(layout)

        # Select first category by default
        if MAIN_CATEGORIES:
            self.select_category(MAIN_CATEGORIES[0])

    def create_category_section(self, title: str, categories: list) -> QWidget:
        """Create a section of category buttons"""
        section = QFrame()
        section.setFrameStyle(QFrame.Shape.StyledPanel)
        section.setStyleSheet(
            """
            QFrame {
                border: 1px solid #555;
                border-radius: 8px;
                background-color: #1e1e1e;
                margin: 4px;
                padding: 8px;
            }
        """
        )

        layout = QVBoxLayout()

        # Section title
        title_label = QLabel(title)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet("color: #ccc; margin-bottom: 8px;")
        layout.addWidget(title_label)

        # Category buttons
        for table_name in categories:
            button = CategoryButton(table_name)
            button.clicked.connect(
                lambda checked, tn=table_name: self.select_category(tn)
            )
            self.category_buttons[table_name] = button
            self.button_group.addButton(button)
            layout.addWidget(button)

        section.setLayout(layout)
        return section

    def select_category(self, table_name: str):
        """Select a category and update the display"""
        if self.current_category == table_name:
            return

        self.current_category = table_name

        # Update button states
        for tn, button in self.category_buttons.items():
            button.setChecked(tn == table_name)

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
        self.new_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0d7d7e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e8d8e;
            }
            QPushButton:pressed {
                background-color: #0c6d6e;
            }
        """
        )
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
