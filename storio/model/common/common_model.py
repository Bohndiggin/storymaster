"""Holds common model classes"""

import dataclasses
from enum import Enum

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from storio.model.database import base_connection, common_queries, schema


class StorioModes(Enum):
    """The modes in storio"""

    LOREKEEPER = "Lorekeeper"
    LITOGRAPHER = "Litographer"


class BaseModel:
    """The base model class for Models"""

    engine: Engine

    def __init__(self):
        self.engine = self.generate_connection()

    def generate_connection(self) -> Engine:
        """Generates the connection used to test"""
        return base_connection.engine

    def load_user_projects(self) -> list[int]:
        """Loads all the project_ids for a user"""
        with Session(self.engine) as session:
            project_id_list = session.execute(
                common_queries.get_project_ids_for_user(self.user)
            ).all()

        return [project.id for project in project_id_list]
