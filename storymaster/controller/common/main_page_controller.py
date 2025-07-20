"""Holds the controller for the main page"""
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt6.QtCore import Qt
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView
# Import the dialogs
from storymaster.view.litographer.add_node_dialog import AddNodeDialog
from storymaster.view.common.open_project_dialog import OpenProjectDialog


class MainWindowController:
    """Controller for the main window"""

    def __init__(self, view: MainView, model: BaseModel):
        self.view = view
        self.model = model
        self.current_project_id = 1 # Default to project 1
        self.current_table_name = None
        self.current_row_data = None
        self.current_foreign_keys = {}
        self.edit_form_widgets = {}
        self.add_form_widgets = {}

        # --- Set up Lorekeeper models ---
        self.db_tree_model = QStandardItemModel()
        self.view.ui.databaseTreeView.setModel(self.db_tree_model)
        self.db_table_model = QStandardItemModel()
        self.view.ui.databaseTableView.setModel(self.db_table_model)

        # --- Set up Litographer scene ---
        self.node_scene = QGraphicsScene()
        self.view.ui.nodeGraphView.setScene(self.node_scene)

        self.connect_signals()
        self.on_litographer_selected() # Start on the litographer page

    def connect_signals(self):
        """Connect all UI signals to their handler methods."""
        # --- Page Navigation ---
        self.view.ui.litographerNavButton.released.connect(self.on_litographer_selected)
        self.view.ui.lorekeeperNavButton.released.connect(self.on_lorekeeper_selected)
        
        # --- File Menu ---
        self.view.ui.actionOpen.triggered.connect(self.on_open_project_clicked)

        # --- Litographer Toolbar ---
        self.view.ui.actionAddNode.triggered.connect(self.on_add_node_clicked)

        # --- Lorekeeper View Signals ---
        self.view.ui.databaseTreeView.clicked.connect(self.on_db_tree_item_clicked)
        self.view.ui.databaseTableView.clicked.connect(self.on_table_row_clicked)
        
        # --- Lorekeeper Form Buttons ---
        self.view.ui.saveChangesButton.clicked.connect(self.on_save_changes_clicked)
        self.view.ui.addNewRowButton.clicked.connect(self.on_add_new_row_clicked)
        self.view.ui.formTabWidget.currentChanged.connect(self.on_tab_changed)

    # --- Project Handling ---
    def on_open_project_clicked(self):
        """Opens a dialog to select a project."""
        dialog = OpenProjectDialog(self.model, self.view)
        project_id = dialog.get_selected_project_id()
        if project_id is not None:
            self.current_project_id = project_id
            print(f"Switched to Project ID: {self.current_project_id}")
            self.view.ui.statusbar.showMessage(f"Opened Project ID: {self.current_project_id}", 5000)
            
            # Refresh the current view with the new project's data
            if self.view.ui.pageStack.currentIndex() == 0:
                self.load_and_draw_nodes()
            else:
                self._refresh_current_table_view()


    # --- Litographer Methods ---

    def on_litographer_selected(self):
        """Handle switching to the Litographer page and loading nodes."""
        self.view.ui.pageStack.setCurrentIndex(0)
        self.load_and_draw_nodes()

    def on_add_node_clicked(self):
        """Handles the 'Add Node' action by opening a dialog."""
        dialog = AddNodeDialog(self.view)
        new_node_data = dialog.get_data()

        if new_node_data:
            new_node_data['project_id'] = self.current_project_id
            
            try:
                self.model.add_row('litography_node', new_node_data)
                self.view.ui.statusbar.showMessage("Successfully added new node.", 5000)
                self.load_and_draw_nodes()
            except Exception as e:
                print(f"Error adding new node: {e}")
                self.view.ui.statusbar.showMessage(f"Error: {e}", 5000)


    def load_and_draw_nodes(self):
        """Fetches node data from the model and draws them on the scene."""
        self.node_scene.clear()
        
        nodes = self.model.get_litography_nodes(project_id=self.current_project_id)
        
        x_pos = 0
        for i, node in enumerate(nodes):
            y_pos = self.view.ui.nodeGraphView.height() - (node.node_height * 200) - 100
            rect_item = QGraphicsRectItem(x_pos, y_pos, 100, 60)
            rect_item.setBrush(QBrush(QColor("#5c4a8e")))
            self.node_scene.addItem(rect_item)
            x_pos += 120


    # --- Lorekeeper Methods ---

    def on_tab_changed(self, index: int):
        """Handle tab switching to populate the 'Add New Row' form when selected."""
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
            self.view.ui.formTabWidget.setCurrentIndex(0)

    def populate_add_form(self):
        """Populates the 'Add New Row' tab with a blank form for the current table."""
        if not self.current_table_name:
            return
        
        # NOTE: Assumes get_table_data can accept a project_id to get correct headers
        headers, _ = self.model.get_table_data(self.current_table_name, project_id=self.current_project_id)
        blank_data = {header: "" for header in headers}
        self._populate_form(self.view.ui.addFormLayout, self.add_form_widgets, blank_data, is_add_form=True)

    def _populate_form(self, layout: QWidget, widget_dict: dict, row_data: dict, is_add_form: bool = False):
        """Generic helper to dynamically create an editable form."""
        self._clear_layout(layout)
        widget_dict.clear()

        for key, value in row_data.items():
            if is_add_form and key.lower() in ['id', 'group_id', 'project_id']:
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
            # NOTE: Assumes get_all_rows_as_dicts can be filtered by project
            dropdown_items = self.model.get_all_rows_as_dicts(referenced_table, project_id=self.current_project_id)
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
                # The ID is already in the form_data for updates
                self.model.update_row(self.current_table_name, form_data)
                self.view.ui.statusbar.showMessage(f"Successfully saved changes to '{self.current_table_name}'.", 5000)
            else:
                # NOTE: Assumes add_row can accept a project_id to find the correct group
                self.model.add_row(self.current_table_name, form_data, project_id=self.current_project_id)
                self.view.ui.statusbar.showMessage(f"Successfully added new row to '{self.current_table_name}'.", 5000)
                self.populate_add_form()

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
            
        self.db_table_model.clear()

        try:
            # Pass the current project ID to filter the data
            headers, data_rows = self.model.get_table_data(self.current_table_name, project_id=self.current_project_id)
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
