"""Arc Type Add/Edit Dialog"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt


class ArcTypeDialog(QDialog):
    """Dialog for adding or editing arc types"""
    
    def __init__(self, model, setting_id, arc_type=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.arc_type = arc_type  # None for add, ArcType object for edit
        
        # Load UI
        ui_path = os.path.join(os.path.dirname(__file__), "arc_type_dialog.ui")
        uic.loadUi(ui_path, self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize UI components"""
        if self.arc_type:
            # Edit mode
            self.titleLabel.setText("Edit Arc Type")
            self.nameEdit.setText(self.arc_type.name)
            self.descriptionEdit.setPlainText(self.arc_type.description or "")
        else:
            # Add mode
            self.titleLabel.setText("Add Arc Type")
            
        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
    def accept(self):
        """Handle OK button click"""
        name = self.nameEdit.text().strip()
        description = self.descriptionEdit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Arc type name is required.")
            return
            
        try:
            if self.arc_type:
                # Edit existing arc type
                self.model.update_arc_type(
                    self.arc_type.id, 
                    name=name, 
                    description=description if description else None
                )
            else:
                # Create new arc type
                self.model.create_arc_type(
                    name=name, 
                    description=description if description else None, 
                    setting_id=self.setting_id
                )
                
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save arc type: {e}")
            
    def get_result(self):
        """Get the dialog result data"""
        return {
            'name': self.nameEdit.text().strip(),
            'description': self.descriptionEdit.toPlainText().strip()
        }