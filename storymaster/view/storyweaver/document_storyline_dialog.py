"""
Dialog for associating a Storyweaver document with a storyline and setting.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_button_style,
    get_list_style,
)


class DocumentStorylineDialog(QDialog):
    """
    A dialog window that allows the user to associate a document with a storyline and setting.
    """

    def __init__(
        self,
        model: BaseModel,
        current_storyline_id: int = None,
        current_setting_id: int = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model = model
        self.selected_storyline_id = current_storyline_id
        self.selected_setting_id = current_setting_id
        self.setWindowTitle("Associate Document with Storyline")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Apply theme styling
        self.setStyleSheet(get_dialog_style() + get_button_style() + get_list_style())

        # --- Create Widgets ---
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel(
            "Select a storyline and setting to associate with this document.\n"
            "The document will automatically switch to this storyline when opened."
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # Horizontal layout for storyline and setting lists
        lists_layout = QHBoxLayout()

        # Storyline group
        storyline_group = QGroupBox("Storyline")
        storyline_layout = QVBoxLayout()
        self.storyline_list = QListWidget()
        self.storyline_list.itemSelectionChanged.connect(self.on_storyline_selection_changed)
        storyline_layout.addWidget(self.storyline_list)
        storyline_group.setLayout(storyline_layout)
        lists_layout.addWidget(storyline_group)

        # Setting group
        setting_group = QGroupBox("Setting")
        setting_layout = QVBoxLayout()
        self.setting_list = QListWidget()
        self.setting_list.itemSelectionChanged.connect(self.on_setting_selection_changed)
        setting_layout.addWidget(self.setting_list)
        setting_group.setLayout(setting_layout)
        lists_layout.addWidget(setting_group)

        main_layout.addLayout(lists_layout)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            current_storyline_id is not None and current_setting_id is not None
        )

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Load data
        self.load_storylines()
        self.load_settings()

    def load_storylines(self):
        """Load available storylines into the list"""
        try:
            storylines = self.model.get_all_storylines()

            for storyline in storylines:
                item = QListWidgetItem(storyline.name)
                item.setData(Qt.ItemDataRole.UserRole, storyline.id)

                # Mark current storyline as selected
                if storyline.id == self.selected_storyline_id:
                    item.setSelected(True)

                self.storyline_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load storylines: {str(e)}")

    def load_settings(self):
        """Load available settings into the list"""
        try:
            settings = self.model.get_all_settings()

            for setting in settings:
                item = QListWidgetItem(setting.name)
                item.setData(Qt.ItemDataRole.UserRole, setting.id)

                # Mark current setting as selected
                if setting.id == self.selected_setting_id:
                    item.setSelected(True)

                self.setting_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")

    def on_storyline_selection_changed(self):
        """Handle storyline selection change"""
        current_item = self.storyline_list.currentItem()
        if current_item:
            self.selected_storyline_id = current_item.data(Qt.ItemDataRole.UserRole)
        else:
            self.selected_storyline_id = None

        # Enable OK button only if both are selected
        self._update_ok_button()

    def on_setting_selection_changed(self):
        """Handle setting selection change"""
        current_item = self.setting_list.currentItem()
        if current_item:
            self.selected_setting_id = current_item.data(Qt.ItemDataRole.UserRole)
        else:
            self.selected_setting_id = None

        # Enable OK button only if both are selected
        self._update_ok_button()

    def _update_ok_button(self):
        """Update OK button enabled state"""
        enabled = self.selected_storyline_id is not None and self.selected_setting_id is not None
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    def get_selected_ids(self) -> tuple[int, int]:
        """Get the selected storyline and setting IDs"""
        return (self.selected_storyline_id, self.selected_setting_id)
