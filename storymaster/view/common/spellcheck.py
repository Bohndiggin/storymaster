"""
Spell Check System for Storymaster
Provides real-time spell checking with visual feedback and suggestions
"""

import re
import os
from typing import List
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QTextCursor,
    QTextCharFormat,
    QColor,
    QSyntaxHighlighter,
    QTextDocument,
    QAction,
)
from PyQt6.QtWidgets import QTextEdit, QLineEdit, QMenu, QApplication


class SpellChecker:
    """
    Core spell checking functionality using multiple backends
    """

    def __init__(self):
        self.enabled = True
        self.custom_words = set()
        self.ignored_words = set()
        self.backend = None
        self.language = "en_US"
        self._load_backend()
        self._load_custom_dictionary()

    def _load_backend(self):
        """Load the best available spell checking backend"""
        # Try different backends in order of preference
        backends = [
            ("enchant", self._init_enchant),
            ("aspell", self._init_aspell),
            ("hunspell", self._init_hunspell),
            ("builtin", self._init_builtin),
        ]

        for name, init_func in backends:
            try:
                self.backend = init_func()
                if self.backend:
                    # Only print once per application run
                    if not hasattr(SpellChecker, "_backend_initialized"):
                        print(f"Spell check backend: {name}")
                        SpellChecker._backend_initialized = True
                    return
            except Exception as e:
                if not hasattr(SpellChecker, "_backend_initialized"):
                    print(f"Failed to initialize {name}: {e}")
                continue

        print("No spell check backend available - using basic word list")
        self.backend = self._init_builtin()

    def _init_enchant(self):
        """Initialize PyEnchant backend (most robust)"""
        try:
            import enchant
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return enchant.Dict(self.language)
        except (ImportError, Exception):
            return None

    def _init_aspell(self):
        """Initialize aspell backend"""
        try:
            import aspell

            return aspell.Speller("lang", self.language)
        except ImportError:
            return None

    def _init_hunspell(self):
        """Initialize hunspell backend"""
        try:
            import hunspell

            return hunspell.HunSpell()
        except ImportError:
            return None

    def _init_builtin(self):
        """Initialize basic built-in word list"""
        return BasicWordList()

    def _load_custom_dictionary(self):
        """Load custom words specific to creative writing"""
        # Common creative writing words that might not be in standard dictionaries
        creative_words = {
            # Fantasy/Sci-fi terms
            "worldbuilding",
            "backstory",
            "storyline",
            "subplot",
            "protagonists",
            "antagonist",
            "deuteragonist",
            "antiheroes",
            "archetype",
            "trope",
            "foreshadowing",
            "MacGuffin",
            "deus",
            "machina",
            "denouement",
            # Character terms
            "characterization",
            "backstories",
            "archetypes",
            "personas",
            "motivations",
            "flaws",
            "quirks",
            "mannerisms",
            # Plot terms
            "inciting",
            "midpoint",
            "climax",
            "resolution",
            "subplot",
            "flashback",
            "flashforward",
            "montage",
            "voiceover",
            # Genre terms
            "fantasy",
            "scifi",
            "dystopian",
            "steampunk",
            "cyberpunk",
            "paranormal",
            "supernatural",
            "magical",
            "mystical",
            # Common proper nouns that authors use
            "Storymaster",
            "Lorekeeper",
            "Litographer",
        }

        self.custom_words.update(creative_words)

        # Try to load user's custom dictionary
        try:
            custom_dict_path = os.path.expanduser(
                "~/.local/share/storymaster/custom_dictionary.txt"
            )
            if os.path.exists(custom_dict_path):
                with open(custom_dict_path, "r", encoding="utf-8") as f:
                    user_words = {line.strip().lower() for line in f if line.strip()}
                    self.custom_words.update(user_words)
        except Exception:
            pass  # Ignore errors loading custom dictionary

    def save_custom_dictionary(self):
        """Save custom words to user dictionary"""
        try:
            dict_dir = os.path.expanduser("~/.local/share/storymaster")
            os.makedirs(dict_dir, exist_ok=True)

            custom_dict_path = os.path.join(dict_dir, "custom_dictionary.txt")
            with open(custom_dict_path, "w", encoding="utf-8") as f:
                for word in sorted(self.custom_words):
                    f.write(f"{word}\n")
        except Exception as e:
            print(f"Failed to save custom dictionary: {e}")

    def is_word_correct(self, word: str) -> bool:
        """Check if a word is spelled correctly"""
        if not self.enabled or not word or not word.isalpha():
            return True

        word_lower = word.lower()

        # Check ignored words
        if word_lower in self.ignored_words:
            return True

        # Check custom words
        if word_lower in self.custom_words:
            return True

        # Check with backend
        if self.backend:
            try:
                if hasattr(self.backend, "check"):
                    return self.backend.check(word)
                elif hasattr(self.backend, "spell"):
                    return self.backend.spell(word)
                elif hasattr(self.backend, "contains"):
                    return self.backend.contains(word_lower)
            except Exception:
                pass

        return True  # Default to correct if check fails

    def get_suggestions(self, word: str) -> List[str]:
        """Get spelling suggestions for a word"""
        if not self.backend or not word:
            return []

        try:
            if hasattr(self.backend, "suggest"):
                suggestions = self.backend.suggest(word)
                return suggestions[:10]  # Limit to 10 suggestions
        except Exception:
            pass

        return []

    def add_word(self, word: str):
        """Add word to custom dictionary"""
        if word and word.isalpha():
            self.custom_words.add(word.lower())
            self.save_custom_dictionary()

    def ignore_word(self, word: str):
        """Ignore word for this session"""
        if word and word.isalpha():
            self.ignored_words.add(word.lower())


class BasicWordList:
    """Basic word list fallback when no other backend is available"""

    def __init__(self):
        # Basic English word list (abbreviated for example)
        self.words = set(
            [
                # Common words that are definitely correct
                "the",
                "be",
                "to",
                "of",
                "and",
                "a",
                "in",
                "that",
                "have",
                "for",
                "not",
                "with",
                "he",
                "as",
                "you",
                "do",
                "at",
                "this",
                "but",
                "his",
                "by",
                "from",
                "they",
                "she",
                "or",
                "an",
                "will",
                "my",
                "one",
                "all",
                "would",
                "there",
                "their",
                "what",
                "so",
                "up",
                "out",
                "if",
                "about",
                "who",
                "get",
                "which",
                "go",
                "me",
                # Add more common words...
                "character",
                "story",
                "plot",
                "scene",
                "chapter",
                "book",
                "write",
                "writing",
                "author",
                "novel",
                "fiction",
                "fantasy",
                "dialogue",
                "description",
                "narrative",
                "protagonist",
                "villain",
            ]
        )

    def contains(self, word: str) -> bool:
        """Check if word is in basic word list"""
        return word.lower() in self.words


class SpellCheckHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter that underlines misspelled words
    """

    def __init__(self, document: QTextDocument, spell_checker: SpellChecker):
        super().__init__(document)
        self.spell_checker = spell_checker
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor(255, 0, 0))
        self.misspelled_format.setUnderlineStyle(
            QTextCharFormat.UnderlineStyle.SpellCheckUnderline
        )

    def highlightBlock(self, text: str):
        """Highlight misspelled words in the text block"""
        if not self.spell_checker.enabled:
            return

        # Find all words in the text
        word_pattern = re.compile(r"\b[a-zA-Z]+\b")

        for match in word_pattern.finditer(text):
            word = match.group()
            start = match.start()
            length = match.end() - match.start()

            if not self.spell_checker.is_word_correct(word):
                self.setFormat(start, length, self.misspelled_format)


class SpellCheckLineEdit(QLineEdit):
    """
    Line edit with spell checking capabilities
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell_checker = SpellChecker()
        self.misspelled_words = set()

        # Timer for delayed spell checking (avoid checking while typing)
        self.spell_check_timer = QTimer()
        self.spell_check_timer.timeout.connect(self._check_spelling)
        self.spell_check_timer.setSingleShot(True)

        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """Handle text changes with delayed spell checking"""
        self.spell_check_timer.stop()
        self.spell_check_timer.start(500)  # Check after 500ms of no typing

    def _check_spelling(self):
        """Check spelling and update styling"""
        text = self.text()
        words = re.findall(r"\b[a-zA-Z]+\b", text)

        self.misspelled_words.clear()
        for word in words:
            if not self.spell_checker.is_word_correct(word):
                self.misspelled_words.add(word)

        # Update visual feedback (could implement red underline styling)
        self._update_spelling_style()

    def _update_spelling_style(self):
        """Update visual styling for misspelled words"""
        # For QLineEdit, we can't easily add underlines like QTextEdit
        # Could implement tooltip showing misspelled words or other feedback
        if self.misspelled_words:
            self.setToolTip(
                f"Possible misspellings: {', '.join(self.misspelled_words)}"
            )
        else:
            self.setToolTip("")

    def contextMenuEvent(self, a0):
        """Add spell check options to context menu"""
        menu = self.createStandardContextMenu()

        if self.misspelled_words:
            menu.addSeparator()

            # Get word at cursor position
            cursor_pos = self.cursorPositionAt(a0.pos())
            text = self.text()
            word_at_cursor = self._get_word_at_position(text, cursor_pos)

            if word_at_cursor in self.misspelled_words:
                suggestions = self.spell_checker.get_suggestions(word_at_cursor)

                if suggestions:
                    for suggestion in suggestions[:5]:  # Show top 5 suggestions
                        action = QAction(suggestion, self)
                        action.triggered.connect(
                            lambda checked, s=suggestion, w=word_at_cursor: self._replace_word(
                                w, s
                            )
                        )
                        menu.addAction(action)

                    menu.addSeparator()

                # Add to dictionary option
                add_action = QAction(f"Add '{word_at_cursor}' to dictionary", self)
                add_action.triggered.connect(
                    lambda: self.spell_checker.add_word(word_at_cursor)
                )
                menu.addAction(add_action)

                # Ignore word option
                ignore_action = QAction(f"Ignore '{word_at_cursor}'", self)
                ignore_action.triggered.connect(
                    lambda: self.spell_checker.ignore_word(word_at_cursor)
                )
                menu.addAction(ignore_action)

        menu.exec(a0.globalPos())

    def _get_word_at_position(self, text: str, pos: int) -> str:
        """Get the word at a specific position"""
        if pos < 0 or pos >= len(text):
            return ""

        start = pos
        while start > 0 and text[start - 1].isalpha():
            start -= 1

        end = pos
        while end < len(text) and text[end].isalpha():
            end += 1

        return text[start:end]

    def _replace_word(self, old_word: str, new_word: str):
        """Replace a misspelled word with a suggestion"""
        text = self.text()
        new_text = text.replace(old_word, new_word)
        self.setText(new_text)


class SpellCheckTextEdit(QTextEdit):
    """
    Text edit with advanced spell checking capabilities
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell_checker = SpellChecker()
        self.highlighter = SpellCheckHighlighter(self.document(), self.spell_checker)

        # Enable spell checking by default
        self.setSpellCheckEnabled(True)

    def setSpellCheckEnabled(self, enabled: bool):
        """Enable or disable spell checking"""
        self.spell_checker.enabled = enabled
        if enabled:
            if not self.highlighter:
                self.highlighter = SpellCheckHighlighter(
                    self.document(), self.spell_checker
                )
        else:
            if self.highlighter:
                self.highlighter.setParent(None)
                self.highlighter = None

        # Trigger re-highlighting
        if self.highlighter:
            self.highlighter.rehighlight()

    def contextMenuEvent(self, e):
        """Add spell check options to context menu"""
        menu = self.createStandardContextMenu()

        # Get word at cursor
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        if word and not self.spell_checker.is_word_correct(word):
            menu.addSeparator()

            suggestions = self.spell_checker.get_suggestions(word)

            if suggestions:
                for suggestion in suggestions[:8]:  # Show top 8 suggestions
                    action = QAction(suggestion, self)
                    action.triggered.connect(
                        lambda checked, s=suggestion: self._replace_current_word(s)
                    )
                    menu.addAction(action)

                menu.addSeparator()

            # Add to dictionary option
            add_action = QAction(f"Add '{word}' to dictionary", self)
            add_action.triggered.connect(lambda: self._add_word_to_dictionary(word))
            menu.addAction(add_action)

            # Ignore word option
            ignore_action = QAction(f"Ignore '{word}'", self)
            ignore_action.triggered.connect(lambda: self._ignore_word(word))
            menu.addAction(ignore_action)

        # Add spell check toggle
        menu.addSeparator()
        toggle_action = QAction(
            (
                "Enable Spell Check"
                if not self.spell_checker.enabled
                else "Disable Spell Check"
            ),
            self,
        )
        toggle_action.triggered.connect(
            lambda: self.setSpellCheckEnabled(not self.spell_checker.enabled)
        )
        menu.addAction(toggle_action)

        menu.exec(e.globalPos())

    def _replace_current_word(self, replacement: str):
        """Replace the word under cursor with a suggestion"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertText(replacement)

    def _add_word_to_dictionary(self, word: str):
        """Add word to custom dictionary"""
        self.spell_checker.add_word(word)
        if self.highlighter:
            self.highlighter.rehighlight()

    def _ignore_word(self, word: str):
        """Ignore word for this session"""
        self.spell_checker.ignore_word(word)
        if self.highlighter:
            self.highlighter.rehighlight()


def enable_spell_check(widget):
    """
    Enable spell checking on a widget

    This function can be used to retrofit existing widgets with spell checking
    """
    if isinstance(widget, QTextEdit):
        # Convert to spell checking text edit
        spell_checker = SpellChecker()
        highlighter = SpellCheckHighlighter(widget.document(), spell_checker)

        # Store references so they don't get garbage collected
        widget._spell_checker = spell_checker
        widget._spell_highlighter = highlighter

        # Add context menu method
        original_context_menu = widget.contextMenuEvent

        def enhanced_context_menu(e):
            menu = widget.createStandardContextMenu()

            # Get word at cursor
            cursor = widget.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            word = cursor.selectedText()

            if word and not spell_checker.is_word_correct(word):
                menu.addSeparator()

                suggestions = spell_checker.get_suggestions(word)
                if suggestions:
                    for suggestion in suggestions[:5]:
                        action = QAction(suggestion, widget)
                        action.triggered.connect(
                            lambda checked, s=suggestion: _replace_word_in_widget(
                                widget, s
                            )
                        )
                        menu.addAction(action)
                    menu.addSeparator()

                add_action = QAction(f"Add '{word}' to dictionary", widget)
                add_action.triggered.connect(lambda: spell_checker.add_word(word))
                menu.addAction(add_action)

            menu.exec(e.globalPos())

        widget.contextMenuEvent = enhanced_context_menu

    elif isinstance(widget, QLineEdit):
        # Add basic spell checking to line edit
        spell_checker = SpellChecker()
        widget._spell_checker = spell_checker

        # Add tooltip with misspelled words
        def check_spelling():
            text = widget.text()
            words = re.findall(r"\b[a-zA-Z]+\b", text)
            misspelled = [w for w in words if not spell_checker.is_word_correct(w)]

            if misspelled:
                widget.setToolTip(f"Possible misspellings: {', '.join(misspelled)}")
            else:
                widget.setToolTip("")

        # Check spelling when text changes
        timer = QTimer()
        timer.timeout.connect(check_spelling)
        timer.setSingleShot(True)
        widget._spell_timer = timer

        def on_text_changed():
            timer.stop()
            timer.start(500)

        widget.textChanged.connect(on_text_changed)


def _replace_word_in_widget(widget, replacement):
    """Helper function to replace word in any text widget"""
    if isinstance(widget, QTextEdit):
        cursor = widget.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertText(replacement)


# Global spell checker instance
_global_spell_checker = None


def get_spell_checker() -> SpellChecker:
    """Get the global spell checker instance"""
    global _global_spell_checker
    if _global_spell_checker is None:
        _global_spell_checker = SpellChecker()
    return _global_spell_checker
