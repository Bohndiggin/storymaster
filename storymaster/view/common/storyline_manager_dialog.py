"""
Storyline Manager Dialog - Allows creating, editing, switching, and deleting storylines.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
)
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_list_style,
    get_dialog_style,
)


class StorylineManagerDialog(QDialog):
    """Dialog for managing storylines."""

    def __init__(self, model, current_storyline_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_storyline_id = current_storyline_id
        self.selected_storyline_id = None
        self.action = None

        self.setWindowTitle("Manage Storylines")
        self.setModal(True)
        self.resize(600, 500)
        self.setStyleSheet(get_dialog_style())
        self.setup_ui()
        self.populate_storylines()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Storylines list
        list_label = QLabel("Available Storylines:")
        layout.addWidget(list_label)

        self.storyline_list = QListWidget()
        self.storyline_list.setStyleSheet(get_list_style())
        self.storyline_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.storyline_list)

        # Edit form section
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(get_input_style())
        self.name_input.setPlaceholderText("Storyline name")
        form_layout.addRow("Name:", self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setStyleSheet(get_input_style())
        self.description_input.setPlaceholderText("Storyline description")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        # Setting selector for new/edit storylines
        self.setting_combo = QComboBox()
        self.setting_combo.setStyleSheet(get_input_style())
        self._populate_settings()
        form_layout.addRow("Setting:", self.setting_combo)

        layout.addLayout(form_layout)

        # Action buttons row 1 - Edit/Create
        edit_button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet(get_button_style("primary"))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.on_save_storyline)

        self.create_btn = QPushButton("Create New Storyline")
        self.create_btn.setStyleSheet(get_button_style("primary"))
        self.create_btn.clicked.connect(self.on_create_storyline)

        edit_button_layout.addWidget(self.save_btn)
        edit_button_layout.addWidget(self.create_btn)
        edit_button_layout.addStretch()
        layout.addLayout(edit_button_layout)

        # Action buttons row 2 - Switch/Delete/Cancel
        button_layout = QHBoxLayout()

        self.switch_btn = QPushButton("Switch to Storyline")
        self.switch_btn.setStyleSheet(get_button_style("primary"))
        self.switch_btn.setEnabled(False)
        self.switch_btn.clicked.connect(self.on_switch_storyline)

        self.delete_btn = QPushButton("Delete Storyline")
        self.delete_btn.setStyleSheet(get_button_style("danger"))
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_storyline)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setStyleSheet(get_button_style())
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.switch_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _populate_settings(self):
        """Populate the settings dropdown."""
        try:
            settings = self.model.get_all_settings()

            # Add "No Setting" option
            self.setting_combo.addItem("-- No Setting --", None)

            for setting in settings:
                display_name = setting.name if setting.name else f"Setting {setting.id}"
                self.setting_combo.addItem(display_name, setting.id)
        except Exception as e:
            print(f"Error populating settings: {e}")

    def populate_storylines(self):
        """Load all storylines into the list."""
        self.storyline_list.clear()
        storylines = self.model.get_all_storylines()

        for storyline in storylines:
            display_name = storyline.name if storyline.name else f"Storyline {storyline.id}"
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, storyline.id)

            if storyline.id == self.current_storyline_id:
                item.setText(f"{display_name} (Current)")
                item.setBackground(Qt.GlobalColor.darkGray)

            self.storyline_list.addItem(item)

    def on_selection_changed(self):
        """Handle selection change in the storylines list."""
        selected_items = self.storyline_list.selectedItems()
        has_selection = len(selected_items) > 0

        if has_selection:
            selected_storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            is_current = selected_storyline_id == self.current_storyline_id

            # Load the selected storyline into the form
            storyline = self.model.get_storyline_by_id(selected_storyline_id)
            if storyline:
                self.name_input.setText(storyline.name or "")
                self.description_input.setPlainText(storyline.description or "")

                # Load linked settings
                linked_settings = self.model.get_settings_for_storyline(selected_storyline_id)
                if linked_settings:
                    # Set to first linked setting
                    for i in range(self.setting_combo.count()):
                        if self.setting_combo.itemData(i) == linked_settings[0].id:
                            self.setting_combo.setCurrentIndex(i)
                            break
                else:
                    self.setting_combo.setCurrentIndex(0)  # No Setting

            self.switch_btn.setEnabled(not is_current)
            self.delete_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
        else:
            self.switch_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.name_input.clear()
            self.description_input.clear()
            self.setting_combo.setCurrentIndex(0)

    def on_save_storyline(self):
        """Save changes to the selected storyline."""
        selected_items = self.storyline_list.selectedItems()
        if not selected_items:
            return

        storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        setting_id = self.setting_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a storyline name.")
            return

        self.action = "update"
        self.selected_storyline_id = storyline_id
        self.updated_name = name
        self.updated_description = description
        self.updated_setting_id = setting_id
        self.accept()

    def on_create_storyline(self):
        """Create a new storyline."""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        setting_id = self.setting_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a storyline name.")
            return

        self.action = "create"
        self.new_storyline_name = name
        self.new_storyline_description = description
        self.new_storyline_setting_id = setting_id
        self.accept()

    def on_switch_storyline(self):
        """Switch to the selected storyline."""
        selected_items = self.storyline_list.selectedItems()
        if selected_items:
            self.selected_storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.action = "switch"
            self.accept()

    def on_delete_storyline(self):
        """Delete the selected storyline."""
        selected_items = self.storyline_list.selectedItems()
        if not selected_items:
            return

        selected_storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        storyline_name = selected_items[0].text().replace(" (Current)", "")

        if selected_storyline_id == self.current_storyline_id:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the current storyline. Switch to another storyline first.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the storyline '{storyline_name}'?\n\n"
            "This will permanently delete all plots, nodes, and story data in this storyline.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_storyline_id = selected_storyline_id
            self.action = "delete"
            self.accept()
