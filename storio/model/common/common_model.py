"""Holds common model classes"""

import dataclasses
from enum import Enum


class StorioModes(Enum):
    """The modes in storio"""

    LOREKEEPER = "Lorekeeper"
    LITOGRAPHER = "Litographer"


class BaseModel:
    """The base model class for Models"""
