"""Holds the classes for the litographer model"""

import typing

from sqlalchemy import sql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import schema


class BaseLitographerPageModel(BaseModel):
    """Base model for litographer"""

    def __init__(self, user: int, group: int, project_id: int):
        super().__init__()
        self.mode = StorioModes.LITOGRAPHER
        self.user = user
        self.group = group
        self.project_id = project_id


class LitographerPlotNodeModel(BaseLitographerPageModel):
    """Model for Plot Nodes"""

    notes: dict[int, schema.LitographyNotes]
    previous_node: typing.Self | None
    next_node: typing.Self | None
    node_table_object: schema.LitographyNode

    def __init__(self, user: int, group: int, project_id: int, node_id: int) -> None:
        super().__init__(user, group, project_id)
        try:
            self._gather_self(node_id)
        except NoResultFound:
            self._create_self()
        self.notes = self.gather_notes()
        self.previous_node = None
        self.next_node = None

    def _gather_self(self, node_id: int) -> None:
        """Gathers self-relevant data from db"""

        with Session(self.engine) as session:
            node = session.execute(
                sql.select(schema.LitographyNode).where(
                    schema.LitographyNode.id == node_id,
                    schema.LitographyNode.project_id == self.project_id,
                )
            ).scalar_one()

            self.node_table_object = node

    def _create_self(self) -> None:
        """Creates a node if one doesn't exist"""

        new_node = schema.LitographyNode(
            node_type=schema.NodeType.OTHER.value, node_height=0.1, project_id=self.project_id
        )

        with Session(self.engine) as session:
            session.add(new_node)
            session.commit()
            session.refresh(new_node)

        self._gather_self(new_node.id)

    def gather_notes(self) -> dict[int, schema.LitographyNotes]:
        """Gathers all related LitographerNodeNotes"""

        with Session(self.engine) as session:
            notes = (
                session.execute(
                    sql.select(schema.LitographyNotes).where(
                        schema.LitographyNotes.linked_node_id
                        == self.node_table_object.id
                    )
                )
                .scalars()
                .all()
            )

            note_list = {note.id: note for note in notes}

        return note_list

    def add_note(self, note_type: schema.NoteType) -> None:
        """Adds a note to the node"""

        new_note = schema.LitographyNotes(
            title="new_note",
            description="",
            note_type=note_type,
            linked_node_id=self.node_table_object.id,
            project_id=self.project_id,
        )

        with Session(self.engine) as session:
            session.add(new_note)
            session.commit()

        self.notes = self.gather_notes()


class LitographerLinkedList(BaseLitographerPageModel):
    """Linked list"""

    head: LitographerPlotNodeModel
    tail: LitographerPlotNodeModel | None

    def __init__(self, user: int, group: int, project_id: int, section_id: int) -> None:
        super().__init__(user, group, project_id)
        self.section_id = section_id
        self.head = None
        self.tail = None

    def load_up(self) -> None:
        """Loads whole list Finds one then searches to beginning then to end"""

        with Session(self.engine) as session:
            temp_node_list = (
                session.execute(
                    sql.select(schema.LitographyNode)
                    .join(schema.LitographyNodeToPlotSection)
                    .where(
                        schema.LitographyNodeToPlotSection.litography_plot_section_id
                        == self.section_id
                    )
                )
                .scalars()
                .all()
            )

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

        new_node = LitographerPlotNodeModel(
            self.user, self.group, self.project_id, node_id
        )

        if not self.head:
            self.head = new_node
            self.tail = new_node

        else:
            self.tail.next_node = new_node
            new_node.previous_node = self.tail
            self.tail = new_node

    def prepend(self, node_id: int) -> None:
        """Add a node to the beginning of the list"""

        new_node = LitographerPlotNodeModel(
            self.user, self.group, self.project_id, node_id
        )

        if not self.head:
            self.head = new_node
            self.tail = new_node

        else:
            new_node.next_node = self.head
            self.head.previous_node = new_node
            self.head = new_node

    def get_node(self, node_id: int) -> LitographerPlotNodeModel:
        """Returns node of id specified"""

        current = self.head

        while current:
            if current.node_table_object.id == node_id:
                return current
            current = current.next_node

        raise IndexError(f"Node {node_id} not in linked list")

    def insert_node(self, node_id: int, prev_id: int | None) -> None:
        """Inserts node after specified id"""

        new_node = LitographerPlotNodeModel(
            self.user, self.group, self.project_id, node_id
        )

        if not self.head:
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
                        new_node.next_node = current.next_node
                        current.next_node = new_node
                        new_node.previous_node = current
                        break
                    else:
                        current.next_node = new_node
                        self.tail = new_node
                        new_node.previous_node = current
                        break
                elif current == self.tail:
                    current.next_node = new_node
                    self.tail = new_node
                    new_node.previous_node = current
                    break
                current = current.next_node

    def delete(self, node_id: int) -> None:
        """Removes node of specified id from the linked list"""

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

        raise IndexError(f"Node {node_id} not in linked list")

    def refresh(self) -> None:
        """Deletes loaded data and reloads from database"""

        current = self.head

        while current:
            self.delete(current.node_table_object.id)
            current = self.head

        self.load_up()

    def move_node_aft(self, node_id: int, destination_node_id: int) -> None:
        """Moves node to be after specified node"""

        target_node = self.get_node(node_id)

        if target_node.previous_node and target_node.next_node:
            target_node.previous_node.next_node = target_node.next_node
            target_node.next_node.previous_node = target_node.previous_node
        if target_node.previous_node and not target_node.next_node:
            self.tail = target_node.previous_node
            target_node.previous_node.next_node = None
        if not target_node.previous_node and target_node.next_node:
            self.head = target_node.next_node
            target_node.next_node.previous_node = None

        destination_node = self.get_node(destination_node_id)

        if not destination_node.next_node:
            destination_node.next_node = target_node
            target_node.previous_node = destination_node
            target_node.next_node = None
            self.tail = target_node

        else:
            target_node.previous_node = destination_node
            target_node.next_node = destination_node.next_node
            destination_node.next_node.previous_node = target_node
            destination_node.next_node = target_node

    def move_node_pre(self, node_id: int, destination_node_id: int) -> None:
        """Moves node before specified node"""

        target_node = self.get_node(node_id)
        destination_node = self.get_node(destination_node_id)

        if target_node.previous_node and target_node.next_node:
            target_node.previous_node.next_node = target_node.next_node
            target_node.next_node.previous_node = target_node.previous_node
        if target_node.previous_node and not target_node.next_node:
            self.tail = target_node.previous_node
            target_node.previous_node.next_node = None
        if not target_node.previous_node and target_node.next_node:
            self.head = target_node.next_node
            target_node.next_node.previous_node = None

        if not destination_node.previous_node:
            destination_node.previous_node = target_node
            target_node.next_node = destination_node
            target_node.previous_node = None
            self.head = target_node

        else:
            target_node.next_node = destination_node
            target_node.previous_node = destination_node.previous_node
            destination_node.previous_node.next_node = target_node
            destination_node.previous_node = target_node

    def display(self) -> list[int]:
        """Returns a list of node_ids in order"""
        nodes = []
        current = self.head
        while current:
            nodes.append(current.node_table_object.id)
            current = current.next_node
        return nodes

    def apply_order_to_tables(self) -> None:
        """Applies current order to table objects"""

        current = self.head

        while current:
            if current.next_node:
                current.node_table_object.next_node = (
                    current.next_node.node_table_object.id
                )
            else:
                current.node_table_object.next_node = None
            if current.previous_node:
                current.node_table_object.previous_node = (
                    current.previous_node.node_table_object.id
                )
            else:
                current.node_table_object.previous_node = None
            current = current.next_node

    def get_tables(self) -> list[schema.LitographyNode]:
        """Returns all the table objects in a list"""

        self.apply_order_to_tables()

        tables: list[schema.LitographyNode] = []
        current = self.head
        while current:
            tables.append(current.node_table_object)
            current = current.next_node
        return tables

    def get_notes(self) -> list[schema.LitographyNotes]:
        """Returns all the notes associated with the linked list"""

        notes: list[schema.LitographyNotes] = []
        current = self.head
        while current:
            notes += current.notes
            current = current.next_node
        return notes


class LitographerPlotSectionModel(BaseLitographerPageModel):
    """Model for Litographer Plot Sections"""

    nodes: LitographerLinkedList
    section_id: int

    def __init__(self, user: int, group: int, project_id: int, section_id: int) -> None:
        super().__init__(user, group, project_id)
        self.section_id = section_id
        self.nodes = LitographerLinkedList(self.user, self.group, self.project_id, self.section_id)
        self.nodes.load_up()

    def update_database(self) -> None:
        """Sends all the data to the database"""
        with Session(self.engine) as session:
            session.add_all(self.nodes.get_tables())
            session.add_all(self.nodes.get_notes())
            session.commit()


class LitographerPlotModel(BaseLitographerPageModel):
    """Model for a whole plot, contains plot sections"""

    plot_table: schema.LitographyPlot
    section_dict: dict[int, LitographerPlotSectionModel]

    def __init__(self, user: int, group: int, project_id: int, plot_id: int):
        super().__init__(user, group, project_id)
        self.plot_id = plot_id
        try:
            self.load_self()
        except NoResultFound:
            self._create_self()
        self.load_plot_sections()

    def load_self(self) -> None:
        """Loads the table object"""

        with Session(self.engine) as session:
            self.plot_table = session.execute(
                sql.select(schema.LitographyPlot).where(
                    schema.LitographyPlot.id == self.plot_id
                )
            ).scalar_one()

    def load_plot_sections(self) -> None:
        """Loads the plot's sections"""

        with Session(self.engine) as session:
            plot_sections = (
                session.execute(
                    sql.select(schema.LitographyPlotSection).where(
                        schema.LitographyPlotSection.section_plot_id == self.plot_id,
                    )
                )
                .scalars()
                .all()
            )

            self.section_dict: dict[int, LitographerPlotSectionModel] = {
                plot_section.id: LitographerPlotSectionModel(
                    self.user, self.group, self.project_id, plot_section.id
                )
                for plot_section in plot_sections
            }

    def _create_self(self) -> None:
        """Creates a new plot. Used when one doesn't exist"""

        new_plot = schema.LitographyPlot(
            title="NewPlot", description="", project_id=self.project_id
        )

        with Session(self.engine) as session:
            session.add(new_plot)
            session.commit()
            session.refresh(new_plot)

        self.plot_id = new_plot.id

        self.load_self()

    def _save_self(self) -> None:
        """Saves the table object associated with this plot"""

        with Session(self.engine) as session:
            session.add(self.plot_table)
            session.commit()

    def save_all(self) -> None:
        """Saves self and all underlying objects"""

        self._save_self()

        for section in self.section_dict.values():
            section.update_database()
