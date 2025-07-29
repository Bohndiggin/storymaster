"""
Defines the dialog for switching between users.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_list_style,
)


class UserSwitcherDialog(QDialog):
    """
    A dialog window that allows the user to switch between users.
    """

    def __init__(self, model: BaseModel, current_user_id: int = None, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_user_id = current_user_id
        self.selected_user_id = None
        self.setWindowTitle("Switch User")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
        )

        # --- Create Widgets ---
        self.user_list = QListWidget()
        self.user_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.user_list.itemDoubleClicked.connect(self.accept)

        # --- Layout ---
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Select a user to switch to:")
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # List
        main_layout.addWidget(self.user_list)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Load users
        self.load_users()

    def load_users(self):
        """Load available users into the list"""
        try:
            users = self.model.get_all_users()

            for user in users:
                item = QListWidgetItem(user.username)
                item.setData(Qt.ItemDataRole.UserRole, user.id)

                # Mark current user
                if user.id == self.current_user_id:
                    item.setText(f"{user.username} (Current)")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)

                self.user_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.user_list.currentItem()
        if current_item and current_item.flags() & Qt.ItemFlag.ItemIsSelectable:
            self.selected_user_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.selected_user_id = None
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def get_selected_user_id(self) -> int | None:
        """Get the selected user ID"""
        return self.selected_user_id
