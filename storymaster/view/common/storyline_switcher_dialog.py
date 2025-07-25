"""
Defines the dialog for switching between storylines.
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


class StorylineSwitcherDialog(QDialog):
    """
    A dialog window that allows the user to switch between storylines.
    """

    def __init__(self, model: BaseModel, current_storyline_id: int = None, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_storyline_id = current_storyline_id
        self.selected_storyline_id = None
        self.setWindowTitle("Switch Storyline")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        # --- Create Widgets ---
        self.storyline_list = QListWidget()
        self.storyline_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.storyline_list.itemDoubleClicked.connect(self.accept)

        # --- Layout ---
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Select a storyline to switch to:")
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # List
        main_layout.addWidget(self.storyline_list)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Load storylines
        self.load_storylines()

    def load_storylines(self):
        """Load available storylines into the list"""
        try:
            storylines = self.model.get_all_storylines()

            for storyline in storylines:
                item = QListWidgetItem(storyline.name)
                item.setData(Qt.ItemDataRole.UserRole, storyline.id)

                # Mark current storyline
                if storyline.id == self.current_storyline_id:
                    item.setText(f"{storyline.name} (Current)")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)

                self.storyline_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load storylines: {str(e)}")

    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.storyline_list.currentItem()
        if current_item and current_item.flags() & Qt.ItemFlag.ItemIsSelectable:
            self.selected_storyline_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.selected_storyline_id = None
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def get_selected_storyline_id(self) -> int | None:
        """Get the selected storyline ID"""
        return self.selected_storyline_id
