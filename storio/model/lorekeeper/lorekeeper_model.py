"""Holds the classes for the lorekeeper model"""

import enum
from typing import Optional, TypeAlias, Union

from sqlalchemy import Engine, sql
from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import base_connection, common_queries, schema

LoreTable: TypeAlias = Union[
    schema.Actor,
    schema.Faction,
    schema.Location,
    schema.History,
    schema.Object_,
    schema.WorldData,
]


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
    ) -> list[LoreTable]:
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


class LorekeeperItemModel(BaseLorekeeperPageModel):
    """Parent Class for individual items on the lorekeeper page"""

    item_table_object: LoreTable

    def __init__(self, item_table_object: LoreTable):
        super().__init__()
        self.item_table_object = item_table_object

    def gather_related(self) -> None:
        """Method to gather related table's data. To Be overwritten"""

class ActorTab(LorekeeperTabModel):
    """Model for the actor tab"""

    table: list[schema.Actor]
    tab_type = LorekeeperTab.ACTOR

class ActorItem(LorekeeperItemModel):
    """Model for a single actor"""

    item_table_object: schema.Actor

    def gather_related(self) -> None:
        """Method to gather related table's data for the Actor Table"""

        with Session(self.engine) as session:
            self.actor_relations = session.execute(
                sql.select(schema.ActorAOnBRelations).where(schema.ActorAOnBRelations.actor_a_id == self.item_table_object.id)
            ).scalars().all()
            self.actor_factions = session.execute(
                sql.select(schema.Faction)
                .join(schema.FactionMembers)
                .where(schema.FactionMembers.actor_id == self.item_table_object.id)
            ).scalars().all()
            self.actor_residence = session.execute(
                sql.select(schema.Location)
                .join(schema.Resident)
                .where(schema.Resident.actor_id == self.item_table_object.id)
            ).scalars().all()
            self.actor_history = session.execute(
                sql.select(schema.History)
                .join(schema.HistoryActor)
                .where(schema.HistoryActor.actor_id == self.item_table_object.id)
            ).scalars().all()
            self.actor_objects = session.execute(
                sql.select(schema.Object_)
                .join(schema.ObjectToOwner)
                .where(schema.ObjectToOwner.actor_id == self.item_table_object.id)
            ).scalars().all()


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


LorekeeperTabModelTypes: TypeAlias = Union[
    ActorTab, FactionTab, LocationTab, HistoryTab, ObjectTab, WorldDataTab
]


class LorekeeperTabModelFactory:
    """Factory to make LorekeeperTabModel children"""

    def open_tab(self, tab_type: LorekeeperTab) -> LorekeeperTabModelTypes:
        """Opens the corresponding tab based on tab_type

        Args:
            tab_type: the lorekeeper tab you want to open

        Returns:
            LorekeeperTabModelTypes: an instance of the lorekeeper tab model

        """

        match tab_type:
            case LorekeeperTab.ACTOR:
                return ActorTab()
            case LorekeeperTab.FACTION:
                return FactionTab()
            case LorekeeperTab.LOCATION:
                return LocationTab()
            case LorekeeperTab.HISTORY:
                return HistoryTab()
            case LorekeeperTab.OBJECT_:
                return ObjectTab()
            case LorekeeperTab.WORLD_DATA:
                return WorldDataTab()

