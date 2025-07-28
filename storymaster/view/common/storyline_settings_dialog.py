"""
Dialog for managing storyline-to-setting relationships
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QGroupBox,
)


class StorylineSettingsDialog(QDialog):
    """Dialog for managing which settings are linked to a storyline"""

    def __init__(self, model, storyline_id, storyline_name, parent=None):
        super().__init__(parent)
        self.model = model
        self.storyline_id = storyline_id
        self.storyline_name = storyline_name

        self.setWindowTitle(f"Manage Settings for {storyline_name}")
        self.setModal(True)
        self.resize(600, 400)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel(f"Settings for storyline: {self.storyline_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Main content area
        content_layout = QHBoxLayout()

        # Available settings (left side)
        available_group = QGroupBox("Available Settings")
        available_layout = QVBoxLayout()

        self.available_list = QListWidget()
        self.available_list.setToolTip("Settings that can be linked to this storyline")
        available_layout.addWidget(self.available_list)

        available_group.setLayout(available_layout)
        content_layout.addWidget(available_group)

        # Control buttons (center)
        button_layout = QVBoxLayout()
        button_layout.addStretch()

        self.link_btn = QPushButton("→ Link")
        self.link_btn.setToolTip("Link selected setting to this storyline")
        self.link_btn.clicked.connect(self.link_setting)
        self.link_btn.setEnabled(False)
        button_layout.addWidget(self.link_btn)

        self.unlink_btn = QPushButton("← Unlink")
        self.unlink_btn.setToolTip("Unlink selected setting from this storyline")
        self.unlink_btn.clicked.connect(self.unlink_setting)
        self.unlink_btn.setEnabled(False)
        button_layout.addWidget(self.unlink_btn)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Linked settings (right side)
        linked_group = QGroupBox("Linked Settings")
        linked_layout = QVBoxLayout()

        self.linked_list = QListWidget()
        self.linked_list.setToolTip("Settings currently linked to this storyline")
        linked_layout.addWidget(self.linked_list)

        linked_group.setLayout(linked_layout)
        content_layout.addWidget(linked_group)

        layout.addLayout(content_layout)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        dialog_buttons.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        dialog_buttons.addWidget(close_btn)

        layout.addLayout(dialog_buttons)

        self.setLayout(layout)

        # Connect selection events
        self.available_list.itemSelectionChanged.connect(
            self.on_available_selection_changed
        )
        self.linked_list.itemSelectionChanged.connect(self.on_linked_selection_changed)

    def load_data(self):
        """Load available and linked settings"""
        try:
            # Load available settings
            available_settings = self.model.get_available_settings_for_storyline(
                self.storyline_id
            )
            self.available_list.clear()

            for setting in available_settings:
                item = QListWidgetItem()
                item.setText(f"{setting.name}")
                if setting.description:
                    item.setToolTip(setting.description)
                item.setData(Qt.ItemDataRole.UserRole, setting.id)
                self.available_list.addItem(item)

            # Load linked settings
            linked_settings = self.model.get_settings_for_storyline(self.storyline_id)
            self.linked_list.clear()

            for setting in linked_settings:
                item = QListWidgetItem()
                item.setText(f"{setting.name}")
                if setting.description:
                    item.setToolTip(setting.description)
                item.setData(Qt.ItemDataRole.UserRole, setting.id)
                self.linked_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")

    def on_available_selection_changed(self):
        """Handle selection change in available settings list"""
        has_selection = len(self.available_list.selectedItems()) > 0
        self.link_btn.setEnabled(has_selection)

    def on_linked_selection_changed(self):
        """Handle selection change in linked settings list"""
        has_selection = len(self.linked_list.selectedItems()) > 0
        self.unlink_btn.setEnabled(has_selection)

    def link_setting(self):
        """Link the selected available setting to the storyline"""
        selected_items = self.available_list.selectedItems()
        if not selected_items:
            return

        setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        setting_name = selected_items[0].text()

        try:
            success = self.model.link_storyline_to_setting(
                self.storyline_id, setting_id
            )
            if success:
                self.load_data()  # Refresh both lists
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully linked '{setting_name}' to storyline '{self.storyline_name}'",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"'{setting_name}' is already linked to this storyline",
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to link setting: {e}")

    def unlink_setting(self):
        """Unlink the selected setting from the storyline"""
        selected_items = self.linked_list.selectedItems()
        if not selected_items:
            return

        setting_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        setting_name = selected_items[0].text()

        # Confirm unlink
        reply = QMessageBox.question(
            self,
            "Confirm Unlink",
            f"Are you sure you want to unlink '{setting_name}' from storyline '{self.storyline_name}'?\n\n"
            f"This will not delete the setting, but characters and other world-building elements "
            f"from this setting will no longer be available in this storyline.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.model.unlink_storyline_from_setting(
                    self.storyline_id, setting_id
                )
                if success:
                    self.load_data()  # Refresh both lists
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Successfully unlinked '{setting_name}' from storyline '{self.storyline_name}'",
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"'{setting_name}' was not linked to this storyline",
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to unlink setting: {e}")

    def get_linked_settings_count(self):
        """Get the number of currently linked settings"""
        return self.linked_list.count()

    def get_available_settings_count(self):
        """Get the number of available settings"""
        return self.available_list.count()
