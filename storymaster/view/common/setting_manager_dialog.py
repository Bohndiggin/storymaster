"""
Setting Manager Dialog - Allows creating, editing, switching, and deleting settings.
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
)
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_list_style,
    get_dialog_style,
)


class SettingManagerDialog(QDialog):
    """Dialog for managing settings (world settings)."""

    def __init__(self, model, current_setting_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_setting_id = current_setting_id
        self.selected_setting_id = None
        self.action = None

        self.setWindowTitle("Manage Settings")
        self.setModal(True)
        self.resize(600, 500)
        self.setStyleSheet(get_dialog_style())
        self.setup_ui()
        self.populate_settings()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Settings list
        list_label = QLabel("Available Settings:")
        layout.addWidget(list_label)

        self.setting_list = QListWidget()
        self.setting_list.setStyleSheet(get_list_style())
        self.setting_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.setting_list)

        # Edit form section
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(get_input_style())
        self.name_input.setPlaceholderText("Setting name")
        form_layout.addRow("Name:", self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setStyleSheet(get_input_style())
        self.description_input.setPlaceholderText("Setting description")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)

        layout.addLayout(form_layout)

        # Action buttons row 1 - Edit/Create
        edit_button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet(get_button_style("primary"))
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.on_save_setting)

        self.create_btn = QPushButton("Create New Setting")
        self.create_btn.setStyleSheet(get_button_style("primary"))
        self.create_btn.clicked.connect(self.on_create_setting)

        edit_button_layout.addWidget(self.save_btn)
        edit_button_layout.addWidget(self.create_btn)
        edit_button_layout.addStretch()
        layout.addLayout(edit_button_layout)

        # Action buttons row 2 - Switch/Delete/Cancel
        button_layout = QHBoxLayout()

        self.switch_btn = QPushButton("Switch to Setting")
        self.switch_btn.setStyleSheet(get_button_style("primary"))
        self.switch_btn.setEnabled(False)
        self.switch_btn.clicked.connect(self.on_switch_setting)

        self.delete_btn = QPushButton("Delete Setting")
        self.delete_btn.setStyleSheet(get_button_style("danger"))
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_setting)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setStyleSheet(get_button_style())
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.switch_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_settings(self):
        """Load all settings into the list."""
        self.setting_list.clear()
        settings = self.model.get_all_settings()

        for setting in settings:
            display_name = setting.name if setting.name else f"Setting {setting.id}"
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, setting.id)

            if setting.id == self.current_setting_id:
                item.setText(f"{display_name} (Current)")
                item.setBackground(Qt.GlobalColor.darkGray)

            self.setting_list.addItem(item)

    def on_selection_changed(self):
        """Handle selection change in the settings list."""
        selected_items = self.setting_list.selectedItems()
        has_selection = len(selected_items) > 0

        if has_selection:
            selected_setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            is_current = selected_setting_id == self.current_setting_id

            # Load the selected setting into the form
            setting = self.model.get_setting_by_id(selected_setting_id)
            if setting:
                self.name_input.setText(setting.name or "")
                self.description_input.setPlainText(setting.description or "")

            self.switch_btn.setEnabled(not is_current)
            self.delete_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
        else:
            self.switch_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.name_input.clear()
            self.description_input.clear()

    def on_save_setting(self):
        """Save changes to the selected setting."""
        selected_items = self.setting_list.selectedItems()
        if not selected_items:
            return

        setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a setting name.")
            return

        self.action = "update"
        self.selected_setting_id = setting_id
        self.updated_name = name
        self.updated_description = description
        self.accept()

    def on_create_setting(self):
        """Create a new setting."""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a setting name.")
            return

        self.action = "create"
        self.new_setting_name = name
        self.new_setting_description = description
        self.accept()

    def on_switch_setting(self):
        """Switch to the selected setting."""
        selected_items = self.setting_list.selectedItems()
        if selected_items:
            self.selected_setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.action = "switch"
            self.accept()

    def on_delete_setting(self):
        """Delete the selected setting."""
        selected_items = self.setting_list.selectedItems()
        if not selected_items:
            return

        selected_setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        setting_name = selected_items[0].text().replace(" (Current)", "")

        if selected_setting_id == self.current_setting_id:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the current setting. Switch to another setting first.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the setting '{setting_name}'?\n\n"
            "This will permanently delete all world-building data in this setting "
            "(characters, locations, factions, etc.).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_setting_id = selected_setting_id
            self.action = "delete"
            self.accept()
