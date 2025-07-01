"""Holds common model classes"""

import dataclasses
from enum import Enum

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from storymaster.model.database import base_connection, common_queries, schema


class StorioModes(Enum):
    """The modes in storio"""

    LOREKEEPER = "Lorekeeper"
    LITOGRAPHER = "Litographer"


class GroupListTypes(Enum):
    ACTORS = "actors"
    BACKGROUNDS = "backgrounds"
    CLASSES = "classes"
    FACTIONS = "factions"
    HISTORY = "history"
    LOCATIONS = "locations"
    OBJECTS = "objects"
    RACES = "races"
    SUB_RACES = "sub_races"
    WORLD_DATAS = "world_datas"


class GroupData:
    """Structure of data grouped"""

    actors: list[schema.Actor]
    backgrounds: list[schema.Background]
    classes: list[schema.Class_]
    factions: list[schema.Faction]
    history: list[schema.History]
    locations: list[schema.Location]
    objects: list[schema.Object_]
    races: list[schema.Race]
    sub_races: list[schema.SubRace]
    world_datas: list[schema.WorldData]

    def __init__(
        self,
        actors: list[schema.Actor],
        backgrounds: list[schema.Background],
        classes: list[schema.Class_],
        factions: list[schema.Faction],
        history: list[schema.History],
        locations: list[schema.Location],
        objects: list[schema.Object_],
        races: list[schema.Race],
        sub_races: list[schema.SubRace],
        world_datas: list[schema.WorldData],
    ) -> None:
        self.actors = actors
        self.backgrounds = backgrounds
        self.classes = classes
        self.factions = factions
        self.history = history
        self.locations = locations
        self.objects = objects
        self.races = races
        self.sub_races = sub_races
        self.world_datas = world_datas

    def get_list(self, list_name: GroupListTypes) -> list[dict[str, str]]:
        """Get a list of an attribute"""

        return_list: list[schema.BaseTable] = getattr(self, list_name.value)

        return [item.as_dict() for item in return_list]


class BaseModel:
    """The base model class for Models"""

    engine: Engine
    user_id: int
    group_data: list[GroupData]

    def __init__(self, user_id: int):
        self.engine = self.generate_connection()
        self.user_id = user_id

    def generate_connection(self) -> Engine:
        """Generates the connection used to test"""
        return base_connection.engine

    def load_user_projects(self) -> list[int]:
        """Loads all the project_ids for a user"""
        with Session(self.engine) as session:
            project_id_list = session.execute(
                common_queries.get_project_ids_for_user(self.user_id)
            ).all()

        return [project.id for project in project_id_list]

    def load_user_data(self) -> list[GroupData]:
        """Loads all data attributed to a single user"""

        group_return: list[GroupData] = []

        with Session(self.engine) as session:
            group_list = (
                session.execute(common_queries.get_group_ids_for_project(1))
                .scalars()
                .all()
            )

            for group in group_list:
                actors = (
                    session.execute(
                        common_queries.get_lorekeeper_actors_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                backgrounds = (
                    session.execute(
                        common_queries.get_lorekeeper_backgrounds_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                classes = (
                    session.execute(
                        common_queries.get_lorekeeper_classes_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                factions = (
                    session.execute(
                        common_queries.get_lorekeeper_factions_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                history = (
                    session.execute(
                        common_queries.get_lorekeeper_history_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                locations = (
                    session.execute(
                        common_queries.get_lorekeeper_locations_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                objects = (
                    session.execute(
                        common_queries.get_lorekeeper_objects_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                races = (
                    session.execute(
                        common_queries.get_lorekeeper_races_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                sub_races = (
                    session.execute(
                        common_queries.get_lorekeeper_sub_races_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                world_datas = (
                    session.execute(
                        common_queries.get_lorekeeper_world_data_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                group_return.append(
                    GroupData(
                        actors=actors,
                        backgrounds=backgrounds,
                        classes=classes,
                        factions=factions,
                        history=history,
                        locations=locations,
                        objects=objects,
                        races=races,
                        sub_races=sub_races,
                        world_datas=world_datas,
                    )
                )

            self.group_data = group_return

            return group_return
