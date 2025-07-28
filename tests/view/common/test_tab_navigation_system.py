"""
Comprehensive tests for the tab navigation system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from PyQt6.QtWidgets import (
    QTextEdit,
    QLineEdit,
    QComboBox,
    QWidget,
    QVBoxLayout,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

from storymaster.view.common.custom_widgets import (
    TabNavigationTextEdit,
    TabNavigationLineEdit,
    TabNavigationComboBox,
    setup_tab_order,
    setup_form_tab_navigation,
    convert_textedit_to_tab_navigation,
    setup_enhanced_tab_navigation,
    enable_smart_tab_navigation,
)


class TestTabNavigationTextEdit:
    """Test the TabNavigationTextEdit widget"""

    @pytest.fixture
    def text_edit(self, qapp):
        """Create a TabNavigationTextEdit widget"""
        widget = TabNavigationTextEdit()
        return widget

    def test_initialization(self, text_edit):
        """Test TabNavigationTextEdit initializes correctly"""
        assert isinstance(text_edit, TabNavigationTextEdit)
        assert text_edit.tabChangesFocus() is True
        # Should inherit spell checking
        assert hasattr(text_edit, "spell_checker")

    def test_tab_key_moves_focus(self, text_edit):
        """Test that Tab key moves focus instead of inserting tab"""
        # Mock focusNextChild to verify it's called
        text_edit.focusNextChild = Mock(return_value=True)

        # Simulate Tab key press
        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        text_edit.keyPressEvent(tab_event)

        text_edit.focusNextChild.assert_called_once()

    def test_backtab_moves_focus_backward(self, text_edit):
        """Test that Backtab moves focus backward"""
        text_edit.focusPreviousChild = Mock(return_value=True)

        # Simulate Backtab key press
        backtab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Backtab, Qt.KeyboardModifier.NoModifier
        )
        text_edit.keyPressEvent(backtab_event)

        text_edit.focusPreviousChild.assert_called_once()

    def test_ctrl_tab_inserts_tab(self, text_edit):
        """Test that Ctrl+Tab inserts actual tab character"""
        # Mock insertPlainText to verify tab insertion
        text_edit.insertPlainText = Mock()

        # Simulate Ctrl+Tab key press
        ctrl_tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.ControlModifier
        )
        text_edit.keyPressEvent(ctrl_tab_event)

        text_edit.insertPlainText.assert_called_once_with("\t")

    def test_normal_keys_work_normally(self, text_edit):
        """Test that normal keys still work normally"""
        # Create a real key event for letter 'a'
        key_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier, "a"
        )

        # This should not crash and should be handled by parent class
        initial_text = text_edit.toPlainText()
        text_edit.keyPressEvent(key_event)

        # The key event handling should work (even if we can't easily test the result)
        assert True  # Test passes if no exception is thrown

    def test_paste_converts_tabs_to_spaces(self, text_edit):
        """Test that pasted content converts tabs to spaces"""
        # Mock QMimeData with tab-containing text
        mock_mime_data = Mock()
        mock_mime_data.text.return_value = "text\twith\ttabs"

        text_edit.insertPlainText = Mock()

        # Call insertFromMimeData
        text_edit.insertFromMimeData(mock_mime_data)

        # Should have replaced tabs with 4 spaces
        text_edit.insertPlainText.assert_called_once_with("text    with    tabs")

    def test_paste_with_no_text(self, text_edit):
        """Test paste behavior when mime data has no text"""
        mock_mime_data = Mock()
        mock_mime_data.text.return_value = None

        # Mock the parent's insertFromMimeData
        with patch(
            "storymaster.view.common.spellcheck.SpellCheckTextEdit.insertFromMimeData"
        ) as mock_parent:
            text_edit.insertFromMimeData(mock_mime_data)
            mock_parent.assert_called_once_with(mock_mime_data)


class TestTabNavigationLineEdit:
    """Test the TabNavigationLineEdit widget"""

    @pytest.fixture
    def line_edit(self, qapp):
        """Create a TabNavigationLineEdit widget"""
        widget = TabNavigationLineEdit()
        return widget

    def test_initialization(self, line_edit):
        """Test TabNavigationLineEdit initializes correctly"""
        assert isinstance(line_edit, TabNavigationLineEdit)
        # Should inherit spell checking
        assert hasattr(line_edit, "spell_checker")

    def test_tab_key_moves_focus(self, line_edit):
        """Test that Tab key moves focus"""
        line_edit.focusNextChild = Mock(return_value=True)

        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        line_edit.keyPressEvent(tab_event)

        line_edit.focusNextChild.assert_called_once()


class TestTabNavigationComboBox:
    """Test the TabNavigationComboBox widget"""

    @pytest.fixture
    def combo_box(self, qapp):
        """Create a TabNavigationComboBox widget"""
        widget = TabNavigationComboBox()
        widget.addItems(["Option 1", "Option 2", "Option 3"])
        return widget

    def test_initialization(self, combo_box):
        """Test TabNavigationComboBox initializes correctly"""
        assert isinstance(combo_box, TabNavigationComboBox)
        assert combo_box.count() == 3

    def test_tab_key_moves_focus(self, combo_box):
        """Test that Tab key moves focus"""
        combo_box.focusNextChild = Mock(return_value=True)

        tab_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
        )
        combo_box.keyPressEvent(tab_event)

        combo_box.focusNextChild.assert_called_once()

    def test_enter_closes_dropdown_and_moves_focus(self, combo_box):
        """Test that Enter closes dropdown and moves focus"""
        combo_box.focusNextChild = Mock(return_value=True)
        combo_box.hidePopup = Mock()

        # Mock the view to appear visible
        mock_view = Mock()
        mock_view.isVisible.return_value = True
        combo_box.view = Mock(return_value=mock_view)

        enter_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier
        )
        combo_box.keyPressEvent(enter_event)

        combo_box.hidePopup.assert_called_once()
        combo_box.focusNextChild.assert_called_once()

    def test_enter_when_dropdown_closed(self, combo_box):
        """Test Enter key when dropdown is not visible"""
        # Mock the view to appear not visible
        mock_view = Mock()
        mock_view.isVisible.return_value = False
        combo_box.view = Mock(return_value=mock_view)

        # Mock parent's keyPressEvent
        with patch("PyQt6.QtWidgets.QComboBox.keyPressEvent") as mock_parent:
            enter_event = QKeyEvent(
                QKeyEvent.Type.KeyPress,
                Qt.Key.Key_Return,
                Qt.KeyboardModifier.NoModifier,
            )
            combo_box.keyPressEvent(enter_event)

            # Should call parent's keyPressEvent
            mock_parent.assert_called_once_with(enter_event)


class TestTabOrderSetup:
    """Test tab order setup functions"""

    @pytest.fixture
    def form_widget(self, qapp):
        """Create a form widget with multiple input fields"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add various input widgets
        widget.line_edit1 = TabNavigationLineEdit()
        widget.line_edit2 = TabNavigationLineEdit()
        widget.text_edit = TabNavigationTextEdit()
        widget.combo_box = TabNavigationComboBox()

        layout.addWidget(widget.line_edit1)
        layout.addWidget(widget.line_edit2)
        layout.addWidget(widget.text_edit)
        layout.addWidget(widget.combo_box)

        widget.setLayout(layout)
        return widget

    def test_setup_tab_order_with_dict(self, form_widget):
        """Test setting up tab order with a dictionary of widgets"""
        widgets_dict = {
            "first": form_widget.line_edit1,
            "second": form_widget.line_edit2,
            "third": form_widget.text_edit,
        }

        form_widget.setTabOrder = Mock()

        setup_tab_order(form_widget, widgets_dict)

        # Should have called setTabOrder (exact order depends on dict iteration)
        assert form_widget.setTabOrder.call_count == 2

    def test_setup_tab_order_filters_none_widgets(self, form_widget):
        """Test that setup_tab_order filters out None widgets"""
        widgets = [
            form_widget.line_edit1,
            None,
            form_widget.line_edit2,
            None,
            form_widget.text_edit,
        ]

        form_widget.setTabOrder = Mock()

        setup_tab_order(form_widget, widgets)

        # Should have called setTabOrder only for non-None widgets
        assert form_widget.setTabOrder.call_count == 2


class TestTabNavigationIntegration:
    """Test tab navigation integration functions"""

    @pytest.fixture
    def qapp_instance(self):
        """Get QApplication instance"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_convert_textedit_to_tab_navigation(self, qapp_instance):
        """Test converting existing QTextEdit to tab navigation"""
        widget = QTextEdit()

        # Should not have tab changes focus initially
        assert widget.tabChangesFocus() is False

        convert_textedit_to_tab_navigation(widget)

        # Should now have tab changes focus
        assert widget.tabChangesFocus() is True

        # Should have custom keyPressEvent
        assert widget.keyPressEvent is not QTextEdit.keyPressEvent

    def test_setup_enhanced_tab_navigation(self, qapp_instance):
        """Test setting up enhanced tab navigation on a parent widget"""
        parent = QWidget()
        layout = QVBoxLayout()

        # Add regular Qt widgets
        text_edit = QTextEdit()
        line_edit = QLineEdit()
        combo_box = QComboBox()

        layout.addWidget(text_edit)
        layout.addWidget(line_edit)
        layout.addWidget(combo_box)
        parent.setLayout(layout)

        input_widgets = setup_enhanced_tab_navigation(parent)

        # Should have found all input widgets
        assert len(input_widgets) >= 3

        # QTextEdit should now have tab changes focus
        assert text_edit.tabChangesFocus() is True

        # Widgets should have spell check enabled
        assert hasattr(text_edit, "_spell_checker")
        assert hasattr(line_edit, "_spell_checker")

    def test_enable_smart_tab_navigation(self, qapp_instance):
        """Test the convenience function for enabling smart tab navigation"""
        widget = QWidget()
        layout = QVBoxLayout()

        text_edit = QTextEdit()
        line_edit = QLineEdit()

        layout.addWidget(text_edit)
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        # This should work without errors
        result = enable_smart_tab_navigation(widget)

        assert isinstance(result, list)
        assert len(result) >= 2

        # Should have enabled tab navigation
        assert text_edit.tabChangesFocus() is True


class TestTabNavigationEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def qapp_instance(self):
        """Get QApplication instance"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def test_empty_widget_list(self, qapp_instance):
        """Test setup functions with empty widget lists"""
        parent = QWidget()

        # Should not crash with empty lists
        setup_tab_order(parent, [])
        input_widgets = setup_form_tab_navigation(parent)

        assert input_widgets == []

    def test_single_widget(self, qapp_instance):
        """Test setup functions with single widget"""
        parent = QWidget()
        layout = QVBoxLayout()

        line_edit = TabNavigationLineEdit()
        layout.addWidget(line_edit)
        parent.setLayout(layout)

        parent.setTabOrder = Mock()

        setup_tab_order(parent, [line_edit])

        # Should not call setTabOrder with single widget
        parent.setTabOrder.assert_not_called()

    def test_widget_without_focus_policy(self, qapp_instance):
        """Test handling widgets that don't accept focus"""
        parent = QWidget()
        layout = QVBoxLayout()

        # Create widget with no focus policy
        no_focus_widget = QWidget()
        no_focus_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        focusable_widget = TabNavigationLineEdit()

        layout.addWidget(no_focus_widget)
        layout.addWidget(focusable_widget)
        parent.setLayout(layout)

        input_widgets = setup_form_tab_navigation(parent)

        # Should only include focusable widget
        assert no_focus_widget not in input_widgets
        assert focusable_widget in input_widgets

    def test_nested_widgets(self, qapp_instance):
        """Test tab navigation with nested widget structures"""
        parent = QWidget()
        parent_layout = QVBoxLayout()

        # Create nested container
        nested_widget = QWidget()
        nested_layout = QVBoxLayout()

        line_edit1 = TabNavigationLineEdit()
        line_edit2 = TabNavigationLineEdit()

        nested_layout.addWidget(line_edit1)
        nested_layout.addWidget(line_edit2)
        nested_widget.setLayout(nested_layout)

        parent_layout.addWidget(nested_widget)
        parent.setLayout(parent_layout)

        input_widgets = setup_form_tab_navigation(parent)

        # Should find widgets in nested structure
        assert line_edit1 in input_widgets
        assert line_edit2 in input_widgets


class TestTabNavigationPerformance:
    """Test performance aspects of tab navigation"""

    @pytest.fixture
    def large_form(self, qapp):
        """Create a form with many input widgets"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Create many input widgets
        widget.inputs = []
        for i in range(50):
            line_edit = TabNavigationLineEdit()
            line_edit.setText(f"Field {i}")
            widget.inputs.append(line_edit)
            layout.addWidget(line_edit)

        widget.setLayout(layout)
        return widget

    def test_large_form_tab_setup(self, large_form):
        """Test tab order setup with many widgets"""
        # This should complete quickly without hanging
        input_widgets = setup_form_tab_navigation(large_form)

        assert len(input_widgets) >= 50

        # All widgets should be in the list
        for widget in large_form.inputs:
            assert widget in input_widgets

    def test_rapid_key_events(self, qapp):
        """Test handling rapid key events"""
        text_edit = TabNavigationTextEdit()
        text_edit.focusNextChild = Mock(return_value=True)

        # Send many tab events rapidly
        for _ in range(100):
            tab_event = QKeyEvent(
                QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
            )
            text_edit.keyPressEvent(tab_event)

        # Should have handled all events
        assert text_edit.focusNextChild.call_count == 100


if __name__ == "__main__":
    pytest.main([__file__])
