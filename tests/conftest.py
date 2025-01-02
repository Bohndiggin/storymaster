"""conftest setup"""

import csv
from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from tqdm import tqdm

from storio.model.database import schema
from storio.model.database.base_connection import get_test_engine, test_engine


@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """Generates / refreshes a test database for testing"""

    def load_from_csv(
        path: str, group_id: int | None = None
    ) -> list[dict[str, str | int]]:
        """loads the csv based on path and returns a list of dictionaries"""

        with open(path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            result_list = []
            for row in reader:
                result_list.append(row)

            if not group_id:
                return result_list
            for result in result_list:
                result["group_id"] = group_id

        return result_list

    def clear_old_data(session: Session, group_id: int) -> Session:
        """deletes all old lorekeeper data from db of a certain group id"""

        with open("tests/seed.sql", "r") as sql_file:
            commands = sql_file.read()

        session.execute(text(commands))

        return session

    print("Initializing Database")
    with Session(test_engine) as session:
        print("Clearing old data")
        session = clear_old_data(session, 1)
        session.commit()
        with tqdm(
            total=21, leave=False, desc="Adding Default Data to Database"
        ) as pbar:
            session.add(schema.User(id=1, username="test"))

            session.commit()
            pbar.update(1)

            session.add(schema.Project(id=1, user_id=1))

            session.commit()
            pbar.update(1)

            session.add(
                schema.LorekeeperGroup(
                    id=1, name="TESTGROUP", description="GROUP FOR TESTING", user_id=1
                )
            )

            session.commit()
            pbar.update(1)

            classes = load_from_csv("tests/model/database/test_data/classes.csv", 1)

            session.add_all([schema.Class_(**i) for i in classes])

            backgrounds = load_from_csv(
                "tests/model/database/test_data/backgrounds.csv", 1
            )

            session.add_all([schema.Background(**i) for i in backgrounds])

            races = load_from_csv("tests/model/database/test_data/races.csv", 1)

            session.add_all([schema.Race(**i) for i in races])

            session.commit()
            pbar.update(1)

            sub_races = load_from_csv("tests/model/database/test_data/sub_races.csv", 1)

            session.add_all([schema.SubRace(**i) for i in sub_races])

            session.commit()
            pbar.update(1)

            actors = load_from_csv("tests/model/database/test_data/actors_test.csv", 1)

            session.add_all([schema.Actor(**i) for i in actors])

            factions = load_from_csv(
                "tests/model/database/test_data/factions_test.csv", 1
            )

            session.add_all([schema.Faction(**i) for i in factions])

            session.commit()
            pbar.update(1)

            faction_members = load_from_csv(
                "tests/model/database/test_data/faction_members_test.csv", 1
            )

            session.add_all([schema.FactionMembers(**i) for i in faction_members])

            faction_relations = load_from_csv(
                "tests/model/database/test_data/faction_relations_test.csv", 1
            )

            session.add_all(
                [schema.FactionAOnBRelations(**i) for i in faction_relations]
            )

            session.commit()
            pbar.update(1)

            histories = load_from_csv(
                "tests/model/database/test_data/historical_fragments_test.csv", 1
            )

            session.add_all([schema.History(**i) for i in histories])

            session.commit()
            pbar.update(1)

            history_actors = load_from_csv(
                "tests/model/database/test_data/involved_history_actor_test.csv", 1
            )

            session.add_all([schema.HistoryActor(**i) for i in history_actors])

            session.commit()
            pbar.update(1)

            locations = load_from_csv(
                "tests/model/database/test_data/location_test.csv", 1
            )

            session.add_all([schema.Location(**i) for i in locations])

            session.commit()
            pbar.update(1)

            history_locations = load_from_csv(
                "tests/model/database/test_data/involved_history_location_test.csv", 1
            )

            session.add_all([schema.HistoryLocation(**i) for i in history_locations])

            location_cities = load_from_csv(
                "tests/model/database/test_data/location_city_test.csv", 1
            )

            session.add_all([schema.LocationCity(**i) for i in location_cities])

            session.commit()
            pbar.update(1)

            location_cities_districts = load_from_csv(
                "tests/model/database/test_data/location_city_districts_test.csv", 1
            )

            session.add_all(
                [schema.LocationCityDistricts(**i) for i in location_cities_districts]
            )

            location_factions = load_from_csv(
                "tests/model/database/test_data/location_to_faction_test.csv", 1
            )

            session.add_all([schema.LocationToFaction(**i) for i in location_factions])

            location_flora_fauna = load_from_csv(
                "tests/model/database/test_data/location_flora_fauna_test.csv", 1
            )

            session.add_all(
                [schema.LocationFloraFauna(**i) for i in location_flora_fauna]
            )

            location_dungeons = load_from_csv(
                "tests/model/database/test_data/location_dungeon_test.csv", 1
            )

            session.add_all([schema.LocationDungeon(**i) for i in location_dungeons])

            residents = load_from_csv(
                "tests/model/database/test_data/residents_test.csv", 1
            )

            session.add_all([schema.Resident(**i) for i in residents])

            session.commit()
            pbar.update(1)

            objects = load_from_csv("tests/model/database/test_data/object_test.csv", 1)

            session.add_all([schema.Object_(**i) for i in objects])

            session.commit()
            pbar.update(1)

            history_objects = load_from_csv(
                "tests/model/database/test_data/involved_history_object_test.csv", 1
            )

            session.add_all([schema.HistoryObject(**i) for i in history_objects])

            world_datas = load_from_csv(
                "tests/model/database/test_data/world_data_test.csv", 1
            )

            session.add_all([schema.WorldData(**i) for i in world_datas])

            session.commit()
            pbar.update(1)

            history_world_data = load_from_csv(
                "tests/model/database/test_data/involved_history_world_data_test.csv", 1
            )

            session.add_all([schema.HistoryWorldData(**i) for i in history_world_data])

            session.commit()
            pbar.update(1)

            node_data_list = load_from_csv(
                "tests/model/database/test_data/node_data_test.csv"
            )

            node_data_list[0]["previous_node"] = None
            node_data_list[-1]["next_node"] = None

            schema_list = [
                schema.LitographyNode(**i, project_id=1) for i in node_data_list
            ]

            session.add_all(schema_list)
            session.commit()
            pbar.update(1)

            note_data_list = load_from_csv(
                "tests/model/database/test_data/note_data_test.csv"
            )

            session.add_all([schema.LitographyNotes(**i) for i in note_data_list])
            session.commit()
            pbar.update(1)

            plot_list = load_from_csv("tests/model/database/test_data/plot.csv")

            session.add_all([schema.LitographyPlot(**i) for i in plot_list])
            session.commit()
            pbar.update(1)

            plot_section_list = load_from_csv(
                "tests/model/database/test_data/plot_section.csv"
            )

            session.add_all(
                [schema.LitographyPlotSection(**i) for i in plot_section_list]
            )
            session.commit()
            pbar.update(1)

            node_to_section_list = load_from_csv(
                "tests/model/database/test_data/node_to_plot_section.csv"
            )

            session.add_all(
                [schema.LitographyNodeToPlotSection(**i) for i in node_to_section_list]
            )
            session.commit()
            pbar.update(1)

            actor_relations = load_from_csv(
                "tests/model/database/test_data/actor_a_on_b.csv"
            )

            session.add_all([schema.ActorAOnBRelations(**i) for i in actor_relations])
            session.commit()
            pbar.update(1)

    with patch(
        "storio.model.litographer.litographer_model.BaseModel.generate_connection",
        new=get_test_engine,
    ):

        yield

    print("Tearing down test environment...")

    with Session(test_engine) as session:
        session = clear_old_data(session, 1)
        session.commit()

    print("Teardown complete")
