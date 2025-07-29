from PyQt6.QtCore import Qt
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

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_button_style,
    get_list_style,
    get_input_style,
)


class UserManagerDialog(QDialog):
    def __init__(self, model: BaseModel, current_user_id: int = None, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_user_id = current_user_id
        self.selected_user_id = None
        self.action = None
        self.new_user_name = None

        self.setWindowTitle("Manage Users")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout()

        # User list
        list_label = QLabel("Available Users:")
        layout.addWidget(list_label)

        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.user_list)

        # New user section
        new_user_layout = QHBoxLayout()
        new_user_label = QLabel("New User Name:")
        self.new_user_input = QLineEdit()
        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.clicked.connect(self.on_add_user)

        new_user_layout.addWidget(new_user_label)
        new_user_layout.addWidget(self.new_user_input)
        new_user_layout.addWidget(self.add_user_btn)
        layout.addLayout(new_user_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.switch_btn = QPushButton("Switch to User")
        self.switch_btn.setEnabled(False)
        self.switch_btn.clicked.connect(self.on_switch_user)

        self.delete_btn = QPushButton("Delete User")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_user)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.switch_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_users(self):
        """Load available users into the list"""
        try:
            self.user_list.clear()
            users = self.model.get_all_users()

            for user in users:
                item = QListWidgetItem(user.username)
                item.setData(Qt.ItemDataRole.UserRole, user.id)

                if user.id == self.current_user_id:
                    item.setText(f"{user.username} (Current)")
                    item.setBackground(Qt.GlobalColor.darkGray)

                self.user_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def on_selection_changed(self):
        selected_items = self.user_list.selectedItems()
        has_selection = len(selected_items) > 0

        self.switch_btn.setEnabled(has_selection)

        if has_selection:
            selected_user_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            is_current = selected_user_id == self.current_user_id
            self.switch_btn.setEnabled(not is_current)
            self.delete_btn.setEnabled(True)
        else:
            self.delete_btn.setEnabled(False)

    def on_add_user(self):
        user_name = self.new_user_input.text().strip()
        if not user_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a username.")
            return

        self.accept()
        self.action = "add"
        self.new_user_name = user_name

    def on_switch_user(self):
        selected_items = self.user_list.selectedItems()
        if selected_items:
            self.selected_user_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.action = "switch"
            self.accept()

    def on_delete_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            return

        selected_user_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        user_name = selected_items[0].text().replace(" (Current)", "")

        if selected_user_id == self.current_user_id:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the current user. Switch to another user first.",
            )
            return

        # Check if user has data
        try:
            user_has_data = self.model.user_has_data(selected_user_id)
            warning_text = f"Are you sure you want to delete the user '{user_name}'?"
            if user_has_data:
                warning_text += "\n\nThis will permanently delete all storylines, settings, and related data for this user."

            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                warning_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.selected_user_id = selected_user_id
                self.action = "delete"
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check user data: {str(e)}")
