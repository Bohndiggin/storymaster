"""
Dialog for importing world building packages into the current setting
"""

import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QScrollArea,
)

from storymaster.view.common.package_utils import (
    get_world_building_packages_path,
    debug_world_building_packages,
)

from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_input_style,
)

# Import the world building import functionality
import sys
from pathlib import Path

# Add scripts directory to path with robust resolution
current_file = Path(__file__).resolve()
# Go up from: storymaster/view/common/import_lore_packages_dialog.py -> project root
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

    def import_world_building_package(
        json_file_path: str, target_setting_id: int
    ) -> bool:
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
        package_name = package_info.get(
            "display_name", os.path.basename(json_file_path)
        )

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
                                    total_imported += 1

                                except Exception as e:
                                    print(f"⚠️  Error importing {table_name} item: {e}")
                                    # Continue with other items

                # Commit all changes
                session.commit()

                if total_imported > 0:
                    print(
                        f"✅ Successfully imported {total_imported} items from {package_name}"
                    )
                else:
                    print(
                        f"ℹ️  No new items imported from {package_name} (all items already exist)"
                    )

                return True

        except Exception as e:
            print(f"❌ Database error during import: {e}")
            return False


class ImportLorePackagesDialog(QDialog):
    """Dialog for importing world building packages into the current setting"""

    def __init__(self, model, current_setting_id, current_setting_name, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_setting_id = current_setting_id
        self.current_setting_name = current_setting_name

        self.setWindowTitle("Import Lore Packages")
        self.setModal(True)
        self.resize(600, 500)

        # Apply theme styling
        self.setStyleSheet(get_dialog_style() + get_button_style() + get_input_style())

        self.package_checkboxes = {}
        self.setup_ui()
        self.load_packages()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Title and info
        title_label = QLabel(f"Import Lore Packages into: {self.current_setting_name}")
        title_label.setStyleSheet(get_label_style("header"))
        layout.addWidget(title_label)

        info_label = QLabel(
            "Select world building packages to import into your current setting."
        )
        info_label.setStyleSheet(get_label_style("info"))
        layout.addWidget(info_label)

        # Package selection area
        packages_group = QGroupBox("Available Lore Packages")
        packages_layout = QVBoxLayout()

        # Scrollable area for packages
        packages_scroll = QScrollArea()
        packages_scroll.setWidgetResizable(True)
        packages_scroll.setMaximumHeight(300)

        self.packages_widget = QGroupBox()
        self.packages_layout = QVBoxLayout()
        self.packages_widget.setLayout(self.packages_layout)
        packages_scroll.setWidget(self.packages_widget)
        packages_layout.addWidget(packages_scroll)

        packages_group.setLayout(packages_layout)
        layout.addWidget(packages_group)

        # Button area
        button_layout = QHBoxLayout()

        # Select/Deselect all buttons
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_packages)
        button_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_packages)
        button_layout.addWidget(deselect_all_btn)

        button_layout.addStretch()

        # Import button
        self.import_btn = QPushButton("Import Selected Packages")
        self.import_btn.setToolTip(
            "Import selected world building packages into the current setting"
        )
        self.import_btn.clicked.connect(self.import_selected_packages)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)

        layout.addLayout(button_layout)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        dialog_buttons.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        dialog_buttons.addWidget(close_btn)

        layout.addLayout(dialog_buttons)
        self.setLayout(layout)

    def load_packages(self):
        """Load available world building packages"""
        # Clear existing checkboxes
        for checkbox_data in self.package_checkboxes.values():
            checkbox_data["checkbox"].setParent(None)
        self.package_checkboxes.clear()

        # Clear layout
        while self.packages_layout.count():
            child = self.packages_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Scan for available packages
        packages_dir = get_world_building_packages_path()

        if packages_dir and os.path.exists(packages_dir):
            package_count = 0
            for filename in sorted(os.listdir(packages_dir)):
                if filename.endswith(".json"):
                    package_path = os.path.join(packages_dir, filename)
                    package_info = self._get_package_info(package_path)

                    if package_info:
                        checkbox = QCheckBox(package_info["display_name"])

                        # Create description text
                        description = package_info.get(
                            "description", "No description available"
                        )
                        category = package_info.get("category", "General")
                        version = package_info.get("version", "1.0")

                        tooltip_text = (
                            f"{description}\n\nCategory: {category}\nVersion: {version}"
                        )
                        checkbox.setToolTip(tooltip_text)
                        checkbox.stateChanged.connect(self.update_import_button_state)

                        self.package_checkboxes[filename] = {
                            "checkbox": checkbox,
                            "path": package_path,
                            "info": package_info,
                        }
                        self.packages_layout.addWidget(checkbox)
                        package_count += 1

            if package_count == 0:
                no_packages_label = QLabel(
                    "No world building packages found.\nPackages should be placed in the 'world_building_packages' directory."
                )
                no_packages_label.setStyleSheet(
                    "color: #888888; font-style: italic; padding: 20px;"
                )
                self.packages_layout.addWidget(no_packages_label)
        else:
            # Generate debug information for troubleshooting
            debug_info = debug_world_building_packages()

            # Show user-friendly message
            no_dir_label = QLabel(
                "World building packages directory not found.\n\nClick 'Show Debug Info' for troubleshooting details."
            )
            no_dir_label.setStyleSheet(
                "color: #888888; font-style: italic; padding: 20px;"
            )
            self.packages_layout.addWidget(no_dir_label)

            # Add debug button
            debug_button = QPushButton("Show Debug Info")
            debug_button.clicked.connect(lambda: self._show_debug_info(debug_info))
            self.packages_layout.addWidget(debug_button)

    def _show_debug_info(self, debug_info: str):
        """Show debug information in a message box for troubleshooting"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("World Building Packages Debug Info")
        msg_box.setText(
            "Debug information for troubleshooting world_building_packages location:"
        )
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
                    "version": "1.0",
                }
        except Exception as e:
            print(f"Error reading package {package_path}: {e}")
            return None

    def select_all_packages(self):
        """Select all package checkboxes"""
        for package_data in self.package_checkboxes.values():
            package_data["checkbox"].setChecked(True)

    def deselect_all_packages(self):
        """Deselect all package checkboxes"""
        for package_data in self.package_checkboxes.values():
            package_data["checkbox"].setChecked(False)

    def update_import_button_state(self):
        """Update import button enabled state"""
        has_packages = any(
            data["checkbox"].isChecked() for data in self.package_checkboxes.values()
        )
        self.import_btn.setEnabled(has_packages)

    def import_selected_packages(self):
        """Import selected world building packages into the current setting"""
        # Get selected packages
        selected_packages = []
        for filename, package_data in self.package_checkboxes.items():
            if package_data["checkbox"].isChecked():
                selected_packages.append(
                    {
                        "path": package_data["path"],
                        "name": package_data["info"]["display_name"],
                    }
                )

        if not selected_packages:
            QMessageBox.warning(
                self,
                "No Packages Selected",
                "Please select at least one package to import.",
            )
            return

        # Confirm import
        package_names = "\n".join([f"• {pkg['name']}" for pkg in selected_packages])
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import {len(selected_packages)} lore package(s) into setting '{self.current_setting_name}'?\n\n"
            f"Packages to import:\n{package_names}\n\n"
            f"This will add new world building data to your setting.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Import packages
        success_count = 0
        error_messages = []

        for package in selected_packages:
            try:
                success = import_world_building_package(
                    package["path"], self.current_setting_id
                )
                if success:
                    success_count += 1
                else:
                    error_messages.append(f"Failed to import {package['name']}")
            except Exception as e:
                error_messages.append(f"Error importing {package['name']}: {str(e)}")

        # Show results
        if success_count == len(selected_packages):
            QMessageBox.information(
                self,
                "Import Successful",
                f"Successfully imported {success_count} lore package(s) into '{self.current_setting_name}'!\n\n"
                f"The new world building data is now available in your setting.",
            )
            # Uncheck all packages after successful import
            self.deselect_all_packages()
        elif success_count > 0:
            error_text = "\n".join(error_messages)
            QMessageBox.warning(
                self,
                "Partial Import",
                f"Imported {success_count} of {len(selected_packages)} packages successfully.\n\n"
                f"Errors:\n{error_text}",
            )
        else:
            error_text = "\n".join(error_messages)
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import any packages.\n\n" f"Errors:\n{error_text}",
            )
