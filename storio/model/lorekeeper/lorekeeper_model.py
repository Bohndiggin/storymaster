"""Holds the classes for the lorekeeper model"""

import enum
import typing

from sqlalchemy import Engine, sql
from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import base_connection, common_queries, schema


class LorekeeperTab(enum.Enum):
    """Enumerator for the different tabs in lorekeeper"""

    ACTOR = schema.Actor
    FACTION = schema.Faction
    LOCATION = schema.Location
    HISTORY = schema.History
    OBJECT_ = schema.Object_
    WORLD_DATA = schema.WorldData


class LorekeeperDataModel:
    """Class for lorekeeper data"""

    class_list: list[schema.Class_]
    background_list: list[schema.Background]
    race_list: list[schema.Race]
    sub_race_list: list[schema.SubRace]
    actor_list: list[schema.Actor]
    faction_list: list[schema.Faction]
    location_list: list[schema.Location]
    history_list: list[schema.History]
    object_list: list[schema.Object_]
    world_data_list: list[schema.WorldData]

    def __init__(self, engine: Engine, target_project: int) -> None:
        """Queries db and returns a self"""

        with Session(engine) as session:
            group = session.execute(
                common_queries.get_group_ids_for_project(target_project)
            ).one()
            self.class_list = list(
                session.execute(
                    common_queries.get_lorekeeper_classes_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.background_list = list(
                session.execute(
                    common_queries.get_lorekeeper_backgrounds_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.race_list = list(
                session.execute(
                    common_queries.get_lorekeeper_races_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.sub_race_list = list(
                session.execute(
                    common_queries.get_lorekeeper_sub_races_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.actor_list = list(
                session.execute(
                    common_queries.get_lorekeeper_actors_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.faction_list = list(
                session.execute(
                    common_queries.get_lorekeeper_factions_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.location_list = list(
                session.execute(
                    common_queries.get_lorekeeper_locations_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.history_list = list(
                session.execute(
                    common_queries.get_lorekeeper_history_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.object_list = list(
                session.execute(
                    common_queries.get_lorekeeper_objects_from_group(group.id)
                )
                .scalars()
                .all()
            )
            self.world_data_list = list(
                session.execute(
                    common_queries.get_lorekeeper_world_data_from_group(group.id)
                )
                .scalars()
                .all()
            )

    def upload_data(self, engine: Engine) -> None:
        """Uploads self to database"""


class BaseLorekeeperPageModel(BaseModel):
    """Base model for Lorekeeper"""

    def __init__(self) -> None:
        super().__init__()
        self.mode = StorioModes.LOREKEEPER
        self.user = 1  # TEMP
        self.group = 1  # TEMP

    def load_user_projects(self) -> list[int]:
        """Loads all the project_ids for a user"""
        with Session(self.engine) as session:
            project_id_list = session.execute(
                common_queries.get_project_ids_for_user(self.user)
            ).all()

        return [project.id for project in project_id_list]


class LorekeeperTabModel(BaseLorekeeperPageModel):
    """Parent Model for the lorekeeper tabs"""

    tab_type: LorekeeperTab

    def __init__(self):
        super().__init__()
        self.table = self.populate_table()

    def populate_table(
        self,
    ) -> list[
        schema.Actor
        | schema.Faction
        | schema.Location
        | schema.History
        | schema.Object_
        | schema.WorldData
    ]:
        """Method to populate table with lorekeeper items of the correct type."""
        with Session(self.engine) as session:
            tab_list = (
                session.execute(
                    sql.select(self.tab_type.value).where(
                        self.tab_type.value.group_id == self.group
                    )
                )
                .scalars()
                .all()
            )

        return tab_list


class ActorTab(LorekeeperTabModel):
    """Model for the actor tab"""

    table: list[schema.Actor]
    tab_type = LorekeeperTab.ACTOR

class FactionTab(LorekeeperTabModel):
    """Model for the faction tab"""

    table: list[schema.Faction]
    tab_type = LorekeeperTab.FACTION

class LocationTab(LorekeeperTabModel):
    """Model for the location tab"""

    table: list[schema.Location]
    tab_type = LorekeeperTab.LOCATION

class HistoryTab(LorekeeperTabModel):
    """Model for the history tab"""
    
    table: list[schema.History]
    tab_type = LorekeeperTab.HISTORY

class ObjectTab(LorekeeperTabModel):
    """Model for the object_ tab"""

    table: list[schema.Object_]
    tab_type = LorekeeperTab.OBJECT_

class WorldDataTab(LorekeeperTabModel):
    """Model for the world data tab"""

    table: list[schema.WorldData]
    tab_type = LorekeeperTab.WORLD_DATA


class LorekeeperItemModel(BaseLorekeeperPageModel):
    """Parent Class for individual items on the lorekeeper page"""

    def gather_related(self) -> None:
        """Method to gather related table's data. To Be overwritten"""
