"""Arc Point Add/Edit Dialog"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt


class ArcPointDialog(QDialog):
    """Dialog for adding or editing arc points"""
    
    def __init__(self, model, arc_id, storyline_id, arc_point=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.arc_id = arc_id
        self.storyline_id = storyline_id
        self.arc_point = arc_point  # None for add, ArcPoint object for edit
        
        # Load UI
        ui_path = os.path.join(os.path.dirname(__file__), "arc_point_dialog.ui")
        uic.loadUi(ui_path, self)
        
        self.setup_ui()
        self.load_nodes()
        
    def setup_ui(self):
        """Initialize UI components"""
        if self.arc_point:
            # Edit mode
            self.titleLabel.setText("Edit Arc Point")
            self.orderSpinBox.setValue(self.arc_point.order_index)
            self.titleEdit.setText(self.arc_point.title)
            self.descriptionEdit.setPlainText(self.arc_point.description or "")
            self.emotionalStateEdit.setPlainText(self.arc_point.emotional_state or "")
            self.relationshipsEdit.setPlainText(self.arc_point.character_relationships or "")
            self.goalsEdit.setPlainText(self.arc_point.goals or "")
            self.conflictEdit.setPlainText(self.arc_point.internal_conflict or "")
            
            # Set node selection
            if self.arc_point.node_id:
                for i in range(self.nodeComboBox.count()):
                    if self.nodeComboBox.itemData(i) == self.arc_point.node_id:
                        self.nodeComboBox.setCurrentIndex(i)
                        break
        else:
            # Add mode
            self.titleLabel.setText("Add Arc Point")
            # Set next order index
            try:
                existing_points = self.model.get_arc_points(self.arc_id)
                next_order = max([p.order_index for p in existing_points], default=0) + 1
                self.orderSpinBox.setValue(next_order)
            except Exception:
                self.orderSpinBox.setValue(1)
                
        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
    def load_nodes(self):
        """Load available story nodes into the combo box"""
        try:
            # Clear existing items except "No Node"
            self.nodeComboBox.clear()
            self.nodeComboBox.addItem("No Node", None)
            
            # Get nodes for the current storyline
            nodes = self.model.get_nodes_for_storyline(self.storyline_id)
            
            for node in nodes:
                display_text = f"Node {node.id}: {node.label or 'Untitled'}"
                self.nodeComboBox.addItem(display_text, node.id)
                
        except Exception as e:
            print(f"Warning: Could not load nodes: {e}")
            
    def accept(self):
        """Handle OK button click"""
        title = self.titleEdit.text().strip()
        order_index = self.orderSpinBox.value()
        description = self.descriptionEdit.toPlainText().strip()
        emotional_state = self.emotionalStateEdit.toPlainText().strip()
        relationships = self.relationshipsEdit.toPlainText().strip()
        goals = self.goalsEdit.toPlainText().strip()
        conflict = self.conflictEdit.toPlainText().strip()
        node_id = self.nodeComboBox.currentData()
        
        if not title:
            QMessageBox.warning(self, "Validation Error", "Arc point title is required.")
            return
            
        try:
            if self.arc_point:
                # Edit existing arc point
                self.model.update_arc_point(
                    self.arc_point.id,
                    title=title,
                    order_index=order_index,
                    description=description if description else None,
                    emotional_state=emotional_state if emotional_state else None,
                    character_relationships=relationships if relationships else None,
                    goals=goals if goals else None,
                    internal_conflict=conflict if conflict else None,
                    node_id=node_id
                )
            else:
                # Create new arc point
                self.model.create_arc_point(
                    arc_id=self.arc_id,
                    title=title,
                    order_index=order_index,
                    description=description if description else None,
                    emotional_state=emotional_state if emotional_state else None,
                    character_relationships=relationships if relationships else None,
                    goals=goals if goals else None,
                    internal_conflict=conflict if conflict else None,
                    node_id=node_id
                )
                
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save arc point: {e}")
            
    def get_result(self):
        """Get the dialog result data"""
        return {
            'title': self.titleEdit.text().strip(),
            'order_index': self.orderSpinBox.value(),
            'description': self.descriptionEdit.toPlainText().strip(),
            'emotional_state': self.emotionalStateEdit.toPlainText().strip(),
            'character_relationships': self.relationshipsEdit.toPlainText().strip(),
            'goals': self.goalsEdit.toPlainText().strip(),
            'internal_conflict': self.conflictEdit.toPlainText().strip(),
            'node_id': self.nodeComboBox.currentData()
        }