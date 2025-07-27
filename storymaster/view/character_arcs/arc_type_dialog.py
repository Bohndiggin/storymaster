"""Arc Type Add/Edit Dialog"""

from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt
from .arc_type_dialog_ui import Ui_ArcTypeDialog
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_dialog_style,
    COLORS
)


class ArcTypeDialog(QDialog):
    """Dialog for adding or editing arc types"""
    
    def __init__(self, model, setting_id, arc_type=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.arc_type = arc_type  # None for add, ArcType object for edit
        
        # Setup UI
        self.ui = Ui_ArcTypeDialog()
        self.ui.setupUi(self)
        
        # Apply theming
        self.setStyleSheet(get_dialog_style())
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize UI components"""
        if self.arc_type:
            # Edit mode
            self.ui.titleLabel.setText("Edit Arc Type")
            self.ui.nameEdit.setText(self.arc_type.name)
            self.ui.descriptionEdit.setPlainText(self.arc_type.description or "")
        else:
            # Add mode
            self.ui.titleLabel.setText("Add Arc Type")
            
        # Apply component theming
        self.ui.titleLabel.setStyleSheet(f"color: {COLORS['text_accent']};")
        self.ui.nameEdit.setStyleSheet(get_input_style())
        self.ui.descriptionEdit.setStyleSheet(get_input_style())
        
        # Style button box
        ok_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok)
        cancel_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Cancel)
        if ok_button:
            ok_button.setStyleSheet(get_button_style('primary'))
        if cancel_button:
            cancel_button.setStyleSheet(get_button_style())
            
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
    def accept(self):
        """Handle OK button click"""
        name = self.ui.nameEdit.text().strip()
        description = self.ui.descriptionEdit.toPlainText().strip()
        
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
            'name': self.ui.nameEdit.text().strip(),
            'description': self.ui.descriptionEdit.toPlainText().strip()
        }