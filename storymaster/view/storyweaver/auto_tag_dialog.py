"""
Dialog for automatic entity tagging in documents.
"""
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QProgressBar
)
from PySide6.QtCore import Qt


class AutoTagDialog(QDialog):
    """Dialog to preview and confirm automatic entity tagging."""

    def __init__(self, matches: List[Dict[str, Any]], parent=None):
        """
        Initialize the auto-tag dialog.

        Args:
            matches: List of found entity matches with keys:
                - entity_name: Name of the entity
                - entity_id: ID of the entity
                - entity_type: Type (character, location, faction)
                - count: Number of occurrences in the document
                - positions: List of (start, end) positions in text
        """
        super().__init__(parent)
        self.matches = matches
        self.selected_entities = set()  # Set of entity_ids to tag

        self.setWindowTitle("Auto-Tag Entities")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Found entities in your document. Select which ones to tag:")
        header.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(header)

        # Table of matches
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tag", "Entity Name", "Type", "Occurrences"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Select buttons
        button_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        button_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_row.addWidget(deselect_all_btn)

        button_row.addStretch()
        layout.addLayout(button_row)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        action_row.addWidget(cancel_btn)

        tag_btn = QPushButton("Tag Selected")
        tag_btn.setDefault(True)
        tag_btn.clicked.connect(self.accept)
        tag_btn.setStyleSheet("background-color: #4A9EFF; font-weight: bold;")
        action_row.addWidget(tag_btn)

        layout.addLayout(action_row)

    def _populate_table(self):
        """Populate the table with entity matches."""
        self.table.setRowCount(len(self.matches))

        for row, match in enumerate(self.matches):
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Default to selected
            checkbox.stateChanged.connect(lambda state, eid=match["entity_id"]: self._on_checkbox_changed(state, eid))

            # Center the checkbox
            checkbox_widget = QTableWidgetItem()
            self.table.setItem(row, 0, checkbox_widget)
            self.table.setCellWidget(row, 0, checkbox)

            # Entity name
            name_item = QTableWidgetItem(match["entity_name"])
            self.table.setItem(row, 1, name_item)

            # Type
            type_item = QTableWidgetItem(match["entity_type"].capitalize())
            self.table.setItem(row, 2, type_item)

            # Occurrence count
            count_item = QTableWidgetItem(str(match["count"]))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, count_item)

            # Add to selected by default
            self.selected_entities.add(match["entity_id"])

    def _on_checkbox_changed(self, state, entity_id):
        """Handle checkbox state change."""
        if state == Qt.Checked:
            self.selected_entities.add(entity_id)
        else:
            self.selected_entities.discard(entity_id)

    def _select_all(self):
        """Select all entities."""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def _deselect_all(self):
        """Deselect all entities."""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def get_selected_entities(self) -> set:
        """Get the set of selected entity IDs."""
        return self.selected_entities
