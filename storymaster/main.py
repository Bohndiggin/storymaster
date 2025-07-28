"""Storio's main file"""

import os
import sys
from pathlib import Path

# Initialize Qt plugin paths for bundled executable
if getattr(sys, 'frozen', False):
    # Running in bundled mode
    bundle_dir = Path(sys._MEIPASS)
    
    # Set Qt plugin paths
    qt_plugin_paths = [
        bundle_dir / 'PyQt6' / 'Qt6' / 'plugins',
        bundle_dir / 'plugins'
    ]
    
    for plugin_path in qt_plugin_paths:
        if plugin_path.exists():
            current_path = os.environ.get('QT_PLUGIN_PATH', '')
            if current_path:
                os.environ['QT_PLUGIN_PATH'] = f"{current_path}{os.pathsep}{plugin_path}"
            else:
                os.environ['QT_PLUGIN_PATH'] = str(plugin_path)
    
    # Set platform plugin path specifically
    platform_path = bundle_dir / 'PyQt6' / 'Qt6' / 'plugins' / 'platforms'
    if platform_path.exists():
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(platform_path)

from PyQt6.QtWidgets import QApplication

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.resolve()))

from storymaster.controller.common.main_page_controller import MainWindowController
from storymaster.controller.common.user_startup import get_startup_user_id
from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import MainView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Get the user ID to use for startup (creates user if none exist)
    user_id = get_startup_user_id()

    view = MainView()
    model = BaseModel(user_id)
    controller = MainWindowController(view, model)
    view.show()

    sys.exit(app.exec())
