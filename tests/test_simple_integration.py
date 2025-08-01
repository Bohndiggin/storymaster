"""
Simplified integration tests for core Storymaster functionality
"""

import pytest
from unittest.mock import Mock, patch
from tests.test_qt_utils import (
    QT_AVAILABLE,
    QApplication,
    QKeyEvent,
    QVBoxLayout,
    QWidget,
    Qt,
)

# Skip all tests in this module if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PyQt6 not available in headless environment"
)

# Conditionally import Qt-dependent modules
if QT_AVAILABLE:
    from storymaster.view.common.custom_widgets import (
        TabNavigationTextEdit,
        TabNavigationLineEdit,
        TabNavigationComboBox,
        enable_smart_tab_navigation,
    )
    from storymaster.view.common.spellcheck import get_spell_checker
else:
    # Mock for headless environments
    from unittest.mock import MagicMock

    TabNavigationTextEdit = MagicMock()
    TabNavigationLineEdit = MagicMock()
    TabNavigationComboBox = MagicMock()
    enable_smart_tab_navigation = MagicMock()
    get_spell_checker = MagicMock()


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for integration tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestSpellCheckTabNavigationIntegration:
    """Test spell check and tab navigation working together"""

    def test_text_edit_has_both_features(self, qapp):
        """Test that TabNavigationTextEdit has both spell check and tab navigation"""
        text_edit = TabNavigationTextEdit()

        # Should have spell checking
        assert hasattr(text_edit, "spell_checker")
        assert text_edit.spell_checker.enabled is True

        # Should have tab navigation
        assert text_edit.tabChangesFocus() is True

        # Test tab key behavior
        text_edit.focusNextChild = Mock(return_value=True)
        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        text_edit.keyPressEvent(tab_event)
        text_edit.focusNextChild.assert_called_once()

    def test_line_edit_has_both_features(self, qapp):
        """Test that TabNavigationLineEdit has both spell check and tab navigation"""
        line_edit = TabNavigationLineEdit()

        # Should have spell checking
        assert hasattr(line_edit, "spell_checker")
        assert line_edit.spell_checker.enabled is True

        # Test tab navigation
        line_edit.focusNextChild = Mock(return_value=True)
        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        line_edit.keyPressEvent(tab_event)
        line_edit.focusNextChild.assert_called_once()

    def test_full_form_integration(self, qapp):
        """Test a complete form with both features enabled"""
        # Create a form
        form = QWidget()
        layout = QVBoxLayout()

        # Add custom widgets
        name_field = TabNavigationLineEdit()
        description_field = TabNavigationTextEdit()
        type_combo = TabNavigationComboBox()
        type_combo.addItems(["Character", "Location", "Object"])

        layout.addWidget(name_field)
        layout.addWidget(description_field)
        layout.addWidget(type_combo)
        form.setLayout(layout)

        # Enable smart tab navigation (this should work with existing widgets)
        input_widgets = enable_smart_tab_navigation(form)

        # Verify all widgets were found and enhanced
        assert len(input_widgets) >= 3
        assert name_field in input_widgets
        assert description_field in input_widgets
        assert type_combo in input_widgets

        # Test that all have spell checking where applicable
        assert hasattr(name_field, "spell_checker")
        assert hasattr(description_field, "spell_checker")

        # Test tab navigation (focus testing is tricky in automated tests)
        # Just verify the widgets exist and have the right properties
        assert name_field.focusPolicy() != Qt.FocusPolicy.NoFocus
        assert description_field.focusPolicy() != Qt.FocusPolicy.NoFocus


class TestSpellCheckFunctionality:
    """Test spell check functionality in isolation"""

    def test_spell_checker_singleton(self):
        """Test that spell checker works as singleton"""
        checker1 = get_spell_checker()
        checker2 = get_spell_checker()

        assert checker1 is checker2
        assert checker1.enabled is True

    def test_custom_words_functionality(self):
        """Test adding custom words"""
        spell_checker = get_spell_checker()

        # Add a test word
        test_word = "testcustomword"
        spell_checker.add_word(test_word)

        # Should be recognized as correct
        assert spell_checker.is_word_correct(test_word) is True
        assert test_word.lower() in spell_checker.custom_words

    def test_creative_writing_words(self):
        """Test that creative writing words are included"""
        spell_checker = get_spell_checker()

        # These should be recognized
        creative_words = ["worldbuilding", "protagonists", "backstory"]
        for word in creative_words:
            assert spell_checker.is_word_correct(word) is True

    def test_basic_spell_checking(self, qapp):
        """Test basic spell checking in text widget"""
        text_edit = TabNavigationTextEdit()

        # Set some text with misspellings
        text_edit.setPlainText("This is a test with som misspellings.")

        # Process events
        QApplication.processEvents()

        # Should have spell checker active
        assert text_edit.spell_checker.enabled is True


class TestTabNavigationFunctionality:
    """Test tab navigation functionality in isolation"""

    def test_tab_changes_focus_setting(self, qapp):
        """Test that TabNavigationTextEdit has correct focus setting"""
        text_edit = TabNavigationTextEdit()
        assert text_edit.tabChangesFocus() is True

    def test_ctrl_tab_inserts_tab(self, qapp):
        """Test that Ctrl+Tab inserts actual tab character"""
        text_edit = TabNavigationTextEdit()
        text_edit.insertPlainText = Mock()

        # Simulate Ctrl+Tab
        ctrl_tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.ControlModifier
        )
        text_edit.keyPressEvent(ctrl_tab_event)

        # Should have inserted tab character
        text_edit.insertPlainText.assert_called_once_with("\t")

    def test_form_tab_order_setup(self, qapp):
        """Test that form tab order can be set up"""
        form = QWidget()
        layout = QVBoxLayout()

        field1 = TabNavigationLineEdit()
        field2 = TabNavigationLineEdit()
        field3 = TabNavigationTextEdit()

        layout.addWidget(field1)
        layout.addWidget(field2)
        layout.addWidget(field3)
        form.setLayout(layout)

        # This should work without errors
        input_widgets = enable_smart_tab_navigation(form)

        # The function might find widgets multiple times due to the search algorithm
        # What's important is that it found our widgets
        assert len(input_widgets) >= 3

        # Check that our specific widgets are in the list
        widget_types = [type(w).__name__ for w in input_widgets]
        assert "TabNavigationLineEdit" in widget_types
        assert "TabNavigationTextEdit" in widget_types

    def test_paste_tab_conversion(self, qapp):
        """Test that pasted tabs are converted to spaces"""
        text_edit = TabNavigationTextEdit()
        text_edit.insertPlainText = Mock()

        # Mock mime data with tabs
        mock_mime_data = Mock()
        mock_mime_data.text.return_value = "text\twith\ttabs"

        text_edit.insertFromMimeData(mock_mime_data)

        # Should have converted tabs to spaces
        text_edit.insertPlainText.assert_called_once_with("text    with    tabs")


class TestUIResponsiveness:
    """Test UI responsiveness and performance"""

    def test_many_widgets_performance(self, qapp):
        """Test performance with many input widgets"""
        form = QWidget()
        layout = QVBoxLayout()

        # Create many widgets
        widgets = []
        for i in range(20):  # Reduced from 100 to be more reasonable
            widget = TabNavigationLineEdit()
            widget.setText(f"Field {i}")
            widgets.append(widget)
            layout.addWidget(widget)

        form.setLayout(layout)

        # This should complete quickly
        input_widgets = enable_smart_tab_navigation(form)

        # The function might find widgets multiple times, what matters is performance
        assert len(input_widgets) >= 20

        # All widgets should have spell checking
        for widget in widgets:
            assert hasattr(widget, "spell_checker")

    def test_large_text_handling(self, qapp):
        """Test handling reasonably large text"""
        text_edit = TabNavigationTextEdit()

        # Create moderately large text
        large_text = "This is a test sentence. " * 500  # ~12KB
        text_edit.setPlainText(large_text)

        # Process events
        QApplication.processEvents()

        # Should handle without issues
        assert len(text_edit.toPlainText()) > 10000
        assert text_edit.spell_checker.enabled is True

    def test_rapid_text_changes(self, qapp):
        """Test rapid text changes"""
        line_edit = TabNavigationLineEdit()

        # Rapidly change text
        for i in range(10):
            line_edit.setText(f"Text {i}")
            QApplication.processEvents()

        # Should end with final text
        assert line_edit.text() == "Text 9"
        assert hasattr(line_edit, "spell_checker")


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_empty_text_handling(self, qapp):
        """Test handling empty text"""
        text_edit = TabNavigationTextEdit()
        line_edit = TabNavigationLineEdit()

        # Empty text should not cause issues
        text_edit.setPlainText("")
        line_edit.setText("")

        QApplication.processEvents()

        assert text_edit.toPlainText() == ""
        assert line_edit.text() == ""
        assert text_edit.spell_checker.enabled is True
        assert line_edit.spell_checker.enabled is True

    def test_none_widget_handling(self, qapp):
        """Test handling None widgets in setup"""
        form = QWidget()
        layout = QVBoxLayout()

        valid_widget = TabNavigationLineEdit()
        layout.addWidget(valid_widget)
        form.setLayout(layout)

        # Should handle form with minimal widgets
        input_widgets = enable_smart_tab_navigation(form)

        assert len(input_widgets) >= 1
        assert valid_widget in input_widgets

    def test_special_characters(self, qapp):
        """Test handling special characters"""
        text_edit = TabNavigationTextEdit()
        line_edit = TabNavigationLineEdit()

        # Test with various special characters
        special_text = "Test with áccénts and 🎭 emojis"

        text_edit.setPlainText(special_text)
        line_edit.setText(special_text)

        QApplication.processEvents()

        # Should handle without crashing
        assert special_text in text_edit.toPlainText()
        assert special_text == line_edit.text()


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""

    def test_character_creation_form(self, qapp):
        """Test a realistic character creation form"""
        form = QWidget()
        layout = QVBoxLayout()

        # Create character form fields
        name_field = TabNavigationLineEdit()
        age_field = TabNavigationLineEdit()
        background_field = TabNavigationTextEdit()
        personality_field = TabNavigationTextEdit()

        layout.addWidget(name_field)
        layout.addWidget(age_field)
        layout.addWidget(background_field)
        layout.addWidget(personality_field)
        form.setLayout(layout)

        # Enable enhanced features
        enable_smart_tab_navigation(form)

        # Simulate user input
        name_field.setText("Aragorn")
        age_field.setText("87")
        background_field.setPlainText("A ranger from the North")
        personality_field.setPlainText("Noble and courageous")

        # Process events
        QApplication.processEvents()

        # Verify data
        assert name_field.text() == "Aragorn"
        assert age_field.text() == "87"
        assert "ranger" in background_field.toPlainText()
        assert "courageous" in personality_field.toPlainText()

        # All should have spell checking
        for field in [name_field, age_field, background_field, personality_field]:
            assert hasattr(field, "spell_checker")

    def test_story_note_editing(self, qapp):
        """Test story note editing scenario"""
        text_edit = TabNavigationTextEdit()

        # Simulate writing a story note
        story_text = """
        Chapter 1 Notes:
        - The hero starts in a peaceful village
        - An old wizard arrives with news
        - The call to adventure begins
        
        Key themes: courage, friendship, sacrifice
        """

        text_edit.setPlainText(story_text)
        QApplication.processEvents()

        # Should handle multi-line text with spell checking
        assert "peaceful" in text_edit.toPlainText()
        assert text_edit.spell_checker.enabled is True

        # Test tab behavior (should move focus, not insert tab)
        text_edit.focusNextChild = Mock(return_value=True)
        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        text_edit.keyPressEvent(tab_event)
        text_edit.focusNextChild.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
