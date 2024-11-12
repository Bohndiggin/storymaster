"""Storio's main file"""

import sys

from PyQt5.QtWidgets import QApplication, QLabel

from storio.model.common.common_model import BaseModel
from storio.view.common.common_view import BaseView

app = QApplication(sys.argv)

window = BaseView()
window.setWindowTitle("Junk")
window.setGeometry(100, 100, 280, 80)

label = QLabel("Yo whaddup", parent=window)
label.move(60, 15)

window.show()

sys.exit(app.exec())
