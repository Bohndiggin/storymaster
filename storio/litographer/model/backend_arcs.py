"""File contains character arc classes"""

import enum
from storio.litographer.model import backend_nodes, utilities


class CharacterArcSectionType(enum.Enum):
    """Enum of different kinds of character arc sections"""

    FALL = "Character does the opposite of growth"
    FLAT = "Character neither grows or falls"
    TIP = "Tipping Point for a character"
    GROW = "Character grows or learns"


class ArcSection(utilities.LinkableClass):
    """ArcSection is the base class of character arc sections"""

    section_name: str
    section_type: CharacterArcSectionType
    nodes: list[backend_nodes.BaseNode]
