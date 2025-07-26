"""Arc Type Manager Dialog"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt

from .arc_type_dialog import ArcTypeDialog


class ArcTypeManagerDialog(QDialog):
    """Dialog for managing arc types"""
    
    def __init__(self, model, setting_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.current_arc_type = None
        
        # Load UI
        ui_path = os.path.join(os.path.dirname(__file__), "arc_type_manager_dialog.ui")
        uic.loadUi(ui_path, self)
        
        self.setup_ui()
        self.connect_signals()
        self.refresh_arc_types()
        
    def setup_ui(self):
        """Initialize UI components"""
        # Configure table
        self.arcTypesTable.setSelectionBehavior(self.arcTypesTable.SelectionBehavior.SelectRows)
        self.arcTypesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.arcTypesTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
    def connect_signals(self):
        """Connect widget signals"""
        self.addArcTypeButton.clicked.connect(self.on_add_arc_type)
        self.editArcTypeButton.clicked.connect(self.on_edit_arc_type)
        self.deleteArcTypeButton.clicked.connect(self.on_delete_arc_type)
        self.arcTypesTable.itemSelectionChanged.connect(self.on_selection_changed)
        self.arcTypesTable.itemDoubleClicked.connect(self.on_edit_arc_type)
        
    def refresh_arc_types(self):
        """Refresh the arc types table"""
        self.arcTypesTable.setRowCount(0)
        
        try:
            arc_types = self.model.get_arc_types(self.setting_id)
            
            self.arcTypesTable.setRowCount(len(arc_types))
            
            for row, arc_type in enumerate(arc_types):
                # Name
                name_item = QTableWidgetItem(arc_type.name)
                name_item.setData(Qt.ItemDataRole.UserRole, arc_type.id)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.arcTypesTable.setItem(row, 0, name_item)
                
                # Description
                description = arc_type.description or ""
                desc_item = QTableWidgetItem(description)
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.arcTypesTable.setItem(row, 1, desc_item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc types: {e}")
            
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.arcTypesTable.selectedItems()
        
        if selected_items:
            row = selected_items[0].row()
            arc_type_id = self.arcTypesTable.item(row, 0).data(Qt.ItemDataRole.UserRole)
            
            try:
                self.current_arc_type = self.model.get_arc_type(arc_type_id)
                self.editArcTypeButton.setEnabled(True)
                self.deleteArcTypeButton.setEnabled(True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load arc type: {e}")
                self.current_arc_type = None
                self.editArcTypeButton.setEnabled(False)
                self.deleteArcTypeButton.setEnabled(False)
        else:
            self.current_arc_type = None
            self.editArcTypeButton.setEnabled(False)
            self.deleteArcTypeButton.setEnabled(False)
            
    def on_add_arc_type(self):
        """Handle add arc type button"""
        dialog = ArcTypeDialog(self.model, self.setting_id, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_arc_types()
            QMessageBox.information(self, "Success", "Arc type added successfully.")
            
    def on_edit_arc_type(self):
        """Handle edit arc type button"""
        if not self.current_arc_type:
            return
            
        dialog = ArcTypeDialog(self.model, self.setting_id, self.current_arc_type, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_arc_types()
            QMessageBox.information(self, "Success", "Arc type updated successfully.")
            
    def on_delete_arc_type(self):
        """Handle delete arc type button"""
        if not self.current_arc_type:
            return
            
        reply = QMessageBox.question(
            self, "Delete Arc Type", 
            f"Are you sure you want to delete the arc type '{self.current_arc_type.name}'?\n\n"
            "This will also delete all character arcs using this type.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_arc_type(self.current_arc_type.id)
                self.refresh_arc_types()
                QMessageBox.information(self, "Success", "Arc type deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete arc type: {e}")