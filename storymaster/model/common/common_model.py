"""Holds common model classes"""

import dataclasses
from enum import Enum

from sqlalchemy import Engine, inspect
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

    actors: list[schema.Actor] | list[None]
    backgrounds: list[schema.Background] | list[None]
    classes: list[schema.Class_] | list[None]
    factions: list[schema.Faction] | list[None]
    history: list[schema.History] | list[None]
    locations: list[schema.Location] | list[None]
    objects: list[schema.Object_] | list[None]
    races: list[schema.Race] | list[None]
    sub_races: list[schema.SubRace] | list[None]
    world_datas: list[schema.WorldData] | list[None]

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

        if not return_list:
            return []

        return [item.as_dict() for item in return_list]


class BaseModel:
    """The base model class for Models"""

    engine: Engine
    user_id: int
    group_data: list[GroupData]
    
    # Mapping of table names to their corresponding ORM classes from the schema
    _table_to_class_map = {
        'user': schema.User,
        'project': schema.Project,
        'lorekeeper_group': schema.LorekeeperGroup,
        'project_to_group': schema.ProjectToGroup,
        'litography_node': schema.LitographyNode,
        'litography_notes': schema.LitographyNotes,
        'litography_plot': schema.LitographyPlot,
        'litography_plot_section': schema.LitographyPlotSection,
        'litography_node_to_plot_section': schema.LitographyNodeToPlotSection,
        'litography_arc': schema.LitographyArc,
        'class': schema.Class_,
        'background': schema.Background,
        'race': schema.Race,
        'sub_race': schema.SubRace,
        'actor': schema.Actor,
        'actor_a_on_b_relations': schema.ActorAOnBRelations,
        'skills': schema.Skills,
        'actor_to_skills': schema.ActorToSkills,
        'faction': schema.Faction,
        'faction_a_on_b_relations': schema.FactionAOnBRelations,
        'faction_members': schema.FactionMembers,
        'location_': schema.Location,
        'location_to_faction': schema.LocationToFaction,
        'location_dungeon': schema.LocationDungeon,
        'location_city': schema.LocationCity,
        'location_city_districts': schema.LocationCityDistricts,
        'residents': schema.Resident,
        'location_flora_fauna': schema.LocationFloraFauna,
        'history': schema.History,
        'history_actor': schema.HistoryActor,
        'history_location': schema.HistoryLocation,
        'history_faction': schema.HistoryFaction,
        'object_': schema.Object_,
        'history_object': schema.HistoryObject,
        'object_to_owner': schema.ObjectToOwner,
        'world_data': schema.WorldData,
        'history_world_data': schema.HistoryWorldData,
        'litography_note_to_actor': schema.LitographyNoteToActor,
        'litography_note_to_background': schema.LitographyNoteToBackground,
        'litography_note_to_faction': schema.LitographyNoteToFaction,
        'litography_note_to_location': schema.LitographyNoteToLocation,
        'litography_note_to_history': schema.LitographyNoteToHistory,
        'litography_note_to_object': schema.LitographyNoteToObject,
        'litography_note_to_world_data': schema.LitographyNoteToWorldData,
        'arc_to_node': schema.ArcToNode,
        'arc_to_actor': schema.ArcToActor,
    }


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
    
    def get_all_table_names(self) -> list[str]:
        """
        Inspects the database and returns a list of all table names.
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_data(self, table_name: str) -> tuple[list[str], list[tuple]]:
        """
        Fetches all data from a specific table using the ORM.

        Args:
            table_name: The name of the table to query.

        Returns:
            A tuple containing:
            - A list of column headers (strings).
            - A list of rows, where each row is a tuple of its values.
        """
        orm_class = self._table_to_class_map.get(table_name)
        
        if not orm_class:
            print(f"Warning: No ORM class found for table '{table_name}'")
            return [], []

        # Get headers directly from the ORM class definition
        headers = [c.name for c in orm_class.__table__.columns]
        
        data = []
        with Session(self.engine) as session:
            # Query the database using the ORM class
            results = session.query(orm_class).all()
            
            # Convert each ORM object into a tuple of its values
            for row_object in results:
                row_data = tuple(getattr(row_object, header) for header in headers)
                data.append(row_data)
            
        return headers, data

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
                actors = list(
                    session.execute(
                        common_queries.get_lorekeeper_actors_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                backgrounds = list(
                    session.execute(
                        common_queries.get_lorekeeper_backgrounds_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                classes = list(
                    session.execute(
                        common_queries.get_lorekeeper_classes_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                factions = list(
                    session.execute(
                        common_queries.get_lorekeeper_factions_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                history = list(
                    session.execute(
                        common_queries.get_lorekeeper_history_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                locations = list(
                    session.execute(
                        common_queries.get_lorekeeper_locations_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                objects = list(
                    session.execute(
                        common_queries.get_lorekeeper_objects_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                races = list(
                    session.execute(
                        common_queries.get_lorekeeper_races_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                sub_races = list(
                    session.execute(
                        common_queries.get_lorekeeper_sub_races_from_group(group)
                    )
                    .scalars()
                    .all()
                )
                world_datas = list(
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
        

    # Add to your BaseModel class in common_model.py

    def get_foreign_key_info(self, table_name: str) -> dict[str, tuple[str, str]]:
        """Gets foreign key relationships for a given table."""
        inspector = inspect(self.engine)
        fks = inspector.get_foreign_keys(table_name)
        fk_info = {}
        for fk in fks:
            local_column = fk['constrained_columns'][0]
            referred_table = fk['referred_table']
            referred_column = fk['referred_columns'][0]
            fk_info[local_column] = (referred_table, referred_column)
        return fk_info

    def get_row_by_id(self, table_name: str, row_id: int) -> dict | None:
        """Fetches a single row from a table by its primary key."""
        orm_class = self._table_to_class_map.get(table_name)
        if not orm_class:
            return None

        with Session(self.engine) as session:
            # This assumes the primary key column is named 'id'.
            result = session.query(orm_class).filter_by(id=row_id).first()

        return result.as_dict() if result else None
