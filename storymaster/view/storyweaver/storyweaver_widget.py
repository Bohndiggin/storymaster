"""
Main Storyweaver widget - integrated writing interface for Storymaster.
"""
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLabel, QToolBar, QPushButton, QFileDialog, QMessageBox,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QIcon

from storymaster.view.storyweaver.text_editor import EntityTextEditor
from storymaster.view.storyweaver.entity_tracker import EntityTracker
from storymaster.models.document import StoryDocument

if TYPE_CHECKING:
    from storymaster.model.database.database_model import Model


class StoryweaverWidget(QWidget):
    """
    Main Storyweaver widget integrating text editor, entity sidebar, and document management.

    Signals:
        entity_search_requested: Emitted when editor needs entity search (query, storyline_id, setting_id)
        document_modified: Emitted when document content changes
    """

    entity_search_requested = Signal(str, int, int)  # (query, storyline_id, setting_id)
    document_modified = Signal(bool)  # is_modified

    def __init__(self, model: "Model", current_storyline_id: int, current_setting_id: int, parent=None):
        super().__init__(parent)

        self.model = model
        self.current_storyline_id = current_storyline_id
        self.current_setting_id = current_setting_id
        self.current_document: Optional[StoryDocument] = None
        self.entity_tracker: Optional[EntityTracker] = None

        # Entity cache for sidebar
        self._entity_list: List[Dict[str, Any]] = []

        # Setup UI
        self._setup_ui()
        self._setup_connections()

        # Autosave timer (30 seconds)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(30000)

    def _setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        # Main splitter (editor | sidebar)
        splitter = QSplitter(Qt.Horizontal)

        # Left: Text editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(5, 5, 5, 5)

        self.editor = EntityTextEditor()
        editor_layout.addWidget(self.editor)

        # Word count label
        self.word_count_label = QLabel("Words: 0")
        editor_layout.addWidget(self.word_count_label)

        splitter.addWidget(editor_widget)

        # Right: Entity sidebar
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)

        # Set initial sizes (75% editor, 25% sidebar)
        splitter.setSizes([750, 250])

        layout.addWidget(splitter)

    def _create_toolbar(self) -> QToolBar:
        """Create the document management toolbar."""
        toolbar = QToolBar("Document")
        toolbar.setMovable(False)

        # New document
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_document)
        toolbar.addAction(new_action)

        # Open document
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_document)
        toolbar.addAction(open_action)

        # Save document
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_document)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Document title label
        self.document_label = QLabel("No document open")
        toolbar.addWidget(self.document_label)

        return toolbar

    def _create_sidebar(self) -> QWidget:
        """Create the entity reference sidebar."""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Entities")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        sidebar_layout.addWidget(title)

        # Entity list
        self.entity_list_widget = QListWidget()
        self.entity_list_widget.setToolTip("Double-click to insert entity at cursor")
        sidebar_layout.addWidget(self.entity_list_widget)

        # Refresh button
        refresh_btn = QPushButton("Refresh Entities")
        refresh_btn.clicked.connect(self._refresh_entity_list)
        sidebar_layout.addWidget(refresh_btn)

        return sidebar

    def _setup_connections(self):
        """Setup signal/slot connections."""
        # Editor signals
        self.editor.entity_requested.connect(self._on_entity_requested)
        self.editor.entity_selected.connect(self._on_entity_selected)
        self.editor.textChanged.connect(self._on_text_changed)

        # Sidebar double-click to insert entity
        self.entity_list_widget.itemDoubleClicked.connect(self._on_entity_double_clicked)

    def _on_entity_requested(self, query: str):
        """Handle entity search request from editor."""
        # Emit signal to controller to fetch entities
        self.entity_search_requested.emit(query, self.current_storyline_id, self.current_setting_id)

    def _on_entity_selected(self, entity_id: str, entity_name: str):
        """Handle entity selection from autocomplete."""
        if self.current_document:
            # Find entity type from cache
            entity_type = "unknown"
            for entity in self._entity_list:
                if entity.get("id") == entity_id:
                    entity_type = entity.get("type", "unknown")
                    break

            # Update document entity map
            self.current_document.update_entity(entity_id, entity_name, entity_type)

    def _on_text_changed(self):
        """Handle text changes in the editor."""
        if self.current_document:
            self.current_document.set_content(self.editor.get_text())
            self.document_modified.emit(True)
            self._update_word_count()

    def _on_entity_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on entity in sidebar."""
        # Parse item text: "EntityName (type) [id]"
        import re
        text = item.text()
        match = re.match(r"^(.+?)\s+\((.+?)\)\s+\[(.+?)\]$", text)
        if match:
            entity_name = match.group(1)
            entity_id = match.group(3)
            self.editor.insert_entity_link(entity_name, entity_id)
            self._on_entity_selected(entity_id, entity_name)

    def _update_word_count(self):
        """Update the word count label."""
        text = self.editor.get_text()
        words = len(text.split())
        self.word_count_label.setText(f"Words: {words}")

    def _autosave(self):
        """Auto-save the current document if modified."""
        if self.current_document and self.current_document.is_modified and self.current_document.path:
            self.current_document.save()
            self.document_modified.emit(False)

    def _refresh_entity_list(self):
        """Refresh the entity list from the controller."""
        self._on_entity_requested("")

    # Public API

    def set_entity_list(self, entities: List[Dict[str, Any]]):
        """
        Update the entity list for autocomplete and sidebar.

        Args:
            entities: List of dicts with keys: id, name, type
        """
        self._entity_list = entities

        # Update editor autocomplete
        self.editor.set_entity_list(entities)

        # Update sidebar
        self.entity_list_widget.clear()
        for entity in entities:
            name = entity.get("name", "")
            entity_type = entity.get("type", "")
            entity_id = entity.get("id", "")
            item_text = f"{name} ({entity_type}) [{entity_id}]"
            self.entity_list_widget.addItem(item_text)

    def update_project_context(self, storyline_id: int, setting_id: int):
        """
        Update the current project context for entity filtering.

        Args:
            storyline_id: Current storyline ID
            setting_id: Current setting ID
        """
        self.current_storyline_id = storyline_id
        self.current_setting_id = setting_id
        self._refresh_entity_list()

    def new_document(self):
        """Create a new document."""
        # Check for unsaved changes
        if self.current_document and self.current_document.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes to current document?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_document()
            elif reply == QMessageBox.Cancel:
                return

        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create New Document",
            "",
            "Storyweaver Documents (*.storyweaver)"
        )

        if not file_path:
            return

        # Ensure .storyweaver extension
        if not file_path.endswith(".storyweaver"):
            file_path += ".storyweaver"

        # Create new document
        self.current_document = StoryDocument()
        self.current_document.create_new(file_path)

        # Clear editor
        self.editor.set_text("")

        # Setup entity tracker
        if self.entity_tracker:
            self.entity_tracker.deleteLater()
        self.entity_tracker = EntityTracker(self.editor.document(), self)

        # Update UI
        self.document_label.setText(f"Document: {file_path.split('/')[-1]}")
        self._update_word_count()
        self.document_modified.emit(False)

    def open_document(self):
        """Open an existing document."""
        # Check for unsaved changes
        if self.current_document and self.current_document.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes to current document?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_document()
            elif reply == QMessageBox.Cancel:
                return

        # Get file to open
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Document",
            "",
            "Storyweaver Documents (*.storyweaver)"
        )

        if not file_path:
            return

        # Load document
        self.current_document = StoryDocument(file_path)
        if not self.current_document.load():
            QMessageBox.warning(self, "Error", "Failed to load document")
            self.current_document = None
            return

        # Set editor content
        self.editor.set_text(self.current_document.content)

        # Setup entity tracker
        if self.entity_tracker:
            self.entity_tracker.deleteLater()
        self.entity_tracker = EntityTracker(self.editor.document(), self)

        # Update UI
        self.document_label.setText(f"Document: {file_path.split('/')[-1]}")
        self._update_word_count()
        self.document_modified.emit(False)

    def save_document(self):
        """Save the current document."""
        if not self.current_document:
            QMessageBox.warning(self, "No Document", "No document is currently open")
            return

        if not self.current_document.path:
            # No path set, do Save As
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Document",
                "",
                "Storyweaver Documents (*.storyweaver)"
            )

            if not file_path:
                return

            if not file_path.endswith(".storyweaver"):
                file_path += ".storyweaver"

            self.current_document.path = file_path

        # Save
        if self.current_document.save():
            self.document_label.setText(f"Document: {self.current_document.path.split('/')[-1]}")
            self.document_modified.emit(False)
        else:
            QMessageBox.warning(self, "Error", "Failed to save document")

    def get_current_document(self) -> Optional[StoryDocument]:
        """Get the currently open document."""
        return self.current_document

    def cleanup(self):
        """Cleanup resources."""
        # Auto-save if needed
        if self.current_document and self.current_document.is_modified:
            self.current_document.save()

        # Stop timers
        self.autosave_timer.stop()
