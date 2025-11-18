"""
Custom text editor with entity linking support.
Integrated version for Storymaster - uses direct database access instead of IPC.
"""
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import QPlainTextEdit, QCompleter, QTextEdit
from PySide6.QtCore import Qt, Signal, QStringListModel, QRect
from PySide6.QtGui import QTextCursor, QKeyEvent, QTextCharFormat, QColor, QFont


class EntityTextEditor(QPlainTextEdit):
    """Text editor with support for [[Entity|ID]] syntax and autocomplete."""

    entity_requested = Signal(str)  # Emitted when user wants to search for entities (search query)
    entity_selected = Signal(str, str)  # (entity_id, entity_name) - emitted when entity inserted

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Monospace", 11))
        self.setTabStopDistance(40)

        # Entity autocomplete
        self._completer: Optional[QCompleter] = None
        self._entity_list: List[Dict[str, Any]] = []
        self._completion_active = False
        self._trigger_pos = -1

        self._setup_completer()

    def _setup_completer(self):
        """Set up the entity completer."""
        self._completer = QCompleter(self)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.activated.connect(self._insert_completion)

        # Start with empty model
        model = QStringListModel([], self)
        self._completer.setModel(model)

    def set_entity_list(self, entities: List[Dict[str, Any]]):
        """
        Update the list of available entities for autocomplete.

        Args:
            entities: List of entity dicts with keys: id, name, type
        """
        self._entity_list = entities

        # Create display strings for completer
        display_list = []
        for entity in entities:
            name = entity.get("name", "")
            entity_type = entity.get("type", "")
            display_list.append(f"{name} ({entity_type})")

        model = QStringListModel(display_list, self)
        self._completer.setModel(model)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for entity autocomplete."""
        # Handle completer popup
        if self._completer and self._completer.popup().isVisible():
            # Let completer handle these keys
            if event.key() in (
                Qt.Key_Enter,
                Qt.Key_Return,
                Qt.Key_Escape,
                Qt.Key_Tab,
                Qt.Key_Backtab,
            ):
                event.ignore()
                return

        # Check for [[ trigger
        if event.text() == '[':
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            if cursor.selectedText() == '[':
                # User typed [[, trigger entity autocomplete
                self._trigger_entity_autocomplete()
                super().keyPressEvent(event)
                return

        # Handle normal key press
        super().keyPressEvent(event)

        # Update completer if active
        if self._completion_active:
            self._update_completer()

    def _trigger_entity_autocomplete(self):
        """Trigger entity autocomplete."""
        cursor = self.textCursor()
        self._trigger_pos = cursor.position()
        self._completion_active = True

        # Request entity list (signal will be handled by controller)
        self.entity_requested.emit("")

        # Show completer
        if self._completer:
            rect = self.cursorRect()
            rect.setWidth(self._completer.popup().sizeHintForColumn(0)
                          + self._completer.popup().verticalScrollBar().sizeHint().width())
            self._completer.complete(rect)

    def _update_completer(self):
        """Update completer based on current text."""
        cursor = self.textCursor()
        current_pos = cursor.position()

        if current_pos < self._trigger_pos:
            # Cursor moved before trigger, cancel completion
            self._completion_active = False
            self._completer.popup().hide()
            return

        # Get text between [[ and cursor
        cursor.setPosition(self._trigger_pos)
        cursor.setPosition(current_pos, QTextCursor.KeepAnchor)
        search_text = cursor.selectedText()

        # Check if we've closed the entity link
        if ']]' in search_text or '\n' in search_text:
            self._completion_active = False
            self._completer.popup().hide()
            return

        # Request filtered results if search text changed
        if search_text:
            self.entity_requested.emit(search_text)

        # Update completer prefix
        self._completer.setCompletionPrefix(search_text)
        if len(self._entity_list) > 0:
            self._completer.popup().show()

    def _insert_completion(self, completion: str):
        """Insert the selected entity."""
        if not self._completer:
            return

        # Parse completion to get entity name and type
        # Format: "EntityName (type)"
        import re
        match = re.match(r"^(.+?)\s+\((.+?)\)$", completion)
        if not match:
            return

        entity_name = match.group(1)
        entity_type = match.group(2)

        # Find the entity in our list
        entity_id = None
        for entity in self._entity_list:
            if entity.get("name") == entity_name and entity.get("type") == entity_type:
                entity_id = entity.get("id")
                break

        if not entity_id:
            return

        # Replace text from trigger position to current position
        cursor = self.textCursor()
        cursor.setPosition(self._trigger_pos)
        cursor.setPosition(self.textCursor().position(), QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

        # Insert entity link
        entity_link = f"{entity_name}|{entity_id}]]"
        cursor.insertText(entity_link)

        self._completion_active = False
        self.entity_selected.emit(entity_id, entity_name)

    def get_text(self) -> str:
        """Get the plain text content."""
        return self.toPlainText()

    def set_text(self, text: str):
        """Set the text content."""
        self.setPlainText(text)

    def insert_entity_link(self, entity_name: str, entity_id: str):
        """Insert an entity link at the cursor position."""
        cursor = self.textCursor()
        link = f"[[{entity_name}|{entity_id}]]"
        cursor.insertText(link)
