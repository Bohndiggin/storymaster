"""Contains connective tables that sit between the two halves of the database"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class LitographyNoteToActor(Base):
    """Represents litography_note_to_actor table"""

    __tablename__ = "litography_note_to_actor"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    actor_id = Column(Integer, ForeignKey("actor.id"), name="actor_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToBackground(Base):
    """Represents litography_note_to_background table"""

    __tablename__ = "litography_note_to_background"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    background_id = Column(Integer, ForeignKey("background.id"), name="background_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToFaction(Base):
    """Represents litography_note_to_faction table"""

    __tablename__ = "litography_note_to_faction"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    faction_id = Column(Integer, ForeignKey("faction.id"), name="faction_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLocation(Base):
    """Represents litography_note_to_location table"""

    __tablename__ = "litography_note_to_location"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    location_id = Column(Integer, ForeignKey("location_.id"), name="location_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToHistory(Base):
    """Represents litography_note_to_history table"""

    __tablename__ = "litography_note_to_history"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    history_id = Column(Integer, ForeignKey("history.id"), name="history_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToObject(Base):
    """Represents litography_note_to_object table"""

    __tablename__ = "litography_note_to_object"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    object_id = Column(Integer, ForeignKey("object_.id"), name="object_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToWorldData(Base):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_note_to_world_data"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    world_data_id = Column(Integer, ForeignKey("world_data.id"), name="world_data_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNodeToPlotSection(Base):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_node_to_plot_section"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    node_id = Column(Integer, ForeignKey("litography_node.id"), name="node_id")
    litography_plot_section_id = Column(
        Integer,
        ForeignKey("litography_plot_section.id"),
        name="litography_plot_section_id",
    )

    node = relationship("LitographyNodes", foreign_keys=[node_id])


class ArcToNode(Base):
    """Represents the arc_to_node table"""

    __tablename__ = "arc_to_node"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    node_id = Column(Integer, ForeignKey("litography_node.id"), name="node_id")
    arc_id = Column(Integer, ForeignKey("litography_arc.id"), name="arc_id")

    node = relationship("LitographyNodes", foreign_keys=[node_id])
    arc = relationship("LitographyArc", foreign_keys=[arc_id])


class ArcToActor(Base):
    """Represents the arc_to_actor table"""

    __tablename__ = "arc_to_actor"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    actor_id = Column(Integer, ForeignKey("actor.id"), nullable=False, name="actor_id")
    arc_id = Column(Integer, ForeignKey("arc.id"), nullable=False, name="arc_id")

    actor = relationship("Actor", foreign_keys=[actor_id])
