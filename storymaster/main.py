"""Storio's main file"""

import sys

from PyQt5.QtWidgets import QApplication, QLabel

from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.resolve()))

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.common_view import BaseView
from storymaster.view.main_page import Ui_MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BaseView()
    window.show()

    sys.exit(app.exec())

