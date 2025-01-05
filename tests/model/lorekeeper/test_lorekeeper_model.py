"""Test file for lorekeeper_model"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from sqlalchemy import sql
from sqlalchemy.orm import Session

from storio.model.database import schema
from storio.model.lorekeeper.lorekeeper_model import (
    ActorItem,
    ActorRelatedTablesEnum,
    ActorTab,
    FactionTab,
    LorekeeperTab,
)

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

    def test_load_item(self, model: ActorTab) -> None:
        result = model.load_item(1)
        assert model.table_items[1] == result
        assert result.item_table_object.as_dict() == {
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

        assert result.user == 1

    def test_actor_item_gather_related(self, model: ActorTab) -> None:
        test_actor = model.load_item(1)

        assert test_actor.actor_classes[0]["class_name"] == "Wizard"
        assert test_actor.actor_backgrounds[0]["background_name"] == "Guild Artisan"
        assert test_actor.actor_race
        assert test_actor.related

    def test_update_database(self, model: ActorTab) -> None:
        test_actor = model.load_item(1)

        test_actor.item_table_object.actor_age = 15

        test_actor.update_database()

        with Session(model.engine) as session:
            result = session.execute(
                sql.select(schema.Actor).where(schema.Actor.id == 1)
            ).scalar_one()

            assert result.actor_age == 15

        test_actor.actor_factions[0]["actor_faction"].actor_role = "test_role"

        test_actor.update_database()

        with Session(model.engine) as session:
            result_faction = session.execute(
                sql.select(schema.FactionMembers).where(
                    schema.FactionMembers.id
                    == test_actor.actor_factions[0]["actor_faction"].id
                )
            ).scalar_one()

            assert result_faction.actor_role == "test_role"

    def test_add_to_database(self, model: ActorTab) -> None:
        test_actor = model.load_item(1)

        target_table = ActorRelatedTablesEnum.RESIDENT

        arguments = {
            "actor_id": test_actor.item_table_object.id,
            "location_id": 1,
            "group_id": test_actor.group,
        }

        test_actor.add_to_database(target_table, arguments)

        with Session(model.engine) as session:
            result = (
                session.execute(
                    sql.select(schema.Resident).where(
                        schema.Resident.actor_id == test_actor.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )

            result_target = result[-1]

            assert result_target.location_id == 1


class TestFactionTab:
    """Class to test FactionTab and FactionItem"""

    @pytest.fixture(scope="function")
    def model(self) -> FactionTab:
        return FactionTab(1, 1, 1)

    def test_init(self, model: FactionTab) -> None:
        assert len(model.table) == 2
        test_faction = model.table[1].as_dict()

        assert test_faction == {
            "id": 1,
            "faction_name": "Mage Guild",
            "faction_description": "the mage guild does magic",
            "goals": "do magic",
            "faction_values": "inteligence",
            "faction_income_sources": "selling staffs",
            "faction_expenses": "books",
            "group_id": 1,
        }

    def test_load_item(self, model: FactionTab) -> None:
        model.load_item(1)

        assert model.table_items[1].item_table_object.id == 1

        assert model.table_items[1].related["members"][0]["actor"] == "Alfred"
        assert (
            model.table_items[1].related["members"][0]["membership"].actor_role
            == "Leader"
        )

    def test_faction_item_update_database(self, model: FactionTab) -> None:
        test_faction = model.load_item(1)

        test_faction.item_table_object.faction_description = "test_text"

        test_faction.faction_relations[0]["relation"].economically = "test_economy"

        test_faction.update_database()

        with Session(model.engine) as session:
            result_faction = session.execute(
                sql.select(schema.Faction).where(schema.Faction.id == 1)
            ).scalar_one()

            result_relation = (
                session.execute(
                    sql.select(schema.FactionAOnBRelations).where(
                        schema.FactionAOnBRelations.faction_a_id == 1
                    )
                )
                .scalars()
                .all()
            )

            assert result_faction.faction_description == "test_text"

            assert result_relation[-1].economically == "test_economy"

    def test_faction_item_add_to_database(self, model: FactionTab) -> None:
        test_faction = model.load_item(1)
