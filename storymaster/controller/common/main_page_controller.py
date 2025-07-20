"""Holds the controller for the main page"""
import pprint
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView


class MainWindowController:
    """Controller for the main window"""

    def __init__(self, view: MainView, model: BaseModel):
        self.view = view
        self.model = model
        self.current_table_name = None # To keep track of the currently displayed table
        self.current_foreign_keys = {} # To store FK info for the current table

        # --- Set up data models for the Lorekeeper page ---
        # Model for the list of database tables
        self.db_tree_model = QStandardItemModel()
        self.view.ui.databaseTreeView.setModel(self.db_tree_model)

        # Model for the data within a selected table
        self.db_table_model = QStandardItemModel()
        self.view.ui.databaseTableView.setModel(self.db_table_model)

        # Connect UI signals to controller methods
        self.connect_signals()

    def connect_signals(self):
        """Connect all UI signals to their handler methods."""
        # Page navigation
        self.view.ui.litographerNavButton.released.connect(
            lambda: self.view.ui.pageStack.setCurrentIndex(0)
        )
        self.view.ui.lorekeeperNavButton.released.connect(self.on_lorekeeper_selected)

        # Lorekeeper view signals
        self.view.ui.databaseTreeView.clicked.connect(self.on_db_tree_item_clicked)
        self.view.ui.databaseTableView.clicked.connect(self.on_table_cell_clicked)

    def on_table_cell_clicked(self, index):
        """
        Displays the full dictionary of the selected row. If a foreign key cell
        is clicked, it displays the data of the referenced foreign row.
        """
        # Get the header/column name for the clicked cell
        column_index = index.column()
        if column_index == 0:  # It's the row number column, show the current row's data
            self.show_current_row_data(index)
            return

        header_item = self.db_table_model.horizontalHeaderItem(column_index)
        if not header_item:
            return
        column_name = header_item.text()

        # Check if the clicked column is a foreign key
        if column_name in self.current_foreign_keys:
            foreign_key_value = index.data()
            if foreign_key_value is None or str(foreign_key_value).strip() == "":
                self.show_current_row_data(index)  # Fallback for empty FK cells
                return

            try:
                fk_id = int(foreign_key_value)
                # Get the table it refers to
                referenced_table, _ = self.current_foreign_keys[column_name]
                
                # Fetch the foreign row data from the model
                # NOTE: This requires get_row_by_id to be implemented in your model
                foreign_row_dict = self.model.get_row_by_id(referenced_table, fk_id)

                if foreign_row_dict:
                    display_text = f"--- Foreign Data from '{referenced_table}' (ID: {fk_id}) ---\n\n"
                    display_text += pprint.pformat(foreign_row_dict)
                    self.view.ui.cellContentDisplay.setText(display_text)
                else:
                    self.view.ui.cellContentDisplay.setText(f"No data found in table '{referenced_table}' with ID: {fk_id}")

            except (ValueError, TypeError):
                # If the FK value isn't a valid ID, just show the current row
                self.show_current_row_data(index)
        else:
            # Default behavior: show the data for the currently selected row
            self.show_current_row_data(index)

    def show_current_row_data(self, index):
        """Helper method to display the data of the currently clicked row."""
        first_item_in_row = self.db_table_model.item(index.row(), 0)
        if not first_item_in_row:
            return
        
        row_dict = first_item_in_row.data(Qt.ItemDataRole.UserRole)
        if row_dict:
            display_text = f"--- Data from '{self.current_table_name}' ---\n\n"
            display_text += pprint.pformat(row_dict)
            self.view.ui.cellContentDisplay.setText(display_text)

    def on_lorekeeper_selected(self):
        """Handle switching to the Lorekeeper page."""
        self.view.ui.pageStack.setCurrentIndex(1)
        # Load the database structure if it hasn't been loaded yet
        if self.db_tree_model.rowCount() == 0:
            self.load_database_structure()

    def load_database_structure(self):
        """
        Fetches table names from the model and populates the tree view.
        """
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
        """
        Fetches and displays the content of the selected table when clicked.
        """
        self.current_table_name = self.db_tree_model.itemFromIndex(index).text()
        print(f"Loading data for table: {self.current_table_name}")
        try:
            self.current_foreign_keys = self.model.get_foreign_key_info(self.current_table_name)
        except Exception as e:
            print(f"Could not get FK info for {self.current_table_name}: {e}")
            self.current_foreign_keys = {}


        self.db_table_model.clear()

        try:
            headers, data_rows = self.model.get_table_data(self.current_table_name)
            
            self.db_table_model.setHorizontalHeaderLabels(headers)

            for i, row_tuple in enumerate(data_rows):
                row_dict = dict(zip(headers, row_tuple))
                row_items = [QStandardItem(str(field)) for field in row_tuple]
                
                full_row_items = row_items
                full_row_items[0].setData(row_dict, Qt.ItemDataRole.UserRole)

                # Make all cells read-only
                for item in full_row_items:
                    item.setEditable(False)
                    
                self.db_table_model.appendRow(full_row_items)
        except Exception as e:
            print(f"Error loading table data for '{self.current_table_name}': {e}")
