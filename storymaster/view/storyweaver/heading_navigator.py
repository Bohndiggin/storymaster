"""
Navigation widget for markdown headings in StoryWeaver.
"""
import re
from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor


class HeadingNavigator(QWidget):
    """
    Navigation pane that displays document headings and allows navigation.

    Signals:
        heading_clicked: Emitted when a heading is clicked (line_number)
    """

    heading_clicked = Signal(int)  # line number

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Document Outline")
        title.setStyleSheet("font-weight: bold; font-size: 11pt; color: #CCCCCC;")
        layout.addWidget(title)

        # Heading list
        self.heading_list = QListWidget()
        self.heading_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #2C2C2C;
            }
            QListWidget::item:hover {
                background-color: #2C2C2C;
            }
            QListWidget::item:selected {
                background-color: #4A9EFF;
                color: #FFFFFF;
            }
        """)
        self.heading_list.itemClicked.connect(self._on_heading_clicked)
        layout.addWidget(self.heading_list)

    def update_headings(self, text: str):
        """
        Extract and display all headings from the document.

        Args:
            text: Full document text
        """
        self.heading_list.clear()

        # Extract headings with their line numbers
        headings = self._extract_headings(text)

        if not headings:
            # Show message if no headings
            item = QListWidgetItem("No headings found")
            item.setFlags(Qt.NoItemFlags)  # Make it non-clickable
            font = QFont()
            font.setItalic(True)
            item.setFont(font)
            item.setForeground(Qt.gray)
            self.heading_list.addItem(item)
            return

        # Add headings to list
        for heading in headings:
            item = QListWidgetItem(heading["display_text"])
            item.setData(Qt.UserRole, heading["line_number"])  # Store line number

            # Style based on heading level
            font = QFont()
            if heading["level"] == 1:
                font.setPointSize(12)
                font.setBold(True)
                item.setForeground(Qt.white)
            elif heading["level"] == 2:
                font.setPointSize(11)
                font.setBold(True)
                item.setForeground(Qt.lightGray)
            else:  # level 3
                font.setPointSize(10)
                item.setForeground(Qt.gray)

            item.setFont(font)

            # Add indentation for nested headings
            indent = "    " * (heading["level"] - 1)
            item.setText(indent + heading["text"])

            self.heading_list.addItem(item)

    def _extract_headings(self, text: str) -> List[Dict]:
        """
        Extract all markdown headings from text.

        Args:
            text: Document text

        Returns:
            List of heading dictionaries with keys: text, level, line_number, display_text
        """
        headings = []
        lines = text.split('\n')

        # Pattern for markdown headings (# , ## , ### )
        heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$')

        for line_num, line in enumerate(lines):
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))  # Count # symbols
                heading_text = match.group(2).strip()

                headings.append({
                    "text": heading_text,
                    "level": level,
                    "line_number": line_num,
                    "display_text": heading_text
                })

        return headings

    def _on_heading_clicked(self, item: QListWidgetItem):
        """Handle heading click event."""
        line_number = item.data(Qt.UserRole)
        if line_number is not None:
            self.heading_clicked.emit(line_number)
