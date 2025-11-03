"""
Defines the dialog for creating a new setting.
"""

import json
import os

# Import the world building import functionality
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
)

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.package_utils import (
    debug_world_building_packages,
    get_world_building_packages_path,
)
from storymaster.view.common.theme import (
    get_button_style,
    get_dialog_style,
    get_input_style,
)

# Add scripts directory to path with robust resolution
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
scripts_dir = project_root / "scripts"

if scripts_dir.exists():
    sys.path.insert(0, str(scripts_dir))

try:
    from import_world_building import import_world_building_package
except ImportError as e:
    # Import the necessary components for the embedded implementation
    import json

    from sqlalchemy.orm import Session

    from storymaster.model.database import schema

    print(
        f"Warning: Could not import import_world_building module ({e}), using embedded implementation"
    )

    def import_world_building_package(json_file_path: str, target_setting_id: int) -> bool:
        """
        Embedded world building package import functionality.
        """
        # Validate file exists
        if not os.path.exists(json_file_path):
            print(f"❌ JSON file not found: {json_file_path}")
            return False

        # Load JSON data
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON file: {e}")
            return False

        # Validate JSON structure
        if not isinstance(package_data, dict):
            print("❌ JSON must be a dictionary with table names as keys")
            return False

        # Get package info if available
        package_info = package_data.get("_package_info", {})
        package_name = package_info.get("display_name", os.path.basename(json_file_path))

        print(f"📦 Importing world building package: {package_name}")
        print(f"🎯 Target setting ID: {target_setting_id}")

        # Table name to SQLAlchemy class mapping (key tables for character arcs)
        table_class_map = {
            "arc_type": schema.ArcType,
            "alignment": schema.Alignment,
            "background": schema.Background,
            "class": schema.Class_,
            "race": schema.Race,
            "sub_race": schema.SubRace,
            "stat": schema.Stat,
            "skills": schema.Skills,
            "actor": schema.Actor,
            "faction": schema.Faction,
            "location_": schema.Location,
            "object_": schema.Object_,
            "world_data": schema.WorldData,
            "history": schema.History,
        }

        # Import using the model's engine
        from storymaster.model.common.common_model import BaseModel

        temp_model = BaseModel(user_id=1)  # Temporary model instance for engine access

        try:
            with Session(temp_model.engine) as session:
                total_imported = 0

                # Import data table by table in dependency order
                table_order = [
                    "alignment",
                    "background",
                    "class",
                    "race",
                    "sub_race",
                    "stat",
                    "skills",
                    "actor",
                    "faction",
                    "location_",
                    "history",
                    "object_",
                    "world_data",
                    "arc_type",
                ]

                for table_name in table_order:
                    if table_name in package_data and table_name in table_class_map:
                        table_data = package_data[table_name]
                        if table_data:  # Only process non-empty tables
                            table_class = table_class_map[table_name]

                            for item_data in table_data:
                                try:
                                    # Update setting_id to target setting
                                    item_data_copy = item_data.copy()

                                    # Remove id field if present (let auto-increment handle it)
                                    if "id" in item_data_copy:
                                        del item_data_copy["id"]

                                    # Override setting_id to target setting
                                    if "setting_id" in item_data_copy:
                                        item_data_copy["setting_id"] = target_setting_id

                                    # Check for duplicates based on name and setting_id (if name field exists)
                                    if hasattr(table_class, "name") and hasattr(
                                        table_class, "setting_id"
                                    ):
                                        existing_item = (
                                            session.query(table_class)
                                            .filter_by(
                                                name=item_data_copy["name"],
                                                setting_id=target_setting_id,
                                            )
                                            .first()
                                        )

                                        if existing_item:
                                            print(
                                                f"⏭️  Skipping duplicate {table_name}: {item_data_copy['name']}"
                                            )
                                            continue

                                    # Create new record
                                    new_item = table_class(**item_data_copy)
                                    session.add(new_item)
                                    session.flush()  # Flush immediately to catch constraint errors
                                    total_imported += 1

                                except Exception as e:
                                    print(f"⚠️  Error importing {table_name} item: {e}")
                                    session.rollback()  # Rollback failed item, continue with others
                                    # Continue with other items

                # Commit all changes
                session.commit()

                print(f"✅ Successfully imported {total_imported} items from {package_name}")
                return True

        except Exception as e:
            print(f"❌ Database error during import: {e}")
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
        self.setStyleSheet(get_dialog_style() + get_button_style() + get_input_style())

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
        packages_dir = get_world_building_packages_path()

        if packages_dir and os.path.exists(packages_dir):
            for filename in sorted(os.listdir(packages_dir)):
                if filename.endswith(".json"):
                    package_path = os.path.join(packages_dir, filename)
                    package_info = self._get_package_info(package_path)

                    if package_info:
                        checkbox = QCheckBox(package_info["display_name"])
                        checkbox.setToolTip(package_info["description"])
                        self.package_checkboxes[filename] = {
                            "checkbox": checkbox,
                            "path": package_path,
                            "info": package_info,
                        }
                        packages_layout.addWidget(checkbox)

        # If no packages found, show a message
        if not self.package_checkboxes:
            if packages_dir:
                # Directory exists but no packages
                no_packages_label = QLabel(
                    "No world building packages found.\nPackages should be placed in the 'world_building_packages' directory."
                )
                no_packages_label.setStyleSheet("color: #888888; font-style: italic;")
                packages_layout.addWidget(no_packages_label)
            else:
                # Directory not found - show debug info
                debug_info = debug_world_building_packages()
                no_dir_label = QLabel(
                    "World building packages directory not found.\n\nClick 'Show Debug Info' for troubleshooting details."
                )
                no_dir_label.setStyleSheet("color: #888888; font-style: italic;")
                packages_layout.addWidget(no_dir_label)

                debug_button = QPushButton("Show Debug Info")
                debug_button.clicked.connect(lambda: self._show_debug_info(debug_info))
                packages_layout.addWidget(debug_button)

        packages_widget.setLayout(packages_layout)
        scroll_area.setWidget(packages_widget)

        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll_area)
        self.packages_group.setLayout(group_layout)

    def _show_debug_info(self, debug_info: str):
        """Show debug information in a message box for troubleshooting"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("World Building Packages Debug Info")
        msg_box.setText("Debug information for troubleshooting world_building_packages location:")
        msg_box.setDetailedText(debug_info)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _get_package_info(self, package_path: str) -> dict | None:
        """
        Extracts package information from a JSON file.
        Returns None if the file is invalid.
        """
        try:
            with open(package_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check if this looks like a world building package
            if isinstance(data, dict) and "_package_info" in data:
                return data["_package_info"]
            else:
                # Fallback: create info from filename
                filename = os.path.basename(package_path)
                name = filename.replace(".json", "").replace("_", " ").title()
                return {
                    "display_name": name,
                    "description": f"World building package: {name}",
                    "category": "General",
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
            user_id = self.user_combo.currentData()

            # Validate that we have a valid user_id
            if user_id is None:
                QMessageBox.critical(
                    self,
                    "Invalid User Selection",
                    "Please select a valid user. If no users are available, "
                    "you may need to create a user first.",
                )
                return None

            setting_data = {
                "name": self.name_line_edit.text().strip(),
                "description": self.description_text_edit.toPlainText().strip(),
                "user_id": user_id,
            }

            # Store selected packages to import after setting is created
            setting_data["_selected_packages"] = self._get_selected_packages()

            return setting_data
        return None

    def _get_selected_packages(self) -> list:
        """
        Returns list of selected package paths.
        """
        selected = []
        for filename, package_data in self.package_checkboxes.items():
            if package_data["checkbox"].isChecked():
                selected.append(package_data["path"])
        return selected

    def import_packages_for_setting(self, package_paths: list, setting_id: int):
        """
        Imports the selected world building packages for a specific setting.
        This should be called after the setting has been created.
        """
        if not package_paths:
            return

        print(
            f"📦 Importing {len(package_paths)} world building packages for setting ID {setting_id}..."
        )

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
