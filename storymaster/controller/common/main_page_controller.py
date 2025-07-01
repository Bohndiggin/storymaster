"""Holds the controller for the main page"""

from storymaster.model.common.common_model import BaseModel, GroupListTypes
from storymaster.view.common.common_view import MainView


class MainWindowController:
    """Controller for the main window"""

    def __init__(self, view: MainView, model: BaseModel):
        self.view = view
        self.model = model
        self.connect_signals()

    def connect_signals(self):
        self.view.ui.pushButton.released.connect(self.handle_button)
        self.view.ui.pushButton_2.released.connect(self.another_button)

    def handle_button(self):
        print("YOU PRESSED DA BUTTON")
        print(self.model.engine)
        print(self.model.load_user_projects())

    def another_button(self):
        print("another one")
        print(self.model.load_user_data())
        print(self.model.group_data[0].get_list(GroupListTypes.ACTORS))

