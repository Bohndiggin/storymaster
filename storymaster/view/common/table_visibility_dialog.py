"""
Dialog for managing which tables are visible in Lorekeeper
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QGroupBox,
    QCheckBox,
)

from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_list_style,
    get_checkbox_style,
    COLORS,
)


class TableVisibilityDialog(QDialog):
    """Dialog for selecting which tables are visible in Lorekeeper"""

    def __init__(self, model, controller, parent=None):
        super().__init__(parent)
        self.model = model
        self.controller = controller
        self.visible_tables = set()

        self.setWindowTitle("Configure Table Visibility")
        self.setModal(True)
        self.resize(500, 600)

        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
            + get_checkbox_style()
        )

        self.setup_ui()
        self.load_tables()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Title and description
        title_label = QLabel("Configure Lorekeeper Table Visibility")
        title_label.setStyleSheet(get_label_style("header"))
        layout.addWidget(title_label)

        desc_label = QLabel(
            "Select which tables should be visible in the Lorekeeper database view:"
        )
        desc_label.setStyleSheet(get_label_style("muted"))
        layout.addWidget(desc_label)

        # Table list group
        tables_group = QGroupBox("Available Tables")
        tables_layout = QVBoxLayout()

        # Control buttons
        control_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_tables)
        control_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_tables)
        control_layout.addWidget(self.deselect_all_btn)

        control_layout.addStretch()
        tables_layout.addLayout(control_layout)

        # Tables list with checkboxes
        self.tables_list = QListWidget()
        self.tables_list.setToolTip(
            "Check tables to show them in Lorekeeper, uncheck to hide them"
        )
        tables_layout.addWidget(self.tables_list)

        tables_group.setLayout(tables_layout)
        layout.addWidget(tables_group)

        # Category filters info
        info_label = QLabel(
            "ℹ️ System tables and junction tables are automatically hidden and cannot be shown."
        )
        info_label.setStyleSheet(
            "color: #a0a0a0; font-style: italic; margin-top: 10px;"
        )
        layout.addWidget(info_label)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_btn.setToolTip("Show all available tables")
        dialog_buttons.addWidget(reset_btn)

        dialog_buttons.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_buttons.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        apply_btn.setStyleSheet(
            "background-color: #5c4a8e; color: white; font-weight: bold;"
        )
        dialog_buttons.addWidget(apply_btn)

        layout.addLayout(dialog_buttons)

        self.setLayout(layout)

    def load_tables(self):
        """Load all available tables and their current visibility state"""
        try:
            # Get all tables that can be shown (already filtered by model)
            all_tables = self.model.get_all_table_names()

            # Get currently visible tables from controller
            current_visible = self.controller.get_visible_tables()
            if current_visible is None:
                # Default: show all available tables
                current_visible = set(all_tables)

            self.visible_tables = set(current_visible)

            # Populate the list
            self.tables_list.clear()

            for table_name in sorted(all_tables):
                item = QListWidgetItem()

                # Create checkbox widget
                checkbox = QCheckBox(self.format_table_name(table_name))
                checkbox.setChecked(table_name in self.visible_tables)
                checkbox.stateChanged.connect(
                    lambda state, table=table_name: self.on_table_toggled(table, state)
                )

                # Add tooltip with description
                checkbox.setToolTip(self.get_table_description(table_name))

                # Add to list
                item.setSizeHint(checkbox.sizeHint())
                self.tables_list.addItem(item)
                self.tables_list.setItemWidget(item, checkbox)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load tables: {e}")

    def format_table_name(self, table_name: str) -> str:
        """Format table name for display (convert snake_case to Title Case)"""
        return table_name.replace("_", " ").title()

    def get_table_description(self, table_name: str) -> str:
        """Get a description for the table"""
        descriptions = {
            "actor": "Characters, NPCs, and other entities in your world",
            "faction": "Organizations, groups, and political entities",
            "location": "Places, regions, and geographical areas",
            "object": "Items, artifacts, and equipment",
            "world_data": "General world-building information and lore",
            "race": "Character races and species",
            "class": "Character classes and professions",
            "background": "Character backgrounds and origins",
            "skills": "Abilities and skills available to characters",
            "actor_to_skills": "Skills assigned to specific characters",
            "history": "Historical events and timeline entries",
            "arc_type": "Types of character development arcs",
        }

        return descriptions.get(table_name, f"Database table: {table_name}")

    def on_table_toggled(self, table_name: str, state: int):
        """Handle when a table checkbox is toggled"""
        if state == Qt.CheckState.Checked.value:
            self.visible_tables.add(table_name)
        else:
            self.visible_tables.discard(table_name)

    def select_all_tables(self):
        """Select all available tables"""
        for i in range(self.tables_list.count()):
            item = self.tables_list.item(i)
            checkbox = self.tables_list.itemWidget(item)
            checkbox.setChecked(True)

    def deselect_all_tables(self):
        """Deselect all tables"""
        for i in range(self.tables_list.count()):
            item = self.tables_list.item(i)
            checkbox = self.tables_list.itemWidget(item)
            checkbox.setChecked(False)

    def reset_to_defaults(self):
        """Reset to default visibility (all tables visible)"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "This will show all available tables. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.select_all_tables()

    def apply_changes(self):
        """Apply the visibility changes"""
        if not self.visible_tables:
            QMessageBox.warning(
                self,
                "No Tables Selected",
                "You must select at least one table to display in Lorekeeper.",
            )
            return

        try:
            # Apply changes via controller
            self.controller.set_visible_tables(self.visible_tables)

            # Show success message
            # User can see the changes in the UI, no need for popup
            pass

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to apply table visibility settings: {e}"
            )

    def get_visible_tables(self) -> set[str]:
        """Get the set of currently selected visible tables"""
        return self.visible_tables.copy()
