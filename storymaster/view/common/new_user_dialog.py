"""
Defines the dialog for creating a new user.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_input_style,
)


class NewUserDialog(QDialog):
    """
    A dialog window that allows creating a new user.
    """

    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Create New User")
        self.setMinimumWidth(350)

        # Apply theme styling
        self.setStyleSheet(get_dialog_style() + get_button_style() + get_input_style())

        # --- Create Widgets ---
        self.username_line_edit = QLineEdit()

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_line_edit)

        # Add some guidance
        info_label = QLabel(
            "Enter a username for the new user. This will be used to organize storylines and settings."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(get_label_style("muted"))

        # --- Dialog Buttons (OK/Cancel) ---
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(info_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Focus on username field
        self.username_line_edit.setFocus()

    def validate_and_accept(self):
        """Validate input before accepting"""
        username = self.username_line_edit.text().strip()

        if not username:
            QMessageBox.warning(self, "Invalid Input", "Please enter a username.")
            return

        if len(username) > 150:  # Based on schema constraint
            QMessageBox.warning(
                self, "Invalid Input", "Username must be 150 characters or less."
            )
            return

        # Check if username already exists
        try:
            existing_users = self.model.get_all_users()
            for user in existing_users:
                if user.username.lower() == username.lower():
                    QMessageBox.warning(
                        self,
                        "Username Exists",
                        "A user with this username already exists.",
                    )
                    return
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to validate username: {str(e)}"
            )
            return

        self.accept()

    def get_user_data(self) -> dict | None:
        """
        Returns the user data if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return {
                "username": self.username_line_edit.text().strip(),
            }
        return None
