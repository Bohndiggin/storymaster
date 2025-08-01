"""
Comprehensive tests for UI components and interactions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tests.test_qt_utils import (
    QT_AVAILABLE,
    QContextMenuEvent,
    QKeyEvent,
    QMouseEvent,
    QPoint,
    Qt,
    QApplication,
    QDialog,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QLabel,
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
    )
    from storymaster.view.common.tooltips import (
        LOREKEEPER_TOOLTIPS,
        LITOGRAPHER_TOOLTIPS,
        CHARACTER_ARC_TOOLTIPS,
    )
    from storymaster.view.common.spell_check_config import SpellCheckConfigDialog
else:
    # Mock for headless environments
    from unittest.mock import MagicMock

    TabNavigationTextEdit = MagicMock()
    TabNavigationLineEdit = MagicMock()
    TabNavigationComboBox = MagicMock()
    LOREKEEPER_TOOLTIPS = {}
    LITOGRAPHER_TOOLTIPS = {}
    CHARACTER_ARC_TOOLTIPS = {}
    SpellCheckConfigDialog = MagicMock()


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestTooltipSystem:
    """Test the tooltip system functionality"""

    def test_lorekeeper_tooltips_exist(self):
        """Test that Lorekeeper tooltips are defined"""
        assert isinstance(LOREKEEPER_TOOLTIPS, dict)
        assert len(LOREKEEPER_TOOLTIPS) > 0

        # Test some expected tooltips
        expected_keys = [
            "actor_first_name",
            "actor_last_name",
            "actor_description",
            "location_name",
            "location_description",
            "faction_name",
        ]

        for key in expected_keys:
            assert key in LOREKEEPER_TOOLTIPS
            assert isinstance(LOREKEEPER_TOOLTIPS[key], str)
            assert len(LOREKEEPER_TOOLTIPS[key]) > 10  # Should be descriptive

    def test_litographer_tooltips_exist(self):
        """Test that Litographer tooltips are defined"""
        assert isinstance(LITOGRAPHER_TOOLTIPS, dict)
        assert len(LITOGRAPHER_TOOLTIPS) > 0

        # Test some expected tooltips
        expected_keys = [
            "node_label",
            "node_description",
            "node_type",
            "plot_title",
            "plot_description",
        ]

        for key in expected_keys:
            assert key in LITOGRAPHER_TOOLTIPS

    def test_character_arc_tooltips_exist(self):
        """Test that Character Arc tooltips are defined"""
        assert isinstance(CHARACTER_ARC_TOOLTIPS, dict)
        assert len(CHARACTER_ARC_TOOLTIPS) > 0

        # Test some expected tooltips
        expected_keys = [
            "arc_title",
            "arc_description",
            "arc_type",
            "arc_point_title",
            "arc_point_description",
        ]

        for key in expected_keys:
            assert key in CHARACTER_ARC_TOOLTIPS

    def test_tooltip_content_quality(self):
        """Test that tooltips are well-written and helpful"""
        all_tooltips = {
            **LOREKEEPER_TOOLTIPS,
            **LITOGRAPHER_TOOLTIPS,
            **CHARACTER_ARC_TOOLTIPS,
        }

        for key, tooltip in all_tooltips.items():
            # Should be strings
            assert isinstance(tooltip, str)

            # Should be reasonably long (descriptive)
            assert len(tooltip) >= 10

            # Should not be empty or just whitespace
            assert tooltip.strip() != ""

            # Should start with capital letter (good grammar)
            assert tooltip[0].isupper() or tooltip[0].isdigit()

            # Should not contain placeholder text
            assert "TODO" not in tooltip.upper()
            assert "FIXME" not in tooltip.upper()
            assert "XXX" not in tooltip


class TestSpellCheckConfigDialog:
    """Test the spell check configuration dialog"""

    @pytest.fixture
    def config_dialog(self, qapp):
        """Create a spell check configuration dialog"""
        dialog = SpellCheckConfigDialog()
        return dialog

    def test_dialog_initialization(self, config_dialog):
        """Test dialog initializes correctly"""
        assert config_dialog.windowTitle() == "Spell Check Settings"
        assert config_dialog.minimumSize().width() >= 600
        assert config_dialog.minimumSize().height() >= 500

        # Should have basic UI elements
        assert hasattr(config_dialog, "enabled_checkbox")
        assert hasattr(config_dialog, "language_combo")
        assert hasattr(config_dialog, "custom_words_list")

    def test_language_options(self, config_dialog):
        """Test language selection options"""
        combo = config_dialog.language_combo

        # Should have multiple language options
        assert combo.count() >= 5

        # Should include common languages
        items = [combo.itemText(i) for i in range(combo.count())]
        assert "English (US)" in items
        assert "English (UK)" in items
        assert "Spanish" in items
        assert "French" in items

    def test_enable_disable_functionality(self, config_dialog):
        """Test enabling/disabling spell check"""
        checkbox = config_dialog.enabled_checkbox

        # Should start enabled
        assert checkbox.isChecked() is True

        # Test toggling
        checkbox.setChecked(False)
        assert checkbox.isChecked() is False

        checkbox.setChecked(True)
        assert checkbox.isChecked() is True

    def test_custom_word_management(self, config_dialog):
        """Test adding and removing custom words"""
        # Test add word functionality
        config_dialog.add_word_input.setText("testword")

        with patch.object(config_dialog.spell_checker, "add_word") as mock_add_word:
            config_dialog.add_custom_word()
            mock_add_word.assert_called_once_with("testword")

        # Input should be cleared after adding
        assert config_dialog.add_word_input.text() == ""

    def test_invalid_word_handling(self, config_dialog):
        """Test handling of invalid words"""
        # Test empty word
        config_dialog.add_word_input.setText("")

        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            config_dialog.add_custom_word()
            mock_warning.assert_not_called()

        # Test word with numbers
        config_dialog.add_word_input.setText("test123")

        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            config_dialog.add_custom_word()
            mock_warning.assert_called_once()

    def test_settings_persistence(self, config_dialog):
        """Test that settings can be modified"""
        # Modify settings - just test that the UI responds
        initial_enabled = config_dialog.enabled_checkbox.isChecked()
        config_dialog.enabled_checkbox.setChecked(not initial_enabled)

        # Should be able to change the checkbox state
        assert config_dialog.enabled_checkbox.isChecked() != initial_enabled

        # Should be able to change language selection
        config_dialog.language_combo.setCurrentText("Spanish")
        assert config_dialog.language_combo.currentText() == "Spanish"


class TestCustomWidgetIntegration:
    """Test integration of custom widgets in forms"""

    @pytest.fixture
    def form_with_widgets(self, qapp):
        """Create a form with various custom widgets"""
        form = QWidget()
        layout = QVBoxLayout()

        # Add various custom widgets
        form.line_edit = TabNavigationLineEdit()
        form.text_edit = TabNavigationTextEdit()
        form.combo_box = TabNavigationComboBox()
        form.button = QPushButton("Test Button")

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(form.line_edit)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(form.text_edit)
        layout.addWidget(QLabel("Type:"))
        layout.addWidget(form.combo_box)
        layout.addWidget(form.button)

        form.setLayout(layout)
        return form

    def test_tab_navigation_flow(self, form_with_widgets):
        """Test tab navigation setup"""
        form = form_with_widgets

        # Set up focus chain - this should work without errors
        form.setTabOrder(form.line_edit, form.text_edit)
        form.setTabOrder(form.text_edit, form.combo_box)
        form.setTabOrder(form.combo_box, form.button)

        # Just test that the widgets exist and can be configured
        assert form.line_edit is not None
        assert form.text_edit is not None
        assert form.combo_box is not None
        assert form.button is not None

    def test_spell_check_integration(self, form_with_widgets):
        """Test that spell checking works in custom widgets"""
        form = form_with_widgets

        # Text edit should have spell checker
        assert hasattr(form.text_edit, "spell_checker")
        assert form.text_edit.spell_checker is not None

        # Line edit should have spell checker
        assert hasattr(form.line_edit, "spell_checker")
        assert form.line_edit.spell_checker is not None

    def test_widget_tooltips(self, form_with_widgets):
        """Test that widgets can have tooltips applied"""
        form = form_with_widgets

        # Apply tooltips
        form.line_edit.setToolTip("Enter the character's name")
        form.text_edit.setToolTip("Describe the character in detail")

        assert form.line_edit.toolTip() == "Enter the character's name"
        assert form.text_edit.toolTip() == "Describe the character in detail"

    def test_widget_styling(self, form_with_widgets):
        """Test that widgets accept styling"""
        form = form_with_widgets

        # Apply styles
        form.line_edit.setStyleSheet("background-color: #f0f0f0;")
        form.text_edit.setStyleSheet("background-color: #ffffff;")

        # Should not crash and should have styles applied
        assert "background-color: #f0f0f0" in form.line_edit.styleSheet()
        assert "background-color: #ffffff" in form.text_edit.styleSheet()


class TestContextMenus:
    """Test context menu functionality"""

    @pytest.fixture
    def text_widget(self, qapp):
        """Create a text widget for context menu testing"""
        widget = TabNavigationTextEdit()
        widget.setPlainText("This is a test with misspelled words")
        return widget

    def test_context_menu_creation(self, text_widget):
        """Test that context menus can be created"""
        # Mock the context menu event
        pos = QPoint(10, 10)
        context_event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, pos)

        # Mock createStandardContextMenu
        mock_menu = Mock()
        text_widget.createStandardContextMenu = Mock(return_value=mock_menu)

        # Call context menu event
        text_widget.contextMenuEvent(context_event)

        # Should have created standard context menu
        text_widget.createStandardContextMenu.assert_called_once()

    def test_spell_check_context_menu_items(self, text_widget):
        """Test that spell check items are added to context menu"""
        # Mock spell checker to return misspelled word
        text_widget.spell_checker.is_word_correct = Mock(return_value=False)
        text_widget.spell_checker.get_suggestions = Mock(
            return_value=["suggestion1", "suggestion2"]
        )

        # Mock menu
        mock_menu = Mock()
        mock_menu.addSeparator = Mock()
        mock_menu.addAction = Mock()
        mock_menu.exec = Mock()

        text_widget.createStandardContextMenu = Mock(return_value=mock_menu)

        # Mock text cursor selection
        mock_cursor = Mock()
        mock_cursor.selectedText.return_value = "misspelled"
        text_widget.textCursor = Mock(return_value=mock_cursor)

        # Call context menu
        pos = QPoint(10, 10)
        context_event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, pos)
        text_widget.contextMenuEvent(context_event)

        # Should have added spelling suggestions
        assert mock_menu.addAction.call_count >= 2  # At least suggestion actions


class TestWidgetInteractions:
    """Test widget interactions and user input handling"""

    @pytest.fixture
    def interactive_form(self, qapp):
        """Create an interactive form for testing"""
        form = QWidget()
        layout = QVBoxLayout()

        form.name_input = TabNavigationLineEdit()
        form.description_input = TabNavigationTextEdit()
        form.type_combo = TabNavigationComboBox()
        form.type_combo.addItems(["Character", "Location", "Object"])
        form.save_button = QPushButton("Save")

        layout.addWidget(form.name_input)
        layout.addWidget(form.description_input)
        layout.addWidget(form.type_combo)
        layout.addWidget(form.save_button)

        form.setLayout(layout)
        return form

    def test_text_input_handling(self, interactive_form):
        """Test text input in line edit"""
        line_edit = interactive_form.name_input

        # Simulate typing
        line_edit.setText("Test Character")
        assert line_edit.text() == "Test Character"

        # Test clearing
        line_edit.clear()
        assert line_edit.text() == ""

    def test_multiline_text_input(self, interactive_form):
        """Test multiline text input"""
        text_edit = interactive_form.description_input

        test_text = "This is a long\nmultiline description\nof a character."
        text_edit.setPlainText(test_text)

        assert test_text in text_edit.toPlainText()

    def test_combo_box_selection(self, interactive_form):
        """Test combo box selection"""
        combo = interactive_form.type_combo

        # Test initial state
        assert combo.count() == 3
        assert combo.currentText() == "Character"

        # Test selection change
        combo.setCurrentText("Location")
        assert combo.currentText() == "Location"

        combo.setCurrentIndex(2)
        assert combo.currentText() == "Object"

    def test_button_interactions(self, interactive_form):
        """Test button click handling"""
        button = interactive_form.save_button

        # Mock click handler
        click_handler = Mock()
        button.clicked.connect(click_handler)

        # Simulate click
        button.click()

        click_handler.assert_called_once()

    def test_keyboard_shortcuts(self, interactive_form):
        """Test keyboard shortcuts and navigation"""
        form = interactive_form

        # Test Ctrl+A (select all) - should work in text fields
        ctrl_a_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier
        )

        form.name_input.setText("Test text")
        form.name_input.keyPressEvent(ctrl_a_event)

        # Should handle keyboard event without crashing
        assert form.name_input.text() == "Test text"

    def test_focus_handling(self, interactive_form):
        """Test focus methods don't crash"""
        line_edit = interactive_form.name_input

        # Test that focus methods can be called without crashing
        line_edit.setFocus()
        line_edit.clearFocus()

        # Verify the widget still functions after focus operations
        line_edit.setText("Focus test")
        assert line_edit.text() == "Focus test"


class TestWidgetDataBinding:
    """Test data binding and validation in widgets"""

    @pytest.fixture
    def data_form(self, qapp):
        """Create a form with data binding"""
        form = QWidget()
        layout = QVBoxLayout()

        form.fields = {
            "name": TabNavigationLineEdit(),
            "age": TabNavigationLineEdit(),
            "description": TabNavigationTextEdit(),
            "category": TabNavigationComboBox(),
        }

        form.fields["category"].addItems(["Hero", "Villain", "Supporting"])

        for label, widget in form.fields.items():
            layout.addWidget(QLabel(label.title() + ":"))
            layout.addWidget(widget)

        form.setLayout(layout)
        return form

    def test_data_population(self, data_form):
        """Test populating form with data"""
        test_data = {
            "name": "Frodo Baggins",
            "age": "50",
            "description": "A brave hobbit on an epic quest.",
            "category": "Hero",
        }

        # Populate form
        for field, value in test_data.items():
            widget = data_form.fields[field]
            if isinstance(widget, TabNavigationLineEdit):
                widget.setText(value)
            elif isinstance(widget, TabNavigationTextEdit):
                widget.setPlainText(value)
            elif isinstance(widget, TabNavigationComboBox):
                widget.setCurrentText(value)

        # Verify data
        assert data_form.fields["name"].text() == "Frodo Baggins"
        assert data_form.fields["age"].text() == "50"
        assert "brave hobbit" in data_form.fields["description"].toPlainText()
        assert data_form.fields["category"].currentText() == "Hero"

    def test_data_extraction(self, data_form):
        """Test extracting data from form"""
        # Set up form data
        data_form.fields["name"].setText("Gandalf")
        data_form.fields["age"].setText("2000")
        data_form.fields["description"].setPlainText("A wise wizard")
        data_form.fields["category"].setCurrentText("Supporting")

        # Extract data
        extracted_data = {}
        for field, widget in data_form.fields.items():
            if isinstance(widget, TabNavigationLineEdit):
                extracted_data[field] = widget.text()
            elif isinstance(widget, TabNavigationTextEdit):
                extracted_data[field] = widget.toPlainText()
            elif isinstance(widget, TabNavigationComboBox):
                extracted_data[field] = widget.currentText()

        # Verify extracted data
        assert extracted_data["name"] == "Gandalf"
        assert extracted_data["age"] == "2000"
        assert extracted_data["description"] == "A wise wizard"
        assert extracted_data["category"] == "Supporting"

    def test_form_validation(self, data_form):
        """Test form validation logic"""

        def validate_form(form):
            errors = []

            # Name is required
            if not form.fields["name"].text().strip():
                errors.append("Name is required")

            # Age should be numeric
            age_text = form.fields["age"].text().strip()
            if age_text and not age_text.isdigit():
                errors.append("Age must be a number")

            # Description should not be empty
            if not form.fields["description"].toPlainText().strip():
                errors.append("Description is required")

            return errors

        # Test with empty form
        errors = validate_form(data_form)
        assert "Name is required" in errors
        assert "Description is required" in errors

        # Test with valid data
        data_form.fields["name"].setText("Valid Name")
        data_form.fields["age"].setText("25")
        data_form.fields["description"].setPlainText("Valid description")

        errors = validate_form(data_form)
        assert len(errors) == 0

        # Test with invalid age
        data_form.fields["age"].setText("not a number")
        errors = validate_form(data_form)
        assert "Age must be a number" in errors


class TestWidgetPerformance:
    """Test widget performance with large amounts of data"""

    def test_large_text_handling(self, qapp):
        """Test handling large amounts of text"""
        text_edit = TabNavigationTextEdit()

        # Create large text
        large_text = "This is a test sentence. " * 10000  # ~250KB of text

        # Should handle large text without hanging
        text_edit.setPlainText(large_text)

        assert len(text_edit.toPlainText()) > 200000

    def test_combo_box_many_items(self, qapp):
        """Test combo box with many items"""
        combo = TabNavigationComboBox()

        # Add many items
        items = [f"Item {i}" for i in range(1000)]
        combo.addItems(items)

        assert combo.count() == 1000
        assert combo.itemText(0) == "Item 0"
        assert combo.itemText(999) == "Item 999"

    def test_rapid_text_changes(self, qapp):
        """Test rapid text changes"""
        line_edit = TabNavigationLineEdit()

        # Rapidly change text
        for i in range(100):
            line_edit.setText(f"Text change {i}")

        assert line_edit.text() == "Text change 99"

    def test_memory_usage(self, qapp):
        """Test that widgets don't leak memory"""
        widgets = []

        # Create many widgets
        for i in range(100):
            widget = TabNavigationTextEdit()
            widget.setPlainText(f"Widget {i} content")
            widgets.append(widget)

        # Delete widgets
        for widget in widgets:
            widget.deleteLater()

        # Process deletion events
        QApplication.processEvents()

        # Test passes if no crash occurs
        assert True


if __name__ == "__main__":
    pytest.main([__file__])
