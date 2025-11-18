"""
Loading dialog with progress indicator for document operations.
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMovie


class LoadingDialog(QDialog):
    """Dialog showing loading progress for document operations."""

    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFixedSize(300, 120)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.message_label)

        # Progress bar (indeterminate mode)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Style
        self.setStyleSheet("""
            LoadingDialog {
                background-color: #2C2C2C;
            }
            QLabel {
                color: #FFFFFF;
            }
            QProgressBar {
                border: 1px solid #4A9EFF;
                border-radius: 3px;
                background-color: #1E1E1E;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4A9EFF;
            }
        """)

    def set_message(self, message: str):
        """Update the loading message."""
        self.message_label.setText(message)

    def show_with_delay(self, delay_ms=100):
        """
        Show the dialog after a short delay.

        This prevents the dialog from flashing for very quick operations.

        Args:
            delay_ms: Milliseconds to wait before showing (default 100ms)
        """
        QTimer.singleShot(delay_ms, self.show)
