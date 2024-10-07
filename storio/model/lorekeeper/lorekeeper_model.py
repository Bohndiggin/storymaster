"""Holds the classes for the lorekeeper model"""

from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import base_connection, common_queries, schema


class BaseLorekeeperModel(BaseModel):
    """Base model for Lorekeeper"""

    def __init__(self) -> None:
        super().__init__()
        self.mode = StorioModes.LOREKEEPER
        self.engine = base_connection.engine
        self.user = 1


class LorekeeperPage(BaseLorekeeperModel):
    """Model for individual pages on the lorekeeper side"""

    def load_user_data(self) -> list[int]:
        """Loads all the group_ids for a user"""
        with Session(self.engine) as session:
            session.execute(common_queries.get_project_ids_for_user(self.user))


class LorekeeperIndividualItem(BaseLorekeeperModel):
    """Class for individual items on the lorekeeper page"""

    def display_self(self) -> None:
        """Function to make an individual item show itself on the side panel"""
