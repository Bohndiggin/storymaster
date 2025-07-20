"""Holds the controller for the main page"""
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QComboBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView


class MainWindowController:
    """Controller for the main window"""

    def __init__(self, view: MainView, model: BaseModel):
        self.view = view
        self.model = model
        self.current_table_name = None
        self.current_row_data = None
        self.current_foreign_keys = {}
        self.edit_form_widgets = {}  # Holds widgets for the 'Edit' form
        self.add_form_widgets = {}   # Holds widgets for the 'Add' form

        # --- Set up data models for the Lorekeeper page ---
        self.db_tree_model = QStandardItemModel()
        self.view.ui.databaseTreeView.setModel(self.db_tree_model)

        self.db_table_model = QStandardItemModel()
        self.view.ui.databaseTableView.setModel(self.db_table_model)

        # Connect UI signals to controller methods
        self.connect_signals()

    def connect_signals(self):
        """Connect all UI signals to their handler methods."""
        self.view.ui.litographerNavButton.released.connect(
            lambda: self.view.ui.pageStack.setCurrentIndex(0)
        )
        self.view.ui.lorekeeperNavButton.released.connect(self.on_lorekeeper_selected)
        self.view.ui.databaseTreeView.clicked.connect(self.on_db_tree_item_clicked)
        self.view.ui.databaseTableView.clicked.connect(self.on_table_row_clicked)
        
        # Connect form buttons
        self.view.ui.saveChangesButton.clicked.connect(self.on_save_changes_clicked)
        self.view.ui.addNewRowButton.clicked.connect(self.on_add_new_row_clicked)
        
        # Connect tab switching to populate the 'Add' form
        self.view.ui.formTabWidget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index: int):
        """Handle tab switching to populate the 'Add New Row' form when selected."""
        # Index 1 corresponds to the 'Add New Row' tab
        if index == 1:
            self.populate_add_form()

    def on_table_row_clicked(self, index):
        """Populates the edit form with the data from the selected row."""
        first_item_in_row = self.db_table_model.item(index.row(), 0)
        if not first_item_in_row:
            return

        self.current_row_data = first_item_in_row.data(Qt.ItemDataRole.UserRole)
        
        if self.current_row_data:
            self._populate_form(self.view.ui.editFormLayout, self.edit_form_widgets, self.current_row_data)
            self.view.ui.formTabWidget.setCurrentIndex(0) # Switch to edit tab

    def populate_add_form(self):
        """Populates the 'Add New Row' tab with a blank form for the current table."""
        if not self.current_table_name:
            return
        
        # Get column names to build the form, but no data
        headers, _ = self.model.get_table_data(self.current_table_name)
        blank_data = {header: "" for header in headers}
        self._populate_form(self.view.ui.addFormLayout, self.add_form_widgets, blank_data, is_add_form=True)

    def _populate_form(self, layout: QWidget, widget_dict: dict, row_data: dict, is_add_form: bool = False):
        """Generic helper to dynamically create an editable form."""
        self._clear_layout(layout)
        widget_dict.clear()

        for key, value in row_data.items():
            # Don't create a field for 'id' in the 'Add New Row' form
            if is_add_form and key.lower() == 'id':
                continue

            label = QLabel(f"{key.replace('_', ' ').title()}:")
            
            if key in self.current_foreign_keys:
                field = self._create_dropdown(key, value)
            else:
                field = self._create_text_field(value)

            if key.lower() == 'id':
                field.setReadOnly(True)

            layout.addRow(label, field)
            widget_dict[key] = field

    def _create_dropdown(self, key, value):
        """Helper to create and populate a QComboBox for a foreign key."""
        field = QComboBox()
        referenced_table, _ = self.current_foreign_keys[key]
        
        try:
            dropdown_items = self.model.get_all_rows_as_dicts(referenced_table)
            field.addItem("None", None)
            
            current_combo_index = 0
            for i, item_dict in enumerate(dropdown_items):
                display_text = str(item_dict.get('name') or item_dict.get('first_name') or item_dict.get("faction_name") or item_dict.get("event_name") or item_dict.get('class_name') or f"ID: {item_dict['id']}")
                field.addItem(display_text, item_dict['id'])
                if item_dict['id'] == value:
                    current_combo_index = i + 1
            
            field.setCurrentIndex(current_combo_index)
        except Exception as e:
            print(f"Could not populate dropdown for {key}: {e}")
        return field

    def _create_text_field(self, value):
        """Helper to create a QLineEdit or QTextEdit based on content length."""
        str_value = str(value) if value is not None else ""
        if "\n" in str_value or len(str_value) > 60:
            field = QTextEdit(str_value)
            field.setMinimumHeight(80)
        else:
            field = QLineEdit(str_value)
        return field

    def on_save_changes_clicked(self):
        """Gathers data from the 'Edit' form and tells the model to save it."""
        self._save_form_data(self.edit_form_widgets, is_update=True)
        
    def on_add_new_row_clicked(self):
        """Gathers data from the 'Add' form and tells the model to create a new row."""
        self._save_form_data(self.add_form_widgets, is_update=False)

    def _save_form_data(self, widget_dict: dict, is_update: bool):
        """Generic helper to gather data from a form and call the model."""
        if not self.current_table_name or not widget_dict:
            print("No data to save.")
            return

        form_data = {}
        for key, widget in widget_dict.items():
            if isinstance(widget, QComboBox):
                form_data[key] = widget.currentData()
            elif isinstance(widget, QLineEdit):
                form_data[key] = widget.text()
            elif isinstance(widget, QTextEdit):
                form_data[key] = widget.toPlainText()
        
        try:
            if is_update:
                print(f"Saving changes for table '{self.current_table_name}':")
                print(form_data)
                self.model.update_row(self.current_table_name, form_data)
                self.view.ui.statusbar.showMessage(f"Successfully saved changes to '{self.current_table_name}'.", 5000)
            else:
                print(f"Adding new row to table '{self.current_table_name}':")
                print(form_data)
                # NOTE: This requires an `add_row` method in your model
                self.model.add_row(self.current_table_name, form_data)
                self.view.ui.statusbar.showMessage(f"Successfully added new row to '{self.current_table_name}'.", 5000)
                self.populate_add_form() # Clear the form after adding

            self._refresh_current_table_view()
        except Exception as e:
            print(f"Error saving data: {e}")
            self.view.ui.statusbar.showMessage(f"Error saving data: {e}", 5000)

    def on_lorekeeper_selected(self):
        """Handle switching to the Lorekeeper page."""
        self.view.ui.pageStack.setCurrentIndex(1)
        if self.db_tree_model.rowCount() == 0:
            self.load_database_structure()

    def load_database_structure(self):
        """Fetches table names from the model and populates the tree view."""
        self.db_tree_model.clear()
        self.db_tree_model.setHorizontalHeaderLabels(['Database Tables'])
        try:
            table_names = self.model.get_all_table_names()
            for table_name in table_names:
                item = QStandardItem(table_name)
                item.setEditable(False)
                self.db_tree_model.appendRow(item)
        except Exception as e:
            print(f"Error loading database structure: {e}")

    def on_db_tree_item_clicked(self, index):
        """Fetches and displays the content of the selected table when clicked."""
        self.current_table_name = self.db_tree_model.itemFromIndex(index).text()
        
        try:
            self.current_foreign_keys = self.model.get_foreign_key_info(self.current_table_name)
        except Exception as e:
            print(f"Could not get FK info for {self.current_table_name}: {e}")
            self.current_foreign_keys = {}

        self._clear_layout(self.view.ui.editFormLayout)
        self._clear_layout(self.view.ui.addFormLayout)
        
        if self.view.ui.formTabWidget.currentIndex() == 1:
            self.populate_add_form()

        self._refresh_current_table_view()

    def _refresh_current_table_view(self):
        """Helper method to reload the data in the main table view."""
        if not self.current_table_name:
            return
            
        print(f"Loading data for table: {self.current_table_name}")
        self.db_table_model.clear()

        try:
            headers, data_rows = self.model.get_table_data(self.current_table_name)
            self.db_table_model.setHorizontalHeaderLabels(headers)

            for row_tuple in data_rows:
                row_dict = dict(zip(headers, row_tuple))
                row_items = [QStandardItem(str(field)) for field in row_tuple]
                
                row_items[0].setData(row_dict, Qt.ItemDataRole.UserRole)

                for item in row_items:
                    item.setEditable(False)
                    
                self.db_table_model.appendRow(row_items)
        except Exception as e:
            print(f"Error loading table data for '{self.current_table_name}': {e}")

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
