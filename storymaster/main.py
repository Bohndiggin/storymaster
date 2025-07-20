"""Storio's main file"""

import sys

from PyQt6.QtWidgets import QApplication, QLabel

from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.resolve()))

from storymaster.view.common.common_view import MainView
from storymaster.model.common.common_model import BaseModel
from storymaster.controller.common.main_page_controller import MainWindowController

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = MainView()
    model = BaseModel(1)
    controller = MainWindowController(view, model)
    view.show()

    sys.exit(app.exec())
