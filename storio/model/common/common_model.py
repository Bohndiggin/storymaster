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
        self.engine = base_connection.engine
