"""File to contain the different kind of nodes and their methods"""

import enum
import os
import typing

from storio.litographer.model import utilities
from storio.model.database import schema


class NodeNotes:
    """Represents notes for nodes"""

    notes: str
    note_type: schema.NoteType

    def __init__(self, notes) -> None:
        self.notes = notes


class BaseNode(utilities.LinkableClass):
    """Base Story Node is the base class that others will inherit from"""

    node_type: schema.NodeType
    node_height: float = 1.0

    def __init__(self) -> None:
        self.notes: list[NodeNotes | None] = []

    def add_node_notes(self, notes: str, note_type: schema.NoteType = schema.NoteType.WHAT) -> None:
        """Method to add a note to the node"""
        self.notes.append(NodeNotes(notes, note_type))


class ExpositionNode(BaseNode):
    """A node to represent a moment in the story where exposition is being delivered"""

    node_type = schema.NodeType.EXPOSITION
    # Do we want default notes to help with a story? Blank? Both?
