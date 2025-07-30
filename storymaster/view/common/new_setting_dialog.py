"""
Defines the dialog for creating a new setting.
"""

import os
import json
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.theme import (
    get_dialog_style,
    get_button_style,
    get_input_style,
)

# Import the world building import functionality
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
try:
    from import_world_building import import_world_building_package
except ImportError:
    # Fallback if import fails
    def import_world_building_package(json_file_path: str, target_setting_id: int):
        print(f"Warning: Could not import from {json_file_path} - import_world_building not available")
        return False


class NewSettingDialog(QDialog):
    """
    A dialog window that allows the user to create a new setting.
    """

    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Create New Setting")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
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
        
        # World building packages
        self.package_checkboxes = {}
        self.packages_group = QGroupBox("World Building Packages")
        
        # --- Configure Widgets ---
        self.description_text_edit.setMaximumHeight(100)
        self._populate_users()
        self._setup_packages_section()

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Setting Name:", self.name_line_edit)
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
        main_layout.addWidget(self.packages_group)
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

    def _setup_packages_section(self):
        """
        Sets up the world building packages section with checkboxes.
        """
        # Create scrollable area for packages
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(300)
        scroll_area.setWidgetResizable(True)
        
        packages_widget = QGroupBox()
        packages_layout = QVBoxLayout()
        
        # Scan for available packages
        packages_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "world_building_packages"
        )
        
        if os.path.exists(packages_dir):
            for filename in sorted(os.listdir(packages_dir)):
                if filename.endswith('.json'):
                    package_path = os.path.join(packages_dir, filename)
                    package_info = self._get_package_info(package_path)
                    
                    if package_info:
                        checkbox = QCheckBox(package_info['display_name'])
                        checkbox.setToolTip(package_info['description'])
                        self.package_checkboxes[filename] = {
                            'checkbox': checkbox,
                            'path': package_path,
                            'info': package_info
                        }
                        packages_layout.addWidget(checkbox)
        
        # If no packages found, show a message
        if not self.package_checkboxes:
            no_packages_label = QLabel("No world building packages found.\nPackages should be placed in the 'world_building_packages' directory.")
            no_packages_label.setStyleSheet("color: #888888; font-style: italic;")
            packages_layout.addWidget(no_packages_label)
        
        packages_widget.setLayout(packages_layout)
        scroll_area.setWidget(packages_widget)
        
        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll_area)
        self.packages_group.setLayout(group_layout)

    def _get_package_info(self, package_path: str) -> dict | None:
        """
        Extracts package information from a JSON file.
        Returns None if the file is invalid.
        """
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this looks like a world building package
            if isinstance(data, dict) and '_package_info' in data:
                return data['_package_info']
            else:
                # Fallback: create info from filename
                filename = os.path.basename(package_path)
                name = filename.replace('.json', '').replace('_', ' ').title()
                return {
                    'display_name': name,
                    'description': f'World building package: {name}',
                    'category': 'General'
                }
        except Exception as e:
            print(f"Error reading package {package_path}: {e}")
            return None

    def get_setting_data(self) -> dict | None:
        """
        Returns the setting data if the dialog is accepted.
        Returns None if canceled.
        """
        if self.exec() == QDialog.DialogCode.Accepted:
            setting_data = {
                "name": self.name_line_edit.text().strip(),
                "description": self.description_text_edit.toPlainText().strip(),
                "user_id": self.user_combo.currentData(),
            }
            
            # Store selected packages to import after setting is created
            setting_data['_selected_packages'] = self._get_selected_packages()
            
            return setting_data
        return None

    def _get_selected_packages(self) -> list:
        """
        Returns list of selected package paths.
        """
        selected = []
        for filename, package_data in self.package_checkboxes.items():
            if package_data['checkbox'].isChecked():
                selected.append(package_data['path'])
        return selected

    def import_packages_for_setting(self, package_paths: list, setting_id: int):
        """
        Imports the selected world building packages for a specific setting.
        This should be called after the setting has been created.
        """
        if not package_paths:
            return
            
        print(f"📦 Importing {len(package_paths)} world building packages for setting ID {setting_id}...")
        
        success_count = 0
        for package_path in package_paths:
            try:
                package_name = os.path.basename(package_path)
                print(f"📦 Importing package: {package_name}")
                
                # Use the specialized world building import
                success = import_world_building_package(package_path, setting_id)
                if success:
                    print(f"✅ Successfully imported {package_name}")
                    success_count += 1
                else:
                    print(f"❌ Failed to import {package_name}")
            except Exception as e:
                print(f"❌ Error importing {package_path}: {e}")
        
        print(f"🎉 Imported {success_count}/{len(package_paths)} world building packages!")
