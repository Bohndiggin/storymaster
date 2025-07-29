"""New Character Arc Management Page - Following Lorekeeper Design Pattern"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QStackedWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QPushButton,
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QTreeWidget,
    QTreeWidgetItem,
    QScrollArea,
)
from PyQt6.QtGui import QFont

from storymaster.model.database import schema
from .arc_type_manager_dialog import ArcTypeManagerDialog
from .arc_point_dialog import ArcPointDialog
from .character_arc_dialog import CharacterArcDialog
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_group_box_style,
    get_splitter_style,
    get_list_style,
    get_dialog_style,
    COLORS,
    FONTS,
)


class CharacterArcBrowser(QWidget):
    """Browser for character arcs - similar to Lorekeeper browser"""

    arc_selected = pyqtSignal(object)  # arc entity
    new_arc_requested = pyqtSignal()
    add_arc_type_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_storyline_id = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the browser UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with add button (removed title to save space)
        header_layout = QHBoxLayout()

        header_layout.addStretch()

        self.add_arc_type_button = QPushButton("Add Arc Type")
        self.add_arc_type_button.setStyleSheet(get_button_style())
        self.add_arc_type_button.clicked.connect(self.on_add_arc_type_button_clicked)
        header_layout.addWidget(self.add_arc_type_button)

        self.new_arc_button = QPushButton("New Arc")
        self.new_arc_button.setStyleSheet(get_button_style("primary"))
        self.new_arc_button.clicked.connect(self.new_arc_requested.emit)
        header_layout.addWidget(self.new_arc_button)

        layout.addLayout(header_layout)

        # Arc list
        self.arc_list = QListWidget()
        self.arc_list.setStyleSheet(get_list_style())
        self.arc_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.arc_list)

        self.setLayout(layout)

    def load_arcs(self, model, storyline_id):
        """Load character arcs for the given storyline"""
        self.current_storyline_id = storyline_id
        self.arc_list.clear()

        if not storyline_id:
            return

        try:
            arcs = model.get_character_arcs(storyline_id)

            if not hasattr(arcs, "__iter__"):
                arcs = []

            for arc in arcs:
                item = QListWidgetItem()

                # Get character names for display
                character_names = []
                for arc_to_actor in arc.actors:
                    actor = arc_to_actor.actor
                    name_parts = [actor.first_name, actor.last_name]
                    full_name = " ".join(part for part in name_parts if part)
                    character_names.append(full_name or "Unknown")

                # Create display text
                if character_names:
                    display_text = f"{arc.title} ({', '.join(character_names[:2])}{'...' if len(character_names) > 2 else ''})"
                else:
                    display_text = arc.title

                item.setText(display_text)
                item.setData(Qt.ItemDataRole.UserRole, arc)

                # Add tooltip with arc type and description
                tooltip_parts = [f"Arc Type: {arc.arc_type.name}"]
                if arc.description:
                    tooltip_parts.append(f"Description: {arc.description}")
                if character_names:
                    tooltip_parts.append(f"Characters: {', '.join(character_names)}")
                item.setToolTip("\n".join(tooltip_parts))

                self.arc_list.addItem(item)

        except Exception as e:
            print(f"Error loading arcs: {e}")

    def on_selection_changed(self):
        """Handle arc selection change"""
        current_item = self.arc_list.currentItem()
        if current_item:
            arc = current_item.data(Qt.ItemDataRole.UserRole)
            self.arc_selected.emit(arc)

    def on_add_arc_type_button_clicked(self):
        """Handle add arc type button click"""
        self.add_arc_type_requested.emit()


class CharacterArcDetailPage(QWidget):
    """Detail page for viewing/editing character arcs - similar to Lorekeeper entity page"""

    arc_saved = pyqtSignal(object)  # arc
    arc_deleted = pyqtSignal(object)  # arc

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_arc = None
        self.current_storyline_id = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the detail page UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(get_splitter_style())

        # Left panel: Arc details
        left_panel = self.create_details_panel()
        splitter.addWidget(left_panel)

        # Right panel: Arc points
        right_panel = self.create_arc_points_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Details panel
        splitter.setStretchFactor(1, 1)  # Arc points panel

        layout.addWidget(splitter)
        self.setLayout(layout)

    def create_details_panel(self):
        """Create the arc details panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 8, 8, 8)

        # Header with arc name and actions
        header_layout = QHBoxLayout()

        self.title_label = QLabel()
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.manage_types_button = QPushButton("Manage Arc Types")

        # Apply button styling
        self.edit_button.setStyleSheet(get_button_style())
        self.delete_button.setStyleSheet(get_button_style("danger"))
        self.manage_types_button.setStyleSheet(get_button_style())

        self.edit_button.clicked.connect(self.edit_arc)
        self.delete_button.clicked.connect(self.delete_arc)
        self.manage_types_button.clicked.connect(self.manage_arc_types)

        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        header_layout.addWidget(self.manage_types_button)

        layout.addLayout(header_layout)

        # Scrollable area for arc details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"QScrollArea {{ background-color: {COLORS['bg_main']}; border: none; }}")

        details_widget = QWidget()
        details_widget.setStyleSheet(f"QWidget {{ background-color: {COLORS['bg_main']}; }}")
        details_layout = QVBoxLayout()

        # Arc information section
        info_group = QGroupBox("Arc Information")
        info_group.setStyleSheet(get_group_box_style())
        info_layout = QFormLayout()

        self.arc_type_edit = QLineEdit()
        self.arc_type_edit.setReadOnly(True)
        self.arc_type_edit.setStyleSheet(get_input_style())
        self.characters_edit = QLineEdit()
        self.characters_edit.setReadOnly(True)
        self.characters_edit.setStyleSheet(get_input_style())
        self.description_edit = QTextEdit()
        self.description_edit.setReadOnly(True)
        self.description_edit.setStyleSheet(get_input_style())
        self.description_edit.setMaximumHeight(100)

        info_layout.addRow("Arc Type:", self.arc_type_edit)
        info_layout.addRow("Characters:", self.characters_edit)
        info_layout.addRow("Description:", self.description_edit)

        info_group.setLayout(info_layout)
        details_layout.addWidget(info_group)

        details_layout.addStretch()
        details_widget.setLayout(details_layout)
        scroll_area.setWidget(details_widget)

        layout.addWidget(scroll_area)
        panel.setLayout(layout)
        return panel

    def create_arc_points_panel(self):
        """Create the arc points panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 4, 8)

        # Header
        header_layout = QHBoxLayout()

        header = QLabel("Arc Points")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        header.setStyleSheet(f"color: {COLORS['text_accent']};")
        header_layout.addWidget(header)

        header_layout.addStretch()

        self.new_point_button = QPushButton("New Point")
        self.new_point_button.setStyleSheet(get_button_style("primary"))
        self.edit_point_button = QPushButton("Edit Point")
        self.edit_point_button.setStyleSheet(get_button_style())
        self.delete_point_button = QPushButton("Delete Point")
        self.delete_point_button.setStyleSheet(get_button_style("danger"))

        self.new_point_button.clicked.connect(self.new_arc_point)
        self.edit_point_button.clicked.connect(self.edit_arc_point)
        self.delete_point_button.clicked.connect(self.delete_arc_point)

        # Initially disable point buttons
        self.edit_point_button.setEnabled(False)
        self.delete_point_button.setEnabled(False)

        header_layout.addWidget(self.new_point_button)
        header_layout.addWidget(self.edit_point_button)
        header_layout.addWidget(self.delete_point_button)

        layout.addLayout(header_layout)

        # Arc points tree
        self.arc_points_tree = QTreeWidget()
        self.arc_points_tree.setHeaderLabels(
            ["Order", "Title", "Story Node", "Emotional State"]
        )
        self.arc_points_tree.setRootIsDecorated(False)
        self.arc_points_tree.setAlternatingRowColors(True)
        self.arc_points_tree.setSortingEnabled(True)
        self.arc_points_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.arc_points_tree.itemSelectionChanged.connect(
            self.on_arc_point_selection_changed
        )

        # Apply theming to tree widget
        tree_style = f"""
            QTreeWidget {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_main']};
                gridline-color: {COLORS['border_main']};
                selection-background-color: {COLORS['primary']};
                alternate-background-color: {COLORS['bg_secondary']};
            }}
            QTreeWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {COLORS['border_main']};
            }}
            QTreeWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                padding: 6px;
                border: 1px solid {COLORS['border_main']};
                font-weight: bold;
            }}
        """
        self.arc_points_tree.setStyleSheet(tree_style)

        layout.addWidget(self.arc_points_tree)
        panel.setLayout(layout)
        return panel

    def set_arc(self, arc, storyline_id):
        """Set the arc to display/edit"""
        self.current_arc = arc
        self.current_storyline_id = storyline_id
        self.update_display()

    def update_display(self):
        """Update the display with current arc data"""
        if not self.current_arc:
            return

        # Update title
        self.title_label.setText(self.current_arc.title)

        # Update arc details
        self.arc_type_edit.setText(self.current_arc.arc_type.name)

        # Load character names
        character_names = []
        for arc_to_actor in self.current_arc.actors:
            actor = arc_to_actor.actor
            name_parts = [actor.first_name, actor.last_name]
            full_name = " ".join(part for part in name_parts if part)
            character_names.append(full_name or "Unknown")
        self.characters_edit.setText(", ".join(character_names))

        self.description_edit.setPlainText(self.current_arc.description or "")

        # Load arc points
        self.load_arc_points()

    def load_arc_points(self):
        """Load and display arc points"""
        self.arc_points_tree.clear()

        if not self.current_arc:
            return

        try:
            arc_points = self.model.get_arc_points(self.current_arc.id)

            for point in arc_points:
                item = QTreeWidgetItem()
                item.setText(0, str(point.order_index))
                item.setText(1, point.title)
                if point.node:
                    item.setText(2, f"{point.node.name} ({point.node.node_type.value})")
                else:
                    item.setText(2, "No Node")
                item.setText(3, point.emotional_state or "")
                item.setData(0, Qt.ItemDataRole.UserRole, point.id)

                self.arc_points_tree.addTopLevelItem(item)

        except Exception as e:
            print(f"Error loading arc points: {e}")

    def on_arc_point_selection_changed(self):
        """Handle arc point selection change"""
        selected_items = self.arc_points_tree.selectedItems()
        has_selection = len(selected_items) > 0

        self.edit_point_button.setEnabled(has_selection)
        self.delete_point_button.setEnabled(has_selection)

    def edit_arc(self):
        """Edit the current arc"""
        if not self.current_arc or not self.current_storyline_id:
            return

        try:
            # Get current setting ID
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(
                    self,
                    "No Settings",
                    "No settings found. Please create a setting first.",
                )
                return

            setting_id = settings[0].id

            dialog = CharacterArcDialog(
                self.model,
                self.current_storyline_id,
                setting_id,
                self.current_arc,
                parent=self,
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh display
                refreshed_arc = self.model.get_character_arc(self.current_arc.id)
                self.current_arc = refreshed_arc
                self.update_display()
                self.arc_saved.emit(self.current_arc)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit arc: {e}")

    def delete_arc(self):
        """Delete the current arc"""
        if not self.current_arc:
            return

        reply = QMessageBox.question(
            self,
            "Delete Arc",
            f"Are you sure you want to delete the arc '{self.current_arc.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_character_arc(self.current_arc.id)
                self.arc_deleted.emit(self.current_arc)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete arc: {e}")

    def manage_arc_types(self):
        """Open arc type manager"""
        try:
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(
                    self,
                    "No Settings",
                    "No settings found. Please create a setting first.",
                )
                return

            setting_id = settings[0].id

            dialog = ArcTypeManagerDialog(self.model, setting_id, self)
            dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open arc type manager: {e}")

    def new_arc_point(self):
        """Create a new arc point"""
        if not self.current_arc or not self.current_storyline_id:
            return

        dialog = ArcPointDialog(
            self.model, self.current_arc.id, self.current_storyline_id, parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_arc_points()

    def edit_arc_point(self):
        """Edit the selected arc point"""
        selected_items = self.arc_points_tree.selectedItems()
        if not selected_items or not self.current_storyline_id:
            return

        try:
            arc_point_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            arc_points = self.model.get_arc_points(self.current_arc.id)
            arc_point = next((p for p in arc_points if p.id == arc_point_id), None)

            if not arc_point:
                QMessageBox.warning(self, "Error", "Arc point not found.")
                return

            dialog = ArcPointDialog(
                self.model,
                self.current_arc.id,
                self.current_storyline_id,
                arc_point,
                parent=self,
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_arc_points()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit arc point: {e}")

    def delete_arc_point(self):
        """Delete the selected arc point"""
        selected_items = self.arc_points_tree.selectedItems()
        if not selected_items:
            return

        arc_point_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Delete Arc Point",
            "Are you sure you want to delete this arc point?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_arc_point(arc_point_id)
                self.load_arc_points()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete arc point: {e}")


class WelcomePage(QWidget):
    """Welcome page shown when no arc is selected"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the welcome page UI"""
        layout = QVBoxLayout()

        # Center the content
        layout.addStretch()

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Welcome message
        welcome_label = QLabel("Character Arc Management")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        welcome_label.setFont(font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(welcome_label)

        description_label = QLabel(
            "Select a character arc from the list to view and edit its details, or create a new arc to get started."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; margin: 20px;"
        )
        center_layout.addWidget(description_label)

        layout.addLayout(center_layout)
        layout.addStretch()

        self.setLayout(layout)


class NewCharacterArcsPage(QWidget):
    """New Character Arc Management Page - Following Lorekeeper Design Pattern"""

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_storyline_id = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(get_splitter_style())

        # Left panel: Arc browser
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel: Arc details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (browser smaller, details larger)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def create_left_panel(self):
        """Create the left browser panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 4, 8)

        # Arc browser
        self.browser = CharacterArcBrowser()
        self.browser.arc_selected.connect(self.on_arc_selected)
        self.browser.new_arc_requested.connect(self.on_new_arc_requested)
        self.browser.add_arc_type_requested.connect(self.on_add_arc_type_requested)
        layout.addWidget(self.browser)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self):
        """Create the right detail panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 8, 8, 8)

        # Stacked widget for welcome page and detail page
        self.detail_stack = QStackedWidget()

        # Welcome page
        self.welcome_page = WelcomePage()
        self.detail_stack.addWidget(self.welcome_page)

        # Detail page
        self.detail_page = CharacterArcDetailPage(self.model)
        self.detail_page.arc_saved.connect(self.on_arc_saved)
        self.detail_page.arc_deleted.connect(self.on_arc_deleted)
        self.detail_stack.addWidget(self.detail_page)

        layout.addWidget(self.detail_stack)
        panel.setLayout(layout)
        return panel

    def refresh_arcs(self, storyline_id):
        """Refresh the arc list for the given storyline"""
        self.current_storyline_id = storyline_id
        self.browser.load_arcs(self.model, storyline_id)

        # Show welcome page when refreshing
        self.detail_stack.setCurrentWidget(self.welcome_page)

    def on_arc_selected(self, arc):
        """Handle arc selection"""
        self.detail_page.set_arc(arc, self.current_storyline_id)
        self.detail_stack.setCurrentWidget(self.detail_page)

    def on_new_arc_requested(self):
        """Handle new arc request"""
        if not self.current_storyline_id:
            QMessageBox.warning(
                self, "No Storyline", "Please select a storyline first."
            )
            return

        try:
            # Get current setting ID
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(
                    self,
                    "No Settings",
                    "No settings found. Please create a setting first.",
                )
                return

            setting_id = settings[0].id

            dialog = CharacterArcDialog(
                self.model, self.current_storyline_id, setting_id, parent=self
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_arcs(self.current_storyline_id)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create character arc: {e}")

    def on_arc_saved(self, arc):
        """Handle arc save"""
        # Refresh the browser to show updated arc
        self.refresh_arcs(self.current_storyline_id)

    def on_arc_deleted(self, arc):
        """Handle arc deletion"""
        # Refresh the browser and show welcome page
        self.refresh_arcs(self.current_storyline_id)
        self.detail_stack.setCurrentWidget(self.welcome_page)

    def on_add_arc_type_requested(self):
        """Handle add arc type request"""
        try:
            # Get current setting ID
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(
                    self,
                    "No Settings",
                    "No settings found. Please create a setting first.",
                )
                return

            setting_id = settings[0].id

            dialog = ArcTypeManagerDialog(self.model, setting_id, self)
            dialog.exec()
            # Always refresh arcs after closing the dialog in case arc types were modified
            self.refresh_arcs(self.current_storyline_id)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open arc type manager: {e}")
