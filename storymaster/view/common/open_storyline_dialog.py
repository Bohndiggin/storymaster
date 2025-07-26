"""
Defines the dialog for opening an existing storyline.
"""

from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QVBoxLayout)

from storymaster.model.common.common_model import BaseModel


class OpenStorylineDialog(QDialog):
    """
    A dialog window that allows the user to select a storyline to open.
    """

    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Open Storyline")
        self.setMinimumWidth(350)

        # --- Create Widgets ---
        self.storyline_combo = QComboBox()

        # --- Configure Widgets ---
        self._populate_storylines()

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Select Storyline:", self.storyline_combo)

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

    def _populate_storylines(self):
        """
        Fetches the list of storylines from the model and populates the combo box.
        """
        try:
            # NOTE: This requires a `get_all_storylines` method in your model
            storylines = self.model.get_all_storylines()
            for storyline in storylines:
                # Display storyline name, store the storyline object's ID as data
                self.storyline_combo.addItem(
                    f"{storyline.name} (ID: {storyline.id})", storyline.id
                )
        except Exception as e:
            print(f"Error populating storylines list: {e}")
            # You could add a disabled item to show the error
            self.storyline_combo.addItem("Could not load storylines.")
            self.storyline_combo.setEnabled(False)

    def get_selected_storyline_id(self) -> int | None:
        """
        Returns the ID of the selected storyline if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.storyline_combo.currentData()
        return None
