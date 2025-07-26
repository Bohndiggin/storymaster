"""Character Arc Management Widget"""

from PyQt6.QtWidgets import QWidget, QListWidgetItem, QTreeWidgetItem, QMessageBox, QDialog
from PyQt6.QtCore import Qt, pyqtSignal

from storymaster.model.database import schema
from .arc_type_manager_dialog import ArcTypeManagerDialog
from .arc_point_dialog import ArcPointDialog
from .character_arc_dialog import CharacterArcDialog
from .character_arc_widget_ui import Ui_CharacterArcWidget


class CharacterArcWidget(QWidget):
    """Main widget for managing character arcs"""
    
    # Signals
    arc_selected = pyqtSignal(int)  # arc_id
    arc_point_selected = pyqtSignal(int)  # arc_point_id
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.current_arc_id = None
        self.current_arc_point_id = None
        self.current_storyline_id = None
        
        # Setup UI
        self.ui = Ui_CharacterArcWidget()
        self.ui.setupUi(self)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Initialize UI components"""
        # Set initial states
        self.ui.arcDetailsTabWidget.setEnabled(False)
        
        # Configure tree widget
        self.ui.arcPointsTreeWidget.setRootIsDecorated(False)
        self.ui.arcPointsTreeWidget.setAlternatingRowColors(True)
        self.ui.arcPointsTreeWidget.setSortingEnabled(True)
        self.ui.arcPointsTreeWidget.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def connect_signals(self):
        """Connect widget signals"""
        # Arc management buttons
        self.ui.newArcButton.clicked.connect(self.on_new_arc)
        self.ui.editArcButton.clicked.connect(self.on_edit_arc)
        self.ui.deleteArcButton.clicked.connect(self.on_delete_arc)
        self.ui.manageArcTypesButton.clicked.connect(self.on_manage_arc_types)
        
        # Arc point management buttons
        self.ui.newArcPointButton.clicked.connect(self.on_new_arc_point)
        self.ui.editArcPointButton.clicked.connect(self.on_edit_arc_point)
        self.ui.deleteArcPointButton.clicked.connect(self.on_delete_arc_point)
        
        # Selection events
        self.ui.arcListWidget.itemSelectionChanged.connect(self.on_arc_selection_changed)
        self.ui.arcPointsTreeWidget.itemSelectionChanged.connect(self.on_arc_point_selection_changed)
        
    def refresh_arcs(self, storyline_id=None):
        """Refresh the list of character arcs"""
        self.current_storyline_id = storyline_id
        self.ui.arcListWidget.clear()
        
        # Don't try to load arcs if no storyline is selected
        if not storyline_id:
            return
        
        try:
            arcs = self.model.get_character_arcs(storyline_id)
            
            # Ensure arcs is iterable (handle case where Mock is returned)
            if not hasattr(arcs, '__iter__'):
                arcs = []
            
            for arc in arcs:
                item = QListWidgetItem()
                item.setText(f"{arc.title} ({arc.arc_type.name})")
                item.setData(Qt.ItemDataRole.UserRole, arc.id)
                
                # Add character names as tooltip
                character_names = [arc_to_actor.actor.first_name or "Unknown" for arc_to_actor in arc.actors]
                if character_names:
                    item.setToolTip(f"Characters: {', '.join(character_names)}")
                
                self.ui.arcListWidget.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load character arcs: {e}")
            
    def refresh_arc_points(self):
        """Refresh the arc points for the current arc"""
        self.ui.arcPointsTreeWidget.clear()
        
        if not self.current_arc_id:
            return
            
        try:
            arc_points = self.model.get_arc_points(self.current_arc_id)  # We'll implement this
            
            for point in arc_points:
                item = QTreeWidgetItem()
                item.setText(0, str(point.order_index))
                item.setText(1, point.title)
                item.setText(2, f"Node {point.node_id}" if point.node_id else "No Node")
                item.setText(3, point.emotional_state or "")
                item.setData(0, Qt.ItemDataRole.UserRole, point.id)
                
                self.ui.arcPointsTreeWidget.addTopLevelItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc points: {e}")
    
    def on_arc_selection_changed(self):
        """Handle arc selection change"""
        selected_items = self.ui.arcListWidget.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            arc_id = item.data(Qt.ItemDataRole.UserRole)
            self.current_arc_id = arc_id
            
            # Enable/disable buttons
            self.ui.editArcButton.setEnabled(True)
            self.ui.deleteArcButton.setEnabled(True)
            self.ui.arcDetailsTabWidget.setEnabled(True)
            self.ui.newArcPointButton.setEnabled(True)
            
            # Load arc details
            self.load_arc_details(arc_id)
            self.refresh_arc_points()
            
            # Emit signal
            self.arc_selected.emit(arc_id)
        else:
            self.current_arc_id = None
            self.ui.editArcButton.setEnabled(False)
            self.ui.deleteArcButton.setEnabled(False)
            self.ui.arcDetailsTabWidget.setEnabled(False)
            self.ui.newArcPointButton.setEnabled(False)
            self.clear_arc_details()
            
    def on_arc_point_selection_changed(self):
        """Handle arc point selection change"""
        selected_items = self.ui.arcPointsTreeWidget.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            arc_point_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.current_arc_point_id = arc_point_id
            
            self.ui.editArcPointButton.setEnabled(True)
            self.ui.deleteArcPointButton.setEnabled(True)
            
            # Emit signal
            self.arc_point_selected.emit(arc_point_id)
        else:
            self.current_arc_point_id = None
            self.ui.editArcPointButton.setEnabled(False)
            self.ui.deleteArcPointButton.setEnabled(False)
    
    def load_arc_details(self, arc_id):
        """Load and display arc details"""
        try:
            arc = self.model.get_character_arc(arc_id)  # We'll implement this
            
            self.ui.arcTitleEdit.setText(arc.title)
            self.ui.arcTypeEdit.setText(arc.arc_type.name)
            self.ui.arcDescriptionEdit.setPlainText(arc.description or "")
            
            # Load character names
            character_names = []
            for arc_to_actor in arc.actors:
                actor = arc_to_actor.actor
                name_parts = [actor.first_name, actor.last_name]
                full_name = " ".join(part for part in name_parts if part)
                character_names.append(full_name or "Unknown")
            
            self.ui.charactersEdit.setText(", ".join(character_names))
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc details: {e}")
            
    def clear_arc_details(self):
        """Clear arc details display"""
        self.ui.arcTitleEdit.clear()
        self.ui.arcTypeEdit.clear()
        self.ui.arcDescriptionEdit.clear()
        self.ui.charactersEdit.clear()
        self.ui.arcPointsTreeWidget.clear()
    
    # Placeholder methods for button handlers - we'll implement these next
    def on_new_arc(self):
        """Handle new arc button"""
        if not self.current_storyline_id:
            QMessageBox.warning(self, "No Storyline", "Please select a storyline first.")
            return
            
        try:
            # Get current setting ID from the model's first setting
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(self, "No Settings", "No settings found. Please create a setting first.")
                return
                
            setting_id = settings[0].id  # Use first setting
            
            dialog = CharacterArcDialog(
                self.model, 
                self.current_storyline_id,
                setting_id,
                parent=self
            )
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_arcs(self.current_storyline_id)
                QMessageBox.information(self, "Success", "Character arc added successfully.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create character arc: {e}")
        
    def on_edit_arc(self):
        """Handle edit arc button"""
        if not self.current_arc_id or not self.current_storyline_id:
            return
            
        try:
            # Get current setting ID from the model's first setting
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(self, "No Settings", "No settings found. Please create a setting first.")
                return
                
            setting_id = settings[0].id  # Use first setting
            
            # Get the character arc data
            character_arc = self.model.get_character_arc(self.current_arc_id)
            
            dialog = CharacterArcDialog(
                self.model, 
                self.current_storyline_id,
                setting_id,
                character_arc,
                parent=self
            )
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_arcs(self.current_storyline_id)
                self.load_arc_details(self.current_arc_id)  # Refresh the details view
                QMessageBox.information(self, "Success", "Character arc updated successfully.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit character arc: {e}")
        
    def on_delete_arc(self):
        """Handle delete arc button"""
        if not self.current_arc_id:
            return
            
        reply = QMessageBox.question(
            self, "Delete Arc", 
            "Are you sure you want to delete this character arc?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_character_arc(self.current_arc_id)
                self.refresh_arcs(self.current_storyline_id)
                QMessageBox.information(self, "Success", "Arc deleted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete arc: {e}")
        
    def on_manage_arc_types(self):
        """Handle manage arc types button"""
        # We need the current setting ID - for now use a default approach
        try:
            # Get current setting ID from the model's first setting
            settings = self.model.get_all_settings()
            if not settings:
                QMessageBox.warning(self, "No Settings", "No settings found. Please create a setting first.")
                return
                
            setting_id = settings[0].id  # Use first setting
            
            dialog = ArcTypeManagerDialog(self.model, setting_id, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open arc type manager: {e}")
        
    def on_new_arc_point(self):
        """Handle new arc point button"""
        if not self.current_arc_id or not self.current_storyline_id:
            return
            
        dialog = ArcPointDialog(
            self.model, 
            self.current_arc_id, 
            self.current_storyline_id, 
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_arc_points()
            QMessageBox.information(self, "Success", "Arc point added successfully.")
        
    def on_edit_arc_point(self):
        """Handle edit arc point button"""
        if not self.current_arc_point_id or not self.current_storyline_id:
            return
            
        try:
            # Get the arc point data
            arc_points = self.model.get_arc_points(self.current_arc_id)
            arc_point = next((p for p in arc_points if p.id == self.current_arc_point_id), None)
            
            if not arc_point:
                QMessageBox.warning(self, "Error", "Arc point not found.")
                return
                
            dialog = ArcPointDialog(
                self.model, 
                self.current_arc_id, 
                self.current_storyline_id, 
                arc_point,
                parent=self
            )
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_arc_points()
                QMessageBox.information(self, "Success", "Arc point updated successfully.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit arc point: {e}")
        
    def on_delete_arc_point(self):
        """Handle delete arc point button"""
        if not self.current_arc_point_id:
            return
            
        reply = QMessageBox.question(
            self, "Delete Arc Point", 
            "Are you sure you want to delete this arc point?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_arc_point(self.current_arc_point_id)
                self.refresh_arc_points()
                QMessageBox.information(self, "Success", "Arc point deleted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete arc point: {e}")