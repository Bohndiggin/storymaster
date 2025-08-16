"""
Spell Check Configuration Dialog and Settings
"""

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QPushButton,
    QTextEdit,
    QLabel,
    QDialogButtonBox,
    QMessageBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
)
from PySide6.QtGui import QFont
from .spellcheck import get_spell_checker
from .theme import (
    get_button_style,
    get_input_style,
    get_group_box_style,
    get_dialog_style,
    COLORS,
)


class SpellCheckConfigDialog(QDialog):
    """
    Configuration dialog for spell check settings
    """

    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spell Check Settings")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(get_dialog_style())

        self.spell_checker = get_spell_checker()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()

        # Main settings splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Basic settings
        left_panel = self.create_settings_panel()
        splitter.addWidget(left_panel)

        # Right panel - Dictionary management
        right_panel = self.create_dictionary_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.apply_settings
        )

        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        if ok_button:
            ok_button.setStyleSheet(get_button_style("primary"))
        if apply_button:
            apply_button.setStyleSheet(get_button_style())
        if cancel_button:
            cancel_button.setStyleSheet(get_button_style())

        layout.addWidget(button_box)
        self.setLayout(layout)

    def create_settings_panel(self):
        """Create the main settings panel"""
        panel = QGroupBox("Spell Check Settings")
        panel.setStyleSheet(get_group_box_style())
        layout = QFormLayout()

        # Enable/disable spell checking
        self.enabled_checkbox = QCheckBox("Enable spell checking")
        self.enabled_checkbox.setToolTip(
            "Turn spell checking on or off for all text fields"
        )
        layout.addRow(self.enabled_checkbox)

        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.setStyleSheet(get_input_style())
        self.language_combo.addItems(
            [
                "English (US)",
                "English (UK)",
                "English (CA)",
                "English (AU)",
                "Spanish",
                "French",
                "German",
                "Italian",
                "Portuguese",
            ]
        )
        self.language_combo.setToolTip("Select the language for spell checking")
        layout.addRow("Language:", self.language_combo)

        # Visual feedback options
        feedback_group = QGroupBox("Visual Feedback")
        feedback_group.setStyleSheet(get_group_box_style())
        feedback_layout = QVBoxLayout()

        self.underline_errors_checkbox = QCheckBox("Underline misspelled words")
        self.underline_errors_checkbox.setToolTip(
            "Show red underlines under misspelled words"
        )
        feedback_layout.addWidget(self.underline_errors_checkbox)

        self.show_suggestions_checkbox = QCheckBox(
            "Show spelling suggestions in context menu"
        )
        self.show_suggestions_checkbox.setToolTip(
            "Right-click on misspelled words to see suggestions"
        )
        feedback_layout.addWidget(self.show_suggestions_checkbox)

        self.tooltip_errors_checkbox = QCheckBox(
            "Show misspellings in tooltips (line edits)"
        )
        self.tooltip_errors_checkbox.setToolTip(
            "Display misspelled words in field tooltips"
        )
        feedback_layout.addWidget(self.tooltip_errors_checkbox)

        feedback_group.setLayout(feedback_layout)
        layout.addRow(feedback_group)

        # Performance options
        performance_group = QGroupBox("Performance")
        performance_group.setStyleSheet(get_group_box_style())
        performance_layout = QFormLayout()

        self.check_delay_combo = QComboBox()
        self.check_delay_combo.setStyleSheet(get_input_style())
        self.check_delay_combo.addItems(["Immediate", "250ms", "500ms", "1 second"])
        self.check_delay_combo.setCurrentText("500ms")
        self.check_delay_combo.setToolTip("Delay before checking spelling while typing")
        performance_layout.addRow("Check delay:", self.check_delay_combo)

        performance_group.setLayout(performance_layout)
        layout.addRow(performance_group)

        panel.setLayout(layout)
        return panel

    def create_dictionary_panel(self):
        """Create the dictionary management panel"""
        panel = QGroupBox("Dictionary Management")
        panel.setStyleSheet(get_group_box_style())
        layout = QVBoxLayout()

        # Custom words section
        custom_group = QGroupBox("Custom Words")
        custom_group.setStyleSheet(get_group_box_style())
        custom_layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Words you've added to your personal dictionary:")
        info_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-style: italic;"
        )
        custom_layout.addWidget(info_label)

        # Custom words list
        self.custom_words_list = QListWidget()
        self.custom_words_list.setStyleSheet(get_input_style())
        self.custom_words_list.setToolTip(
            "Your personal dictionary words - double-click to remove"
        )
        custom_layout.addWidget(self.custom_words_list)

        # Add/remove custom words
        custom_buttons_layout = QHBoxLayout()

        self.add_word_input = QLineEdit()
        self.add_word_input.setStyleSheet(get_input_style())
        self.add_word_input.setPlaceholderText("Add word to dictionary...")
        self.add_word_input.setToolTip(
            "Type a word and click Add to include it in your dictionary"
        )
        custom_buttons_layout.addWidget(self.add_word_input)

        self.add_word_button = QPushButton("Add")
        self.add_word_button.setStyleSheet(get_button_style("primary"))
        self.add_word_button.clicked.connect(self.add_custom_word)
        custom_buttons_layout.addWidget(self.add_word_button)

        self.remove_word_button = QPushButton("Remove Selected")
        self.remove_word_button.setStyleSheet(get_button_style("danger"))
        self.remove_word_button.clicked.connect(self.remove_custom_word)
        custom_buttons_layout.addWidget(self.remove_word_button)

        custom_layout.addLayout(custom_buttons_layout)
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        # Built-in words section
        builtin_group = QGroupBox("Creative Writing Dictionary")
        builtin_group.setStyleSheet(get_group_box_style())
        builtin_layout = QVBoxLayout()

        builtin_info = QLabel(
            "Storymaster includes specialized terms for creative writing:\n"
            "• Fantasy/sci-fi terminology\n"
            "• Plot and character development terms\n"
            "• Genre-specific vocabulary\n"
            "• Writing craft terminology"
        )
        builtin_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        builtin_info.setWordWrap(True)
        builtin_layout.addWidget(builtin_info)

        self.creative_words_checkbox = QCheckBox("Include creative writing terms")
        self.creative_words_checkbox.setChecked(True)
        self.creative_words_checkbox.setToolTip(
            "Include specialized vocabulary for fiction writing"
        )
        builtin_layout.addWidget(self.creative_words_checkbox)

        builtin_group.setLayout(builtin_layout)
        layout.addWidget(builtin_group)

        # Dictionary info
        info_group = QGroupBox("Dictionary Information")
        info_group.setStyleSheet(get_group_box_style())
        info_layout = QFormLayout()

        self.backend_label = QLabel("Loading...")
        self.backend_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        info_layout.addRow("Backend:", self.backend_label)

        self.words_count_label = QLabel("Calculating...")
        self.words_count_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        info_layout.addRow("Custom words:", self.words_count_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        panel.setLayout(layout)
        return panel

    def load_settings(self):
        """Load current spell check settings"""
        # Load basic settings
        self.enabled_checkbox.setChecked(self.spell_checker.enabled)

        # Load language (map from internal code to display name)
        language_map = {
            "en_US": "English (US)",
            "en_GB": "English (UK)",
            "en_CA": "English (CA)",
            "en_AU": "English (AU)",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
        }

        display_language = language_map.get(self.spell_checker.language, "English (US)")
        index = self.language_combo.findText(display_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # Load feedback settings (default to True for all)
        self.underline_errors_checkbox.setChecked(True)
        self.show_suggestions_checkbox.setChecked(True)
        self.tooltip_errors_checkbox.setChecked(True)

        # Load custom words
        self.load_custom_words()

        # Load dictionary backend info
        self.update_dictionary_info()

    def load_custom_words(self):
        """Load custom words into the list"""
        self.custom_words_list.clear()
        for word in sorted(self.spell_checker.custom_words):
            # Only show words that are likely user-added (not built-in creative terms)
            if len(word) > 2 and word.isalpha():
                item = QListWidgetItem(word)
                item.setToolTip(f"Double-click to remove '{word}' from dictionary")
                self.custom_words_list.addItem(item)

        self.words_count_label.setText(f"{self.custom_words_list.count()} words")

        # Connect double-click to remove
        self.custom_words_list.itemDoubleClicked.connect(self.on_word_double_clicked)

    def update_dictionary_info(self):
        """Update dictionary backend information"""
        if hasattr(self.spell_checker.backend, "__class__"):
            backend_name = self.spell_checker.backend.__class__.__name__
            if "enchant" in backend_name.lower():
                self.backend_label.setText("PyEnchant (Recommended)")
                self.backend_label.setStyleSheet(f"color: {COLORS['primary']};")
            elif "basic" in backend_name.lower():
                self.backend_label.setText("Basic Word List (Limited)")
                self.backend_label.setStyleSheet(f"color: {COLORS['warning']};")
            else:
                self.backend_label.setText(backend_name)
        else:
            self.backend_label.setText("Unknown")

    def add_custom_word(self):
        """Add a word to the custom dictionary"""
        word = self.add_word_input.text().strip()
        if word and word.isalpha():
            self.spell_checker.add_word(word)
            self.add_word_input.clear()
            self.load_custom_words()
            # Word appears in the list, no need for popup
        elif word:
            QMessageBox.warning(
                self, "Invalid Word", "Please enter a single word with only letters."
            )

    def remove_custom_word(self):
        """Remove selected word from custom dictionary"""
        current_item = self.custom_words_list.currentItem()
        if current_item:
            word = current_item.text()
            reply = QMessageBox.question(
                self,
                "Remove Word",
                f"Remove '{word}' from your dictionary?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.spell_checker.custom_words.discard(word.lower())
                self.spell_checker.save_custom_dictionary()
                self.load_custom_words()

    def on_word_double_clicked(self, item):
        """Handle double-click on word item"""
        self.custom_words_list.setCurrentItem(item)
        self.remove_custom_word()

    def apply_settings(self):
        """Apply settings without closing dialog"""
        self.save_settings()
        self.settings_changed.emit()
        # Settings applied - user can see changes in UI

    def save_settings(self):
        """Save current settings"""
        # Save basic settings
        self.spell_checker.enabled = self.enabled_checkbox.isChecked()

        # Save language
        language_map = {
            "English (US)": "en_US",
            "English (UK)": "en_GB",
            "English (CA)": "en_CA",
            "English (AU)": "en_AU",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
        }

        display_language = self.language_combo.currentText()
        internal_language = language_map.get(display_language, "en_US")

        if internal_language != self.spell_checker.language:
            self.spell_checker.language = internal_language
            # Would need to reload backend with new language

    def accept(self):
        """Accept dialog and save settings"""
        self.save_settings()
        self.settings_changed.emit()
        super().accept()


def show_spell_check_config(parent=None):
    """
    Convenience function to show spell check configuration dialog
    """
    dialog = SpellCheckConfigDialog(parent)
    return dialog.exec()
