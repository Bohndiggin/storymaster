"""
Defines the dialog for opening an existing project.
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
)

from storymaster.model.common.common_model import BaseModel


class OpenProjectDialog(QDialog):
    """
    A dialog window that allows the user to select a project to open.
    """

    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Open Project")
        self.setMinimumWidth(350)

        # --- Create Widgets ---
        self.project_combo = QComboBox()

        # --- Configure Widgets ---
        self._populate_projects()

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Select Project:", self.project_combo)

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

    def _populate_projects(self):
        """
        Fetches the list of projects from the model and populates the combo box.
        """
        try:
            # NOTE: This requires a `get_all_projects` method in your model
            projects = self.model.get_all_projects()
            for project in projects:
                # Display project name, store the project object's ID as data
                self.project_combo.addItem(
                    f"{project.name} (ID: {project.id})", project.id
                )
        except Exception as e:
            print(f"Error populating projects list: {e}")
            # You could add a disabled item to show the error
            self.project_combo.addItem("Could not load projects.")
            self.project_combo.setEnabled(False)

    def get_selected_project_id(self) -> int | None:
        """
        Returns the ID of the selected project if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.project_combo.currentData()
        return None
