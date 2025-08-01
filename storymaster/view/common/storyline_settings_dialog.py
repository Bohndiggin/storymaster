"""
Dialog for managing storyline-to-setting relationships
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
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QScrollArea,
    QComboBox,
)

from storymaster.view.common.package_utils import get_world_building_packages_path, debug_world_building_packages

from storymaster.view.common.theme import (
    get_dialog_style,
    get_label_style,
    get_button_style,
    get_list_style,
    get_input_style,
)

# Import the world building import functionality
import sys
from pathlib import Path

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
    
    print(f"Warning: Could not import import_world_building module ({e}), using embedded implementation")
    
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
            with open(json_file_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON file: {e}")
            return False
        
        # Validate JSON structure
        if not isinstance(package_data, dict):
            print("❌ JSON must be a dictionary with table names as keys")
            return False
        
        # Get package info if available
        package_info = package_data.get('_package_info', {})
        package_name = package_info.get('display_name', os.path.basename(json_file_path))
        
        print(f"📦 Importing world building package: {package_name}")
        print(f"🎯 Target setting ID: {target_setting_id}")
        
        # Table name to SQLAlchemy class mapping (key tables for character arcs)
        table_class_map = {
            'arc_type': schema.ArcType,
            'alignment': schema.Alignment,
            'background': schema.Background, 
            'class': schema.Class_,
            'race': schema.Race,
            'sub_race': schema.SubRace,
            'stat': schema.Stat,
            'skills': schema.Skills,
            'actor': schema.Actor,
            'faction': schema.Faction,
            'location_': schema.Location,
            'object_': schema.Object_,
            'world_data': schema.WorldData,
            'history': schema.History,
        }
        
        # Import using the model's engine
        from storymaster.model.common.common_model import BaseModel
        temp_model = BaseModel(user_id=1)  # Temporary model instance for engine access
        
        try:
            with Session(temp_model.engine) as session:
                total_imported = 0
                
                # Import data table by table in dependency order
                table_order = [
                    'alignment', 'background', 'class', 'race', 'sub_race', 'stat', 'skills',
                    'actor', 'faction', 'location_', 'history', 'object_', 'world_data', 'arc_type'
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
                                    item_data_copy['setting_id'] = target_setting_id
                                    
                                    # Check for duplicates based on name and setting_id (if name field exists)
                                    if hasattr(table_class, 'name') and hasattr(table_class, 'setting_id'):
                                        existing_item = session.query(table_class).filter_by(
                                            name=item_data_copy['name'],
                                            setting_id=target_setting_id
                                        ).first()
                                        
                                        if existing_item:
                                            print(f"⏭️  Skipping duplicate {table_name}: {item_data_copy['name']}")
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
                
                print(f"✅ Successfully imported {total_imported} items from {package_name}")
                return True
                
        except Exception as e:
            print(f"❌ Database error during import: {e}")
            return False


class StorylineSettingsDialog(QDialog):
    """Dialog for managing which settings are linked to a storyline"""

    def __init__(self, model, storyline_id, storyline_name, parent=None):
        super().__init__(parent)
        self.model = model
        self.storyline_id = storyline_id
        self.storyline_name = storyline_name

        self.setWindowTitle(f"Manage Settings for {storyline_name}")
        self.setModal(True)
        self.resize(800, 600)
        
        # Apply theme styling
        self.setStyleSheet(
            get_dialog_style()
            + get_button_style()
            + get_list_style()
            + get_input_style()
        )

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel(f"Settings for storyline: {self.storyline_name}")
        title_label.setStyleSheet(get_label_style("header"))
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

        # World building packages import section
        import_group = QGroupBox("Import World Building Packages")
        import_layout = QVBoxLayout()
        
        # Target setting selection
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Import to Setting:"))
        self.target_setting_combo = QComboBox()
        self.target_setting_combo.setToolTip("Select which linked setting to import packages into")
        target_layout.addWidget(self.target_setting_combo)
        target_layout.addStretch()
        import_layout.addLayout(target_layout)
        
        # Package selection area
        self.package_checkboxes = {}
        packages_scroll = QScrollArea()
        packages_scroll.setMaximumHeight(150)
        packages_scroll.setWidgetResizable(True)
        
        self.packages_widget = QGroupBox()
        self.packages_layout = QVBoxLayout()
        self.packages_widget.setLayout(self.packages_layout)
        packages_scroll.setWidget(self.packages_widget)
        import_layout.addWidget(packages_scroll)
        
        # Import button
        import_btn_layout = QHBoxLayout()
        import_btn_layout.addStretch()
        self.import_packages_btn = QPushButton("Import Selected Packages")
        self.import_packages_btn.setToolTip("Import selected world building packages into the chosen setting")
        self.import_packages_btn.clicked.connect(self.import_selected_packages)
        self.import_packages_btn.setEnabled(False)
        import_btn_layout.addWidget(self.import_packages_btn)
        import_layout.addLayout(import_btn_layout)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

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
        self.target_setting_combo.currentIndexChanged.connect(self.on_target_setting_changed)
        
        # Load packages
        self.load_packages()

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

            # Update target setting combo
            self.update_target_setting_combo()

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

    def update_target_setting_combo(self):
        """Update the target setting combo box with linked settings"""
        self.target_setting_combo.clear()
        
        # Add linked settings to combo
        for i in range(self.linked_list.count()):
            item = self.linked_list.item(i)
            setting_name = item.text()
            setting_id = item.data(Qt.ItemDataRole.UserRole)
            self.target_setting_combo.addItem(setting_name, setting_id)
        
        # Enable/disable import functionality based on available settings
        has_settings = self.target_setting_combo.count() > 0
        self.target_setting_combo.setEnabled(has_settings)
        self.update_import_button_state()

    def on_target_setting_changed(self):
        """Handle target setting selection change"""
        self.update_import_button_state()

    def update_import_button_state(self):
        """Update import button enabled state"""
        has_target = self.target_setting_combo.count() > 0
        has_packages = any(data['checkbox'].isChecked() for data in self.package_checkboxes.values())
        self.import_packages_btn.setEnabled(has_target and has_packages)

    def load_packages(self):
        """Load available world building packages"""
        # Clear existing checkboxes
        for checkbox_data in self.package_checkboxes.values():
            checkbox_data['checkbox'].setParent(None)
        self.package_checkboxes.clear()
        
        # Clear layout
        while self.packages_layout.count():
            child = self.packages_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Scan for available packages
        packages_dir = get_world_building_packages_path()
        
        if packages_dir and os.path.exists(packages_dir):
            for filename in sorted(os.listdir(packages_dir)):
                if filename.endswith('.json'):
                    package_path = os.path.join(packages_dir, filename)
                    package_info = self._get_package_info(package_path)
                    
                    if package_info:
                        checkbox = QCheckBox(package_info['display_name'])
                        checkbox.setToolTip(package_info['description'])
                        checkbox.stateChanged.connect(self.update_import_button_state)
                        
                        self.package_checkboxes[filename] = {
                            'checkbox': checkbox,
                            'path': package_path,
                            'info': package_info
                        }
                        self.packages_layout.addWidget(checkbox)
        
        # If no packages found, show a message
        if not self.package_checkboxes:
            if packages_dir:
                # Directory exists but no packages
                no_packages_label = QLabel("No world building packages found.\nPackages should be placed in the 'world_building_packages' directory.")
                no_packages_label.setStyleSheet("color: #888888; font-style: italic;")
                self.packages_layout.addWidget(no_packages_label)
            else:
                # Directory not found - show debug info
                debug_info = debug_world_building_packages()
                no_dir_label = QLabel("World building packages directory not found.\n\nClick 'Show Debug Info' for troubleshooting details.")
                no_dir_label.setStyleSheet("color: #888888; font-style: italic;")
                self.packages_layout.addWidget(no_dir_label)
                
                debug_button = QPushButton("Show Debug Info")
                debug_button.clicked.connect(lambda: self._show_debug_info(debug_info))
                self.packages_layout.addWidget(debug_button)

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

    def import_selected_packages(self):
        """Import selected world building packages into the target setting"""
        # Get target setting
        target_setting_id = self.target_setting_combo.currentData()
        target_setting_name = self.target_setting_combo.currentText()
        
        if not target_setting_id:
            QMessageBox.warning(self, "No Target Setting", "Please select a setting to import packages into.")
            return
        
        # Get selected packages
        selected_packages = []
        for filename, package_data in self.package_checkboxes.items():
            if package_data['checkbox'].isChecked():
                selected_packages.append({
                    'path': package_data['path'],
                    'name': package_data['info']['display_name']
                })
        
        if not selected_packages:
            QMessageBox.warning(self, "No Packages Selected", "Please select at least one package to import.")
            return
        
        # Confirm import
        package_names = "\n".join([f"• {pkg['name']}" for pkg in selected_packages])
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import {len(selected_packages)} world building package(s) into setting '{target_setting_name}'?\n\n"
            f"Packages to import:\n{package_names}\n\n"
            f"This will add new world building data to the setting.",
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
                success = import_world_building_package(package['path'], target_setting_id)
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
                f"Successfully imported {success_count} world building package(s) into '{target_setting_name}'!"
            )
            # Uncheck all packages after successful import
            for package_data in self.package_checkboxes.values():
                package_data['checkbox'].setChecked(False)
        elif success_count > 0:
            error_text = "\n".join(error_messages)
            QMessageBox.warning(
                self,
                "Partial Import",
                f"Imported {success_count} of {len(selected_packages)} packages successfully.\n\n"
                f"Errors:\n{error_text}"
            )
        else:
            error_text = "\n".join(error_messages)
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import any packages.\n\n"
                f"Errors:\n{error_text}"
            )
