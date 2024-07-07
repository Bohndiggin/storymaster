"""Contains all the litographer tables"""

import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class PlotSectionType(enum.Enum):
    """Enum of different Types of Plot Section"""

    LOWER = "Tension lowers"
    FLAT = "Tension sustains"
    RISING = "Increases tension"
    POINT = "Singular moment"

class NodeType(enum.Enum):
    """Different types of story Nodes"""

    EXPOSITION = "exposition"
    ACTION = "action"
    REACTION = "reaction"
    TWIST = "twist"
    DEVELOPMENT = "development"


class NoteType(enum.Enum):
    """Types of notes that can be added to nodes"""

    WHAT = "what"
    WHY = "why"
    HOW = "how"
    WHEN = "when"
    WHERE = "where"
    OTHER = "other"

class LitographyNode(Base):
    """Represents litography_node table"""

    __tablename__ = 'litography_node'

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    node_type = Column(
        Enum(NodeType), nullable=False, name="NodeType"
    )
    node_height = Column(
        Float, nullable=False, name="NodeHeight"
    )
    previous_node = Column(
        Integer, nullable=True, name="PreviousNode"
    )
    next_node = Column(
        Integer, nullable=True, name="NextNode"
    )
    node_notes_id = Column(
        Integer, nullable=True, name='NodeNotesID'
    )

class LitographyNodeToNotes(Base):
    """Represents litography_node_to_notes table"""

    __tablename__ = 'litography_node_to_notes'

class LitographyPlot(Base):
    """Represents litography_plot table"""

    __tablename__ = 'litography_plot'

    id = Column(Integer, nullable=False, primary_key=True, name="ID")


class LitographyArc(Base):
    """Represents the litography_arc table"""

    __tablename__ = 'litography_arc'

    id = Column(Integer, nullable=True, primary_key=True, name="ID")

class ArcToActor(Base):
    """Represents the arc_to_actor table"""

    __tablename__ = 'arc_to_actor'

    id = Column(Integer, nullable=True, primary_key=True, name="ID")




