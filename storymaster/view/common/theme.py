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
    "button_height": "36px",
    "input_height": "32px",
    "splitter_width": "3px",
}

# Fonts
FONTS = {
    "size_small": "12px",
    "size_normal": "13px",
    "size_medium": "14px",
    "size_large": "16px",
    "size_title": "18px",
    "size_header": "20px",
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
            background-color: {COLORS['bg_input']} !important;
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            padding: {DIMENSIONS['padding_medium']};
            color: {COLORS['text_primary']} !important;
            font-size: {FONTS['size_normal']};
            min-height: {DIMENSIONS['input_height']};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_secondary']} !important;
        }}
        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
            background-color: {COLORS['bg_main']} !important;
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_dark']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
            background-color: {COLORS['bg_input']};
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
            min-height: 70px;
            background-color: {COLORS['bg_input']} !important;
        }}
        QTextEdit::viewport {{
            background-color: {COLORS['bg_input']};
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
            min-height: 24px;
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
            background-color: transparent;
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
        QFormLayout QLabel {{
            background-color: transparent;
            color: {COLORS['text_primary']};
        }}
    """


def get_table_style():
    """Get unified table styling"""
    return f"""
        QTableWidget {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            gridline-color: {COLORS['border_dark']};
            selection-background-color: {COLORS['primary']};
        }}
        QTableWidget::item {{
            padding: {DIMENSIONS['padding_medium']};
            border-bottom: 1px solid {COLORS['border_dark']};
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
        }}
        QTableWidget::item:hover {{
            background-color: {COLORS['bg_tertiary']};
        }}
        QHeaderView::section {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_secondary']};
            padding: {DIMENSIONS['padding_medium']};
            border: 1px solid {COLORS['border_main']};
            font-weight: {FONTS['weight_bold']};
        }}
    """


def get_tab_style():
    """Get unified tab widget styling"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS['border_main']};
            background-color: {COLORS['bg_secondary']};
            border-radius: {DIMENSIONS['border_radius']};
        }}
        QTabBar::tab {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_secondary']};
            padding: {DIMENSIONS['padding_medium']} {DIMENSIONS['padding_large']};
            margin-right: {DIMENSIONS['margin_small']};
            border: 1px solid {COLORS['border_main']};
            border-bottom: none;
            border-top-left-radius: {DIMENSIONS['border_radius']};
            border-top-right-radius: {DIMENSIONS['border_radius']};
            font-size: {FONTS['size_normal']};
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
            border-bottom: 1px solid {COLORS['bg_secondary']};
        }}
        QTabBar::tab:hover {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_primary']};
        }}
    """


def get_checkbox_style():
    """Get unified checkbox styling"""
    return f"""
        QCheckBox {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            spacing: {DIMENSIONS['padding_medium']};
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius_small']};
            background-color: {COLORS['bg_input']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORS['border_light']};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {COLORS['bg_main']};
            border-color: {COLORS['border_dark']};
        }}
    """


def get_slider_style():
    """Get unified slider styling"""
    return f"""
        QSlider::groove:horizontal {{
            background: {COLORS['bg_input']};
            height: 6px;
            border-radius: 3px;
            border: 1px solid {COLORS['border_main']};
        }}
        QSlider::handle:horizontal {{
            background: {COLORS['primary']};
            border: 1px solid {COLORS['primary']};
            width: 18px;
            margin: -7px 0;
            border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {COLORS['primary_hover']};
            border-color: {COLORS['primary_hover']};
        }}
        QSlider::sub-page:horizontal {{
            background: {COLORS['primary']};
            border-radius: 3px;
        }}
    """


def get_spinbox_style():
    """Get unified spinbox styling"""
    return f"""
        QSpinBox {{
            background-color: {COLORS['bg_input']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            padding: {DIMENSIONS['padding_medium']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            min-height: {DIMENSIONS['input_height']};
        }}
        QSpinBox:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_secondary']};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
            width: 16px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {COLORS['bg_tertiary']};
        }}
    """


def get_dateedit_style():
    """Get unified date edit styling"""
    return f"""
        QDateEdit {{
            background-color: {COLORS['bg_input']};
            border: 1px solid {COLORS['border_main']};
            border-radius: {DIMENSIONS['border_radius']};
            padding: {DIMENSIONS['padding_medium']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            min-height: {DIMENSIONS['input_height']};
        }}
        QDateEdit:focus {{
            border-color: {COLORS['primary']};
            background-color: {COLORS['bg_secondary']};
        }}
        QDateEdit::drop-down {{
            border: none;
            width: 20px;
        }}
    """


def get_label_style(label_type="normal"):
    """Get unified label styling"""
    base_style = f"""
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            background-color: transparent;
        }}
    """

    if label_type == "header":
        return (
            base_style
            + f"""
        QLabel {{
            font-size: {FONTS['size_large']};
            font-weight: {FONTS['weight_bold']};
            color: {COLORS['text_accent']};
        }}
        """
        )
    elif label_type == "muted":
        return (
            base_style
            + f"""
        QLabel {{
            color: {COLORS['text_muted']};
            font-style: italic;
        }}
        """
        )
    elif label_type == "bold":
        return (
            base_style
            + f"""
        QLabel {{
            font-weight: {FONTS['weight_bold']};
        }}
        """
        )
    elif label_type == "small":
        return (
            base_style
            + f"""
        QLabel {{
            font-size: {FONTS['size_small']};
            color: {COLORS['text_secondary']};
        }}
        """
        )

    return base_style


def get_main_window_style():
    """Get the main window application stylesheet"""
    return f"""
        /* --- Dark Theme inspired by DaVinci Resolve --- */
        QWidget {{
            background-color: {COLORS['bg_secondary']}; /* Consistent base background */
            color: {COLORS['text_primary']};
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: {FONTS['size_normal']};
        }}

        QMainWindow {{
            background-color: {COLORS['bg_main']}; /* Main window background */
        }}

        /* --- Stacked Widget & Pages --- */
        QStackedWidget > QWidget {{
            background-color: {COLORS['bg_secondary']}; /* Consistent with base widget background */
        }}
        
        /* --- Ensure all container widgets have consistent background --- */
        QFrame {{
            background-color: {COLORS['bg_secondary']};
        }}
        
        QScrollArea {{
            background-color: {COLORS['bg_secondary']};
        }}
        
        QScrollArea QWidget {{
            background-color: {COLORS['bg_secondary']};
        }}
        
        /* --- Specific page containers --- */
        QWidget[class="page"] {{
            background-color: {COLORS['bg_secondary']};
        }}

        /* --- Context Info Bar --- */
        #contextInfoBar {{
            background-color: {COLORS['bg_secondary']};
            border-top: 1px solid {COLORS['border_dark']};
            border-bottom: 1px solid {COLORS['border_dark']};
        }}

        #contextInfoBar QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            font-size: {FONTS['size_small']};
            font-weight: {FONTS['weight_normal']};
            padding: {DIMENSIONS['padding_small']} {DIMENSIONS['padding_medium']};
            border: none;
            text-align: center;
        }}

        #contextInfoBar QPushButton:hover {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_primary']};
        }}

        #contextInfoBar QPushButton:pressed {{
            background-color: {COLORS['border_main']};
        }}

        #contextInfoBar QLabel {{
            color: {COLORS['text_muted']};
            font-size: {FONTS['size_small']};
            padding: 0 {DIMENSIONS['padding_small']};
        }}

        /* --- Bottom Navigation Bar --- */
        #bottomNavBar {{
            background-color: {COLORS['bg_main']};
            border-top: 1px solid {COLORS['border_main']};
        }}

        #bottomNavBar QPushButton {{
            background-color: transparent;
            color: {COLORS['text_secondary']};
            border: none;
            padding: {DIMENSIONS['padding_medium']} {DIMENSIONS['padding_large']};
            font-weight: {FONTS['weight_bold']};
            font-size: {FONTS['size_medium']};
        }}

        #bottomNavBar QPushButton:hover {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_primary']};
        }}

        #bottomNavBar QPushButton:checked {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_primary']};
            border-bottom: 2px solid {COLORS['primary']};
        }}

        /* --- Menu, Tool, and Status Bars --- */
        QMenuBar {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: {DIMENSIONS['padding_small']} {DIMENSIONS['padding_medium']};
        }}

        QMenuBar::item:selected {{
            background-color: {COLORS['bg_tertiary']};
        }}

        QMenu {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
        }}

        QMenu::item:selected {{
            background-color: {COLORS['bg_tertiary']};
        }}

        QToolBar {{
            background-color: {COLORS['bg_secondary']};
            border: none;
            padding: {DIMENSIONS['margin_small']};
        }}

        QStatusBar {{
            background-color: {COLORS['bg_secondary']};
            border-top: 1px solid {COLORS['border_main']};
        }}

        /* --- Widgets inside pages --- */
        QSplitter::handle {{
            background-color: {COLORS['border_main']};
        }}

        QSplitter::handle:hover {{
            background-color: {COLORS['border_light']};
        }}

        QSplitter::handle:pressed {{
            background-color: {COLORS['primary']};
        }}

        /* --- Tree and List Widgets --- */
        QTreeWidget, QListWidget {{
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_main']};
            color: {COLORS['text_primary']};
            font-size: {FONTS['size_normal']};
            alternate-background-color: {COLORS['bg_main']};
        }}

        QTreeWidget::item, QListWidget::item {{
            padding: {DIMENSIONS['padding_small']} {DIMENSIONS['padding_medium']};
            border-bottom: 1px solid {COLORS['border_dark']};
        }}

        QTreeWidget::item:selected, QListWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
        }}

        QTreeWidget::item:hover, QListWidget::item:hover {{
            background-color: {COLORS['bg_tertiary']};
        }}

        /* --- Headers --- */
        QHeaderView::section {{
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_secondary']};
            padding: {DIMENSIONS['padding_medium']};
            border: 1px solid {COLORS['border_main']};
            font-weight: {FONTS['weight_bold']};
        }}

        /* --- Scroll Bars --- */
        QScrollBar:vertical {{
            background: {COLORS['bg_secondary']};
            width: 12px;
            border: 1px solid {COLORS['border_main']};
        }}

        QScrollBar::handle:vertical {{
            background: {COLORS['bg_tertiary']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {COLORS['border_light']};
        }}

        QScrollBar:horizontal {{
            background: {COLORS['bg_secondary']};
            height: 12px;
            border: 1px solid {COLORS['border_main']};
        }}

        QScrollBar::handle:horizontal {{
            background: {COLORS['bg_tertiary']};
            border-radius: 6px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['border_light']};
        }}

        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
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
        + get_table_style()
        + get_tab_style()
        + get_checkbox_style()
        + get_slider_style()
        + get_spinbox_style()
        + get_dateedit_style()
    )
