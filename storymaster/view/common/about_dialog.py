from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtGui import QFont
import storymaster


class AboutDialog(QDialog):
    """About dialog showing application information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Storymaster")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        self.resize(400, 300)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # App name
        app_name = QLabel("Storymaster")
        app_name_font = QFont()
        app_name_font.setPointSize(18)
        app_name_font.setBold(True)
        app_name.setFont(app_name_font)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name)

        # Version
        version_label = QLabel(f"Version {storymaster.__version__}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        description = QLabel(
            "A PyQt6-based creative writing tool that combines visual story plotting "
            "with comprehensive world-building."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # Features
        features_label = QLabel("Features:")
        features_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(features_label)

        features_text = QLabel(
            "• Litographer: Visual node-based story structure planning\n"
            "• Lorekeeper: Database-driven world-building system\n"
            "• Multi-plot support with linked-list navigation\n"
            "• Comprehensive character and world management"
        )
        features_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(features_text)

        # Copyright
        copyright_label = QLabel(f"Copyright © 2025 {storymaster.__author__}")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

        # License
        license_label = QLabel("Licensed under the MIT License")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)

        # Spacer
        layout.addStretch()

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setMinimumWidth(80)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def apply_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2e2e2e;
                color: #dcdcdc;
            }
            QLabel {
                color: #dcdcdc;
                border: none;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #dcdcdc;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
                border-color: #3a3a3a;
            }
        """
        )
