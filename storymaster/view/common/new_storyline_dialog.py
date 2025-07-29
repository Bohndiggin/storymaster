"""
Defines the dialog for creating a new storyline.
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_button_style,
    get_input_style,
)


class NewStorylineDialog(QDialog):
    """
    A dialog window that allows the user to create a new storyline.
    """

    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Create New Storyline")
        self.setMinimumWidth(400)
        
        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_input_style()
        )

        # --- Create Widgets ---
        self.name_line_edit = QLineEdit()
        self.description_text_edit = QTextEdit()
        self.user_combo = QComboBox()

        # --- Configure Widgets ---
        self.description_text_edit.setMaximumHeight(100)
        self._populate_users()

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Storyline Name:", self.name_line_edit)
        form_layout.addRow("Description:", self.description_text_edit)
        form_layout.addRow("User:", self.user_combo)

        # --- Dialog Buttons (OK/Cancel) ---
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def _populate_users(self):
        """
        Fetches the list of users from the model and populates the combo box.
        """
        try:
            # Get all users from the user table
            users = self.model.get_all_rows_as_dicts("user")
            for user in users:
                # Display username, store the user ID as data
                self.user_combo.addItem(user["username"], user["id"])
        except Exception as e:
            print(f"Error populating users list: {e}")
            # Add a disabled item to show the error
            self.user_combo.addItem("Could not load users.")
            self.user_combo.setEnabled(False)

    def get_storyline_data(self) -> dict | None:
        """
        Returns the storyline data if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return {
                "name": self.name_line_edit.text().strip(),
                "description": self.description_text_edit.toPlainText().strip(),
                "user_id": self.user_combo.currentData(),
            }
        return None
