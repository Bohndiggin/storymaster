"""Holds common model classes"""


class BaseModel:
    def __init__(self) -> None:
        self.message: str = "First Test"

    def get_message(self) -> str:
        return self.message
