"""Test file for lorekeeper_model"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from sqlalchemy import sql
from sqlalchemy.orm import Session

from storio.model.database import schema
from storio.model.database.base_connection import get_test_engine
from storio.model.lorekeeper.lorekeeper_model import ActorTab, LorekeeperTab

fake = Faker()


class TestActorTab:
    """class to test ActorTab"""

    @pytest.fixture(scope="function")
    def model(self) -> ActorTab:
        return ActorTab(1, 1, 1)

    def test_init(self, model: ActorTab) -> None:
        assert model.tab_type == LorekeeperTab.ACTOR
        assert model.table_items == {}

        result = model.table[1].as_dict()

        assert result == {
            "id": 1,
            "first_name": "Alfred",
            "middle_name": "T",
            "last_name": "Wizzler",
            "title": "Dr.",
            "actor_age": 506,
            "class_id": 13,
            "actor_level": 20,
            "background_id": 9,
            "job": "Mage Guild Master ",
            "actor_role": "quest giver",
            "race_id": 4,
            "sub_race_id": 2,
            "alignment": "LN",
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 18,
            "wisdom": 10,
            "charisma": 10,
            "ideal": "Knowlege",
            "bond": "The Guild",
            "flaw": "Greed",
            "appearance": "Old funny man with big beard",
            "strengths": "magic",
            "weaknesses": "beard",
            "notes": "huh",
            "group_id": 1,
        }
