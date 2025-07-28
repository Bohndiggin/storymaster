"""
Defines the dialog for switching between settings.
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


class SettingSwitcherDialog(QDialog):
    """
    A dialog window that allows the user to switch between settings.
    """

    def __init__(self, model: BaseModel, current_setting_id: int = None, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_setting_id = current_setting_id
        self.selected_setting_id = None
        self.setWindowTitle("Switch Setting")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        # --- Create Widgets ---
        self.setting_list = QListWidget()
        self.setting_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.setting_list.itemDoubleClicked.connect(self.accept)

        # --- Layout ---
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Select a setting to switch to:")
        header_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # List
        main_layout.addWidget(self.setting_list)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Load settings
        self.load_settings()

    def load_settings(self):
        """Load available settings into the list"""
        try:
            settings = self.model.get_all_settings()

            for setting in settings:
                item = QListWidgetItem(setting.name)
                item.setData(Qt.ItemDataRole.UserRole, setting.id)

                # Mark current setting
                if setting.id == self.current_setting_id:
                    item.setText(f"{setting.name} (Current)")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)

                self.setting_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {str(e)}")

    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.setting_list.currentItem()
        if current_item and current_item.flags() & Qt.ItemFlag.ItemIsSelectable:
            self.selected_setting_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        else:
            self.selected_setting_id = None
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def get_selected_setting_id(self) -> int | None:
        """Get the selected setting ID"""
        return self.selected_setting_id
