"""Test file for litographer_model"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from sqlalchemy import sql
from sqlalchemy.orm import Session

from storio.model.database import schema
from storio.model.database.base_connection import get_test_engine
from storio.model.database.schema.base import NoteType
from storio.model.litographer.litographer_model import LitographerPlotNodeModel

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
            result_node = session.execute(
                sql.select(schema.LitographyNode)
            ).scalar_one()

            assert model.node_table_object.id == result_node.id

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

        assert model.notes[1].title == "new_note"

        model.add_note(NoteType.WHAT)
        
        assert list(model.notes.keys()) == [1, 2]

        test = schema.LitographyNotes(
            id=1,
            title="new_note",
            description="",
            note_type=NoteType.OTHER,
            linked_node_id=model.node_table_object.id,
            project_id=model.project_id,
        )

        assert model.notes[1].title == test.title
        assert model.notes[1].description == test.description
        assert model.notes[1].note_type == test.note_type

        
