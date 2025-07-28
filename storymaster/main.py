"""Storio's main file"""

import sys
from pathlib import Path

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
