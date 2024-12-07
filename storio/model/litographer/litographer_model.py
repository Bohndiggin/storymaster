"""Holds the classes for the litographer model"""

from sqlalchemy import sql
from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import schema


class BaseLitographerPageModel(BaseModel):
    """Base model for litographer"""

    def __init__(self):
        super().__init__()
        self.mode = StorioModes.LITOGRAPHER
        self.user = 1  # TEMP
        self.group = 1  # TEMP


class LitographerNodeNote(BaseLitographerPageModel):
    """Model for notes attached to nodes"""

    title: str
    description: str
    note_type: schema.NoteType


class LitographerPlotNodeModel(BaseLitographerPageModel):
    """Model for Plot Nodes"""

    height: float
    node_type: schema.NodeType
    notes: list[LitographerNodeNote]
    previous_node: "LitographerPlotNodeModel" | None
    next_node: "LitographerPlotNodeModel" | None
    node_id: int

    def __init__(self, node_id: int):
        super().__init__()
        self.node_id = node_id
        self.notes = self.gather_notes(node_id)
        self.previous_node = None
        self.next_node = None

    def gather_notes(self, node_id: int) -> list[LitographerNodeNote]:
        """Gathers all related LitographerNodeNotes"""

        with Session(self.engine) as session:
            session.execute(
                sql.select(schema.LitographyNotes).where(
                    schema.LitographyNotes.linked_node_id == self.node_id
                )
            )


class LitographerLinkedList:
    """Linked list"""

    head: LitographerPlotNodeModel
    tail: LitographerPlotNodeModel | None

    def __init__(self) -> None:
        super().__init__()
        self.head = None
        self.tail = None

    def append(self, node_id: int) -> None:
        """Add a new node at the end of the list"""

        new_node = LitographerPlotNodeModel(node_id)

        if not self.head:
            self.head = new_node
            self.tail = new_node

        else:
            self.tail.next_node = new_node
            new_node.previous_node = self.tail
            self.tail = new_node

    def prepend(self, node_id: int) -> None:
        """Add a node to the beginning of the list"""

        new_node = LitographerPlotNodeModel(node_id)

        if not self.head:
            self.head = new_node
            self.tail = new_node

        else:
            new_node.next_node = self.head
            self.head.previous_node = new_node
            self.head = new_node

    def delete(self, node_id: int) -> None:
        """Deletes node of specified id"""

        current = self.head
        while current:
            if current.node_id == node_id:
                if current.previous_node:
                    current.previous_node.next_node = current.next_node
                else:
                    self.head = current.next_node
                if current.next_node:
                    current.next_node.previous_node = current.previous_node
                else:
                    self.tail = current.previous_node
                return
            current = current.next_node

    def display(self) -> list:
        """Prints list of nodes in order"""
        nodes = []
        current = self.head
        while current:
            nodes.append(current.node_id)
            current = current.next_node
        return nodes


class LitographerPlotSectionModel(BaseLitographerPageModel):
    """Model for Litographer Plot Sections"""

    nodes: LitographerPlotNodeModel


class LitographerPlotModel(BaseLitographerPageModel):
    """Model for a whole plot, contains plot sections"""
