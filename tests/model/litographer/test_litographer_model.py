"""Test file for litographer_model"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from sqlalchemy import sql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from storio.model.database import schema
from storio.model.database.base_connection import get_test_engine
from storio.model.database.schema.base import NoteType
from storio.model.litographer.litographer_model import (
    LitographerLinkedList,
    LitographerPlotModel,
    LitographerPlotNodeModel,
    LitographerPlotSectionModel,
)

fake = Faker()


class TestLitographerPlotNodeModel:
    """Test class for LitographerPlotNodeModel"""

    @pytest.fixture(scope="class")
    @patch(
        "storio.model.litographer.litographer_model.BaseModel.generate_connection",
        new=get_test_engine,
    )
    def model(self) -> LitographerPlotNodeModel:
        return LitographerPlotNodeModel(1, 1, 1, 1)

    def test_init(self, model: LitographerPlotNodeModel) -> None:
        """Tests _gather_self first with one that works, then with one that doesn't"""

        assert model.node_table_object
        with Session(model.engine) as session:
            result_node = (
                session.execute(sql.select(schema.LitographyNode)).scalars().all()
            )

            assert model.node_table_object.id == result_node[0].id

        with patch(
            "storio.model.litographer.litographer_model.BaseModel.generate_connection",
            new=get_test_engine,
        ):
            new_node = LitographerPlotNodeModel(1, 1, 1, 1)

            assert new_node.node_table_object.id == model.node_table_object.id

    def test_gather_self_failing(self):
        """Tests when gather_self returns NoResultFound by asking for a node that doesn't exist"""

        with patch(
            "storio.model.litographer.litographer_model.BaseModel.generate_connection",
            new=get_test_engine,
        ):
            new_node = LitographerPlotNodeModel(1, 1, 1, 2)

            assert new_node.node_table_object.id != 1

            with Session(new_node.engine) as session:
                result_node = session.execute(
                    sql.select(schema.LitographyNode).where(
                        schema.LitographyNode.id == new_node.node_table_object.id
                    )
                ).scalar_one()

                assert result_node.id == new_node.node_table_object.id

    def test_add_note(self, model: LitographerPlotNodeModel) -> None:
        """tests adding notes and editing them"""

        model.add_note(NoteType.OTHER)

        assert model.notes[2].title == "new_note"

        model.add_note(NoteType.WHAT)

        assert list(model.notes.keys()) == [1, 2, 3]

        test = schema.LitographyNotes(
            id=1,
            title="new_note",
            description="",
            note_type=NoteType.OTHER,
            linked_node_id=model.node_table_object.id,
            project_id=model.project_id,
        )

        assert model.notes[2].title == test.title
        assert model.notes[2].description == test.description
        assert model.notes[2].note_type == test.note_type


class TestLitographerLinkedList:
    """test class for LitographerLinkedList"""

    @pytest.fixture(scope="function")
    @patch(
        "storio.model.litographer.litographer_model.BaseModel.generate_connection",
        new=get_test_engine,
    )
    def model(self) -> LitographerLinkedList:
        return LitographerLinkedList(1, 1, 1, 1)

    def test_load_up(self, model: LitographerLinkedList) -> None:
        model.load_up()
        assert model.head.node_table_object.id == 1
        assert model.head.next_node.node_table_object.id == 2
        assert model.tail.node_table_object.id == 3
        assert model.display() == [1, 2, 3]

    def test_append(self, model: LitographerLinkedList) -> None:
        model.load_up()

        model.append(4)

        assert model.display() == [1, 2, 3, 4]

    def test_prepend(self, model: LitographerLinkedList) -> None:
        model.load_up()

        model.prepend(5)

        assert model.display() == [5, 1, 2, 3]

    def test_get_node(self, model: LitographerLinkedList) -> None:
        model.load_up()

        result = model.get_node(2)

        assert result.node_table_object.id == 2

    def test_get_node_no_node(self, model: LitographerLinkedList) -> None:
        model.load_up()

        with pytest.raises(IndexError):
            model.get_node(100)

    def test_insert_node(self, model: LitographerLinkedList) -> None:
        model.load_up()

        model.insert_node(6, 2)

        assert model.display() == [1, 2, 6, 3]

        model.insert_node(7, 3)

        assert model.display() == [1, 2, 6, 3, 7]

    def test_delete(self, model: LitographerLinkedList) -> None:
        model.load_up()

        model.delete(2)

        assert model.display() == [1, 3]

    def test_delete_fail(self, model: LitographerLinkedList) -> None:
        model.load_up()
        with pytest.raises(IndexError):
            model.delete(4)

    def test_refresh(self, model: LitographerLinkedList) -> None:
        model.load_up()

        first_node = model.get_node(1)

        model.refresh()

        refreshed_node = model.get_node(1)

        assert not first_node is refreshed_node

    def test_move_node_aft(self, model: LitographerLinkedList) -> None:
        model.load_up()
        model.move_node_aft(2, 3)

        assert model.display() == [1, 3, 2]

        model.move_node_aft(1, 3)

        assert model.display() == [3, 1, 2]

    def test_move_node_pre(self, model: LitographerLinkedList) -> None:
        model.load_up()
        model.move_node_pre(3, 1)

        assert model.display() == [3, 1, 2]

        model.move_node_pre(2, 1)

        assert model.display() == [3, 2, 1]

    def test_display(self, model: LitographerLinkedList) -> None:
        model.load_up()

        assert model.display() == [1, 2, 3]

    def test_apply_order_to_tables(self, model: LitographerLinkedList) -> None:
        model.load_up()
        model.move_node_pre(1, 3)

        assert model.head.node_table_object.id == 2
        assert model.head.next_node.node_table_object.id == 1
        assert model.tail.node_table_object.id == 3

        assert model.head.node_table_object.previous_node == 1

        model.apply_order_to_tables()

        assert model.head.node_table_object.previous_node == None

    def test_get_tables(self, model: LitographerLinkedList) -> None:
        model.load_up()
        model.move_node_pre(1, 3)

        assert model.head.node_table_object.id == 2
        assert model.head.next_node.node_table_object.id == 1
        assert model.tail.node_table_object.id == 3

        result = model.get_tables()

        assert result[0].id == 2
        assert type(result[0]) == schema.LitographyNode

    def test_get_notes(self, model: LitographerLinkedList) -> None:
        model.load_up()
        notes = model.get_notes()

        assert notes[0] == 1


class TestLitographerPlotSectionModel:
    """class to test LitographerPlotSectionModel"""

    @pytest.fixture(scope="function")
    @patch(
        "storio.model.litographer.litographer_model.BaseModel.generate_connection",
        new=get_test_engine,
    )
    def model(self) -> LitographerPlotSectionModel:
        return LitographerPlotSectionModel(1, 1, 1, 1)

    def test_init(self, model: LitographerPlotSectionModel) -> None:
        assert model.nodes.display() == [1, 2, 3]


class TestLitographerPlotModel:
    """Class to test LitographerPlotModel"""

    @pytest.fixture(scope="function")
    def model(self) -> LitographerPlotModel:
        return LitographerPlotModel(1, 1, 1, 1)

    def test_init(self, model: LitographerPlotModel) -> None:
        assert model.plot_table.id == 1

    @patch(
        "storio.model.litographer.litographer_model.LitographerPlotModel._create_self"
    )
    @patch("storio.model.litographer.litographer_model.LitographerPlotModel.load_self")
    def test_init_fail(
        self, mock_load_self: MagicMock, mock_create_self: MagicMock
    ) -> None:
        def fail_load():
            raise NoResultFound

        mock_load_self.side_effect = fail_load

        test_model = LitographerPlotModel(1, 1, 1, 1)

        mock_create_self.assert_called_once()

        assert test_model

    def test_load_self(self, model: LitographerPlotModel) -> None:
        model.load_self()

        result = model.plot_table.as_dict()

        assert result == {
            "id": 1,
            "title": "test_plot",
            "description": "this is the test plot",
            "project_id": 1,
        }

    def test_load_plot_sections(self, model: LitographerPlotModel) -> None:
        model
        assert model.section_dict[1].section_id == 1

    def test_create_self(self) -> None:
        test_model = LitographerPlotModel(1, 1, 1, 100)

        with Session(test_model.engine) as session:
            result_table = session.execute(
                sql.select(schema.LitographyPlot).where(schema.LitographyPlot.id == 2)
            ).scalar_one()

        result_table_dict = result_table.as_dict()

        assert result_table_dict == {
            "id": 2,
            "title": "NewPlot",
            "description": "",
            "project_id": 1,
        }
