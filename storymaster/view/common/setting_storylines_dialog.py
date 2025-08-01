"""
Dialog for managing setting-to-storyline relationships
Select a setting, then choose which storylines to connect
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
    QComboBox,
)

from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_list_style,
    get_input_style,
    COLORS,
)


class SettingStorylinesDialog(QDialog):
    """Dialog for selecting a setting and managing its storyline connections"""

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_setting_id = None
        self.current_setting_name = ""

        self.setWindowTitle("Manage Setting Storylines")
        self.setModal(True)
        self.resize(700, 500)

        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
            + get_input_style()
        )

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Setting selection
        setting_layout = QHBoxLayout()
        setting_label = QLabel("Select Setting:")
        setting_label.setStyleSheet(get_label_style("bold"))
        self.setting_combo = QComboBox()
        self.setting_combo.currentIndexChanged.connect(self.on_setting_changed)

        setting_layout.addWidget(setting_label)
        setting_layout.addWidget(self.setting_combo)
        setting_layout.addStretch()
        layout.addLayout(setting_layout)

        # Current setting label
        self.current_setting_label = QLabel("Select a setting to manage its storylines")
        self.current_setting_label.setStyleSheet(get_label_style("header"))
        layout.addWidget(self.current_setting_label)

        # Main content area
        content_layout = QHBoxLayout()

        # Available storylines (left side)
        available_group = QGroupBox("Available Storylines")
        available_layout = QVBoxLayout()

        self.available_list = QListWidget()
        self.available_list.setToolTip(
            "Storylines that can be connected to this setting"
        )
        available_layout.addWidget(self.available_list)

        available_group.setLayout(available_layout)
        content_layout.addWidget(available_group)

        # Control buttons (center)
        button_layout = QVBoxLayout()
        button_layout.addStretch()

        self.connect_btn = QPushButton("→ Connect")
        self.connect_btn.setToolTip("Connect selected storyline to this setting")
        self.connect_btn.clicked.connect(self.connect_storyline)
        self.connect_btn.setEnabled(False)
        button_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("← Disconnect")
        self.disconnect_btn.setToolTip(
            "Disconnect selected storyline from this setting"
        )
        self.disconnect_btn.clicked.connect(self.disconnect_storyline)
        self.disconnect_btn.setEnabled(False)
        button_layout.addWidget(self.disconnect_btn)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Connected storylines (right side)
        connected_group = QGroupBox("Connected Storylines")
        connected_layout = QVBoxLayout()

        self.connected_list = QListWidget()
        self.connected_list.setToolTip("Storylines currently connected to this setting")
        connected_layout.addWidget(self.connected_list)

        connected_group.setLayout(connected_layout)
        content_layout.addWidget(connected_group)

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
        self.connected_list.itemSelectionChanged.connect(
            self.on_connected_selection_changed
        )

        # Initially disable content
        self.set_content_enabled(False)

    def load_settings(self):
        """Load all settings into the combo box"""
        try:
            settings = self.model.get_all_settings()
            self.setting_combo.clear()
            self.setting_combo.addItem("-- Select Setting --", None)

            for setting in settings:
                display_name = setting.name if setting.name else f"Setting {setting.id}"
                self.setting_combo.addItem(display_name, setting.id)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")

    def on_setting_changed(self):
        """Handle setting selection change"""
        setting_id = self.setting_combo.currentData()
        if setting_id is None:
            self.current_setting_id = None
            self.current_setting_name = ""
            self.current_setting_label.setText(
                "Select a setting to manage its storylines"
            )
            self.set_content_enabled(False)
            return

        self.current_setting_id = setting_id
        self.current_setting_name = self.setting_combo.currentText()
        self.current_setting_label.setText(
            f"Managing storylines for: {self.current_setting_name}"
        )
        self.set_content_enabled(True)
        self.load_storylines()

    def set_content_enabled(self, enabled):
        """Enable/disable the storyline management content"""
        self.available_list.setEnabled(enabled)
        self.connected_list.setEnabled(enabled)
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)

    def load_storylines(self):
        """Load available and connected storylines for the current setting"""
        if not self.current_setting_id:
            return

        try:
            # Load available storylines (not connected to this setting)
            available_storylines = self.model.get_available_storylines_for_setting(
                self.current_setting_id
            )
            self.available_list.clear()

            for storyline in available_storylines:
                item = QListWidgetItem()
                item.setText(storyline.name)
                if storyline.description:
                    item.setToolTip(storyline.description)
                item.setData(Qt.ItemDataRole.UserRole, storyline.id)
                self.available_list.addItem(item)

            # Load connected storylines
            connected_storylines = self.model.get_storylines_for_setting(
                self.current_setting_id
            )
            self.connected_list.clear()

            for storyline in connected_storylines:
                item = QListWidgetItem()
                item.setText(storyline.name)
                if storyline.description:
                    item.setToolTip(storyline.description)
                item.setData(Qt.ItemDataRole.UserRole, storyline.id)
                self.connected_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load storylines: {e}")

    def on_available_selection_changed(self):
        """Handle selection change in available storylines list"""
        has_selection = len(self.available_list.selectedItems()) > 0
        self.connect_btn.setEnabled(has_selection and self.current_setting_id)

    def on_connected_selection_changed(self):
        """Handle selection change in connected storylines list"""
        has_selection = len(self.connected_list.selectedItems()) > 0
        self.disconnect_btn.setEnabled(has_selection and self.current_setting_id)

    def connect_storyline(self):
        """Connect the selected available storyline to the current setting"""
        if not self.current_setting_id:
            return

        selected_items = self.available_list.selectedItems()
        if not selected_items:
            return

        storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        storyline_name = selected_items[0].text()

        try:
            success = self.model.link_storyline_to_setting(
                storyline_id, self.current_setting_id
            )
            if success:
                self.load_storylines()  # Refresh both lists
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"Storyline '{storyline_name}' is already connected to this setting",
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect storyline: {e}")

    def disconnect_storyline(self):
        """Disconnect the selected storyline from the current setting"""
        if not self.current_setting_id:
            return

        selected_items = self.connected_list.selectedItems()
        if not selected_items:
            return

        storyline_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        storyline_name = selected_items[0].text()

        # Confirm disconnect
        reply = QMessageBox.question(
            self,
            "Confirm Disconnect",
            f"Are you sure you want to disconnect storyline '{storyline_name}' from setting '{self.current_setting_name}'?\n\n"
            f"This will remove access to characters and world-building elements from this setting "
            f"within the storyline.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.model.unlink_storyline_from_setting(
                    storyline_id, self.current_setting_id
                )
                if success:
                    self.load_storylines()  # Refresh both lists
                else:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"Storyline '{storyline_name}' was not connected to this setting",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to disconnect storyline: {e}"
                )
