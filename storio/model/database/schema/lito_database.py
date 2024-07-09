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

    __tablename__ = "litography_node"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    node_type = Column(Enum(NodeType), nullable=False, name="NodeType")
    node_height = Column(Float, nullable=False, name="NodeHeight")
    previous_node = Column(Integer, nullable=True, name="PreviousNode")
    next_node = Column(Integer, nullable=True, name="NextNode")


class LitographyNotes(Base):
    """Represents litography_notes table"""

    __tablename__ = "litography_notes"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    linked_node = Column(
        Integer, ForeignKey("litography_node.ID"), nullable=False, name="LinkedNode"
    )
    title = Column(String(250), nullable=False, name="Title")
    description = Column(String, nullable=True, name="Description")


class LitographyNoteToLorekeeperActor(Base):
    """Represents litography_note_to_lorekeeper_actor table"""

    __tablename__ = "litography_note_to_lorekeeper_actor"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    actor_id = Column(Integer, ForeignKey('actor.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyNoteToLorekeeperBackground(Base):
    """Represents litography_note_to_lorekeeper_background table"""

    __tablename__ = "litography_note_to_lorekeeper_background"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    background_id = Column(Integer, ForeignKey('background.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])


class LitographyNoteToLorekeeperFaction(Base):
    """Represents litography_note_to_lorekeeper_faction table"""

    __tablename__ = "litography_note_to_lorekeeper_faction"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    faction_id = Column(Integer, ForeignKey('faction.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyNoteToLorekeeperLocation(Base):
    """Represents litography_note_to_lorekeeper_location table"""

    __tablename__ = "litography_note_to_lorekeeper_location"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    location_id = Column(Integer, ForeignKey('location_.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyNoteToLorekeeperHistory(Base):
    """Represents litography_note_to_lorekeeper_history table"""

    __tablename__ = "litography_note_to_lorekeeper_history"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    history_id = Column(Integer, ForeignKey('history.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyNoteToLorekeeperObject(Base):
    """Represents litography_note_to_lorekeeper_object table"""

    __tablename__ = "litography_note_to_lorekeeper_object"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    object_id = Column(Integer, ForeignKey('object_.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyNoteToLorekeeperWorldData(Base):
    """Represents litography_note_to_lorekeeper_world_data table"""

    __tablename__ = "litography_note_to_lorekeeper_world_data"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    note_id = Column(Integer, ForeignKey('litography_notes.id'))
    world_data_id = Column(Integer, ForeignKey('world_data.id'))

    note = relationship('LitographyNotes', foreign_keys=[note_id])

class LitographyPlotSection(Base):
    """Represents litography_plot_section table"""

    __tablename__ = 'litography_plot_section'

    id = Column(Integer, nullable=False, primary_key=True, name="ID")
    section_type = Column(Enum(PlotSectionType), nullable=False, name="PlotSectionType")
    section_nodes = Column(Integer, nullable=False)

class LitographyPlot(Base):
    """Represents litography_plot table"""

    __tablename__ = "litography_plot"

    id = Column(Integer, nullable=False, primary_key=True, name="ID")



class LitographyArc(Base):
    """Represents the litography_arc table"""

    __tablename__ = "litography_arc"

    id = Column(Integer, nullable=True, primary_key=True, name="ID")


class ArcToActor(Base):
    """Represents the arc_to_actor table"""

    __tablename__ = "arc_to_actor"

    id = Column(Integer, nullable=True, primary_key=True, name="ID")
