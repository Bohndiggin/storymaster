"""
Main Storyweaver widget - integrated writing interface for Storymaster.
"""
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLabel, QToolBar, QPushButton, QFileDialog, QMessageBox,
    QListWidgetItem, QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QObject, QPoint
from PySide6.QtGui import QAction, QIcon

from storymaster.view.storyweaver.text_editor import EntityTextEditor
from storymaster.view.storyweaver.entity_tracker import EntityTracker
from storymaster.view.storyweaver.auto_tag_dialog import AutoTagDialog
from storymaster.view.storyweaver.loading_dialog import LoadingDialog
from storymaster.models.document import StoryDocument

if TYPE_CHECKING:
    from storymaster.model.database.database_model import Model




class StoryweaverWidget(QWidget):
    """
    Main Storyweaver widget integrating text editor, entity sidebar, and document management.

    Signals:
        entity_search_requested: Emitted when editor needs entity search (query, storyline_id, setting_id)
        entity_hover_requested: Emitted when user hovers over entity (entity_id, entity_type, storyline_id, setting_id)
        document_modified: Emitted when document content changes
    """

    entity_search_requested = Signal(str, int, int)  # (query, storyline_id, setting_id)
    entity_hover_requested = Signal(str, str, int, int)  # (entity_id, entity_type, storyline_id, setting_id)
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

        # Popup position tracking (for sidebar clicks)
        self._sidebar_popup_pos: Optional[QPoint] = None

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

        # Text editor (no sidebar)
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(5, 5, 5, 5)

        self.editor = EntityTextEditor()
        editor_layout.addWidget(self.editor)

        # Word count label
        self.word_count_label = QLabel("Words: 0")
        editor_layout.addWidget(self.word_count_label)

        layout.addWidget(editor_widget)

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

        # Auto-tag entities
        auto_tag_action = QAction("Auto-Tag Entities", self)
        auto_tag_action.setToolTip("Automatically find and tag entities in the document")
        auto_tag_action.triggered.connect(self.auto_tag_entities)
        toolbar.addAction(auto_tag_action)

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
        self.editor.entity_hover.connect(self._on_entity_hover)
        self.editor.textChanged.connect(self._on_text_changed)

    def _on_entity_requested(self, query: str):
        """Handle entity search request from editor."""
        # Emit signal to controller to fetch entities
        self.entity_search_requested.emit(query, self.current_storyline_id, self.current_setting_id)

    def _on_entity_hover(self, entity_id: str, entity_type: str):
        """Handle entity hover event from editor."""
        # Emit signal to controller to fetch entity details
        self.entity_hover_requested.emit(entity_id, entity_type, self.current_storyline_id, self.current_setting_id)

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
        Update the entity list for autocomplete.

        Args:
            entities: List of dicts with keys: id, name, type
        """
        self._entity_list = entities

        # Update editor autocomplete
        self.editor.set_entity_list(entities)

    def show_entity_details(self, name: str, entity_type: str, details: str, entity_id: str = None):
        """
        Show entity details in the hover card.

        Args:
            name: Entity name
            entity_type: Entity type
            details: Formatted details string
            entity_id: Entity ID (optional, for navigation to Lorekeeper)
        """
        # If we have a sidebar popup position, use that; otherwise use editor's stored position
        if self._sidebar_popup_pos:
            # Show at sidebar position
            self.editor._info_card.set_entity_info(name, entity_type, details, entity_id)
            self.editor._info_card.show_at_position(self._sidebar_popup_pos)
            # Clear the position after use
            self._sidebar_popup_pos = None
        else:
            # Show at editor position (from clicking entity link in text)
            self.editor.show_entity_info(name, entity_type, details)

    def hide_info_cards(self):
        """Hide any visible info cards."""
        self.editor.hide_info_card()

    def preload_entities(self):
        """Preload entity list for faster autocomplete."""
        self._refresh_entity_list()

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

        # Get save location (directory name)
        file_path = QFileDialog.getSaveFileName(
            self, "Create New Document",
            "",
            "Storyweaver Documents (*.storyweaver)"
        )[0]

        if not file_path:
            return

        # Ensure .storyweaver extension
        if not file_path.endswith(".storyweaver"):
            file_path += ".storyweaver"

        # Note: .storyweaver is actually a directory bundle, not a file
        # The save dialog will create the directory structure

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

        # Get directory to open (.storyweaver is a directory bundle)
        file_path = QFileDialog.getExistingDirectory(
            self, "Open Storyweaver Document",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not file_path:
            return

        # Validate it's a .storyweaver directory
        if not file_path.endswith(".storyweaver"):
            QMessageBox.warning(
                self, "Invalid Document",
                "Please select a .storyweaver document directory"
            )
            return

        # Store file path for loading
        self._pending_file_path = file_path

        # Show loading dialog
        self.loading_dialog = LoadingDialog("Loading document...", self)
        self.loading_dialog.show()

        # Force process events to show dialog
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        # Use QTimer to load after dialog is visible
        QTimer.singleShot(50, self._do_load_document)

    def _do_load_document(self):
        """Actually load the document (called via QTimer)."""
        from PySide6.QtWidgets import QApplication

        try:
            file_path = self._pending_file_path

            # Update message
            self.loading_dialog.set_message("Opening document...")
            QApplication.processEvents()

            # Load document
            self.current_document = StoryDocument(file_path)

            self.loading_dialog.set_message("Loading content...")
            QApplication.processEvents()

            if not self.current_document.load():
                self.loading_dialog.close()
                QMessageBox.warning(self, "Error", "Failed to load document")
                self.current_document = None
                return

            # Set editor content
            self.loading_dialog.set_message("Rendering content...")
            QApplication.processEvents()

            self.editor.set_text(self.current_document.content)

            # Setup entity tracker
            if self.entity_tracker:
                self.entity_tracker.deleteLater()
            self.entity_tracker = EntityTracker(self.editor.document(), self)

            # Update UI
            self.document_label.setText(f"Document: {file_path.split('/')[-1]}")
            self._update_word_count()
            self.document_modified.emit(False)

            # Close loading dialog
            self.loading_dialog.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.loading_dialog.close()
            QMessageBox.warning(self, "Error", f"Failed to load document: {e}")
            self.current_document = None

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

    def auto_tag_entities(self):
        """Automatically detect and tag entities in the current document."""
        if not self.current_document:
            QMessageBox.warning(self, "No Document", "No document is currently open")
            return

        if not self._entity_list:
            QMessageBox.warning(
                self, "No Entities",
                "No entities available. Make sure you're in a project with entities."
            )
            return

        # Get current document text
        text = self.editor.get_text()

        if not text.strip():
            QMessageBox.information(self, "Empty Document", "The document is empty")
            return

        # Find all entity mentions in the text
        matches = self._find_entity_matches(text)

        if not matches:
            QMessageBox.information(
                self, "No Matches",
                "No entity names found in the document"
            )
            return

        # Show dialog for user to select which entities to tag
        dialog = AutoTagDialog(matches, self)
        if dialog.exec() == QDialog.Accepted:
            selected_entities = dialog.get_selected_entities()
            if selected_entities:
                self._apply_entity_tags(text, matches, selected_entities)

    def _find_entity_matches(self, text: str) -> List[Dict[str, Any]]:
        """
        Find all entity name occurrences in the text, including aliases.

        Args:
            text: Document text to search

        Returns:
            List of match dictionaries with entity info and positions
        """
        matches = []

        for entity in self._entity_list:
            entity_name = entity.get("name", "")
            entity_id = entity.get("id", "")
            entity_type = entity.get("type", "")
            aliases = entity.get("aliases", [])

            if not entity_name or len(entity_name) < 3:  # Skip very short names
                continue

            # Collect all names to search for (canonical + aliases)
            names_to_search = [entity_name] + [a for a in aliases if len(a) >= 3]

            # Track all matches for this entity (canonical + aliases)
            all_found_matches = []
            match_texts = {}  # Store what text was found at each position

            for name in names_to_search:
                # Find all occurrences (case-insensitive, word boundaries)
                pattern = r'\b' + re.escape(name) + r'\b'
                found = list(re.finditer(pattern, text, re.IGNORECASE))

                for match in found:
                    # Store the actual text found (preserves case and alias used)
                    match_texts[match.start()] = text[match.start():match.end()]
                    all_found_matches.append(match)

            if all_found_matches:
                # Check if any occurrence is already tagged
                already_tagged = any(
                    self._is_already_tagged(text, match.start(), match_texts.get(match.start(), entity_name))
                    for match in all_found_matches
                )

                if not already_tagged:
                    matches.append({
                        "entity_name": entity_name,
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "count": len(all_found_matches),
                        "positions": [(m.start(), m.end()) for m in all_found_matches],
                        "match_texts": match_texts  # Store which text was found at each position
                    })

        # Sort by occurrence count (most common first)
        matches.sort(key=lambda x: x["count"], reverse=True)

        return matches

    def _is_already_tagged(self, text: str, position: int, entity_name: str) -> bool:
        """
        Check if an entity mention is already tagged.

        Args:
            text: Full document text
            position: Start position of the entity name
            entity_name: Name of the entity

        Returns:
            True if already tagged, False otherwise
        """
        # Look backwards for [[ before the entity name
        search_start = max(0, position - 10)
        prefix = text[search_start:position]

        return '[[' in prefix

    def _apply_entity_tags(self, original_text: str, matches: List[Dict[str, Any]], selected_entities: set):
        """
        Apply entity tags to the document, preserving aliases.

        Args:
            original_text: Original document text
            matches: List of all entity matches
            selected_entities: Set of entity IDs to tag
        """
        # Filter matches to only selected entities
        selected_matches = [m for m in matches if m["entity_id"] in selected_entities]

        if not selected_matches:
            return

        # Sort all positions in reverse order to avoid offset issues
        replacements = []
        for match in selected_matches:
            match_texts = match.get("match_texts", {})
            for start, end in match["positions"]:
                # Get the actual text found at this position (alias or canonical name)
                actual_text = match_texts.get(start, original_text[start:end])
                replacements.append({
                    "start": start,
                    "end": end,
                    "entity_name": match["entity_name"],
                    "entity_id": match["entity_id"],
                    "actual_text": actual_text
                })

        # Sort by position (reverse) to replace from end to start
        replacements.sort(key=lambda x: x["start"], reverse=True)

        # Track unique aliases found for each entity
        aliases_to_add = {}  # entity_id -> set of aliases

        # Apply replacements
        new_text = original_text
        for repl in replacements:
            actual_text = repl["actual_text"]
            entity_name = repl["entity_name"]
            entity_id = repl["entity_id"]

            # If the actual text differs from canonical name, it's an alias
            if actual_text.lower() != entity_name.lower():
                if entity_id not in aliases_to_add:
                    aliases_to_add[entity_id] = set()
                aliases_to_add[entity_id].add(actual_text)

            tagged_text = f"[[{actual_text}|{entity_id}]]"

            # Replace in the text
            new_text = new_text[:repl["start"]] + tagged_text + new_text[repl["end"]:]

        # Update the editor
        self.editor.set_text(new_text)

        # Mark document as modified and add discovered aliases to document
        self.current_document.set_content(new_text)

        # Add all discovered aliases to the document metadata
        for entity_id, aliases in aliases_to_add.items():
            for alias in aliases:
                self.current_document.add_alias(entity_id, alias)

        self.document_modified.emit(True)

        # Show success message
        total_tags = sum(len(m["positions"]) for m in selected_matches)
        alias_count = sum(len(aliases) for aliases in aliases_to_add.values())
        message = f"Successfully tagged {total_tags} entity mentions"
        if alias_count > 0:
            message += f"\nDiscovered and saved {alias_count} alias(es)"
        QMessageBox.information(self, "Tagging Complete", message)

    def cleanup(self):
        """Cleanup resources."""
        # Auto-save if needed
        if self.current_document and self.current_document.is_modified:
            self.current_document.save()

        # Stop timers
        self.autosave_timer.stop()
