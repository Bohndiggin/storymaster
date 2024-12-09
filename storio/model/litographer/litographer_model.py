"""Holds the classes for the litographer model"""

import typing
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

    def __init__(self, title: str, description: str, note_type: schema.NoteType):
        super().__init__()
        self.title = title
        self.description = description
        self.note_type = note_type


class LitographerPlotNodeModel(BaseLitographerPageModel):
    """Model for Plot Nodes"""

    notes: list[LitographerNodeNote]
    previous_node: typing.Self | None
    next_node: typing.Self | None
    node_table_object: schema.LitographyNode

    def __init__(self, node_id: int) -> None:
        super().__init__()
        self.gather_self(node_id)
        self.notes = self.gather_notes(node_id)
        self.previous_node = None
        self.next_node = None
        self.fill_in_previous_next()

    def gather_self(self, node_id: int) -> None:
        """Gathers self-relevant data from db"""

        with Session(self.engine) as session:
            node = session.execute(
                sql.select(schema.LitographyNode)
                .where(schema.LitographyNode.id == node_id)
            ).scalar_one()

            self.node_table_object = node



    def gather_notes(self, node_id: int) -> list[LitographerNodeNote]:
        """Gathers all related LitographerNodeNotes"""

        with Session(self.engine) as session:
            notes = (
                session.execute(
                    sql.select(schema.LitographyNotes).where(
                        schema.LitographyNotes.linked_node_id == node_id
                    )
                )
                .scalars()
                .all()
            )

            note_list = [
                LitographerNodeNote(note.title, note.description, note.note_type)
                for note in notes
            ]

        return note_list

    def fill_in_previous_next(self) -> None:
        """"""


class LitographerLinkedList(BaseLitographerPageModel):
    """Linked list"""

    head: LitographerPlotNodeModel
    tail: LitographerPlotNodeModel | None

    def __init__(self) -> None:
        super().__init__()
        self.head = None
        self.tail = None

    def load_up(self, plot_section_id: int) -> None:
        """Loads whole list Finds one then searches to beginning then to end"""

        with Session(self.engine) as session:
            temp_node_list = session.execute(
                sql.select(schema.LitographyNode)
                .join(schema.LitographyNodeToPlotSection)
                .where(schema.LitographyNodeToPlotSection.litography_plot_section_id == plot_section_id)
            ).scalars().all()

            self.insert_node(temp_node_list[0].id, None)
            current = self.head
            while current.node_table_object.previous_node:
                if current.node_table_object.previous_node:
                    self.prepend(current.node_table_object.previous_node)
                current = self.head

            current = self.tail
            while current.node_table_object.next_node:
                self.append(current.node_table_object.next_node)
                current = self.tail

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

    def insert_node(self, node_id: int, prev_id: int | None) -> None:
        """Inserts node after specified id"""

        new_node = LitographerPlotNodeModel(node_id)

        if not prev_id:
            self.head = new_node
            self.tail = new_node
            return

        if not self.tail:
            self.head = new_node
            self.tail = new_node
        else:
            current = self.head
            while current:
                if current.node_table_object.id == prev_id:
                    if current.next_node:
                        current.next_node.previous_node = new_node
                        current.next_node = new_node
                        new_node.previous_node = current
                    else:
                        current.next_node = new_node
                        self.tail = new_node
                        new_node.previous_node = current
                elif current == self.tail:
                    current.next_node = new_node
                    self.tail = new_node
                    new_node.previous_node = current

    def delete(self, node_id: int) -> None:
        """Deletes node of specified id"""

        current = self.head
        while current:
            if current.node_table_object.id == node_id:
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
            nodes.append(current.node_table_object.id)
            current = current.next_node
        return nodes


class LitographerPlotSectionModel(BaseLitographerPageModel):
    """Model for Litographer Plot Sections"""

    nodes: LitographerLinkedList
    section_id: int

    def __init__(self, section_id: int) -> None:
        super().__init__()
        self.section_id = section_id
        self.nodes = LitographerLinkedList()
        self.nodes.load_up(self.section_id)



class LitographerPlotModel(BaseLitographerPageModel):
    """Model for a whole plot, contains plot sections"""
