"""Contains connective tables that sit between the two halves of the database"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class LitographyNoteToLorekeeperActor(Base):
    """Represents litography_note_to_lorekeeper_actor table"""

    __tablename__ = "litography_note_to_lorekeeper_actor"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    actor_id = Column(Integer, ForeignKey("actor.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperBackground(Base):
    """Represents litography_note_to_lorekeeper_background table"""

    __tablename__ = "litography_note_to_lorekeeper_background"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    background_id = Column(Integer, ForeignKey("background.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperFaction(Base):
    """Represents litography_note_to_lorekeeper_faction table"""

    __tablename__ = "litography_note_to_lorekeeper_faction"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    faction_id = Column(Integer, ForeignKey("faction.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperLocation(Base):
    """Represents litography_note_to_lorekeeper_location table"""

    __tablename__ = "litography_note_to_lorekeeper_location"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    location_id = Column(Integer, ForeignKey("location_.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperHistory(Base):
    """Represents litography_note_to_lorekeeper_history table"""

    __tablename__ = "litography_note_to_lorekeeper_history"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    history_id = Column(Integer, ForeignKey("history.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperObject(Base):
    """Represents litography_note_to_lorekeeper_object table"""

    __tablename__ = "litography_note_to_lorekeeper_object"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    object_id = Column(Integer, ForeignKey("object_.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLorekeeperWorldData(Base):
    """Represents litography_note_to_lorekeeper_world_data table"""

    __tablename__ = "litography_note_to_lorekeeper_world_data"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"))
    world_data_id = Column(Integer, ForeignKey("world_data.id"))

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class ArcToActor(Base):
    """Represents the arc_to_actor table"""

    __tablename__ = "arc_to_actor"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    actor_id = Column(Integer, ForeignKey("actor.id"), nullable=False, name="actor_id")
    arc_id = Column(Integer, ForeignKey("arc.id"), nullable=False, name="arc_id")

    actor = relationship("Actor", foreign_keys=[actor_id])
