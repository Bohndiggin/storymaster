"""
Unified theming system for Storymaster UI components
Provides consistent styling across all pages and dialogs
"""

# Color palette
COLORS = {
    # Main colors
    "primary": "#0d7d7e",  # Teal accent
    "primary_hover": "#0e8d8e",  # Lighter teal
    "primary_pressed": "#0c6d6e",  # Darker teal
    # Background colors
    "bg_main": "#1e1e1e",  # Main background
    "bg_secondary": "#2b2b2b",  # Secondary background
    "bg_tertiary": "#3c3c3c",  # Tertiary background
    "bg_input": "#2b2b2b",  # Input fields
    # Border colors
    "border_main": "#555",  # Main borders
    "border_light": "#666",  # Light borders
    "border_lighter": "#777",  # Lighter borders
    "border_dark": "#444",  # Dark borders
    # Text colors
    "text_primary": "#ffffff",  # Primary text
    "text_secondary": "#cccccc",  # Secondary text
    "text_muted": "#888888",  # Muted text
    "text_accent": "#0d7d7e",  # Accent text
    # Status colors
    "success": "#4a9eff",  # Success/info
    "warning": "#ffa726",  # Warning
    "error": "#ff5252",  # Error
}

# Common dimensions
DIMENSIONS = {
    "border_radius": "4px",
    "border_radius_small": "2px",
    "border_radius_large": "8px",
    "padding_small": "4px",
    "padding_medium": "8px",
    "padding_large": "12px",
    "margin_small": "2px",
    "margin_medium": "4px",
    "margin_large": "8px",
    "button_height": "32px",
    "input_height": "28px",
    "splitter_width": "3px",
}

# Fonts
FONTS = {
    "size_small": "10px",
    "size_normal": "11px",
    "size_medium": "12px",
    "size_large": "14px",
    "size_title": "16px",
    "size_header": "18px",
    "weight_normal": "normal",
    "weight_bold": "bold",
}


def get_button_style(button_type="primary"):
    """Get unified button styling"""
    base_style = f"""
        QPushButton {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            padding: {DIMENSIONS['padding_medium']} {DIMENSIONS['padding_large']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            min-height: {DIMENSIONS['button_height']};
            font-weight: {FONTS['weight_normal']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['bg_tertiary']};
            border-color: {COLORS['border_light']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['border_main']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_dark']};
        }}
    """

    if button_type == "primary":
        return (
            base_style
            + f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
            font-weight: {FONTS['weight_bold']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
            border-color: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_pressed']};
            border-color: {COLORS['primary_pressed']};
        }}
        """
        )
    elif button_type == "danger":
        return (
            base_style
            + f"""
        QPushButton {{
            background-color: {COLORS['error']};
            border-color: {COLORS['error']};
        }}
        QPushButton:hover {{
            background-color: #ff6b6b;
            border-color: #ff6b6b;
        }}
        QPushButton:pressed {{
            background-color: #e04848;
            border-color: #e04848;
        }}
        """
        )

    return base_style


def get_input_style():
    """Get unified input field styling"""
    return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {COLORS['bg_input']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            padding: {DIMENSIONS['padding_medium']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            min-height: {DIMENSIONS['input_height']};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_secondary']};
        }}
        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_dark']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {COLORS['text_secondary']};
            border-top: none;
            border-left: none;
            width: 6px;
            height: 6px;
            margin-right: 6px;
        }}
        QTextEdit {{
            min-height: 60px;
        }}
    """


def get_list_style():
    """Get unified list widget styling"""
    return f"""
        QListWidget {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            alternate-background-color: {COLORS['bg_main']};
        }}
        QListWidget::item {{
            padding: {DIMENSIONS['padding_medium']} {DIMENSIONS['padding_medium']};
            border-bottom: 1px solid {COLORS['border_dark']};
            min-height: 20px;
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
        }}
        QListWidget::item:hover {{
            background-color: {COLORS['bg_tertiary']};
        }}
    """


def get_group_box_style():
    """Get unified group box styling"""
    return f"""
        QGroupBox {{
            font-size: {FONTS['size_medium']};
            font-weight: {FONTS['weight_bold']};
            color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            margin-top: {DIMENSIONS['padding_medium']};
            padding-top: {DIMENSIONS['padding_medium']};
            background-color: {COLORS['bg_main']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {DIMENSIONS['padding_medium']};
            padding: 0 {DIMENSIONS['padding_medium']} 0 {DIMENSIONS['padding_medium']};
            background-color: {COLORS['bg_main']};
        }}
    """


def get_splitter_style():
    """Get unified splitter styling"""
    return f"""
        QSplitter::handle {{
            background: {COLORS['border_main']};
            border: 1px solid {COLORS['border_light']};
            border-radius: {DIMENSIONS['border_radius_small']};
        }}
        QSplitter::handle:hover {{
            background: {COLORS['border_light']};
            border-color: {COLORS['border_lighter']};
        }}
        QSplitter::handle:pressed {{
            background: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
    """


def get_dialog_style():
    """Get unified dialog styling"""
    return f"""
        QDialog {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_primary']};
        }}
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
        }}
        QLabel[class="header"] {{
            font-size: {FONTS['size_large']};
            font-weight: {FONTS['weight_bold']};
            color: {COLORS['text_accent']};
        }}
        QLabel[class="muted"] {{
            color: {COLORS['text_muted']};
            font-style: italic;
        }}
    """


def get_complete_style():
    """Get the complete unified style sheet"""
    return (
        get_button_style("secondary")
        + get_input_style()
        + get_list_style()
        + get_group_box_style()
        + get_splitter_style()
        + get_dialog_style()
    )
