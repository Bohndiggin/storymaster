"""
Dialog for managing notes linked to a litography node.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QSplitter,
    QGroupBox,
    QLabel,
)
from PyQt6.QtCore import Qt
from storymaster.model.database.schema.base import NoteType


class NodeNotesDialog(QDialog):
    """
    Dialog for viewing and managing notes linked to a specific node.
    """

    def __init__(self, node_data, controller, parent=None):
        super().__init__(parent)
        self.node_data = node_data
        self.controller = controller
        self.current_note = None
        
        self.setWindowTitle(f"Notes for Node (Type: {node_data.node_type.name.title()})")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_notes()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout()
        
        # Node info section
        node_info_group = QGroupBox("Node Information")
        node_info_layout = QFormLayout()
        node_info_layout.addRow("Node Type:", QLabel(self.node_data.node_type.name.title()))
        node_info_layout.addRow("Node Height:", QLabel(f"{self.node_data.node_height:.2f}"))
        node_info_group.setLayout(node_info_layout)
        main_layout.addWidget(node_info_group)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Notes list
        left_widget = QGroupBox("Notes")
        left_layout = QVBoxLayout()
        
        self.notes_list = QListWidget()
        self.notes_list.itemSelectionChanged.connect(self.on_note_selected)
        left_layout.addWidget(self.notes_list)
        
        # List control buttons
        list_buttons_layout = QHBoxLayout()
        self.add_note_btn = QPushButton("Add Note")
        self.delete_note_btn = QPushButton("Delete Note")
        self.delete_note_btn.setEnabled(False)
        
        self.add_note_btn.clicked.connect(self.add_note)
        self.delete_note_btn.clicked.connect(self.delete_note)
        
        list_buttons_layout.addWidget(self.add_note_btn)
        list_buttons_layout.addWidget(self.delete_note_btn)
        left_layout.addLayout(list_buttons_layout)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right side - Note editor
        right_widget = QGroupBox("Note Editor")
        right_layout = QFormLayout()
        
        self.note_type_combo = QComboBox()
        for note_type in NoteType:
            self.note_type_combo.addItem(note_type.name.title(), note_type)
        
        self.note_title_edit = QLineEdit()
        self.note_description_edit = QTextEdit()
        
        right_layout.addRow("Note Type:", self.note_type_combo)
        right_layout.addRow("Title:", self.note_title_edit)
        right_layout.addRow("Description:", self.note_description_edit)
        
        # Note editor buttons
        editor_buttons_layout = QHBoxLayout()
        self.save_note_btn = QPushButton("Save Note")
        self.cancel_edit_btn = QPushButton("Cancel")
        
        self.save_note_btn.clicked.connect(self.save_note)
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        
        editor_buttons_layout.addWidget(self.save_note_btn)
        editor_buttons_layout.addWidget(self.cancel_edit_btn)
        right_layout.addRow(editor_buttons_layout)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # Disable editor initially
        self.set_editor_enabled(False)
        
        main_layout.addWidget(splitter)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
    def set_editor_enabled(self, enabled):
        """Enable or disable the note editor"""
        self.note_type_combo.setEnabled(enabled)
        self.note_title_edit.setEnabled(enabled)
        self.note_description_edit.setEnabled(enabled)
        self.save_note_btn.setEnabled(enabled)
        self.cancel_edit_btn.setEnabled(enabled)
        
    def load_notes(self):
        """Load notes for the current node"""
        self.notes_list.clear()
        notes = self.controller.get_notes_for_node(self.node_data.id)
        
        for note in notes:
            item = QListWidgetItem(f"[{note.note_type.name}] {note.title}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)
            
    def on_note_selected(self):
        """Handle note selection from the list"""
        current_item = self.notes_list.currentItem()
        if current_item:
            self.current_note = current_item.data(Qt.ItemDataRole.UserRole)
            self.load_note_to_editor(self.current_note)
            self.set_editor_enabled(True)
            self.delete_note_btn.setEnabled(True)
        else:
            self.current_note = None
            self.clear_editor()
            self.set_editor_enabled(False)
            self.delete_note_btn.setEnabled(False)
            
    def load_note_to_editor(self, note):
        """Load a note's data into the editor"""
        # Find the note type in the combo box
        for i in range(self.note_type_combo.count()):
            if self.note_type_combo.itemData(i) == note.note_type:
                self.note_type_combo.setCurrentIndex(i)
                break
                
        self.note_title_edit.setText(note.title)
        self.note_description_edit.setPlainText(note.description or "")
        
    def clear_editor(self):
        """Clear the note editor"""
        self.note_type_combo.setCurrentIndex(0)
        self.note_title_edit.clear()
        self.note_description_edit.clear()
        
    def add_note(self):
        """Add a new note"""
        self.current_note = None
        self.clear_editor()
        self.set_editor_enabled(True)
        self.note_title_edit.setFocus()
        
    def save_note(self):
        """Save the current note"""
        title = self.note_title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Invalid Input", "Note title cannot be empty.")
            return
            
        note_type = self.note_type_combo.currentData()
        description = self.note_description_edit.toPlainText()
        
        try:
            if self.current_note:
                # Update existing note
                self.controller.update_note(
                    self.current_note.id,
                    title=title,
                    description=description,
                    note_type=note_type
                )
            else:
                # Create new note
                self.controller.create_note(
                    node_id=self.node_data.id,
                    title=title,
                    description=description,
                    note_type=note_type
                )
                
            self.load_notes()
            self.clear_editor()
            self.set_editor_enabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")
            
    def cancel_edit(self):
        """Cancel editing and clear the editor"""
        self.clear_editor()
        self.set_editor_enabled(False)
        self.current_note = None
        self.notes_list.clearSelection()
        
    def delete_note(self):
        """Delete the selected note"""
        if not self.current_note:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the note '{self.current_note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_note(self.current_note.id)
                self.load_notes()
                self.clear_editor()
                self.set_editor_enabled(False)
                self.current_note = None
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {str(e)}")