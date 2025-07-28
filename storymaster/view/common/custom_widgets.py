"""
Custom widgets for Storymaster with improved tab navigation and user experience
"""

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent, QFocusEvent
from PyQt6.QtWidgets import QTextEdit, QLineEdit, QComboBox, QApplication
from .spellcheck import SpellCheckTextEdit, SpellCheckLineEdit, enable_spell_check


class TabNavigationTextEdit(SpellCheckTextEdit):
    """
    Custom QTextEdit that uses Tab key for navigation instead of inserting tab characters

    Features:
    - Tab moves to next widget in tab order
    - Shift+Tab moves to previous widget
    - Ctrl+Tab inserts actual tab character (for when users really need it)
    - Built-in spell checking with red underlines
    - Right-click context menu with spelling suggestions
    - Maintains all other QTextEdit functionality
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabChangesFocus(True)  # This is the key setting!

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events with custom tab behavior"""

        # Handle Ctrl+Tab to insert actual tab if user really needs it
        if (
            event.key() == Qt.Key.Key_Tab
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            # Insert actual tab character
            self.insertPlainText("\t")
            return

        # Handle regular Tab and Shift+Tab for navigation
        if event.key() == Qt.Key.Key_Tab:
            # Move to next widget
            self.focusNextChild()
            return
        elif event.key() == Qt.Key.Key_Backtab or (
            event.key() == Qt.Key.Key_Tab
            and event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        ):
            # Move to previous widget
            self.focusPreviousChild()
            return

        # For all other keys, use default behavior
        super().keyPressEvent(event)

    def insertFromMimeData(self, source):
        """Handle paste operations to avoid unwanted tab characters"""
        # Get the text and replace any tabs with spaces
        text = source.text()
        if text:
            # Replace tabs with 4 spaces to maintain formatting but avoid tab issues
            cleaned_text = text.replace("\t", "    ")
            self.insertPlainText(cleaned_text)
        else:
            super().insertFromMimeData(source)


class TabNavigationLineEdit(SpellCheckLineEdit):
    """
    Enhanced QLineEdit with improved tab navigation and spell checking

    Features:
    - Tab moves to next widget in tab order
    - Basic spell checking with tooltip feedback
    - Consistent behavior with other input widgets
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        # Tab and Shift+Tab work naturally in QLineEdit for navigation
        # Just ensure we're handling them properly
        if event.key() == Qt.Key.Key_Tab:
            self.focusNextChild()
            return
        elif event.key() == Qt.Key.Key_Backtab or (
            event.key() == Qt.Key.Key_Tab
            and event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        ):
            self.focusPreviousChild()
            return

        super().keyPressEvent(event)


class TabNavigationComboBox(QComboBox):
    """
    Enhanced QComboBox with improved tab navigation
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        # For combo boxes, we want Enter/Return to close dropdown and move to next field
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.view().isVisible():
                # Close the dropdown first
                self.hidePopup()
                # Then move to next field
                self.focusNextChild()
                return

        # Handle tab navigation
        if event.key() == Qt.Key.Key_Tab:
            self.focusNextChild()
            return
        elif event.key() == Qt.Key.Key_Backtab or (
            event.key() == Qt.Key.Key_Tab
            and event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        ):
            self.focusPreviousChild()
            return

        super().keyPressEvent(event)


def setup_tab_order(widget, field_widgets):
    """
    Set up logical tab order for a form widget

    Args:
        widget: The parent widget containing the form
        field_widgets: List or dict of widgets to include in tab order
    """
    if isinstance(field_widgets, dict):
        # If it's a dict, extract the widgets in a logical order
        widgets = list(field_widgets.values())
    else:
        widgets = field_widgets

    # Filter out None widgets and ensure they're all focusable
    focusable_widgets = []
    for w in widgets:
        if w is not None and w.focusPolicy() != Qt.FocusPolicy.NoFocus:
            focusable_widgets.append(w)

    # Set up tab order
    for i in range(len(focusable_widgets) - 1):
        widget.setTabOrder(focusable_widgets[i], focusable_widgets[i + 1])


def setup_form_tab_navigation(form_widget):
    """
    Automatically set up tab navigation for a form widget

    This function finds all input widgets in a form and sets up logical tab order
    """
    # Find all focusable input widgets
    input_widgets = []

    # Look for common input widget types
    widget_types = (
        TabNavigationLineEdit,
        QLineEdit,
        TabNavigationTextEdit,
        QTextEdit,
        TabNavigationComboBox,
        QComboBox,
    )

    def find_widgets(parent):
        """Recursively find input widgets"""
        for child in parent.findChildren(widget_types):
            if child.focusPolicy() != Qt.FocusPolicy.NoFocus:
                input_widgets.append(child)

    find_widgets(form_widget)

    # Sort widgets by their vertical position to create logical tab order
    input_widgets.sort(key=lambda w: (w.y(), w.x()))

    # Set up tab order
    for i in range(len(input_widgets) - 1):
        form_widget.setTabOrder(input_widgets[i], input_widgets[i + 1])

    return input_widgets


def convert_textedit_to_tab_navigation(widget):
    """
    Convert existing QTextEdit widgets to use tab navigation

    This is a helper function for retrofitting existing forms
    """
    if isinstance(widget, QTextEdit) and not isinstance(widget, TabNavigationTextEdit):
        # We can't change the class, but we can modify the behavior
        widget.setTabChangesFocus(True)

        # Store original keyPressEvent
        original_key_press = widget.keyPressEvent

        def custom_key_press(event):
            """Custom key press handler"""
            # Handle Ctrl+Tab to insert actual tab
            if (
                event.key() == Qt.Key.Key_Tab
                and event.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                widget.insertPlainText("\t")
                return

            # Handle regular Tab for navigation (setTabChangesFocus should handle this)
            if event.key() == Qt.Key.Key_Tab:
                widget.focusNextChild()
                return
            elif event.key() == Qt.Key.Key_Backtab or (
                event.key() == Qt.Key.Key_Tab
                and event.modifiers() == Qt.KeyboardModifier.ShiftModifier
            ):
                widget.focusPreviousChild()
                return

            # Use original behavior for other keys
            original_key_press(event)

        # Replace the method
        widget.keyPressEvent = custom_key_press


def setup_enhanced_tab_navigation(parent_widget):
    """
    Set up enhanced tab navigation and spell checking for all widgets in a parent

    This function:
    1. Converts existing QTextEdit widgets to use tab navigation
    2. Enables spell checking on text input widgets
    3. Sets up logical tab order
    4. Ensures consistent behavior across all input widgets
    """
    # Convert existing QTextEdit widgets
    for text_edit in parent_widget.findChildren(QTextEdit):
        convert_textedit_to_tab_navigation(text_edit)
        # Enable spell checking if it's not already a SpellCheckTextEdit
        if not isinstance(text_edit, (TabNavigationTextEdit, SpellCheckTextEdit)):
            enable_spell_check(text_edit)

    # Enable spell checking on QLineEdit widgets too
    for line_edit in parent_widget.findChildren(QLineEdit):
        if not isinstance(line_edit, (TabNavigationLineEdit, SpellCheckLineEdit)):
            enable_spell_check(line_edit)

    # Set up form tab navigation
    input_widgets = setup_form_tab_navigation(parent_widget)

    return input_widgets


# Convenience function for easy integration
def enable_smart_tab_navigation(widget_or_dialog):
    """
    One-line function to enable smart tab navigation and spell checking on any widget or dialog

    Features enabled:
    - Smart tab navigation (Tab moves between fields)
    - Spell checking with visual feedback
    - Right-click spelling suggestions
    - Custom dictionary support

    Usage:
        enable_smart_tab_navigation(self)  # In dialog __init__
        enable_smart_tab_navigation(my_form_widget)  # For specific widgets
    """
    return setup_enhanced_tab_navigation(widget_or_dialog)
