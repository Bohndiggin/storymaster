"""
Comprehensive tests for the spell check system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QTextEdit, QLineEdit, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QContextMenuEvent

from storymaster.view.common.spellcheck import (
    SpellChecker,
    SpellCheckTextEdit,
    SpellCheckLineEdit,
    SpellCheckHighlighter,
    BasicWordList,
    enable_spell_check,
    get_spell_checker,
)


class TestSpellChecker:
    """Test the core SpellChecker class"""

    def test_spell_checker_initialization(self):
        """Test spell checker initializes correctly"""
        checker = SpellChecker()
        assert checker.enabled is True
        assert isinstance(checker.custom_words, set)
        assert isinstance(checker.ignored_words, set)
        assert checker.language == "en_US"
        assert checker.backend is not None

    def test_basic_word_list_fallback(self):
        """Test that basic word list works as fallback"""
        with patch(
            "storymaster.view.common.spellcheck.SpellChecker._init_enchant",
            return_value=None,
        ), patch(
            "storymaster.view.common.spellcheck.SpellChecker._init_aspell",
            return_value=None,
        ), patch(
            "storymaster.view.common.spellcheck.SpellChecker._init_hunspell",
            return_value=None,
        ):

            checker = SpellChecker()
            assert isinstance(checker.backend, BasicWordList)

    def test_creative_writing_words_loaded(self):
        """Test that creative writing words are loaded"""
        checker = SpellChecker()

        # Check some creative writing terms are in custom words
        creative_terms = {"worldbuilding", "protagonists", "antagonist", "backstory"}
        for term in creative_terms:
            assert term in checker.custom_words

    def test_is_word_correct_basic(self):
        """Test basic word correctness checking"""
        checker = SpellChecker()

        # Common words should be correct
        assert checker.is_word_correct("the") is True
        assert checker.is_word_correct("story") is True

        # Empty/non-alpha strings should be considered correct
        assert checker.is_word_correct("") is True
        assert checker.is_word_correct("123") is True
        assert checker.is_word_correct("test123") is True

    def test_is_word_correct_custom_words(self):
        """Test custom words are recognized"""
        checker = SpellChecker()

        # Creative writing terms should be correct
        assert checker.is_word_correct("worldbuilding") is True
        assert checker.is_word_correct("protagonists") is True
        assert checker.is_word_correct("Storymaster") is True

    def test_add_word_to_custom_dictionary(self):
        """Test adding words to custom dictionary"""
        checker = SpellChecker()

        test_word = "testword"
        checker.add_word(test_word)

        assert test_word.lower() in checker.custom_words
        assert checker.is_word_correct(test_word) is True

    def test_ignore_word_functionality(self):
        """Test ignoring words for session"""
        checker = SpellChecker()

        test_word = "unknownword"
        checker.ignore_word(test_word)

        assert test_word.lower() in checker.ignored_words
        assert checker.is_word_correct(test_word) is True

    def test_spell_checker_disabled(self):
        """Test spell checker when disabled"""
        checker = SpellChecker()
        checker.enabled = False

        # All words should be considered correct when disabled
        assert checker.is_word_correct("definitelymisspelled") is True

    def test_get_suggestions(self):
        """Test getting spelling suggestions"""
        checker = SpellChecker()

        # Mock backend with suggestions
        checker.backend = Mock()
        checker.backend.suggest = Mock(return_value=["suggestion1", "suggestion2"])

        suggestions = checker.get_suggestions("testword")
        assert isinstance(suggestions, list)
        # Should limit to 10 suggestions max
        assert len(suggestions) <= 10


class TestBasicWordList:
    """Test the BasicWordList fallback"""

    def test_basic_word_list_initialization(self):
        """Test basic word list creates properly"""
        word_list = BasicWordList()
        assert hasattr(word_list, "words")
        assert isinstance(word_list.words, set)
        assert len(word_list.words) > 0

    def test_basic_word_list_contains(self):
        """Test basic word list word checking"""
        word_list = BasicWordList()

        # Should contain common words
        assert word_list.contains("the") is True
        assert word_list.contains("story") is True

        # Should not contain random strings
        assert word_list.contains("xyzabc") is False


class TestSpellCheckTextEdit:
    """Test the SpellCheckTextEdit widget"""

    @pytest.fixture
    def text_edit(self, qapp):
        """Create a SpellCheckTextEdit widget"""
        widget = SpellCheckTextEdit()
        return widget

    def test_spell_check_text_edit_initialization(self, text_edit):
        """Test SpellCheckTextEdit initializes correctly"""
        assert hasattr(text_edit, "spell_checker")
        assert hasattr(text_edit, "highlighter")
        assert text_edit.spell_checker.enabled is True

    def test_spell_check_enable_disable(self, text_edit):
        """Test enabling/disabling spell check"""
        # Should start enabled
        assert text_edit.spell_checker.enabled is True
        assert text_edit.highlighter is not None

        # Disable spell check
        text_edit.setSpellCheckEnabled(False)
        assert text_edit.spell_checker.enabled is False

        # Re-enable spell check
        text_edit.setSpellCheckEnabled(True)
        assert text_edit.spell_checker.enabled is True
        assert text_edit.highlighter is not None

    def test_replace_current_word(self, text_edit):
        """Test replacing current word functionality"""
        text_edit.setPlainText("This is a tset word")

        # Position cursor on "tset"
        cursor = text_edit.textCursor()
        cursor.setPosition(10)  # Position on "tset"
        text_edit.setTextCursor(cursor)

        # Replace with "test"
        text_edit._replace_current_word("test")

        assert "test" in text_edit.toPlainText()
        assert "tset" not in text_edit.toPlainText()

    def test_add_word_to_dictionary(self, text_edit):
        """Test adding word to dictionary from widget"""
        test_word = "customword"
        text_edit._add_word_to_dictionary(test_word)

        assert test_word.lower() in text_edit.spell_checker.custom_words

    def test_ignore_word(self, text_edit):
        """Test ignoring word from widget"""
        test_word = "ignoreword"
        text_edit._ignore_word(test_word)

        assert test_word.lower() in text_edit.spell_checker.ignored_words


class TestSpellCheckLineEdit:
    """Test the SpellCheckLineEdit widget"""

    @pytest.fixture
    def line_edit(self, qapp):
        """Create a SpellCheckLineEdit widget"""
        widget = SpellCheckLineEdit()
        return widget

    def test_spell_check_line_edit_initialization(self, line_edit):
        """Test SpellCheckLineEdit initializes correctly"""
        assert hasattr(line_edit, "spell_checker")
        assert hasattr(line_edit, "misspelled_words")
        assert hasattr(line_edit, "spell_check_timer")

    def test_text_changed_triggers_timer(self, line_edit):
        """Test that text changes trigger spell check timer"""
        with patch.object(line_edit.spell_check_timer, "start") as mock_start:
            line_edit.setText("test text")
            mock_start.assert_called_with(500)

    def test_spell_checking_updates_tooltip(self, line_edit):
        """Test that misspelled words update tooltip"""
        # Mock spell checker to return specific misspelled words
        line_edit.spell_checker.is_word_correct = Mock(
            side_effect=lambda x: x != "misspelled"
        )

        line_edit.setText("good misspelled words")
        line_edit._check_spelling()

        tooltip = line_edit.toolTip()
        assert "misspelled" in tooltip

    def test_get_word_at_position(self, line_edit):
        """Test getting word at cursor position"""
        line_edit.setText("hello world test")

        # Test getting word at different positions
        assert line_edit._get_word_at_position("hello world", 0) == "hello"
        assert line_edit._get_word_at_position("hello world", 6) == "world"
        assert line_edit._get_word_at_position("hello world", 2) == "hello"

    def test_replace_word(self, line_edit):
        """Test replacing word in line edit"""
        line_edit.setText("This is tset")
        line_edit._replace_word("tset", "test")

        assert line_edit.text() == "This is test"


class TestSpellCheckHighlighter:
    """Test the syntax highlighter for spell checking"""

    @pytest.fixture
    def highlighter(self, qapp):
        """Create a spell check highlighter"""
        text_edit = SpellCheckTextEdit()
        return text_edit.highlighter

    def test_highlighter_initialization(self, highlighter):
        """Test highlighter initializes correctly"""
        assert hasattr(highlighter, "spell_checker")
        assert hasattr(highlighter, "misspelled_format")

    def test_highlight_block_when_disabled(self, highlighter):
        """Test highlighting when spell check is disabled"""
        highlighter.spell_checker.enabled = False

        # Should not highlight anything when disabled
        # This is mostly testing that it doesn't crash
        highlighter.highlightBlock("test misspelled words")

    def test_highlight_block_with_misspellings(self, highlighter):
        """Test highlighting identifies misspelled words"""
        # Mock spell checker to identify specific misspellings
        highlighter.spell_checker.is_word_correct = Mock(
            side_effect=lambda x: x != "misspelled"
        )

        with patch.object(highlighter, "setFormat") as mock_format:
            highlighter.highlightBlock("good misspelled words")

            # Should have called setFormat for the misspelled word
            mock_format.assert_called()


class TestSpellCheckIntegration:
    """Test spell check integration with existing widgets"""

    @pytest.fixture
    def qapp_instance(self):
        """Get QApplication instance"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_enable_spell_check_on_text_edit(self, qapp_instance):
        """Test enabling spell check on existing QTextEdit"""
        widget = QTextEdit()
        enable_spell_check(widget)

        assert hasattr(widget, "_spell_checker")
        assert hasattr(widget, "_spell_highlighter")

    def test_enable_spell_check_on_line_edit(self, qapp_instance):
        """Test enabling spell check on existing QLineEdit"""
        widget = QLineEdit()
        enable_spell_check(widget)

        assert hasattr(widget, "_spell_checker")
        assert hasattr(widget, "_spell_timer")

    def test_global_spell_checker_singleton(self):
        """Test that global spell checker is a singleton"""
        checker1 = get_spell_checker()
        checker2 = get_spell_checker()

        assert checker1 is checker2


class TestSpellCheckPerformance:
    """Test spell check performance and edge cases"""

    def test_large_text_performance(self, qapp):
        """Test spell checking with large text"""
        text_edit = SpellCheckTextEdit()

        # Create large text with some misspellings
        large_text = "This is a large text document. " * 1000 + "misspeled word"

        # This should not hang or crash
        text_edit.setPlainText(large_text)

        # Give it time to process
        QApplication.processEvents()

        assert len(text_edit.toPlainText()) > 30000

    def test_rapid_text_changes(self, qapp):
        """Test rapid text changes don't cause issues"""
        line_edit = SpellCheckLineEdit()

        # Rapidly change text
        for i in range(10):
            line_edit.setText(f"test text {i}")
            QApplication.processEvents()

        # Should handle rapid changes gracefully
        assert line_edit.text() == "test text 9"

    def test_empty_text_handling(self, qapp):
        """Test handling empty text"""
        text_edit = SpellCheckTextEdit()
        line_edit = SpellCheckLineEdit()

        # Empty text should not cause issues
        text_edit.setPlainText("")
        line_edit.setText("")

        QApplication.processEvents()

        assert text_edit.toPlainText() == ""
        assert line_edit.text() == ""

    def test_special_characters_handling(self, qapp):
        """Test handling text with special characters"""
        text_edit = SpellCheckTextEdit()

        special_text = "Test with émojis 🎉 and spëcial chars: áéíóú"
        text_edit.setPlainText(special_text)

        QApplication.processEvents()

        # Should handle special characters without crashing
        assert special_text in text_edit.toPlainText()


if __name__ == "__main__":
    pytest.main([__file__])
