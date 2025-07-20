"""Holds the controller for the main page"""
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit
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
        self.form_widgets = {}  # To hold references to the generated input fields

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
        self.view.ui.saveChangesButton.clicked.connect(self.on_save_changes_clicked)

    def on_table_row_clicked(self, index):
        """Populates the edit form with the data from the selected row."""
        first_item_in_row = self.db_table_model.item(index.row(), 0)
        if not first_item_in_row:
            return

        # Retrieve the full row data dictionary stored in the item
        self.current_row_data = first_item_in_row.data(Qt.ItemDataRole.UserRole)
        
        if self.current_row_data:
            self.populate_edit_form(self.current_row_data)

    def populate_edit_form(self, row_data: dict):
        """Dynamically creates an editable form based on the row data."""
        self._clear_layout(self.view.ui.editFormLayout)
        self.form_widgets.clear()

        for key, value in row_data.items():
            label = QLabel(f"{key.replace('_', ' ').title()}:")
            
            # Use QTextEdit for long text, QLineEdit for others
            str_value = str(value) if value is not None else ""
            if "\n" in str_value or len(str_value) > 60:
                field = QTextEdit(str_value)
                field.setMinimumHeight(80)
            else:
                field = QLineEdit(str_value)

            # Make the 'id' field read-only
            if key.lower() == 'id':
                field.setReadOnly(True)

            self.view.ui.editFormLayout.addRow(label, field)
            self.form_widgets[key] = field

    def on_save_changes_clicked(self):
        """Gathers data from the form and tells the model to save it."""
        if not self.current_row_data or not self.form_widgets:
            print("No data selected to save.")
            return

        updated_data = {}
        for key, widget in self.form_widgets.items():
            if isinstance(widget, QLineEdit):
                updated_data[key] = widget.text()
            elif isinstance(widget, QTextEdit):
                updated_data[key] = widget.toPlainText()
        
        print(f"Saving changes for table '{self.current_table_name}':")
        print(updated_data)

        # Call the model to update the database
        try:
            if not self.current_table_name:
                return
            self.model.update_row(self.current_table_name, updated_data)
            # Refresh the table view to show changes
            self._refresh_current_table_view()
            self.view.ui.statusbar.showMessage(f"Successfully saved changes to '{self.current_table_name}'.", 5000)
        except Exception as e:
            print(f"Error updating row: {e}")
            self.view.ui.statusbar.showMessage(f"Error saving changes: {e}", 5000)


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
        self._clear_layout(self.view.ui.editFormLayout) # Clear form when table changes
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
                
                # Store the full dictionary in the first item of the row
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
