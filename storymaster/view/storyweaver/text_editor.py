"""
Custom text editor with entity linking support.
Integrated version for Storymaster - uses direct database access instead of IPC.
"""
from typing import Optional, List, Dict, Any, Tuple
import re
from PySide6.QtWidgets import QPlainTextEdit, QCompleter, QTextEdit, QLabel, QVBoxLayout, QFrame, QMenu, QInputDialog, QMessageBox
from PySide6.QtCore import Qt, Signal, QStringListModel, QRect, QTimer, QPoint, QEvent
from PySide6.QtGui import (
    QTextCursor, QKeyEvent, QTextCharFormat, QColor, QFont,
    QSyntaxHighlighter, QTextDocument, QPainter, QAbstractTextDocumentLayout,
    QMouseEvent, QAction, QContextMenuEvent, QCursor
)
from PySide6.QtWidgets import QApplication
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


# Compiled regex patterns (compile once at module load for performance)
CODE_PATTERN = re.compile(r'(`)([^`]+?)(`)')
BOLD_PATTERN = re.compile(r'(\*\*)([^*]+?)(\*\*)')
UNDERLINE_PATTERN = re.compile(r'(__)([^_]+?)(__)')
STRIKETHROUGH_PATTERN = re.compile(r'(~~)([^~]+?)(~~)')
ITALIC_ASTERISK_PATTERN = re.compile(r'(?<!\*)(\*)(?!\*)([^*]+?)(?<!\*)(\*)(?!\*)')
ITALIC_UNDERSCORE_PATTERN = re.compile(r'(?<!_)(_)(?!_)([^_]+?)(?<!_)(_)(?!_)')
LINK_PATTERN = re.compile(r'(\[)([^\]]+?)(\]\()([^\)]+?)(\))')
IMAGE_PATTERN = re.compile(r'(!\[)([^\]]*?)(\]\()([^\)]+?)(\))')


@dataclass
class BlockData:
    """Data for a text block to be highlighted in a worker thread."""
    block_number: int
    text: str
    position: int


@dataclass
class FormatInstruction:
    """A single formatting instruction (position, length, format_type)."""
    position: int
    length: int
    format_type: str  # e.g., 'entity', 'bold', 'italic', 'code', etc.


class ClickableLabel(QLabel):
    """Label that emits a signal when clicked."""
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class EntityInfoCard(QFrame):
    """Popup card that displays entity information on hover."""

    entity_clicked = Signal(str, str)  # (entity_id, entity_type)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)

        self._current_entity_id = None
        self._current_entity_type = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title label (entity name) - now clickable
        self.title_label = ClickableLabel()
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #4A9EFF; text-decoration: underline;")
        self.title_label.setToolTip("Click to view in Lorekeeper")
        self.title_label.clicked.connect(self._on_title_clicked)
        layout.addWidget(self.title_label)

        # Type label
        self.type_label = QLabel()
        self.type_label.setStyleSheet("font-style: italic; color: #888;")
        layout.addWidget(self.type_label)

        # Details label
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        self.details_label.setMaximumWidth(300)
        layout.addWidget(self.details_label)

        # Style the card
        self.setStyleSheet("""
            EntityInfoCard {
                background-color: #2C2C2C;
                border: 1px solid #4A9EFF;
                border-radius: 4px;
            }
        """)

        self.hide()

    def set_entity_info(self, name: str, entity_type: str, details: str, entity_id: str = None):
        """Set the entity information to display."""
        self.title_label.setText(name)
        self.type_label.setText(f"Type: {entity_type.capitalize()}")
        self.details_label.setText(details)

        # Store entity info for click handling
        self._current_entity_id = entity_id
        self._current_entity_type = entity_type

        # Adjust size to content
        self.adjustSize()

    def _on_title_clicked(self):
        """Handle click on entity title."""
        if self._current_entity_id and self._current_entity_type:
            self.entity_clicked.emit(self._current_entity_id, self._current_entity_type)
            self.hide()

    def show_at_position(self, pos: QPoint):
        """Show the card at a specific position."""
        self.move(pos)
        self.show()
        self.raise_()


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown with entity links."""

    def __init__(self, parent: QTextDocument, editor):
        super().__init__(parent)
        self.editor = editor

        # Track first slow setFormat call for debugging
        self._first_slow_format_logged = False

        # Progressive highlighting state
        self._progressive_timer = QTimer()
        self._progressive_timer.setSingleShot(True)
        self._progressive_timer.timeout.connect(self._highlight_next_chunk)
        self._progressive_current_block = 0
        self._progressive_total_blocks = 0
        self._progressive_active = False

        # Store format instructions for each block (block_number -> list of FormatInstructions)
        self._format_cache: Dict[int, List[FormatInstruction]] = {}

        # Performance profiling counters for FORMATTING (not regex)
        self._format_perf = {
            'entity': 0.0,
            'entity_hidden': 0.0,
            'code': 0.0,
            'code_block': 0.0,
            'bold': 0.0,
            'italic': 0.0,
            'underline': 0.0,
            'strikethrough': 0.0,
            'links': 0.0,
            'headings': 0.0,
            'lists': 0.0,
            'blockquote': 0.0,
            'other': 0.0,
            'total_blocks': 0,
            'total_setformat_calls': 0
        }

        # Counter for highlightBlock() calls
        self._highlight_block_call_count = 0

        # Format for entity name (underlined and colored)
        self.entity_format = QTextCharFormat()
        self.entity_format.setFontUnderline(True)
        self.entity_format.setUnderlineColor(QColor("#4A9EFF"))
        self.entity_format.setForeground(QColor("#4A9EFF"))

        # Format for invisible syntax
        # Use ONLY transparency (fast - no layout recalculation)
        # NOTE: setFontPointSize(0.1) causes 12s delay - DO NOT USE!
        # NOTE: setFontLetterSpacing() also causes issues
        self.hidden_format = QTextCharFormat()
        self.hidden_format.setForeground(QColor(0, 0, 0, 0))  # Fully transparent
        # Trade-off: Characters are invisible but still take up space
        # For true "dual representation" (visual vs actual text), we'd need a more complex approach

        # Markdown formats
        self.heading1_format = QTextCharFormat()
        self.heading1_format.setFontWeight(QFont.Bold)
        self.heading1_format.setFontPointSize(18)
        self.heading1_format.setForeground(QColor("#FFFFFF"))

        self.heading2_format = QTextCharFormat()
        self.heading2_format.setFontWeight(QFont.Bold)
        self.heading2_format.setFontPointSize(16)
        self.heading2_format.setForeground(QColor("#CCCCCC"))

        self.heading3_format = QTextCharFormat()
        self.heading3_format.setFontWeight(QFont.Bold)
        self.heading3_format.setFontPointSize(14)
        self.heading3_format.setForeground(QColor("#AAAAAA"))

        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Bold)

        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)

        self.strikethrough_format = QTextCharFormat()
        self.strikethrough_format.setFontStrikeOut(True)
        self.strikethrough_format.setForeground(QColor("#888888"))

        self.underline_format = QTextCharFormat()
        self.underline_format.setFontUnderline(True)

        self.code_format = QTextCharFormat()
        self.code_format.setFontFamily("Monospace")
        self.code_format.setBackground(QColor("#3C3C3C"))
        self.code_format.setForeground(QColor("#00FF00"))

        self.code_block_format = QTextCharFormat()
        self.code_block_format.setFontFamily("Monospace")
        self.code_block_format.setBackground(QColor("#2C2C2C"))
        self.code_block_format.setForeground(QColor("#00FF00"))

        self.heading4_format = QTextCharFormat()
        self.heading4_format.setFontWeight(QFont.Bold)
        self.heading4_format.setFontPointSize(13)
        self.heading4_format.setForeground(QColor("#999999"))

        self.heading5_format = QTextCharFormat()
        self.heading5_format.setFontWeight(QFont.Bold)
        self.heading5_format.setFontPointSize(12)
        self.heading5_format.setForeground(QColor("#888888"))

        self.heading6_format = QTextCharFormat()
        self.heading6_format.setFontWeight(QFont.Bold)
        self.heading6_format.setFontPointSize(11)
        self.heading6_format.setForeground(QColor("#777777"))

        self.blockquote_format = QTextCharFormat()
        self.blockquote_format.setForeground(QColor("#AAAAAA"))
        self.blockquote_format.setFontItalic(True)

        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#5DADE2"))
        self.link_format.setFontUnderline(True)

        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#FFA500"))

        self.task_checkbox_format = QTextCharFormat()
        self.task_checkbox_format.setForeground(QColor("#00AA00"))

        self.hr_format = QTextCharFormat()
        self.hr_format.setForeground(QColor("#555555"))
        self.hr_format.setFontWeight(QFont.Bold)

        # Entity highlighting for plain text approach (multipass)
        self._entity_names: List[str] = []
        self._entity_patterns: List[re.Pattern] = []  # One pattern per entity

    def set_entity_names(self, entity_names: List[str]):
        """Set the list of entity names to highlight and compile individual patterns."""
        self._entity_names = entity_names
        if entity_names:
            # Multipass approach: compile one simple pattern per entity
            # Much faster than one huge pattern with all entities
            self._entity_patterns = []
            for name in entity_names:
                # Escape special regex characters
                escaped_name = re.escape(name)
                # Pattern: \bEntityName('s)?\b (with optional possessive)
                pattern_str = r'\b' + escaped_name + r"(?:'s)?\b"
                pattern = re.compile(pattern_str, re.IGNORECASE)
                self._entity_patterns.append(pattern)
        else:
            self._entity_patterns = []


    def _is_inside_entity_link(self, start: int, end: int, entity_ranges: list) -> bool:
        """Check if a range overlaps with any entity link."""
        for entity_start, entity_end in entity_ranges:
            # Check if there's any overlap
            if not (end <= entity_start or start >= entity_end):
                return True
        return False

    def _print_performance_summary(self):
        """Print a summary of formatting performance."""
        total_blocks = self._format_perf['total_blocks']
        total_calls = self._format_perf['total_setformat_calls']
        if total_blocks == 0:
            return

        print(f"\n{'='*70}")
        print(f"FORMATTING PERFORMANCE SUMMARY")
        print(f"  highlightBlock() calls: {self._highlight_block_call_count}")
        print(f"  Blocks formatted: {total_blocks}")
        print(f"  setFormat() calls: {total_calls}")
        print(f"{'='*70}")

        # Calculate total time spent in formatting
        total_time = sum(v for k, v in self._format_perf.items()
                        if k not in ['total_blocks', 'total_setformat_calls'])

        # Sort by time spent (descending)
        sorted_counters = sorted(
            [(k, v) for k, v in self._format_perf.items()
             if k not in ['total_blocks', 'total_setformat_calls']],
            key=lambda x: x[1],
            reverse=True
        )

        for format_type, time_ms in sorted_counters:
            if time_ms > 0:
                pct = (time_ms / total_time * 100) if total_time > 0 else 0
                avg_per_block = time_ms / total_blocks
                print(f"  {format_type:20s}: {time_ms:8.1f}ms total | {avg_per_block:6.3f}ms/block | {pct:5.1f}%")

        print(f"{'-'*70}")
        print(f"  {'TOTAL':20s}: {total_time:8.1f}ms")
        print(f"  {'Avg per block':20s}: {total_time/total_blocks:8.3f}ms")
        if total_calls > 0:
            print(f"  {'Avg per setFormat()':20s}: {total_time/total_calls:8.3f}ms")
        print(f"{'='*70}\n")

    def _populate_cache(self, document: QTextDocument):
        """
        Populate the format cache by processing all blocks in parallel.
        This is a synchronous operation that prepares the cache before highlighting.
        """
        print(f"[{datetime.datetime.now()}]     Populating cache for {document.blockCount()} blocks...")

        # Reset performance counters
        for key in self._format_perf:
            self._format_perf[key] = 0
        self._highlight_block_call_count = 0

        # Clear format cache
        self._format_cache.clear()

        # Extract all block data
        block_data = []
        block = document.firstBlock()
        while block.isValid():
            block_data.append(BlockData(
                block_number=block.blockNumber(),
                text=block.text(),
                position=block.position()
            ))
            block = block.next()

        # Process blocks in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._process_block_in_thread, bd) for bd in block_data]
            for future in as_completed(futures):
                block_number, instructions = future.result()
                self._format_cache[block_number] = instructions

        # Store block data for cache validation
        self._block_data = block_data

        print(f"[{datetime.datetime.now()}]     Cache populated with {len(self._format_cache)} blocks")

    def start_progressive_rehighlight(self):
        """Start progressive multithreaded rehighlighting (non-blocking)."""
        # Reset performance counters
        for key in self._format_perf:
            self._format_perf[key] = 0
        self._highlight_block_call_count = 0

        print(f"[{datetime.datetime.now()}]     MarkdownHighlighter: Starting multithreaded progressive rehighlight...")

        # Cancel any existing progressive highlighting
        if self._progressive_active:
            self._progressive_timer.stop()

        # Clear format cache since we're doing a full rehighlight
        self._format_cache.clear()

        # Disable editor updates during highlighting to prevent expensive repaints
        # This is the KEY optimization - prevents Qt from recalculating layout on every block
        self.editor.setUpdatesEnabled(False)

        # Initialize progressive state
        doc = self.document()
        if doc:
            self._progressive_current_block = 0
            self._progressive_total_blocks = doc.blockCount()
            self._progressive_active = True

            # Extract all block data (thread-safe copy of text content)
            print(f"[{datetime.datetime.now()}]     MarkdownHighlighter: Extracting {self._progressive_total_blocks} blocks for multithreaded processing...")
            self._block_data = []
            block = doc.firstBlock()
            while block.isValid():
                self._block_data.append(BlockData(
                    block_number=block.blockNumber(),
                    text=block.text(),
                    position=block.position()
                ))
                block = block.next()

            print(f"[{datetime.datetime.now()}]     MarkdownHighlighter: Starting multithreaded highlighting...")
            # Start highlighting the first chunk
            self._highlight_next_chunk()

    def _highlight_next_chunk(self):
        """Highlight the next chunk of blocks using multithreading."""
        if not self._progressive_active:
            return

        doc = self.document()
        if not doc:
            self._progressive_active = False
            return

        chunk_start_time = datetime.datetime.now()

        # Use smaller chunks (50 blocks) to yield to event loop more frequently
        chunk_size = 50
        end_block = min(self._progressive_current_block + chunk_size, self._progressive_total_blocks)

        # Get block data for this chunk
        chunk_blocks = self._block_data[self._progressive_current_block:end_block]

        # Process blocks in parallel (CPU-bound regex work in threads)
        # Use 4 workers for good parallelism without overwhelming the system
        regex_start = datetime.datetime.now()
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all blocks in the chunk to be processed in parallel
            futures = [executor.submit(self._process_block_in_thread, block_data)
                      for block_data in chunk_blocks]

            # Collect results and apply formats immediately as they complete
            # This allows UI to remain responsive
            completed_count = 0
            for future in as_completed(futures):
                block_number, instructions = future.result()
                # Store format instructions in cache
                self._format_cache[block_number] = instructions
                completed_count += 1

        regex_end = datetime.datetime.now()
        regex_duration = (regex_end - regex_start).total_seconds() * 1000

        # Don't apply formatting during progressive load - just cache the instructions
        # We'll trigger a single rehighlight at the end which is much faster
        format_start = datetime.datetime.now()
        # No-op - formatting will be applied automatically when Qt calls highlightBlock()
        format_end = datetime.datetime.now()
        format_duration = (format_end - format_start).total_seconds() * 1000

        self._progressive_current_block = end_block

        chunk_duration = (datetime.datetime.now() - chunk_start_time).total_seconds() * 1000
        print(f"[{datetime.datetime.now()}]     Chunk {self._progressive_current_block}/{self._progressive_total_blocks}: "
              f"regex={regex_duration:.1f}ms, format={format_duration:.1f}ms, total={chunk_duration:.1f}ms")

        # Process events to keep UI responsive
        QApplication.processEvents()

        # Check if we're done
        if self._progressive_current_block >= self._progressive_total_blocks:
            self._progressive_active = False

            # Cache is fully populated! Now format the entire document
            print(f"[{datetime.datetime.now()}]     Cache fully populated. Formatting entire document...")

            # Format the entire document to get full performance data
            format_start = datetime.datetime.now()
            self.rehighlight()
            format_duration = (datetime.datetime.now() - format_start).total_seconds() * 1000

            # Re-enable editor updates
            self.editor.setUpdatesEnabled(True)

            print(f"[{datetime.datetime.now()}]     Document formatted in {format_duration:.1f}ms")
            print(f"[{datetime.datetime.now()}]     Document ready!")

            # Print performance summary AFTER we've formatted all blocks
            self._print_performance_summary()
        else:
            # Schedule next chunk immediately - no delay needed
            self._progressive_timer.start(0)

    def _apply_cached_formatting_direct(self):
        """
        Apply all cached formatting directly to the document using QTextCursor.
        This bypasses QSyntaxHighlighter entirely for much better performance.

        Unfortunately, Qt's text formatting is inherently slow - even with all
        optimizations, applying thousands of individual format changes takes time.
        """
        doc = self.document()
        cursor = QTextCursor(doc)

        # Block ALL signals during formatting
        doc.blockSignals(True)
        doc.setUndoRedoEnabled(False)

        # Begin editing block to batch all changes
        cursor.beginEditBlock()

        try:
            # Don't show syntax markers (we're just formatting the whole document)
            show_syntax = False

            # Process each block that has cached instructions
            block = doc.firstBlock()
            while block.isValid():
                block_number = block.blockNumber()

                if block_number in self._format_cache:
                    instructions = self._format_cache[block_number]
                    block_start_pos = block.position()

                    # Apply each format instruction for this block
                    for instruction in instructions:
                        # Convert block-relative position to document-absolute position
                        abs_position = block_start_pos + instruction.position

                        # Get the format for this instruction
                        fmt = self._get_format_for_type(instruction.format_type, show_syntax)
                        if fmt:
                            # Set cursor to the position and select the text
                            cursor.setPosition(abs_position)
                            cursor.setPosition(abs_position + instruction.length, QTextCursor.KeepAnchor)

                            # Apply the format
                            cursor.setCharFormat(fmt)

                block = block.next()

        finally:
            # End editing block
            cursor.endEditBlock()

            # Re-enable signals and undo/redo
            doc.setUndoRedoEnabled(True)
            doc.blockSignals(False)

    def _extract_format_instructions(self, text: str) -> List[FormatInstruction]:
        """
        Extract all format instructions from text using regex (thread-safe, no GUI).

        Returns:
            List of FormatInstruction objects describing where to apply formats
        """
        instructions = []

        # Track entity link positions to avoid formatting inside them
        entity_ranges = []

        # Code blocks (```...```) - must be checked before other patterns
        if text.strip().startswith('```'):
            instructions.append(FormatInstruction(0, len(text), 'code_block'))
            return instructions

        # Horizontal rules (---, ***, ___)
        hr_patterns = [r'^---+$', r'^\*\*\*+$', r'^___+$']
        for pattern in hr_patterns:
            if re.match(pattern, text.strip()):
                instructions.append(FormatInstruction(0, len(text), 'hr'))
                return instructions

        # Headings
        if text.startswith('###### '):
            instructions.append(FormatInstruction(0, 7, 'heading_syntax'))
            instructions.append(FormatInstruction(7, len(text) - 7, 'heading6'))
            return instructions
        elif text.startswith('##### '):
            instructions.append(FormatInstruction(0, 6, 'heading_syntax'))
            instructions.append(FormatInstruction(6, len(text) - 6, 'heading5'))
            return instructions
        elif text.startswith('#### '):
            instructions.append(FormatInstruction(0, 5, 'heading_syntax'))
            instructions.append(FormatInstruction(5, len(text) - 5, 'heading4'))
            return instructions
        elif text.startswith('### '):
            instructions.append(FormatInstruction(0, 4, 'heading_syntax'))
            instructions.append(FormatInstruction(4, len(text) - 4, 'heading3'))
            return instructions
        elif text.startswith('## '):
            instructions.append(FormatInstruction(0, 3, 'heading_syntax'))
            instructions.append(FormatInstruction(3, len(text) - 3, 'heading2'))
            return instructions
        elif text.startswith('# '):
            instructions.append(FormatInstruction(0, 2, 'heading_syntax'))
            instructions.append(FormatInstruction(2, len(text) - 2, 'heading1'))
            return instructions

        # Blockquote
        if text.startswith('> '):
            instructions.append(FormatInstruction(0, 2, 'blockquote_syntax'))
            instructions.append(FormatInstruction(2, len(text) - 2, 'blockquote'))
            return instructions

        # Task lists
        task_unchecked = re.match(r'^(\s*-\s+\[\s\])\s+(.*)$', text)
        task_checked = re.match(r'^(\s*-\s+\[x\])\s+(.*)$', text, re.IGNORECASE)
        if task_unchecked:
            instructions.append(FormatInstruction(0, len(task_unchecked.group(1)), 'task_checkbox'))
            return instructions
        elif task_checked:
            instructions.append(FormatInstruction(0, len(task_checked.group(1)), 'task_checkbox'))
            instructions.append(FormatInstruction(len(task_checked.group(1)) + 1, len(task_checked.group(2)), 'strikethrough'))
            return instructions

        # Unordered lists
        list_match = re.match(r'^(\s*[-*+]\s+)', text)
        if list_match:
            instructions.append(FormatInstruction(0, len(list_match.group(1)), 'list'))

        # Ordered lists
        ordered_list_match = re.match(r'^(\s*\d+\.\s+)', text)
        if ordered_list_match:
            instructions.append(FormatInstruction(0, len(ordered_list_match.group(1)), 'list'))

        # Helper to check if range overlaps with entity links
        def is_inside_entity(start: int, end: int) -> bool:
            for entity_start, entity_end in entity_ranges:
                if not (end <= entity_start or start >= entity_end):
                    return True
            return False

        # Inline code
        for match in CODE_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 1, 'code_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'code'))
            instructions.append(FormatInstruction(match.start(3), 1, 'code_syntax'))

        # Bold
        for match in BOLD_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 2, 'bold_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'bold'))
            instructions.append(FormatInstruction(match.start(3), 2, 'bold_syntax'))

        # Underline
        for match in UNDERLINE_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 2, 'underline_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'underline'))
            instructions.append(FormatInstruction(match.start(3), 2, 'underline_syntax'))

        # Strikethrough
        for match in STRIKETHROUGH_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 2, 'strikethrough_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'strikethrough'))
            instructions.append(FormatInstruction(match.start(3), 2, 'strikethrough_syntax'))

        # Italic (asterisk)
        for match in ITALIC_ASTERISK_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 1, 'italic_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'italic'))
            instructions.append(FormatInstruction(match.start(3), 1, 'italic_syntax'))

        # Italic (underscore)
        for match in ITALIC_UNDERSCORE_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 1, 'italic_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'italic'))
            instructions.append(FormatInstruction(match.start(3), 1, 'italic_syntax'))

        # Links
        for match in LINK_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 1, 'link_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'link'))
            instructions.append(FormatInstruction(match.start(3), 2, 'link_syntax'))
            instructions.append(FormatInstruction(match.start(4), len(match.group(4)), 'link_syntax'))
            instructions.append(FormatInstruction(match.start(5), 1, 'link_syntax'))

        # Images
        for match in IMAGE_PATTERN.finditer(text):
            if is_inside_entity(match.start(), match.end()):
                continue
            instructions.append(FormatInstruction(match.start(1), 2, 'image_syntax'))
            instructions.append(FormatInstruction(match.start(2), len(match.group(2)), 'link'))
            instructions.append(FormatInstruction(match.start(3), 2, 'image_syntax'))
            instructions.append(FormatInstruction(match.start(4), len(match.group(4)), 'image_syntax'))
            instructions.append(FormatInstruction(match.start(5), 1, 'image_syntax'))

        return instructions

    def _process_block_in_thread(self, block_data: BlockData) -> Tuple[int, List[FormatInstruction]]:
        """
        Process a block's text in a worker thread (thread-safe, no GUI access).

        This does the CPU-intensive regex matching. The actual formatting
        is applied later in the main thread.

        Returns:
            Tuple of (block_number, list of FormatInstructions)
        """
        instructions = self._extract_format_instructions(block_data.text)
        return (block_data.block_number, instructions)

    def _get_format_for_type(self, format_type: str, show_syntax: bool) -> Optional[QTextCharFormat]:
        """
        Get the QTextCharFormat for a given format type.

        Args:
            format_type: The type of format (e.g., 'bold', 'italic', 'entity')
            show_syntax: Whether to show markdown syntax (affects syntax format types)

        Returns:
            QTextCharFormat or None if syntax should be hidden
        """
        # Syntax formats (hidden unless cursor is in block)
        syntax_types = ['heading_syntax', 'blockquote_syntax', 'code_syntax', 'bold_syntax',
                       'underline_syntax', 'strikethrough_syntax', 'italic_syntax',
                       'link_syntax', 'image_syntax', 'entity_hidden']

        if format_type in syntax_types and not show_syntax:
            return self.hidden_format

        # Content formats
        format_map = {
            'entity': self.entity_format,
            'entity_hidden': self.hidden_format,
            'code_block': self.code_block_format,
            'hr': self.hr_format,
            'heading1': self.heading1_format,
            'heading2': self.heading2_format,
            'heading3': self.heading3_format,
            'heading4': self.heading4_format,
            'heading5': self.heading5_format,
            'heading6': self.heading6_format,
            'blockquote': self.blockquote_format,
            'task_checkbox': self.task_checkbox_format,
            'strikethrough': self.strikethrough_format,
            'list': self.list_format,
            'code': self.code_format,
            'bold': self.bold_format,
            'underline': self.underline_format,
            'italic': self.italic_format,
            'link': self.link_format,
        }

        return format_map.get(format_type)

    def setFormat(self, start: int, length: int, fmt: QTextCharFormat):
        """Override setFormat to add timing debug."""
        t_start = datetime.datetime.now()
        super().setFormat(start, length, fmt)
        duration_ms = (datetime.datetime.now() - t_start).total_seconds() * 1000

        # Debug: Log first slow setFormat call (likely the bottleneck)
        if duration_ms > 100 and not self._first_slow_format_logged:
            self._first_slow_format_logged = True
            print(f"[{datetime.datetime.now()}] ⚠️ FIRST SLOW setFormat: took {duration_ms:.1f}ms")
            print(f"    Block: {self.currentBlock().blockNumber()}")
            print(f"    Text: {self.currentBlock().text()[:100]}")
            print(f"    Format: {fmt}")

    def _timed_setFormat(self, start: int, length: int, fmt: QTextCharFormat, format_type: str):
        """Wrapper around setFormat() to track performance (for cache path)."""
        t_start = datetime.datetime.now()
        self.setFormat(start, length, fmt)
        duration_ms = (datetime.datetime.now() - t_start).total_seconds() * 1000

        # Track by general category
        category = format_type.replace('_syntax', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '')
        if category.startswith('heading'):
            category = 'headings'
        elif category in ['link', 'image']:
            category = 'links'
        elif category in ['list', 'task_checkbox', 'hr']:
            category = 'lists'

        if category in self._format_perf:
            self._format_perf[category] += duration_ms
        else:
            self._format_perf['other'] += duration_ms

        self._format_perf['total_setformat_calls'] += 1

    def highlightBlock(self, text: str):
        """Apply highlighting to markdown and entity links."""
        if not text:
            return

        # Debug: Time this block's highlighting
        block_start = datetime.datetime.now()

        self._highlight_block_call_count += 1
        self._format_perf['total_blocks'] += 1
        block_number = self.currentBlock().blockNumber()

        # Check if cursor is in this block to show/hide markdown syntax
        cursor_block = self.editor.textCursor().block()
        show_syntax = (cursor_block == self.currentBlock())

        # Debug: track cache usage
        use_cache = block_number in self._format_cache
        if not hasattr(self, '_cache_hits'):
            self._cache_hits = 0
            self._cache_misses = 0

        if use_cache:
            self._cache_hits += 1
        else:
            self._cache_misses += 1

        # Check if we have cached format instructions for this block
        if block_number in self._format_cache:
            # Check if cached data is still valid by comparing text
            cached_block_data = None
            if hasattr(self, '_block_data') and block_number < len(self._block_data):
                cached_block_data = self._block_data[block_number]

            # If text has changed, invalidate cache and recompute
            if cached_block_data is None or cached_block_data.text != text:
                # Text changed, remove from cache and fall through to recompute
                del self._format_cache[block_number]
            else:
                # Use cached format instructions (from parallel processing)
                instructions = self._format_cache[block_number]
                for instruction in instructions:
                    fmt = self._get_format_for_type(instruction.format_type, show_syntax)
                    if fmt:
                        self._timed_setFormat(instruction.position, instruction.length, fmt, instruction.format_type)

                # Still need to apply entity highlighting (not cached because entity list loads after cache)
                # Track entity ranges to avoid conflicts
                entity_ranges = []
                if self._entity_patterns:
                    for pattern in self._entity_patterns:
                        for match in pattern.finditer(text):
                            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                                continue
                            self.setFormat(match.start(), len(match.group(0)), self.entity_format)
                return

        # Fall back to original highlighting logic for real-time edits
        # (This path is used when user types, not during initial load)

        # Track entity link positions to avoid formatting inside them
        entity_ranges = []

        # Code blocks (```...```) - must be checked before other patterns
        if text.strip().startswith('```'):
            self.setFormat(0, len(text), self.code_block_format)
            return  # Don't apply other formatting inside code blocks

        # Horizontal rules (---, ***, ___)
        hr_patterns = [r'^---+$', r'^\*\*\*+$', r'^___+$']
        for pattern in hr_patterns:
            if re.match(pattern, text.strip()):
                self.setFormat(0, len(text), self.hr_format)
                return  # Don't apply other formatting to horizontal rules

        # Headings (must be checked before other patterns to avoid conflicts)
        if text.startswith('###### '):
            if not show_syntax:
                self.setFormat(0, 7, self.hidden_format)
            self.setFormat(7, len(text) - 7, self.heading6_format)
            return
        elif text.startswith('##### '):
            if not show_syntax:
                self.setFormat(0, 6, self.hidden_format)
            self.setFormat(6, len(text) - 6, self.heading5_format)
            return
        elif text.startswith('#### '):
            if not show_syntax:
                self.setFormat(0, 5, self.hidden_format)
            self.setFormat(5, len(text) - 5, self.heading4_format)
            return
        elif text.startswith('### '):
            if not show_syntax:
                self.setFormat(0, 4, self.hidden_format)
            self.setFormat(4, len(text) - 4, self.heading3_format)
            return
        elif text.startswith('## '):
            if not show_syntax:
                self.setFormat(0, 3, self.hidden_format)
            self.setFormat(3, len(text) - 3, self.heading2_format)
            return
        elif text.startswith('# '):
            if not show_syntax:
                self.setFormat(0, 2, self.hidden_format)
            self.setFormat(2, len(text) - 2, self.heading1_format)
            return

        # Blockquote
        if text.startswith('> '):
            if not show_syntax:
                self.setFormat(0, 2, self.hidden_format)
            self.setFormat(2, len(text) - 2, self.blockquote_format)
            return

        # Task lists (- [ ] or - [x])
        task_unchecked = re.match(r'^(\s*-\s+\[\s\])\s+(.*)$', text)
        task_checked = re.match(r'^(\s*-\s+\[x\])\s+(.*)$', text, re.IGNORECASE)
        if task_unchecked:
            self.setFormat(0, len(task_unchecked.group(1)), self.task_checkbox_format)
            return
        elif task_checked:
            self.setFormat(0, len(task_checked.group(1)), self.task_checkbox_format)
            # Strike through the task text
            self.setFormat(len(task_checked.group(1)) + 1, len(task_checked.group(2)), self.strikethrough_format)
            return

        # Unordered lists (-, *, +)
        list_match = re.match(r'^(\s*[-*+]\s+)', text)
        if list_match:
            self.setFormat(0, len(list_match.group(1)), self.list_format)

        # Ordered lists (1., 2., etc.)
        ordered_list_match = re.match(r'^(\s*\d+\.\s+)', text)
        if ordered_list_match:
            self.setFormat(0, len(ordered_list_match.group(1)), self.list_format)

        # Now apply inline formatting (bold, italic, etc.)
        # These need to be applied in the right order to avoid conflicts
        # Skip formatting inside entity links

        # Inline code `text` (must be before other inline formatting)
        for match in CODE_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide backticks
                self.setFormat(match.start(1), 1, self.hidden_format)
                self.setFormat(match.start(3), 1, self.hidden_format)
            # Format as code
            self.setFormat(match.start(2), len(match.group(2)), self.code_format)

        # Bold **text** (must be before italic to avoid conflicts)
        for match in BOLD_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide asterisks
                self.setFormat(match.start(1), 2, self.hidden_format)
                self.setFormat(match.start(3), 2, self.hidden_format)
            # Bold the content
            self.setFormat(match.start(2), len(match.group(2)), self.bold_format)

        # Underline __text__
        for match in UNDERLINE_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide underscores
                self.setFormat(match.start(1), 2, self.hidden_format)
                self.setFormat(match.start(3), 2, self.hidden_format)
            # Underline the content
            self.setFormat(match.start(2), len(match.group(2)), self.underline_format)

        # Strikethrough ~~text~~
        for match in STRIKETHROUGH_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide tildes
                self.setFormat(match.start(1), 2, self.hidden_format)
                self.setFormat(match.start(3), 2, self.hidden_format)
            # Strike through the content
            self.setFormat(match.start(2), len(match.group(2)), self.strikethrough_format)

        # Italic *text* or _text_ (must be after bold/underline to avoid conflicts)
        for match in ITALIC_ASTERISK_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide asterisks
                self.setFormat(match.start(1), 1, self.hidden_format)
                self.setFormat(match.start(3), 1, self.hidden_format)
            # Italicize the content
            self.setFormat(match.start(2), len(match.group(2)), self.italic_format)

        # Italic with underscores _text_
        for match in ITALIC_UNDERSCORE_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide underscores
                self.setFormat(match.start(1), 1, self.hidden_format)
                self.setFormat(match.start(3), 1, self.hidden_format)
            # Italicize the content
            self.setFormat(match.start(2), len(match.group(2)), self.italic_format)

        # Links [text](url)
        for match in LINK_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide markdown syntax, show only link text
                self.setFormat(match.start(1), 1, self.hidden_format)
                self.setFormat(match.start(3), 2, self.hidden_format)
                self.setFormat(match.start(4), len(match.group(4)), self.hidden_format)
                self.setFormat(match.start(5), 1, self.hidden_format)
            # Format link text
            self.setFormat(match.start(2), len(match.group(2)), self.link_format)

        # Images ![alt](url)
        for match in IMAGE_PATTERN.finditer(text):
            if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                continue
            if not show_syntax:
                # Hide markdown syntax
                self.setFormat(match.start(1), 2, self.hidden_format)
                self.setFormat(match.start(3), 2, self.hidden_format)
                self.setFormat(match.start(4), len(match.group(4)), self.hidden_format)
                self.setFormat(match.start(5), 1, self.hidden_format)
            # Format alt text with link format
            self.setFormat(match.start(2), len(match.group(2)), self.link_format)

        # Entity name highlighting (multipass approach - entire document)
        if self._entity_patterns:
            # Iterate through each entity pattern (multipass)
            for pattern in self._entity_patterns:
                for match in pattern.finditer(text):
                    # Check if this position overlaps with any other formatted region
                    if self._is_inside_entity_link(match.start(), match.end(), entity_ranges):
                        continue
                    # Highlight the entity name
                    self.setFormat(match.start(), len(match.group(0)), self.entity_format)

        # Debug: Log if this block took more than 100ms
        block_duration = (datetime.datetime.now() - block_start).total_seconds() * 1000
        if block_duration > 100:
            print(f"[{datetime.datetime.now()}] ⚠️ SLOW highlightBlock: block {block_number} took {block_duration:.1f}ms")


class EntityTextEditor(QTextEdit):
    """Text editor with support for [[Entity|ID]] syntax and autocomplete."""

    entity_requested = Signal(str)  # Emitted when user wants to search for entities (search query)
    entity_selected = Signal(str, str)  # (entity_id, entity_name) - emitted when entity inserted
    entity_hover = Signal(str, str)  # (entity_id, entity_type) - emitted when hovering over entity
    entity_navigation_requested = Signal(str, str)  # (entity_id, entity_type) - emitted when user clicks to navigate to entity
    alias_add_requested = Signal(str, str, str)  # (entity_id, entity_name, current_display_text) - request to add alias
    alias_use_requested = Signal(str)  # (alias) - request to replace current entity link with alias
    entity_create_requested = Signal(str, str)  # (entity_name, entity_type) - request to create new entity

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Monospace", 11))
        self.setTabStopDistance(40)
        self.setAcceptRichText(False)  # We handle formatting ourselves

        # Enable mouse tracking for hover cursor changes
        self.setMouseTracking(True)

        # Entity autocomplete
        self._completer: Optional[QCompleter] = None
        self._entity_list: List[Dict[str, Any]] = []
        self._completion_active = False
        self._trigger_pos = -1
        self._inline_mode = False  # True when completing without [[

        # Click-based info card
        self._info_card = EntityInfoCard(self)
        self._info_card.entity_clicked.connect(self.entity_navigation_requested.emit)
        self._last_clicked_entity: Optional[str] = None
        self._click_pos: Optional[QPoint] = None

        # Install markdown syntax highlighter
        self._highlighter = MarkdownHighlighter(self.document(), self)

        # Flag for deferred highlighting
        self._pending_highlight = False
        self._highlighter_ready = False

        # Timer for updating display after text changes
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._update_entity_display)


        # Connect to text changes
        self.textChanged.connect(self._on_text_changed)

        # Connect cursor position changes to trigger rehighlighting
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

        self._setup_completer()

    def _setup_completer(self):
        """Set up the entity completer."""
        self._completer = QCompleter(self)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.activated.connect(self._insert_completion)

        # Configure popup to show more items and size appropriately
        popup = self._completer.popup()
        popup.setMinimumWidth(400)
        popup.setMinimumHeight(250)
        # Let it size based on content, but cap max visible items
        self._completer.setMaxVisibleItems(15)

        # Start with empty model
        model = QStringListModel([], self)
        self._completer.setModel(model)

    def set_entity_list(self, entities: List[Dict[str, Any]]):
        """
        Update the list of available entities for autocomplete.

        Args:
            entities: List of entity dicts with keys: id, name, type, aliases (optional)
        """
        self._entity_list = entities

        # Create display strings for completer
        display_list = []
        for entity in entities:
            name = entity.get("name", "")
            entity_type = entity.get("type", "")
            aliases = entity.get("aliases", [])

            # Format: "EntityName (type) [alias1, alias2]" or "EntityName (type)"
            if aliases:
                alias_str = ", ".join(aliases)
                display_list.append(f"{name} ({entity_type}) [{alias_str}]")
            else:
                display_list.append(f"{name} ({entity_type})")

            # Also add entries for each alias to make them searchable
            for alias in aliases:
                display_list.append(f"{alias} → {name} ({entity_type})")

        model = QStringListModel(display_list, self)
        self._completer.setModel(model)

        # Force the popup to recalculate its size based on the new model
        popup = self._completer.popup()
        popup.setUpdatesEnabled(True)
        popup.updateGeometry()

        # Extract entity names for highlighting (including aliases)
        entity_names = []
        for entity in entities:
            name = entity.get("name", "")
            if name:
                entity_names.append(name)
            aliases = entity.get("aliases", [])
            entity_names.extend(aliases)

        # Pass entity names to highlighter for plain-text matching
        self._highlighter.set_entity_names(entity_names)

        # If highlighter is ready but not yet activated, activate it now
        if self._highlighter_ready:
            print(f"[{datetime.datetime.now()}]   Entity list loaded - activating highlighter...")
            self._activate_highlighter_if_ready()
        # Otherwise, if highlighter is already active, trigger rehighlight
        # (This ensures aliases show up immediately when added)
        elif self._highlighter and self._highlighter.document():
            self._highlighter.rehighlight()


    def _activate_highlighter_if_ready(self):
        """Activate highlighter on first user interaction if cache is ready."""
        if self._highlighter_ready and self._highlighter:
            print(f"[{datetime.datetime.now()}]   First user interaction - activating highlighter...")
            activate_start = datetime.datetime.now()
            self._highlighter.setDocument(self.document())
            # Explicitly trigger rehighlight to apply cached formatting
            self._highlighter.rehighlight()
            activate_duration = (datetime.datetime.now() - activate_start).total_seconds() * 1000
            print(f"[{datetime.datetime.now()}]   Highlighter activated in {activate_duration:.1f}ms")
            self._highlighter_ready = False

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for entity autocomplete."""
        # Activate highlighter on first keystroke if ready
        self._activate_highlighter_if_ready()

        if event.text() == "\r":
            pass
        # Debug: Print timestamp when 'P' is pressed
        if event.text().upper() == 'P':
            import datetime
            print(f"[{datetime.datetime.now()}] *** USER PRESSED 'P' - UI IS RESPONSIVE ***")

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
        else:
            # Check for inline entity autocomplete (without [[)
            self._check_inline_autocomplete()

    def _check_inline_autocomplete(self):
        """Check if we should show inline autocomplete for entity names."""
        cursor = self.textCursor()

        # Get the word being typed (go back to last word boundary)
        word_start = cursor.position()
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        current_word = cursor.selectedText()

        # Only trigger if word is at least 2 characters and starts with uppercase
        if len(current_word) >= 2 and current_word[0].isupper():
            # Check if this matches any entity names
            matching_entities = [
                entity for entity in self._entity_list
                if entity.get("name", "").lower().startswith(current_word.lower())
            ]

            if matching_entities:
                # Set trigger position to start of current word
                self._trigger_pos = self.textCursor().position() - len(current_word)
                self._completion_active = True
                self._inline_mode = True  # Flag to indicate inline completion

                # Update completer with matching entities
                self._completer.setCompletionPrefix(current_word)

                # Show completer at cursor
                rect = self.cursorRect()
                # Don't set width - let the popup use its minimum width
                self._completer.complete(rect)

    def _trigger_entity_autocomplete(self):
        """Trigger entity autocomplete."""
        cursor = self.textCursor()
        self._trigger_pos = cursor.position()
        self._completion_active = True
        self._inline_mode = False  # Not inline mode, using [[ syntax

        # Request entity list (signal will be handled by controller)
        self.entity_requested.emit("")

        # Show completer
        if self._completer:
            rect = self.cursorRect()
            # Don't set width - let the popup use its minimum width
            self._completer.complete(rect)

    def _update_completer(self):
        """Update completer based on current text."""
        cursor = self.textCursor()
        current_pos = cursor.position()

        # Validate trigger position is still valid
        doc_length = self.document().characterCount()
        if self._trigger_pos >= doc_length or current_pos < self._trigger_pos:
            # Trigger position is invalid or cursor moved before trigger, cancel completion
            self._completion_active = False
            self._inline_mode = False
            self._completer.popup().hide()
            return

        # Get text between trigger position and cursor
        try:
            cursor.setPosition(self._trigger_pos)
            cursor.setPosition(current_pos, QTextCursor.KeepAnchor)
            search_text = cursor.selectedText()
        except:
            # If setting position fails, cancel completion
            self._completion_active = False
            self._inline_mode = False
            self._completer.popup().hide()
            return

        # Check exit conditions based on mode
        if self._inline_mode:
            # In inline mode, exit on space or newline
            if ' ' in search_text or '\n' in search_text:
                self._completion_active = False
                self._inline_mode = False
                self._completer.popup().hide()
                return
        else:
            # In [[ mode, exit on ]] or newline
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
        """Insert the selected entity (plain text, no syntax)."""
        if not self._completer:
            return

        # Parse completion to get entity name and type
        # Three possible formats:
        # 1. "EntityName (type)"
        # 2. "EntityName (type) [alias1, alias2]"
        # 3. "alias → EntityName (type)"

        display_text = None
        entity_name = None
        entity_type = None
        entity_id = None

        # Check for alias format: "alias → EntityName (type)"
        alias_match = re.match(r"^(.+?)\s+→\s+(.+?)\s+\((.+?)\)$", completion)
        if alias_match:
            display_text = alias_match.group(1)  # The alias
            entity_name = alias_match.group(2)   # The canonical name
            entity_type = alias_match.group(3)
        else:
            # Standard format: "EntityName (type)" or "EntityName (type) [aliases]"
            match = re.match(r"^(.+?)\s+\((.+?)\)(?:\s+\[.+?\])?$", completion)
            if match:
                entity_name = match.group(1)
                entity_type = match.group(2)
                display_text = entity_name  # Use canonical name as display

        if not entity_name or not entity_type:
            return

        # Find the entity in our list
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

        # Insert just the entity name as plain text
        cursor.insertText(display_text)

        self._completion_active = False
        self._inline_mode = False
        self.entity_selected.emit(entity_id, entity_name)

        # Refresh entity list to show all entities again
        self.entity_requested.emit("")

    def _get_entity_at_click(self, cursor: QTextCursor) -> Optional[str]:
        """
        Get entity name at click position, handling multi-word names.

        Expands selection outward from clicked word to find matching entity names.

        Args:
            cursor: Cursor at click position

        Returns:
            Matched entity name/alias, or None if no match
        """
        if not self._entity_list:
            return None

        # Start with the clicked word
        cursor.select(QTextCursor.WordUnderCursor)
        clicked_word = cursor.selectedText().strip()

        if not clicked_word:
            return None

        # Get the full text of the current block for context
        block_text = cursor.block().text()
        word_start = cursor.selectionStart() - cursor.block().position()
        word_end = cursor.selectionEnd() - cursor.block().position()

        # Try progressively larger selections (up to 5 words in each direction)
        for expand_left in range(5):
            for expand_right in range(5):
                # Calculate start and end positions for expanded selection
                # Move left by expand_left words
                start_pos = word_start
                for _ in range(expand_left):
                    # Find previous word boundary
                    while start_pos > 0 and block_text[start_pos - 1].isspace():
                        start_pos -= 1
                    while start_pos > 0 and not block_text[start_pos - 1].isspace():
                        start_pos -= 1

                # Move right by expand_right words
                end_pos = word_end
                for _ in range(expand_right):
                    # Find next word boundary
                    while end_pos < len(block_text) and block_text[end_pos].isspace():
                        end_pos += 1
                    while end_pos < len(block_text) and not block_text[end_pos].isspace():
                        end_pos += 1

                # Extract the candidate text
                candidate = block_text[start_pos:end_pos].strip()

                if not candidate:
                    continue

                # Check if this matches any entity name or alias (case-insensitive)
                for entity in self._entity_list:
                    name = entity.get("name", "")
                    aliases = entity.get("aliases", [])

                    if (name.lower() == candidate.lower() or
                        any(alias.lower() == candidate.lower() for alias in aliases)):
                        return candidate

        return None

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events to detect clicks on entity names."""
        # Activate highlighter on first click if ready
        self._activate_highlighter_if_ready()

        # Check if left-clicking on text that matches an entity name
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())

            # Try to find multi-word entity names by expanding selection
            clicked_text = self._get_entity_at_click(cursor)

            if clicked_text and self._entity_list:
                # Find all entities matching this text (case-insensitive)
                matching_entities = []
                for entity in self._entity_list:
                    name = entity.get("name", "")
                    aliases = entity.get("aliases", [])

                    # Check if clicked text matches entity name or any alias
                    if (name.lower() == clicked_text.lower() or
                        any(alias.lower() == clicked_text.lower() for alias in aliases)):
                        matching_entities.append(entity)

                if matching_entities:
                    if len(matching_entities) == 1:
                        # Single match - show info popup directly
                        entity = matching_entities[0]
                        entity_id = entity.get("id", "")
                        entity_type = entity.get("type", "")
                        entity_name = entity.get("name", "")

                        # Register entity in document (so aliases can be added later)
                        self.entity_selected.emit(entity_id, entity_name)

                        # Show info card
                        self._last_clicked_entity = entity_id
                        self._click_pos = event.globalPos() + QPoint(10, 10)
                        self.entity_hover.emit(entity_id, entity_type)

                        event.accept()
                        return
                    else:
                        # Multiple matches - show menu to choose
                        self._show_entity_selection_menu(matching_entities, event.globalPos())
                        event.accept()
                        return

        # Not clicking on entity, handle normally
        super().mousePressEvent(event)

    def _show_entity_selection_menu(self, entities: List[Dict[str, Any]], pos: QPoint):
        """Show menu to select which entity when multiple matches exist."""
        menu = QMenu(self)
        menu.setTitle("Select Entity")

        for entity in entities:
            name = entity.get("name", "")
            entity_type = entity.get("type", "")
            entity_id = entity.get("id", "")

            action = QAction(f"{name} ({entity_type})", self)
            action.triggered.connect(
                lambda checked=False, eid=entity_id, etype=entity_type, pos=pos:
                self._show_entity_from_menu(eid, etype, pos)
            )
            menu.addAction(action)

        menu.exec(pos)

    def _show_entity_from_menu(self, entity_id: str, entity_type: str, pos: QPoint):
        """Show entity info after selection from menu."""
        # Find entity name from the list
        entity_name = ""
        for entity in self._entity_list:
            if entity.get("id") == entity_id:
                entity_name = entity.get("name", "")
                break

        # Register entity in document (so aliases can be added later)
        if entity_name:
            self.entity_selected.emit(entity_id, entity_name)

        self._last_clicked_entity = entity_id
        self._click_pos = pos + QPoint(10, 10)
        self.entity_hover.emit(entity_id, entity_type)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        super().mouseMoveEvent(event)

    def show_entity_info(self, name: str, entity_type: str, details: str, entity_id: str = None):
        """
        Display entity info card. Called by controller with entity details.

        Args:
            name: Entity name
            entity_type: Entity type (character, location, faction)
            details: Details text to display
            entity_id: Entity ID (optional, defaults to last clicked entity)
        """
        if hasattr(self, '_click_pos') and self._click_pos:
            # Use provided entity_id or fall back to last clicked entity
            if entity_id is None:
                entity_id = getattr(self, '_last_clicked_entity', None)
            self._info_card.set_entity_info(name, entity_type, details, entity_id)
            self._info_card.show_at_position(self._click_pos)

    def hide_info_card(self):
        """Hide the info card if visible."""
        self._info_card.hide()
        self._last_clicked_entity = None

    def _on_text_changed(self):
        """Handle text changes to update display."""
        # Hide info card when text changes
        self._info_card.hide()
        # Debounce the update to avoid excessive processing
        self._update_timer.start(100)

    def _on_cursor_position_changed(self):
        """Handle cursor position changes to show/hide markdown syntax."""
        # Rehighlight the current block and previous block to update visibility
        cursor = self.textCursor()
        current_block = cursor.block()

        # Rehighlight current block
        self._highlighter.rehighlightBlock(current_block)

        # Also rehighlight previous block in case we moved away from it
        if hasattr(self, '_last_cursor_block') and self._last_cursor_block != current_block:
            self._highlighter.rehighlightBlock(self._last_cursor_block)

        self._last_cursor_block = current_block

    def _update_entity_display(self):
        """Update the display to show entity names without link syntax."""
        # This method is called after text changes to refresh the highlighter
        # The highlighter will automatically apply formatting
        pass

    def get_text(self) -> str:
        """Get the plain text content (with entity link syntax intact)."""
        return self.toPlainText()

    def trigger_deferred_highlight(self):
        """Trigger highlighting if it was deferred during set_text()."""
        if self._pending_highlight and self._highlighter:
            print(f"[{datetime.datetime.now()}]   Triggering deferred progressive highlight...")
            self._pending_highlight = False

            # Populate the format cache FIRST (before reattaching highlighter)
            print(f"[{datetime.datetime.now()}]   Populating format cache...")
            cache_start = datetime.datetime.now()
            self._highlighter._populate_cache(self.document())
            cache_duration = (datetime.datetime.now() - cache_start).total_seconds() * 1000
            print(f"[{datetime.datetime.now()}]   Cache populated in {cache_duration:.1f}ms")

            # DON'T reattach highlighter yet! This would trigger expensive rehighlight.
            # Instead, mark as ready and reattach on first user interaction.
            self._highlighter_ready = True
            print(f"[{datetime.datetime.now()}]   Highlighter ready (will activate on first interaction)")
            print(f"[{datetime.datetime.now()}] *** DOCUMENT IS NOW EDITABLE ***")

    def set_text(self, text: str, defer_highlight: bool = True):
        """
        Set the text content.

        Args:
            text: The text to set
            defer_highlight: If True, defer syntax highlighting (default: True for performance)
        """
        print(f"[{datetime.datetime.now()}]   set_text: START (text length: {len(text)})")

        # Temporarily detach highlighter to prevent it from running during setPlainText()
        # (Qt calls highlightBlock() for each block during insertion, which is slow)
        if self._highlighter:
            print(f"[{datetime.datetime.now()}]   set_text: Detaching highlighter...")
            self._highlighter.setDocument(None)

        # Block signals to avoid triggering text changed while setting
        print(f"[{datetime.datetime.now()}]   set_text: Calling setPlainText()...")
        self.blockSignals(True)
        self.setPlainText(text)
        print(f"[{datetime.datetime.now()}]   set_text: setPlainText() DONE")
        self.blockSignals(False)

        # DON'T reattach highlighter yet! setDocument() triggers automatic rehighlight
        # We'll reattach it later when we're ready to do progressive highlighting

        # Schedule progressive rehighlight if requested
        if self._highlighter:
            if defer_highlight:
                print(f"[{datetime.datetime.now()}]   set_text: Deferring rehighlight (will happen after document fully loads)")
                # Store flag to rehighlight later - don't schedule it now
                # This prevents QApplication.processEvents() from triggering it immediately
                self._pending_highlight = True
            else:
                print(f"[{datetime.datetime.now()}]   set_text: Reattaching highlighter and scheduling immediate rehighlight")
                self._highlighter.setDocument(self.document())
                QTimer.singleShot(0, self._highlighter.rehighlight)

        print(f"[{datetime.datetime.now()}]   set_text: END")

    def insert_entity_link(self, entity_name: str, entity_id: str):
        """Insert an entity name at the cursor position (plain text, no syntax)."""
        cursor = self.textCursor()
        cursor.insertText(entity_name)

    def _get_entity_at_cursor(self, cursor: QTextCursor) -> Optional[tuple]:
        """
        Get entity information at the cursor position.

        Returns:
            None (entity links no longer supported in new plain-text approach)
        """
        return None

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Show context menu with alias management."""
        # Refresh entity list to ensure we have all entities (not just filtered ones from autocomplete)
        self.entity_requested.emit("")
        # Process events to allow the entity list to be updated before showing menu
        QApplication.processEvents()

        # Create standard context menu
        menu = self.createStandardContextMenu()

        # Check if there's selected text
        cursor = self.textCursor()
        selected_text = cursor.selectedText().strip()

        if selected_text and self._entity_list:
            # Check if selected text is already an entity name or alias
            is_entity_or_alias = False
            for entity in self._entity_list:
                name = entity.get("name", "")
                aliases = entity.get("aliases", [])
                if (name.lower() == selected_text.lower() or
                    any(alias.lower() == selected_text.lower() for alias in aliases)):
                    is_entity_or_alias = True
                    break

            # Only show "Add as alias" if the text is NOT already an entity/alias
            if not is_entity_or_alias:
                # Add option to create alias for selected text
                menu.addSeparator()

                # Create submenu for adding alias
                alias_menu = menu.addMenu(f"Add '{selected_text}' as alias for...")

                # Group entities by type
                entities_by_type = {}
                for entity in self._entity_list:
                    entity_type = entity.get("type", "unknown")
                    if entity_type not in entities_by_type:
                        entities_by_type[entity_type] = []
                    entities_by_type[entity_type].append(entity)

                # Add entities grouped by type (with plural labels for clarity)
                type_labels = {
                    "actor": "Actors",
                    "location": "Locations",
                    "faction": "Factions",
                    "object": "Objects",
                    "worlddata": "World Data"
                }
                for entity_type in sorted(entities_by_type.keys()):
                    # Use plural label if available, otherwise capitalize and add 's'
                    label = type_labels.get(entity_type.lower(), f"{entity_type.capitalize()}s")
                    type_menu = alias_menu.addMenu(label)
                    for entity in sorted(entities_by_type[entity_type], key=lambda e: e.get("name", "")):
                        entity_name = entity.get("name", "")
                        entity_id = entity.get("id", "")

                        action = QAction(entity_name, self)
                        action.triggered.connect(
                            lambda checked=False, eid=entity_id, ename=entity_name, alias=selected_text:
                            self._add_alias_for_entity(eid, ename, alias)
                        )
                        type_menu.addAction(action)

        # Add "Add to Lorekeeper" option for creating new entities
        if selected_text:
            menu.addSeparator()

            # Create submenu for adding to Lorekeeper
            lorekeeper_menu = menu.addMenu(f"Add '{selected_text}' to Lorekeeper as...")

            # Add entity type options (matching database schema)
            entity_types = [
                ("Actor", "actor"),
                ("Location", "location"),
                ("Faction", "faction"),
                ("Object", "object"),
                ("World Data", "worlddata")
            ]

            for label, entity_type in entity_types:
                action = QAction(label, self)
                action.triggered.connect(
                    lambda checked=False, name=selected_text, etype=entity_type:
                    self.entity_create_requested.emit(name, etype)
                )
                lorekeeper_menu.addAction(action)

        # Show menu
        menu.exec(event.globalPos())

    def _add_alias_for_entity(self, entity_id: str, entity_name: str, alias: str):
        """Add an alias for an entity and request entity list refresh."""
        # Emit signal to request adding the alias
        self.alias_add_requested.emit(entity_id, entity_name, alias)

        # Request entity list refresh to pick up the new alias
        self.entity_requested.emit("")

    def _tag_selected_text_as_entity(self, entity_id: str, entity_name: str, selected_text: str):
        """
        Tag the selected text as an entity link and optionally add as alias.

        Args:
            entity_id: The entity ID to tag with
            entity_name: The canonical entity name
            selected_text: The text that was selected
        """
        # Get the current selection
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        # Replace selected text with entity link
        entity_link = f"[[{selected_text}|{entity_id}]]"
        cursor.insertText(entity_link)

        # If the selected text differs from canonical name, ask if it should be added as an alias
        if selected_text.lower() != entity_name.lower():
            reply = QMessageBox.question(
                self,
                "Add as Alias?",
                f"'{selected_text}' differs from the canonical name '{entity_name}'.\n\n"
                f"Would you like to add '{selected_text}' as an alias?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Emit signal to add the alias
                self.alias_add_requested.emit(entity_id, entity_name, selected_text)

        # Emit entity selected signal
        self.entity_selected.emit(entity_id, entity_name)

    def _show_add_alias_dialog(self, entity_id: str, entity_name: str, current_display: str):
        """Show dialog to add an alias for an entity."""
        alias, ok = QInputDialog.getText(
            self,
            "Add Alias",
            f"Add alias for '{entity_name}':\n(Current display: '{current_display}')",
            text=current_display
        )

        if ok and alias and alias.strip():
            alias = alias.strip()
            # Emit signal to parent to handle adding the alias
            self.alias_add_requested.emit(entity_id, entity_name, alias)

    def replace_entity_at_cursor(self, new_display_text: str):
        """
        Replace the entity link at the stored cursor position with new display text.

        Args:
            new_display_text: New text to display for the entity
        """
        if not hasattr(self, '_context_menu_cursor_pos'):
            return

        cursor = self.textCursor()
        cursor.setPosition(self._context_menu_cursor_pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self._context_menu_match_length)

        # Get the entity ID from the selected text
        selected = cursor.selectedText()
        match = re.match(r'\[\[([^\|]+?)\|([^\]]+?)\]\]', selected)
        if match:
            entity_id = match.group(2)
            new_link = f"[[{new_display_text}|{entity_id}]]"
            cursor.insertText(new_link)
