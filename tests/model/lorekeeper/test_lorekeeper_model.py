"""Test file for lorekeeper_model"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from sqlalchemy import sql
from sqlalchemy.orm import Session

from storymaster.model.database import schema
from storymaster.model.lorekeeper.lorekeeper_model import (
    ActorItem,
    ActorRelatedTablesEnum,
    ActorTab,
    FactionRelatedTablesEnum,
    FactionTab,
    LocationTab,
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

        assert (
            test_actor.actor_classes[list(test_actor.actor_classes.keys())[0]][
                "class_name"
            ]
            == "Wizard"
        )
        assert test_actor.actor_backgrounds[9]["background_name"] == "Guild Artisan"
        assert test_actor.actor_race
        assert test_actor.related

    def test_update_database(self, model: ActorTab) -> None:
        test_actor = model.load_item(3)

        test_actor.item_table_object.actor_age = 15

        test_actor.update_database()

        with Session(model.engine) as session:
            result = session.execute(
                sql.select(schema.Actor).where(schema.Actor.id == 3)
            ).scalar_one()

            assert result.actor_age == 15

        test_actor.actor_factions[3]["actor_faction"].actor_role = "test_role"

        test_actor.update_database()

        with Session(model.engine) as session:
            result_faction = session.execute(
                sql.select(schema.FactionMembers).where(
                    schema.FactionMembers.id
                    == test_actor.actor_factions[3]["actor_faction"].id
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

            test_actor.remove_from_database(
                ActorRelatedTablesEnum.RESIDENT, result_target.id
            )

    def test_remove_from_database(self, model: ActorTab) -> None:
        test_actor = model.load_item(1)
        target_id = list(test_actor.actor_history.keys())[-1]
        test_actor.remove_from_database(ActorRelatedTablesEnum.HISTORY_ACTOR, target_id)
        with Session(model.engine) as session:
            result_history = (
                session.execute(
                    sql.select(schema.HistoryActor).where(
                        schema.HistoryActor.actor_id == test_actor.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )

            assert len(list(result_history)) == 1


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

        assert model.table_items[1].related["members"][1]["actor"] == "Alfred"
        assert (
            model.table_items[1].related["members"][1]["membership"].actor_role
            == "Leader"
        )

    def test_faction_item_update_database(self, model: FactionTab) -> None:
        test_faction = model.load_item(2)

        test_faction.item_table_object.faction_description = "test_text"

        test_faction.faction_relations[2]["relation"].economically = "test_economy"

        test_faction.update_database()

        with Session(model.engine) as session:
            result_faction = session.execute(
                sql.select(schema.Faction).where(schema.Faction.id == 2)
            ).scalar_one()

            result_relation = (
                session.execute(
                    sql.select(schema.FactionAOnBRelations).where(
                        schema.FactionAOnBRelations.faction_a_id == 2
                    )
                )
                .scalars()
                .all()
            )

            assert result_faction.faction_description == "test_text"

            assert result_relation[-1].economically == "test_economy"

    def test_faction_item_add_to_database(self, model: FactionTab) -> None:
        test_faction = model.load_item(1)
        target_table = FactionRelatedTablesEnum.LOCATION_TO_FACTION
        test_data = {
            "location_id": 1,
            "faction_id": test_faction.item_table_object.id,
            "faction_presence": 0.1,
            "faction_power": 0.99,
            "notes": "test_notes",
            "group_id": 1,
        }
        test_faction.add_to_database(target_table, test_data)

        with Session(model.engine) as session:
            result_rows = (
                session.execute(
                    sql.select(schema.LocationToFaction).where(
                        schema.LocationToFaction.faction_id
                        == test_faction.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )

            assert result_rows[-1].as_dict() == {
                "id": 5,
                "location_id": 1,
                "faction_id": 1,
                "faction_presence": 0.1,
                "faction_power": 0.99,
                "notes": "test_notes",
                "group_id": 1,
            }

    def test_remove_from_database(self, model: FactionTab) -> None:
        test_faction = model.load_item(1)
        target_id = list(test_faction.faction_members.keys())[-1]
        test_faction.remove_from_database(
            FactionRelatedTablesEnum.FACTION_MEMBERS, target_id
        )

        with Session(model.engine) as session:
            result_members = (
                session.execute(sql.select(schema.FactionMembers)).scalars().all()
            )

            result_ids = [result.id for result in result_members]

            assert target_id not in result_ids


class TestLocationTab:
    """Class to test LocationTab and LocationItem"""

    @pytest.fixture(scope="function")
    def model(self) -> LocationTab:
        return LocationTab(1, 1, 1)

    def test_init(self, model: LocationTab) -> None:
        assert len(model.table) == 4

        test_location = model.table[1].as_dict()

        assert test_location == {
            "id": 1,
            "location_name": "Castle City",
            "location_type": "city",
            "location_description": "the big city",
            "sights": "pretty",
            "smells": "stinky",
            "sounds": "loud",
            "feels": "home",
            "tastes": "yum",
            "coordinates": "A1",
            "group_id": 1,
        }

    def test_load_item(self, model: LocationTab) -> None:
        test_location = model.load_item(1)

        assert model.table_items[1] == test_location

    def test_location_item_init(self, model: LocationTab) -> None:
        test_location = model.load_item(1)
        assert test_location.user == 1

    def test_location_item_gather_related(self, model: LocationTab) -> None:
        test_location = model.load_item(1)

        assert test_location.related

        expected_location_residents_dict = {
            1: {"resident": "Alfred"},
            2: {"resident": "Elouise"},
            3: {"resident": "Barry"},
        }
        expected_location_dungeons_dict = {}
        expected_location_history_dict = {1: {"history": "betrayal"}}

        assert test_location.related["residents"] == expected_location_residents_dict
        assert test_location.related["factions"][1]["faction"] == "Mage Guild"
        assert test_location.related["dungeons"] == expected_location_dungeons_dict
        assert test_location.related["cities"][1]["location"] == "Castle City"
        assert test_location.related["districts"][1]["location"] == "Flower District"
        assert test_location.related["flora_fauna"][1]["location"] == "Castle City"
        assert test_location.related["history"] == expected_location_history_dict

    def test_location_item_update_database(self, model: LocationTab) -> None:
        test_location = model.load_item(2)

        test_location.item_table_object.coordinates = "B2"
        test_location.location_factions[3]["location_faction"].faction_power = 0.95
        test_location.update_database()

        with Session(model.engine) as session:
            result_location = session.execute(
                sql.select(schema.Location).where(schema.Location.id == 2)
            ).scalar_one()

            assert result_location.coordinates == "B2"

            result_location_faction = session.execute(
                sql.select(schema.LocationToFaction).where(
                    schema.LocationToFaction.id == 3
                )
            ).scalar_one()

            assert result_location_faction.faction_power == 0.95

        test_location.item_table_object.coordinates = "A1"
        test_location.location_factions[3]["location_faction"].faction_power = 1.01
        test_location.update_database()
