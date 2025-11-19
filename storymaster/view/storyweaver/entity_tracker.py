"""
High-performance entity tracking system for StoryWeaver.

Monitors QTextDocument changes and maintains a real-time index of all entity
references using incremental parsing strategies to handle large documents.
"""

from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtGui import QTextDocument, QTextCursor, QTextBlock
import re
from typing import Set, Optional, List

from .entity_index import EntityIndex, EntityReference


class ParseWorker(QObject):
    """
    Background worker for parsing entities in a document.

    Runs in a separate thread to avoid blocking the UI during initial parse.
    """

    # Signals
    progress = Signal(int, int)  # (current_block, total_blocks)
    finished = Signal(list)  # List[tuple[EntityReference, list[EntityReference]]]
    error = Signal(str)

    def __init__(self, document: QTextDocument, entity_pattern, entity_marker):
        super().__init__()
        self.document = document
        self.entity_pattern = entity_pattern
        self.entity_marker = entity_marker
        self._cancelled = False

    def cancel(self):
        """Cancel the parsing operation."""
        self._cancelled = True

    def parse(self):
        """
        Parse all blocks in the document and collect entities.

        Returns results as a list of (block_number, entities) tuples.
        """
        import datetime
        try:
            print(f"[{datetime.datetime.now()}]     ParseWorker: Starting parse in background thread...")
            results = []  # List of (block_number, [EntityReference])

            # Count total blocks
            total_blocks = self.document.blockCount()
            print(f"[{datetime.datetime.now()}]     ParseWorker: Total blocks to parse: {total_blocks}")

            # Parse each block
            block = self.document.firstBlock()
            parsed_count = 0

            while block.isValid() and not self._cancelled:
                block_number = block.blockNumber()
                entities = self._parse_block_content(block, block_number)

                if entities:
                    results.append((block_number, entities))

                parsed_count += 1

                # Emit progress every 50 blocks to avoid signal spam
                if parsed_count % 50 == 0:
                    self.progress.emit(parsed_count, total_blocks)

                block = block.next()

            # Emit final progress
            if not self._cancelled:
                print(f"[{datetime.datetime.now()}]     ParseWorker: Parse complete. Found {sum(len(entities) for _, entities in results)} entities")
                self.progress.emit(total_blocks, total_blocks)
                self.finished.emit(results)

        except Exception as e:
            print(f"[{datetime.datetime.now()}]     ParseWorker: ERROR: {e}")
            self.error.emit(str(e))

    def _parse_block_content(self, block: QTextBlock, block_number: int) -> List[EntityReference]:
        """Parse a single block and return entities found."""
        text = block.text()
        start_pos = block.position()

        # Quick check: does this block even have entity markers?
        if not self.entity_marker.search(text):
            return []

        entities = []

        # Find entities
        for match in self.entity_pattern.finditer(text):
            display_name = match.group(1).strip()
            entity_id = match.group(2).strip() if match.group(2) else None

            # Generate temporary ID if none provided
            if not entity_id:
                entity_id = f"temp_{display_name}"

            ref = EntityReference(
                entity_id=entity_id,
                display_name=display_name,
                start_pos=start_pos + match.start(),
                end_pos=start_pos + match.end(),
                block_number=block_number
            )
            entities.append(ref)

        return entities


class EntityTracker(QObject):
    """
    Connects to QTextDocument and maintains real-time entity tracking.

    Uses differential parsing to only reprocess changed paragraphs,
    making it efficient for large documents (500K+ words).

    Signals:
        entities_updated: Emitted when entities are found/updated
        entity_added: Emitted when a new entity is detected
        entity_removed: Emitted when an entity is deleted
        parse_progress: Emitted during initial parse (current, total)
        parse_complete: Emitted when initial parse finishes
    """

    # Emitted with list of all current entities
    entities_updated = Signal(list)  # List[EntityReference]

    # Emitted with individual entity changes
    entity_added = Signal(object)  # EntityReference
    entity_removed = Signal(object)  # EntityReference

    # Emitted during async parsing
    parse_progress = Signal(int, int)  # (current_block, total_blocks)
    parse_complete = Signal()  # Emitted when async parse finishes

    # Pattern for [[Display Name|entity_id]] or [[Display Name]]
    # Group 1: Display name
    # Group 2: Entity ID (optional)
    ENTITY_PATTERN = re.compile(r'\[\[([^|\]]+?)(?:\|([^\]]+?))?\]\]')

    # Quick check pattern - only look for opening brackets
    ENTITY_MARKER = re.compile(r'\[\[')

    def __init__(self, text_document: QTextDocument, parent=None, async_parse: bool = True):
        """
        Initialize entity tracker for a document.

        Args:
            text_document: QTextDocument to monitor
            parent: Optional parent QObject
            async_parse: If True, perform initial parse asynchronously (default: True)
        """
        super().__init__(parent)

        self.document = text_document
        self.entity_index = EntityIndex()

        # Debounce timer for rapid edits
        self.parse_timer = QTimer(self)
        self.parse_timer.timeout.connect(self._parse_dirty_blocks)
        self.parse_timer.setSingleShot(True)

        # Track which blocks need reparsing
        self.dirty_blocks: Set[int] = set()

        # Track whether we're in a bulk operation
        self.bulk_operation = False

        # Thread for async parsing
        self.parse_thread: Optional[QThread] = None
        self.parse_worker: Optional[ParseWorker] = None

        # Connect to document changes
        self.document.contentsChange.connect(self._on_content_change)

        # Do initial parse (async or sync)
        if async_parse:
            self._async_full_reparse()
        else:
            self._full_reparse()

    def _on_content_change(self, position: int, removed: int, added: int) -> None:
        """
        Handle document changes efficiently.

        Strategy:
        - Small changes (typing): incremental update with minimal reparsing
        - Large changes (paste): batch update with debouncing
        - Smart detection of entity boundaries

        Args:
            position: Character position where change occurred
            removed: Number of characters removed
            added: Number of characters added
        """
        delta = added - removed

        # Determine change type and strategy
        if removed == 0 and added == 1:
            # Single character typed - most common case
            self._handle_character_insertion(position, delta)

        elif removed == 1 and added == 0:
            # Single character deleted
            self._handle_character_deletion(position, delta)

        elif removed > 1000 or added > 1000:
            # Very large change - defer parsing significantly
            self._handle_bulk_change(position, removed, added, delta, debounce_ms=500)

        elif removed > 100 or added > 100:
            # Medium-large change - defer parsing
            self._handle_bulk_change(position, removed, added, delta, debounce_ms=300)

        else:
            # Small multi-character change
            self._handle_block_change(position, removed, added, delta)

    def _handle_character_insertion(self, position: int, delta: int) -> None:
        """
        Optimize for single character typing.

        Only reparse if:
        1. We're typing inside an entity
        2. We might be creating an entity (typed '[')

        Args:
            position: Position where character was inserted
            delta: Always 1 for single character
        """
        # Shift all entities after this position
        self.entity_index.shift_after_position(position + 1, delta)

        # Check if we're inside an entity or creating one
        entity_at_pos = self.entity_index.get_entity_at_position(position)

        if entity_at_pos:
            # Typing inside an entity - reparse its block
            self._mark_block_dirty(entity_at_pos.block_number)
            self._schedule_parse(debounce_ms=150)

        else:
            # Check if we might be starting an entity
            # Look back 1 character to see if we have '[['
            cursor = QTextCursor(self.document)
            cursor.setPosition(max(0, position - 1))
            cursor.setPosition(position + 1, QTextCursor.KeepAnchor)
            text = cursor.selectedText()

            if '[[' in text or ']]' in text:
                # Might be creating/completing an entity
                block_num = self.document.findBlock(position).blockNumber()
                self._mark_block_dirty(block_num)
                self._schedule_parse(debounce_ms=150)

    def _handle_character_deletion(self, position: int, delta: int) -> None:
        """
        Optimize for single character deletion.

        Args:
            position: Position where character was deleted
            delta: Always -1 for single character
        """
        # Check if we're deleting inside an entity
        entity_at_pos = self.entity_index.get_entity_at_position(position)

        # Shift entities after this position
        self.entity_index.shift_after_position(position, delta)

        if entity_at_pos:
            # Deleting inside an entity - reparse its block
            self._mark_block_dirty(entity_at_pos.block_number)
            self._schedule_parse(debounce_ms=150)
        else:
            # Check if we might have deleted part of entity markers
            cursor = QTextCursor(self.document)
            cursor.setPosition(max(0, position - 2))
            cursor.setPosition(min(self.document.characterCount(), position + 2),
                             QTextCursor.KeepAnchor)
            text = cursor.selectedText()

            if '[' in text or ']' in text:
                block_num = self.document.findBlock(position).blockNumber()
                self._mark_block_dirty(block_num)
                self._schedule_parse(debounce_ms=150)

    def _handle_block_change(self, position: int, removed: int, added: int, delta: int) -> None:
        """
        Handle small to medium multi-character changes.

        Args:
            position: Position where change occurred
            removed: Characters removed
            added: Characters added
            delta: Net change (added - removed)
        """
        # Remove entities in the changed range
        removed_entities = self.entity_index.remove_range(position, position + removed)

        # Emit removal signals
        for entity in removed_entities:
            self.entity_removed.emit(entity)

        # Shift entities after the change
        self.entity_index.shift_after_position(position + removed, delta)

        # Mark affected block(s) as dirty
        start_block = self.document.findBlock(position)
        end_block = self.document.findBlock(position + added)

        for block_num in range(start_block.blockNumber(), end_block.blockNumber() + 1):
            self._mark_block_dirty(block_num)

        # Schedule parse with short debounce
        self._schedule_parse(debounce_ms=200)

    def _handle_bulk_change(self, position: int, removed: int, added: int,
                           delta: int, debounce_ms: int = 300) -> None:
        """
        Handle large changes (paste, bulk delete, etc.).

        Args:
            position: Position where change occurred
            removed: Characters removed
            added: Characters added
            delta: Net change
            debounce_ms: Milliseconds to debounce parsing
        """
        # Remove entities in the changed range
        removed_entities = self.entity_index.remove_range(position, position + removed)

        for entity in removed_entities:
            self.entity_removed.emit(entity)

        # Shift entities after the change
        self.entity_index.shift_after_position(position + removed, delta)

        # Mark all affected blocks dirty
        start_block = self.document.findBlock(position)
        end_block = self.document.findBlock(position + added)

        for block_num in range(start_block.blockNumber(), end_block.blockNumber() + 1):
            self._mark_block_dirty(block_num)

        # Schedule parse with longer debounce for large changes
        self._schedule_parse(debounce_ms=debounce_ms)

    def _mark_block_dirty(self, block_number: int) -> None:
        """
        Mark a block as needing reparsing.

        Args:
            block_number: Block number to mark
        """
        self.dirty_blocks.add(block_number)

    def _schedule_parse(self, debounce_ms: int = 300) -> None:
        """
        Schedule parsing of dirty blocks with debouncing.

        Args:
            debounce_ms: Milliseconds to wait before parsing
        """
        self.parse_timer.stop()
        self.parse_timer.start(debounce_ms)

    def _parse_dirty_blocks(self) -> None:
        """
        Parse all blocks marked as dirty.

        Called by the debounce timer after edits settle.
        """
        if not self.dirty_blocks:
            return

        # Parse each dirty block
        for block_num in sorted(self.dirty_blocks):
            self._parse_block(block_num)

        self.dirty_blocks.clear()

        # Emit updated entity list
        self.entities_updated.emit(self.entity_index.get_all_entities())

    def _parse_block(self, block_number: int) -> None:
        """
        Parse a single paragraph for entities.

        Uses regex to find entity patterns and updates the index.

        Args:
            block_number: Block number to parse
        """
        block = self.document.findBlockByNumber(block_number)
        if not block.isValid():
            return

        text = block.text()
        start_pos = block.position()

        # Quick check: does this block even have entity markers?
        if not self.ENTITY_MARKER.search(text):
            # No entities possible - just clear this block
            self.entity_index.remove_block(block_number)
            return

        # Remove old entities from this block
        removed = self.entity_index.remove_block(block_number)
        for entity in removed:
            self.entity_removed.emit(entity)

        # Find new entities
        for match in self.ENTITY_PATTERN.finditer(text):
            display_name = match.group(1).strip()
            entity_id = match.group(2).strip() if match.group(2) else None

            # Generate temporary ID if none provided
            if not entity_id:
                entity_id = f"temp_{display_name}"

            ref = EntityReference(
                entity_id=entity_id,
                display_name=display_name,
                start_pos=start_pos + match.start(),
                end_pos=start_pos + match.end(),
                block_number=block_number
            )

            self.entity_index.add_entity(ref)
            # Only emit individual signals if not in bulk operation
            if not self.bulk_operation:
                self.entity_added.emit(ref)

    def _async_full_reparse(self) -> None:
        """
        Perform full document parse asynchronously in a background thread.

        This prevents UI blocking for large documents.
        """
        # Cancel any existing parse
        if self.parse_thread and self.parse_thread.isRunning():
            if self.parse_worker:
                self.parse_worker.cancel()
            self.parse_thread.quit()
            self.parse_thread.wait()

        # Create worker and thread
        self.parse_worker = ParseWorker(self.document, self.ENTITY_PATTERN, self.ENTITY_MARKER)
        self.parse_thread = QThread()

        # Move worker to thread
        self.parse_worker.moveToThread(self.parse_thread)

        # Connect signals
        self.parse_worker.progress.connect(self._on_parse_progress)
        self.parse_worker.finished.connect(self._on_parse_finished)
        self.parse_worker.error.connect(self._on_parse_error)
        self.parse_thread.started.connect(self.parse_worker.parse)

        # Clean up when done
        self.parse_worker.finished.connect(self.parse_thread.quit)
        self.parse_thread.finished.connect(self._cleanup_parse_thread)

        # Start parsing
        self.parse_thread.start()

    def _on_parse_progress(self, current: int, total: int) -> None:
        """Handle progress updates from async parser."""
        self.parse_progress.emit(current, total)

    def _on_parse_finished(self, results: List[tuple]) -> None:
        """
        Handle completion of async parse.

        Args:
            results: List of (block_number, [EntityReference]) tuples
        """
        # Enable bulk operation mode to suppress individual signals
        self.bulk_operation = True

        # Clear existing index
        self.entity_index.clear()

        # Add all entities from results
        for block_number, entities in results:
            for entity in entities:
                self.entity_index.add_entity(entity)

        # Disable bulk operation mode
        self.bulk_operation = False

        # Emit single update with all entities
        self.entities_updated.emit(self.entity_index.get_all_entities())
        self.parse_complete.emit()

    def _on_parse_error(self, error_msg: str) -> None:
        """Handle errors from async parser."""
        print(f"Entity parse error: {error_msg}")
        self.parse_complete.emit()

    def _cleanup_parse_thread(self) -> None:
        """Clean up the parse thread after it finishes."""
        if self.parse_worker:
            self.parse_worker.deleteLater()
            self.parse_worker = None
        if self.parse_thread:
            self.parse_thread.deleteLater()
            self.parse_thread = None

    def _full_reparse(self) -> None:
        """
        Full document reparse (synchronous).

        Use sparingly - only on initialization or major document structure changes.
        For incremental edits, rely on block-based reparsing.
        For large documents, prefer _async_full_reparse() to avoid blocking UI.
        """
        # Enable bulk operation mode to suppress individual signals
        self.bulk_operation = True

        # Clear existing index
        self.entity_index.clear()

        # Parse every block
        block = self.document.firstBlock()
        while block.isValid():
            self._parse_block(block.blockNumber())
            block = block.next()

        # Disable bulk operation mode
        self.bulk_operation = False

        # Emit full entity list
        self.entities_updated.emit(self.entity_index.get_all_entities())

    def force_reparse(self) -> None:
        """
        Force a full reparse of the document.

        Public method for manual reparsing when needed.
        """
        self._full_reparse()

    def get_entity_at_cursor(self, cursor: QTextCursor) -> Optional[EntityReference]:
        """
        Get the entity at the cursor position, if any.

        Args:
            cursor: QTextCursor to check

        Returns:
            EntityReference if cursor is inside an entity, None otherwise
        """
        return self.entity_index.get_entity_at_position(cursor.position())

    def get_all_entities(self) -> List[EntityReference]:
        """
        Get all entities in the document.

        Returns:
            List of all EntityReference objects
        """
        return self.entity_index.get_all_entities()

    def get_entity_count(self) -> int:
        """
        Get the total number of entities in the document.

        Returns:
            Number of entities
        """
        return len(self.entity_index)

    def get_entities_in_block(self, block_number: int) -> List[EntityReference]:
        """
        Get all entities in a specific block.

        Args:
            block_number: Block number to query

        Returns:
            List of entities in the block
        """
        return self.entity_index.get_entities_in_block(block_number)
