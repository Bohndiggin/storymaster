"""
Helper module for handling imports in CI environments
"""

import sys
import os
from unittest.mock import MagicMock

# Check if we're in a CI environment where Qt imports will fail
def is_ci_environment():
    """Check if we're running in a CI environment"""
    return (
        'CI' in os.environ or 
        'GITHUB_ACTIONS' in os.environ or 
        '--headless' in sys.argv or
        os.environ.get('QT_QPA_PLATFORM') == 'offscreen'
    )

def safe_import_application_module(module_name):
    """Safely import an application module, mocking it if Qt is not available"""
    if is_ci_environment():
        # In CI, try the import and mock if it fails
        try:
            return __import__(module_name, fromlist=[''])
        except ImportError as e:
            if 'libEGL' in str(e) or 'DLL load failed' in str(e) or 'QtCore' in str(e):
                # Create a mock module
                mock_module = MagicMock()
                
                # Add common attributes based on the module
                if 'plot_manager_dialog' in module_name:
                    mock_module.PlotManagerDialog = MagicMock()
                elif 'main_page_controller' in module_name:
                    mock_module.create_node_item = MagicMock()
                    mock_module.CircleNodeItem = MagicMock()
                    mock_module.DiamondNodeItem = MagicMock()
                    mock_module.HexagonNodeItem = MagicMock()
                    mock_module.RectangleNodeItem = MagicMock()
                    mock_module.StarNodeItem = MagicMock()
                    mock_module.TriangleNodeItem = MagicMock()
                elif 'custom_widgets' in module_name:
                    mock_module.TabNavigationTextEdit = MagicMock()
                    mock_module.TabNavigationLineEdit = MagicMock()
                    mock_module.TabNavigationComboBox = MagicMock()
                    mock_module.enable_smart_tab_navigation = MagicMock()
                elif 'spellcheck' in module_name:
                    mock_module.SpellChecker = MagicMock()
                    mock_module.SpellCheckTextEdit = MagicMock()
                    mock_module.SpellCheckLineEdit = MagicMock()
                    mock_module.SpellCheckHighlighter = MagicMock()
                    mock_module.BasicWordList = MagicMock()
                    mock_module.enable_spell_check = MagicMock()
                    mock_module.get_spell_checker = MagicMock()
                elif 'new_user_dialog' in module_name:
                    mock_module.NewUserDialog = MagicMock()
                elif 'new_setting_dialog' in module_name:
                    mock_module.NewSettingDialog = MagicMock()
                elif 'new_storyline_dialog' in module_name:
                    mock_module.NewStorylineDialog = MagicMock()
                elif 'storyline_settings_dialog' in module_name:
                    mock_module.StorylineSettingsDialog = MagicMock()
                elif 'spell_check_config' in module_name:
                    mock_module.SpellCheckConfigDialog = MagicMock()
                
                # Cache the mock in sys.modules to avoid repeated imports
                sys.modules[module_name] = mock_module
                return mock_module
            else:
                # Re-raise other import errors
                raise
    else:
        # Not in CI, import normally
        return __import__(module_name, fromlist=[''])


def safe_import_from_module(module_name, *item_names):
    """Safely import specific items from a module"""
    module = safe_import_application_module(module_name)
    
    if len(item_names) == 1:
        return getattr(module, item_names[0])
    else:
        return tuple(getattr(module, name) for name in item_names)