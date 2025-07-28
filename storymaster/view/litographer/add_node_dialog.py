"""
Defines the dialog for adding a new Litography Node.
"""

from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QVBoxLayout)

from storymaster.model.database import schema
from storymaster.view.common.theme import get_input_style, get_dialog_style, get_button_style
from storymaster.view.common.tooltips import apply_litographer_tooltips
from storymaster.view.common.custom_widgets import enable_smart_tab_navigation


class AddNodeDialog(QDialog):
    """
    A dialog window that presents a form to add a new Litography Node.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Node")
        self.setMinimumWidth(300)
        self.setStyleSheet(get_dialog_style())

        # --- Create Widgets ---
        self.node_type_combo = QComboBox()
        self.node_type_combo.setStyleSheet(get_input_style())
        apply_litographer_tooltips(self.node_type_combo, "node_type")

        # --- Configure Widgets ---
        # Populate the node type combo box from the NodeType enum
        for node_type in schema.NodeType:
            # Add the user-friendly name and store the actual enum member as data
            self.node_type_combo.addItem(
                node_type.name.title().replace("_", " "), node_type
            )


        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Node Type:", self.node_type_combo)

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
        
        # Set up enhanced tab navigation
        enable_smart_tab_navigation(self)

    def get_data(self) -> dict | None:
        """
        Returns the data entered in the form as a dictionary if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            return {
                "node_type": self.node_type_combo.currentData(),
            }
        return None
