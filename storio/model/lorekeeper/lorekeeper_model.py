"""Holds the classes for the lorekeeper model"""

import enum
import typing
from typing import Optional, TypeAlias, Union

from sqlalchemy import Engine, sql
from sqlalchemy.orm import Session

from storio.model.common.common_model import BaseModel, StorioModes
from storio.model.database import base_connection, common_queries, schema

LorekeeperMainTable: TypeAlias = Union[
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
    table: dict[int, LorekeeperMainTable]
    table_items: dict[int, "LorekeeperItemModel"]

    def __init__(self):
        super().__init__()
        self.table = self.populate_table()

    def refresh(self) -> None:
        """Pulls data again"""
        self.table = self.populate_table()

    def populate_table(
        self,
    ) -> dict[int, LorekeeperMainTable]:
        """Method to populate table with lorekeeper items of the correct type."""
        with Session(self.engine) as session:
            table_list = (
                session.execute(
                    sql.select(self.tab_type.value).where(
                        self.tab_type.value.group_id == self.group
                    )
                )
                .scalars()
                .all()
            )
            table_dict = {item.id: item for item in table_list}

        return table_dict

    def update_database(self) -> None:
        """Updates the database with changed data for all entries"""

        for item in self.table_items.values():
            item.update_database()

    def load_item(self, item_number: int) -> typing.Any:
        """Creates a single item from the table. TO BE OVERWRITTEN"""


class LorekeeperItemModel(BaseLorekeeperPageModel):
    """Parent Class for individual items on the lorekeeper page"""

    item_table_object: LorekeeperMainTable
    related: dict[
        str, list[dict[str, typing.Any]]
    ]  # Contains data from intersticial tables along with the proper name

    def __init__(self, item_table_object: LorekeeperMainTable):
        super().__init__()
        self.item_table_object = item_table_object
        self.gather_related()

    def gather_related(self) -> None:
        """Method to gather related table's data. To Be overwritten"""
        return

    def _update_self_database(self) -> None:
        """Updates the item_table_object in the database"""

        with Session(self.engine) as session:
            session.merge(self.item_table_object)
            session.commit()

    def update_database(self) -> None:
        """Method to update the database with any changed data. TO BE OVERWRITTEN"""
        return
    
    def add_to_database(self) -> None:
        """Method to add an entry to the database. TO BE OVERWRITTEN"""
        return


LorekeeperActorRelatedTable: TypeAlias = Union[
    schema.ActorAOnBRelations,
    schema.ActorToSkills,
    schema.HistoryActor,
    schema.Resident,
    schema.ObjectToOwner,
    schema.FactionMembers
]

class ActorItem(LorekeeperItemModel):
    """Model for a single actor"""

    item_table_object: schema.Actor

    def gather_related(self) -> None:
        """Method to gather related table's data for the Actor Table"""

        with Session(self.engine) as session:
            self.actor_classes = (
                session.execute(
                    sql.select(schema.Class_)
                    .where(schema.Class_.id == self.item_table_object.class_id)
                )
                .scalars()
                .all()
            )
            self.actor_classes = [
                {"class": i} for i in self.actor_classes
            ]
            self.actor_backgrounds = (
                session.execute(
                    sql.select(schema.Background)
                    .where(schema.Background.id == self.item_table_object.background_id)
                )
                .scalars()
                .all()
            )
            self.actor_backgrounds = [
                {"background": i} for i in self.actor_backgrounds
            ]
            self.actor_race = (
                session.execute(
                    sql.select(schema.Race)
                    .where(schema.Race.id == self.item_table_object.race_id)
                )
                .scalars()
                .all()
            )
            self.actor_race = [
                {"race": i} for i in self.actor_race
            ]
            self.actor_subrace = (
                session.execute(
                    sql.select(schema.SubRace)
                    .where(schema.SubRace == self.item_table_object.sub_race_id)
                )
                .scalars()
                .all()
            )
            self.actor_subrace = [
                {"subrace": i} for i in self.actor_subrace
            ]
            self.actor_relations = (
                session.execute(
                    sql.select(schema.ActorAOnBRelations).where(
                        schema.ActorAOnBRelations.actor_a_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.actor_relations = [
                {"other_actor": i.actor_b.first_name, "relation": i}
                for i in self.actor_relations
            ]
            self.actor_factions = (
                session.execute(
                    sql.select(schema.FactionMembers).where(
                        schema.FactionMembers.actor_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.actor_factions = [
                {"faction": i.faction.faction_name, "actor_faction": i}
                for i in self.actor_factions
            ]
            self.actor_residence = (
                session.execute(
                    sql.select(schema.Resident).where(
                        schema.Resident.actor_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.actor_residence = [
                {"location": i.location.location_name} for i in self.actor_residence
            ]
            self.actor_history = (
                session.execute(
                    sql.select(schema.HistoryActor).where(
                        schema.HistoryActor.actor_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.actor_history = [
                {"history": i.history.event_name} for i in self.actor_history
            ]
            self.actor_objects = (
                session.execute(
                    sql.select(schema.ObjectToOwner).where(
                        schema.ObjectToOwner.actor_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.actor_objects = [
                {"object": i.object.object_name} for i in self.actor_objects
            ]
            self.actor_skills = (
                session.execute(
                    sql.select(schema.Skills)
                    .join(schema.ActorToSkills)
                    .where(schema.ActorToSkills.actor_id == self.item_table_object.id)
                )
                .scalars()
                .all()
            )
            self.actor_skills = [
                {"skill": i} for i in self.actor_skills
            ]

            self.related = {
                "relations": self.actor_relations,
                "factions": self.actor_factions,
                "locations": self.actor_residence,
                "history": self.actor_history,
                "objects": self.actor_objects,
                "skills": self.actor_skills,
                "classes": self.actor_classes,
                "backgrounds": self.actor_backgrounds,
                "race": self.actor_race,
                "subrace": self.actor_subrace
            }

    def update_database(self) -> None:
        """Updated the database with any changed data."""

        self._update_self_database()

        with Session(self.engine) as session:

            for relation in self.actor_relations:
                session.merge(relation["relation"])

            for faction in self.actor_factions:
                session.merge(faction["actor_faction"])

            session.commit()

    def add_to_database(self, target_table: LorekeeperActorRelatedTable): # ADD TO FRONT END???
        """Adds to database"""


class ActorTab(LorekeeperTabModel):
    """Model for the actor tab"""

    table: dict[int, schema.Actor]
    tab_type = LorekeeperTab.ACTOR
    table_items: dict[int, ActorItem] = {}

    def load_item(self, item_number: int) -> ActorItem:
        """Creates an ActorItem

        Args:
            item_number: non-zero indexed id of the item being requested

        Returns:
            ActorItem instance of the item requested

        """

        self.table_items[item_number] = ActorItem(self.table[item_number])

        return self.table_items[item_number]


class FactionItem(LorekeeperItemModel):
    """Model for a single Faction"""

    item_table_object: schema.Faction

    def gather_related(self) -> None:
        """Gathers related data related to the faction tab"""

        with Session(self.engine) as session:
            self.faction_relations = (
                session.execute(
                    sql.select(schema.FactionAOnBRelations).where(
                        schema.FactionAOnBRelations.faction_a_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.faction_relations = [
                {"other_faction": i.faction_b.faction_name, "relation": i}
                for i in self.faction_relations
            ]
            self.faction_members = (
                session.execute(
                    sql.select(
                        schema.FactionMembers,
                    ).where(
                        schema.FactionMembers.faction_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.faction_members = [
                {"actor": i.actor.first_name, "membership": i}
                for i in self.faction_members
            ]
            self.faction_history = (
                session.execute(
                    sql.select(schema.HistoryFaction).where(
                        schema.HistoryFaction.faction_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.faction_history = [
                {"history": i.history.event_name} for i in self.faction_history
            ]
            self.faction_locations = (
                session.execute(
                    sql.select(schema.LocationToFaction).where(
                        schema.LocationToFaction.faction_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.faction_locations = [
                {"location": i.location.location_name} for i in self.faction_locations
            ]

            self.related = {
                "relations": self.faction_relations,
                "members": self.faction_members,
                "history": self.faction_history,
                "locations": self.faction_locations,
            }

    def update_database(self) -> None:
        """Updates the database with any changed data"""

        self._update_self_database()

        with Session(self.engine) as session:
            for relation in self.faction_relations:
                session.merge(relation["relation"])

            for member in self.faction_members:
                session.merge(member["membership"])

            session.commit()


class FactionTab(LorekeeperTabModel):
    """Model for the faction tab"""

    table: dict[int, schema.Faction]
    tab_type = LorekeeperTab.FACTION
    table_items: dict[int, FactionItem] = {}

    def load_item(self, item_number: int) -> FactionItem:
        """Creates Faction Item

        Args:
            item_number: int of the item from the table

        Returns:
            FactionItem of the request
        """

        self.table_items[item_number] = FactionItem(self.table[item_number])

        return self.table_items[item_number]


class LocationItem(LorekeeperItemModel):
    """Model for single location"""

    item_table_object: schema.Location

    def gather_related(self) -> None:
        """Gathers data related to the location"""

        with Session(self.engine) as session:
            self.location_residents = (
                session.execute(
                    sql.select(schema.Resident).where(
                        schema.Resident.location_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_residents = [
                {"resident": i.actor.first_name} for i in self.location_residents
            ]
            self.location_factions = (
                session.execute(
                    sql.select(schema.LocationToFaction).where(
                        schema.LocationToFaction.location_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_factions = [
                {"faction": i.faction.faction_name, "location_faction": i}
                for i in self.location_factions
            ]
            self.location_dungeons = (
                session.execute(
                    sql.select(schema.LocationDungeon).where(
                        schema.LocationDungeon.location_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_dungeons = [
                {"location": i.location.location_name, "dungeon": i}
                for i in self.location_dungeons
            ]
            self.location_cities = (
                session.execute(
                    sql.select(schema.LocationCity).where(
                        schema.LocationCity.location_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_cities = [
                {"location": i.location.location_name, "city": i}
                for i in self.location_cities
            ]
            self.location_city_districts = (
                session.execute(
                    sql.select(schema.LocationCityDistricts).where(
                        schema.LocationCityDistricts.location_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_city_districts = [
                {"location": i.district.location_name, "district": i}
                for i in self.location_city_districts
            ]
            self.location_flora_fauna = (
                session.execute(
                    sql.select(schema.LocationFloraFauna).where(
                        schema.LocationFloraFauna.location_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_flora_fauna = [
                {"location": i.location_.location_name, "flora_fauna": i}
                for i in self.location_flora_fauna
            ]
            self.location_history = (
                session.execute(
                    sql.select(schema.HistoryLocation).where(
                        schema.HistoryLocation.location_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.location_history = [
                {"history": i.history.event_name} for i in self.location_history
            ]

            self.related = {
                "residents": self.location_residents,
                "factions": self.location_factions,
                "dungeons": self.location_dungeons,
                "cities": self.location_cities,
                "districts": self.location_city_districts,
                "flora_fauna": self.location_flora_fauna,
                "history": self.location_history,
            }

    def update_database(self) -> None:
        """Updates database for self and other tables"""

        self._update_self_database()

        with Session(self.engine) as session:
            for location_faction in self.location_factions:
                session.merge(location_faction["location_faction"])

            for location_dungeon in self.location_dungeons:
                session.merge(location_dungeon["dungeon"])

            for location_city in self.location_cities:
                session.merge(location_city["city"])

            for location_district in self.location_city_districts:
                session.merge(location_district["district"])

            for flora_fauna in self.location_flora_fauna:
                session.merge(flora_fauna["flora_fauna"])

            session.commit()


class LocationTab(LorekeeperTabModel):
    """Model for the location tab"""

    table: dict[int, schema.Location]
    tab_type = LorekeeperTab.LOCATION
    table_items: dict[int, LocationItem] = {}

    def load_item(self, item_number: int) -> LocationItem:
        """Creates LocationItem

        Args:
            item_number: int of the item from the table

        Returns:
            LocationItem of the request
        """

        self.table_items[item_number] = LocationItem(self.table[item_number])

        return self.table_items[item_number]


class HistoryItem(LorekeeperItemModel):
    """Model for a history Item"""

    item_table_object: schema.History

    def gather_related(self) -> None:
        """Gathers related table data"""

        with Session(self.engine) as session:
            self.history_actors = (
                session.execute(
                    sql.select(schema.HistoryActor).where(
                        schema.HistoryActor.history_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.history_actors = [
                {"actor": i.actor.first_name} for i in self.history_actors
            ]
            self.history_locations = (
                session.execute(
                    sql.select(schema.HistoryLocation).where(
                        schema.HistoryLocation.history_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.history_locations = [
                {"location": i.location.location_name} for i in self.history_locations
            ]
            self.history_factions = (
                session.execute(
                    sql.select(schema.HistoryFaction).where(
                        schema.HistoryFaction.history_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.history_factions = [
                {"faction": i.faction.faction_name} for i in self.history_factions
            ]
            self.history_objects = (
                session.execute(
                    sql.select(schema.HistoryObject).where(
                        schema.HistoryObject.history_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.history_objects = [
                {"object": i.object.object_name} for i in self.history_objects
            ]

            self.related = {
                "actors": self.history_actors,
                "locations": self.history_locations,
                "factions": self.history_factions,
                "objects": self.history_objects,
            }

    def update_database(self) -> None:
        """Updates database for self only, since others aren't needed"""

        self._update_self_database()


class HistoryTab(LorekeeperTabModel):
    """Model for the history tab"""

    table: dict[int, schema.History]
    tab_type = LorekeeperTab.HISTORY
    table_items: dict[int, HistoryItem] = {}

    def load_item(self, item_number: int) -> HistoryItem:
        """Creates HistoryItem

        Args:
            item_number: int of the item from the table

        Returns:
            HistoryItem of the request
        """

        self.table_items[item_number] = HistoryItem(self.table[item_number])

        return self.table_items[item_number]
    

class ObjectItem(LorekeeperItemModel):
    """Model for a single object_ item"""

    item_table_object: schema.Object_

    def gather_related(self) -> None:
        """Gathers Related table Data"""

        with Session(self.engine) as session:
            self.object_owners = (
                session.execute(
                    sql.select(schema.ObjectToOwner).where(
                        schema.ObjectToOwner.object_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.object_owners = [
                {"owner": i.actor.first_name} for i in self.object_owners
            ]
            self.object_history = (
                session.execute(
                    sql.select(schema.HistoryObject).where(
                        schema.HistoryObject.object_id == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.object_history = [
                {"history": i.history.event_name} for i in self.object_history
            ]

            self.related = {
                "owners": self.object_owners,
                "history": self.object_history,
            }

    def update_database(self) -> None:
        """Updates database for self only, since others aren't needed"""

        self._update_self_database()

class ObjectTab(LorekeeperTabModel):
    """Model for the object_ tab"""

    table: dict[int, schema.Object_]
    tab_type = LorekeeperTab.OBJECT_
    table_items: dict[int, ObjectItem] = {}

    def load_item(self, item_number: int) -> ObjectItem:
        """Creates ObjectItem

        Args:
            item_number: int of the item from the table

        Returns:
            ObjectItem of the request
        """

        self.table_items[item_number] = ObjectItem(self.table[item_number])

        return self.table_items[item_number]
    

class WorldDataItem(LorekeeperItemModel):
    """Model for a single item of world data"""

    item_table_object: schema.WorldData

    def gather_related(self) -> None:
        """Gathers data related to this world data"""

        with Session(self.engine) as session:
            self.world_data_history = (
                session.execute(
                    sql.select(schema.HistoryWorldData).where(
                        schema.HistoryWorldData.world_data_id
                        == self.item_table_object.id
                    )
                )
                .scalars()
                .all()
            )
            self.world_data_history = [
                {"history": i.history.event_name} for i in self.world_data_history
            ]

            self.related = {"history": self.world_data_history}
            
    def update_database(self) -> None:
        """Updates database for self only, since others aren't needed"""

        self._update_self_database()


class WorldDataTab(LorekeeperTabModel):
    """Model for the world data tab"""

    table: dict[int, schema.WorldData]
    tab_type = LorekeeperTab.WORLD_DATA
    table_items: dict[int, WorldDataItem] = {}

    def load_item(self, item_number: int) -> WorldDataItem:
        """Creates WorldDataItem

        Args:
            item_number: int of the item from the table

        Returns:
            WorldDataItem of the request
        """

        self.table_items[item_number] = WorldDataItem(self.table[item_number])

        return self.table_items[item_number]


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
