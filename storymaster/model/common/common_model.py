"""Holds common model classes"""

import dataclasses
from enum import Enum

from sqlalchemy import (
    Column,
    Engine,
    Float,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    inspect,
)
from sqlalchemy.orm import Session, joinedload

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
        "user": schema.User,
        "storyline": schema.Storyline,
        "setting": schema.Setting,
        "storyline_to_setting": schema.StorylineToSetting,
        "litography_node": schema.LitographyNode,
        "litography_notes": schema.LitographyNotes,
        "litography_plot": schema.LitographyPlot,
        "litography_plot_section": schema.LitographyPlotSection,
        "litography_node_to_plot_section": schema.LitographyNodeToPlotSection,
        "litography_arc": schema.LitographyArc,
        "class": schema.Class_,
        "background": schema.Background,
        "race": schema.Race,
        "sub_race": schema.SubRace,
        "actor": schema.Actor,
        "actor_a_on_b_relations": schema.ActorAOnBRelations,
        "skills": schema.Skills,
        "actor_to_skills": schema.ActorToSkills,
        "faction": schema.Faction,
        "faction_a_on_b_relations": schema.FactionAOnBRelations,
        "faction_members": schema.FactionMembers,
        "location_": schema.Location,
        "location_to_faction": schema.LocationToFaction,
        "location_dungeon": schema.LocationDungeon,
        "location_city": schema.LocationCity,
        "location_city_districts": schema.LocationCityDistricts,
        "residents": schema.Resident,
        "location_flora_fauna": schema.LocationFloraFauna,
        "history": schema.History,
        "history_actor": schema.HistoryActor,
        "history_location": schema.HistoryLocation,
        "history_faction": schema.HistoryFaction,
        "object_": schema.Object_,
        "history_object": schema.HistoryObject,
        "object_to_owner": schema.ObjectToOwner,
        "world_data": schema.WorldData,
        "history_world_data": schema.HistoryWorldData,
        "litography_note_to_actor": schema.LitographyNoteToActor,
        "litography_note_to_background": schema.LitographyNoteToBackground,
        "litography_note_to_faction": schema.LitographyNoteToFaction,
        "litography_note_to_location": schema.LitographyNoteToLocation,
        "litography_note_to_history": schema.LitographyNoteToHistory,
        "litography_note_to_object": schema.LitographyNoteToObject,
        "litography_note_to_world_data": schema.LitographyNoteToWorldData,
        "litography_note_to_class": schema.LitographyNoteToClass,
        "litography_note_to_race": schema.LitographyNoteToRace,
        "litography_note_to_sub_race": schema.LitographyNoteToSubRace,
        "litography_note_to_skills": schema.LitographyNoteToSkills,
        "arc_to_node": schema.ArcToNode,
        "arc_to_actor": schema.ArcToActor,
        "alignment": schema.Alignment,
        "stat": schema.Stat,
        "actor_to_race": schema.ActorToRace,
        "actor_to_class": schema.ActorToClass,
        "actor_to_stat": schema.ActorToStat,
    }

    def __init__(self, user_id: int):
        self.engine = self.generate_connection()
        self.user_id = user_id

    def generate_connection(self) -> Engine:
        """Generates the connection used to test"""
        return base_connection.engine

    def load_user_storylines(self) -> list[int]:
        """Loads all the storyline_ids for a user"""
        with Session(self.engine) as session:
            storyline_id_list = session.execute(
                common_queries.get_storyline_ids_for_user(self.user_id)
            ).all()

        return [storyline.id for storyline in storyline_id_list]

    # --- Litographer Methods ---

    def get_litography_nodes(self, storyline_id: int) -> list[schema.LitographyNode]:
        """Fetches all litography nodes for a given storyline."""
        with Session(self.engine) as session:
            nodes = (
                session.query(schema.LitographyNode)
                .options(joinedload(schema.LitographyNode.storyline))
                .filter_by(storyline_id=storyline_id)
                .all()
            )
        return nodes

    # --- Lorekeeper Methods ---

    def get_all_table_names(self) -> list[str]:
        """
        Inspects the database and returns a list of user-visible table names.
        Filters out system tables and junction tables that shouldn't be directly edited.
        """
        inspector = inspect(self.engine)
        all_tables = inspector.get_table_names()

        # Tables that should be hidden from the Lorekeeper UI
        hidden_tables = {
            "user",
            "storyline",
            "setting",
            "storyline_to_setting",
            "litography_node",
            "litography_notes",
            "litography_plot",
            "litography_plot_section",
            "litography_node_to_plot_section",
            "litography_arc",
            "litography_note_to_actor",
            "litography_note_to_background",
            "litography_note_to_class",
            "litography_note_to_faction",
            "litography_note_to_history",
            "litography_note_to_location",
            "litography_note_to_object",
            "litography_note_to_race",
            "litography_note_to_sub_race",
            "litography_note_to_world_data",
            "actor_a_on_b_relations",
            "faction_a_on_b_relations",
            "history_actor",
            "history_location",
            "history_faction",
            "history_object",
            "history_world_data",
            "litography_note_to_skills",
            "arc_to_actor",
            "arc_to_node",
            "actor_to_race",
            "actor_to_class",
            "actor_to_stat",
        }

        return [table for table in all_tables if table not in hidden_tables]

    def get_table_data(
        self,
        table_name: str,
        storyline_id: int | None = None,
        setting_id: int | None = None,
    ) -> tuple[list[str], list[tuple]]:
        """
        Fetches all data from a specific table, optionally filtered by storyline_id or setting_id.
        If both are provided, setting_id takes precedence.
        """
        orm_class = self._table_to_class_map.get(table_name)

        if not orm_class:
            return [], []

        headers = [c.name for c in orm_class.__table__.columns]

        with Session(self.engine) as session:
            query = session.query(orm_class)

            # Filter by setting_id if the table has that column
            if hasattr(orm_class, "setting_id"):
                if setting_id:
                    # Direct setting_id filtering takes precedence
                    query = query.filter_by(setting_id=setting_id)
                elif storyline_id:
                    # Fall back to deriving setting_id from storyline_id
                    storyline_setting_link = (
                        session.query(schema.StorylineToSetting)
                        .filter_by(storyline_id=storyline_id)
                        .first()
                    )
                    if storyline_setting_link:
                        query = query.filter_by(
                            setting_id=storyline_setting_link.setting_id
                        )

            results = query.all()

            data = []
            for row_object in results:
                row_data = tuple(getattr(row_object, header) for header in headers)
                data.append(row_data)

        return headers, data

    def get_foreign_key_info(self, table_name: str) -> dict[str, tuple[str, str]]:
        """Gets foreign key relationships for a given table."""
        inspector = inspect(self.engine)
        fks = inspector.get_foreign_keys(table_name)
        fk_info = {}
        for fk in fks:
            local_column = fk["constrained_columns"][0]
            referred_table = fk["referred_table"]
            referred_column = fk["referred_columns"][0]
            fk_info[local_column] = (referred_table, referred_column)
        return fk_info

    def get_column_types(self, table_name: str) -> dict[str, str]:
        """Gets column types for a given table."""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)

        column_types = {}
        for column in columns:
            column_name = column["name"]
            column_type = str(column["type"])

            # Normalize type names to standard categories
            if "INTEGER" in column_type.upper() or "INT" in column_type.upper():
                column_types[column_name] = "integer"
            elif (
                "FLOAT" in column_type.upper()
                or "REAL" in column_type.upper()
                or "DECIMAL" in column_type.upper()
                or "NUMERIC" in column_type.upper()
            ):
                column_types[column_name] = "float"
            elif "BOOLEAN" in column_type.upper() or "BOOL" in column_type.upper():
                column_types[column_name] = "boolean"
            elif "TEXT" in column_type.upper() or "CLOB" in column_type.upper():
                column_types[column_name] = "text"
            elif (
                "VARCHAR" in column_type.upper()
                or "CHAR" in column_type.upper()
                or "STRING" in column_type.upper()
            ):
                column_types[column_name] = "string"
            else:
                # Default to string for unknown types
                column_types[column_name] = "string"

        return column_types

    def get_row_by_id(self, table_name: str, row_id: int) -> dict | None:
        """Fetches a single row from a table by its primary key."""
        orm_class = self._table_to_class_map.get(table_name)
        if not orm_class:
            return None

        with Session(self.engine) as session:
            result = session.query(orm_class).filter_by(id=row_id).first()

        return result.as_dict() if result else None

    def get_all_rows_as_dicts(
        self,
        table_name: str,
        storyline_id: int | None = None,
        setting_id: int | None = None,
    ) -> list[dict]:
        """Fetches all rows from a table as dicts, optionally filtered by storyline or setting."""
        orm_class = self._table_to_class_map.get(table_name)
        if not orm_class:
            return []

        with Session(self.engine) as session:
            query = session.query(orm_class)

            # Filter by setting_id if the table has that column
            if hasattr(orm_class, "setting_id"):
                if setting_id:
                    # Direct setting_id filtering takes precedence
                    query = query.filter_by(setting_id=setting_id)
                elif storyline_id:
                    # Fall back to deriving setting_id from storyline_id
                    storyline_setting_link = (
                        session.query(schema.StorylineToSetting)
                        .filter_by(storyline_id=storyline_id)
                        .first()
                    )
                    if storyline_setting_link:
                        query = query.filter_by(
                            setting_id=storyline_setting_link.setting_id
                        )

            results = query.all()

        return [row.as_dict() for row in results]

    def get_all_storylines(self) -> list[schema.Storyline]:
        """Fetches all storylines from the database for the current user."""
        with Session(self.engine) as session:
            storylines = (
                session.query(schema.Storyline).filter_by(user_id=self.user_id).all()
            )
            return storylines

    def get_all_settings(self) -> list[schema.Setting]:
        """Fetches all settings from the database for the current user."""
        with Session(self.engine) as session:
            settings = (
                session.query(schema.Setting).filter_by(user_id=self.user_id).all()
            )
            return settings

    def get_all_users(self) -> list[schema.User]:
        """Fetches all users from the database."""
        with Session(self.engine) as session:
            users = session.query(schema.User).all()
            return users

    def create_user(self, username: str) -> schema.User:
        """Creates a new user in the database."""
        with Session(self.engine) as session:
            new_user = schema.User(username=username)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user

    def delete_user(self, user_id: int):
        """Deletes a user and all related data from the database."""
        with Session(self.engine) as session:
            # Get the user
            user = session.query(schema.User).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            # Delete all storylines for this user (cascade will handle related data)
            storylines = (
                session.query(schema.Storyline).filter_by(user_id=user_id).all()
            )
            for storyline in storylines:
                session.delete(storyline)

            # Delete all settings for this user (cascade will handle related data)
            settings = session.query(schema.Setting).filter_by(user_id=user_id).all()
            for setting in settings:
                session.delete(setting)

            # Delete the user
            session.delete(user)
            session.commit()

    def user_has_data(self, user_id: int) -> bool:
        """Checks if a user has any storylines or settings."""
        with Session(self.engine) as session:
            storyline_count = (
                session.query(schema.Storyline).filter_by(user_id=user_id).count()
            )
            setting_count = (
                session.query(schema.Setting).filter_by(user_id=user_id).count()
            )
            return storyline_count > 0 or setting_count > 0

    def get_user_by_id(self, user_id: int) -> schema.User | None:
        """Gets a user by ID."""
        with Session(self.engine) as session:
            return session.query(schema.User).filter_by(id=user_id).first()

    def switch_user(self, new_user_id: int) -> bool:
        """
        Switches the current user context to a different user.
        Returns True if successful, False if user doesn't exist.
        """
        # Verify the user exists
        user = self.get_user_by_id(new_user_id)
        if user:
            self.user_id = new_user_id
            return True
        return False

    def get_current_user(self) -> schema.User | None:
        """Gets the current user object."""
        return self.get_user_by_id(self.user_id)

    def update_row(self, table_name: str, data_dict: dict):
        """
        Updates a single row in the database.
        """
        orm_class = self._table_to_class_map.get(table_name)
        if not orm_class:
            raise ValueError(f"No ORM class found for table '{table_name}'")

        pk_value = data_dict.get("id")
        if pk_value is None:
            raise ValueError("Data for update must include an 'id' field.")

        with Session(self.engine) as session:
            item_to_update = (
                session.query(orm_class).filter_by(id=int(pk_value)).first()
            )

            if not item_to_update:
                raise ValueError(f"No item found in '{table_name}' with id {pk_value}")

            for key, value in data_dict.items():
                if key == "id":
                    continue

                if value == "" and key in orm_class.__table__.columns:
                    col_type = orm_class.__table__.columns[key].type
                    if isinstance(col_type, (Integer, Float)):
                        value = None

                setattr(item_to_update, key, value)

            session.commit()
            print(f"Successfully updated row {pk_value} in {table_name}")

    def add_row(
        self,
        table_name: str,
        data_dict: dict,
        storyline_id: int | None = None,
        setting_id: int | None = None,
    ):
        """
        Adds a new row to the database, associating it with the correct setting.
        If both storyline_id and setting_id are provided, setting_id takes precedence.
        """
        orm_class = self._table_to_class_map.get(table_name)
        if not orm_class:
            raise ValueError(f"No ORM class found for table '{table_name}'")

        if "id" in data_dict:
            del data_dict["id"]

        with Session(self.engine) as session:
            # If the table has a setting_id column, set it appropriately
            if hasattr(orm_class, "setting_id"):
                if setting_id:
                    # Direct setting_id takes precedence
                    data_dict["setting_id"] = setting_id
                elif storyline_id:
                    # Fall back to deriving setting_id from storyline_id
                    storyline_setting_link = (
                        session.query(schema.StorylineToSetting)
                        .filter_by(storyline_id=storyline_id)
                        .first()
                    )
                    if not storyline_setting_link:
                        raise ValueError(
                            f"No Setting found for Storyline ID {storyline_id}"
                        )
                    data_dict["setting_id"] = storyline_setting_link.setting_id

            # Convert empty strings to None for numeric types
            for key, value in data_dict.items():
                if value == "" and key in orm_class.__table__.columns:
                    col_type = orm_class.__table__.columns[key].type
                    if isinstance(col_type, (Integer, Float)):
                        data_dict[key] = None

            new_item = orm_class(**data_dict)
            session.add(new_item)
            session.commit()
            print(f"Successfully added new row to {table_name}")

    def load_user_data(self) -> list[GroupData]:
        """Loads all data attributed to a single user"""
        setting_return: list[GroupData] = []
        with Session(self.engine) as session:
            setting_list = (
                session.execute(common_queries.get_setting_ids_for_storyline(1))
                .scalars()
                .all()
            )
            for setting in setting_list:
                actors = list(
                    session.execute(
                        common_queries.get_lorekeeper_actors_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                backgrounds = list(
                    session.execute(
                        common_queries.get_lorekeeper_backgrounds_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                classes = list(
                    session.execute(
                        common_queries.get_lorekeeper_classes_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                factions = list(
                    session.execute(
                        common_queries.get_lorekeeper_factions_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                history = list(
                    session.execute(
                        common_queries.get_lorekeeper_history_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                locations = list(
                    session.execute(
                        common_queries.get_lorekeeper_locations_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                objects = list(
                    session.execute(
                        common_queries.get_lorekeeper_objects_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                races = list(
                    session.execute(
                        common_queries.get_lorekeeper_races_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                sub_races = list(
                    session.execute(
                        common_queries.get_lorekeeper_sub_races_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                world_datas = list(
                    session.execute(
                        common_queries.get_lorekeeper_world_data_from_setting(setting)
                    )
                    .scalars()
                    .all()
                )
                setting_return.append(
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
            self.group_data = setting_return
            return setting_return

    # Character Arc Management Methods
    def get_character_arcs(
        self, storyline_id: int | None = None
    ) -> list[schema.LitographyArc]:
        """Get all character arcs for a storyline"""
        with Session(self.engine) as session:
            query = session.query(schema.LitographyArc)

            if storyline_id:
                query = query.filter(schema.LitographyArc.storyline_id == storyline_id)

            return query.options(
                joinedload(schema.LitographyArc.arc_type),
                joinedload(schema.LitographyArc.actors).joinedload(
                    schema.ArcToActor.actor
                ),
            ).all()

    # Storyline-to-Setting Management Methods
    def get_settings_for_storyline(self, storyline_id: int) -> list[schema.Setting]:
        """Get all settings linked to a storyline"""
        with Session(self.engine) as session:
            storyline = (
                session.query(schema.Storyline)
                .filter(schema.Storyline.id == storyline_id)
                .options(
                    joinedload(schema.Storyline.storyline_to_settings).joinedload(
                        schema.StorylineToSetting.setting
                    )
                )
                .first()
            )

            if storyline:
                return [sts.setting for sts in storyline.storyline_to_settings]
            return []

    def get_storylines_for_setting(self, setting_id: int) -> list[schema.Storyline]:
        """Get all storylines linked to a setting"""
        with Session(self.engine) as session:
            setting = (
                session.query(schema.Setting)
                .filter(schema.Setting.id == setting_id)
                .options(
                    joinedload(schema.Setting.storyline_to_setting).joinedload(
                        schema.StorylineToSetting.storyline
                    )
                )
                .first()
            )

            if setting:
                return [sts.storyline for sts in setting.storyline_to_setting]
            return []

    def link_storyline_to_setting(self, storyline_id: int, setting_id: int) -> bool:
        """Link a storyline to a setting"""
        with Session(self.engine) as session:
            # Check if link already exists
            existing = (
                session.query(schema.StorylineToSetting)
                .filter(
                    schema.StorylineToSetting.storyline_id == storyline_id,
                    schema.StorylineToSetting.setting_id == setting_id,
                )
                .first()
            )

            if existing:
                return False  # Link already exists

            # Create new link
            link = schema.StorylineToSetting(
                storyline_id=storyline_id, setting_id=setting_id
            )
            session.add(link)
            session.commit()
            return True

    def unlink_storyline_from_setting(self, storyline_id: int, setting_id: int) -> bool:
        """Unlink a storyline from a setting"""
        with Session(self.engine) as session:
            link = (
                session.query(schema.StorylineToSetting)
                .filter(
                    schema.StorylineToSetting.storyline_id == storyline_id,
                    schema.StorylineToSetting.setting_id == setting_id,
                )
                .first()
            )

            if link:
                session.delete(link)
                session.commit()
                return True
            return False  # Link didn't exist

    def get_available_settings_for_storyline(
        self, storyline_id: int
    ) -> list[schema.Setting]:
        """Get all settings that could be linked to a storyline (not already linked)"""
        with Session(self.engine) as session:
            # Get all settings for this user
            all_settings = (
                session.query(schema.Setting)
                .filter(schema.Setting.user_id == self.user_id)
                .all()
            )

            # Get currently linked settings
            linked_settings = self.get_settings_for_storyline(storyline_id)
            linked_setting_ids = {setting.id for setting in linked_settings}

            # Return settings not already linked
            return [
                setting
                for setting in all_settings
                if setting.id not in linked_setting_ids
            ]

    def get_available_storylines_for_setting(
        self, setting_id: int
    ) -> list[schema.Storyline]:
        """Get all storylines that could be linked to a setting (not already linked)"""
        with Session(self.engine) as session:
            # Get all storylines for this user
            all_storylines = (
                session.query(schema.Storyline)
                .filter(schema.Storyline.user_id == self.user_id)
                .all()
            )

            # Get currently linked storylines
            linked_storylines = self.get_storylines_for_setting(setting_id)
            linked_storyline_ids = {storyline.id for storyline in linked_storylines}

            # Return storylines not already linked
            return [
                storyline
                for storyline in all_storylines
                if storyline.id not in linked_storyline_ids
            ]

    def get_character_arc(self, arc_id: int) -> schema.LitographyArc:
        """Get a specific character arc by ID"""
        with Session(self.engine) as session:
            arc = (
                session.query(schema.LitographyArc)
                .options(
                    joinedload(schema.LitographyArc.arc_type),
                    joinedload(schema.LitographyArc.actors).joinedload(
                        schema.ArcToActor.actor
                    ),
                )
                .filter(schema.LitographyArc.id == arc_id)
                .first()
            )

            if not arc:
                raise ValueError(f"Character arc with ID {arc_id} not found")
            return arc

    def get_arc_points(self, arc_id: int) -> list[schema.ArcPoint]:
        """Get all arc points for a character arc"""
        with Session(self.engine) as session:
            return (
                session.query(schema.ArcPoint)
                .options(joinedload(schema.ArcPoint.node))
                .filter(schema.ArcPoint.arc_id == arc_id)
                .order_by(schema.ArcPoint.order_index)
                .all()
            )

    def get_arc_types(self, setting_id: int | None = None) -> list[schema.ArcType]:
        """Get all arc types for a setting"""
        with Session(self.engine) as session:
            query = session.query(schema.ArcType)

            if setting_id:
                query = query.filter(schema.ArcType.setting_id == setting_id)

            return query.all()

    def create_character_arc(
        self,
        title: str,
        description: str,
        arc_type_id: int,
        storyline_id: int,
        actor_ids: list[int] | None = None,
    ) -> schema.LitographyArc:
        """Create a new character arc"""
        with Session(self.engine) as session:
            # Create the arc
            arc = schema.LitographyArc(
                title=title,
                description=description,
                arc_type_id=arc_type_id,
                storyline_id=storyline_id,
            )
            session.add(arc)
            session.flush()  # Get the ID

            # Link to actors if provided
            if actor_ids:
                for actor_id in actor_ids:
                    arc_to_actor = schema.ArcToActor(arc_id=arc.id, actor_id=actor_id)
                    session.add(arc_to_actor)

            session.commit()
            return arc

    def update_character_arc(
        self,
        arc_id: int,
        title: str | None = None,
        description: str | None = None,
        arc_type_id: int | None = None,
        actor_ids: list[int] | None = None,
    ) -> schema.LitographyArc:
        """Update an existing character arc"""
        with Session(self.engine) as session:
            arc = (
                session.query(schema.LitographyArc)
                .filter(schema.LitographyArc.id == arc_id)
                .first()
            )

            if not arc:
                raise ValueError(f"Character arc with ID {arc_id} not found")

            if title is not None:
                arc.title = title
            if description is not None:
                arc.description = description
            if arc_type_id is not None:
                arc.arc_type_id = arc_type_id

            # Update actor links if provided
            if actor_ids is not None:
                # Remove existing links
                session.query(schema.ArcToActor).filter(
                    schema.ArcToActor.arc_id == arc_id
                ).delete()

                # Add new links
                for actor_id in actor_ids:
                    arc_to_actor = schema.ArcToActor(arc_id=arc_id, actor_id=actor_id)
                    session.add(arc_to_actor)

            session.commit()
            return arc

    def delete_character_arc(self, arc_id: int):
        """Delete a character arc and all its arc points"""
        with Session(self.engine) as session:
            # Delete arc points first
            session.query(schema.ArcPoint).filter(
                schema.ArcPoint.arc_id == arc_id
            ).delete()

            # Delete actor links
            session.query(schema.ArcToActor).filter(
                schema.ArcToActor.arc_id == arc_id
            ).delete()

            # Delete the arc
            session.query(schema.LitographyArc).filter(
                schema.LitographyArc.id == arc_id
            ).delete()

            session.commit()

    def create_arc_point(
        self,
        arc_id: int,
        title: str,
        order_index: int,
        description: str | None = None,
        emotional_state: str | None = None,
        character_relationships: str | None = None,
        goals: str | None = None,
        internal_conflict: str | None = None,
        node_id: int | None = None,
    ) -> schema.ArcPoint:
        """Create a new arc point"""
        with Session(self.engine) as session:
            arc_point = schema.ArcPoint(
                arc_id=arc_id,
                title=title,
                order_index=order_index,
                description=description,
                emotional_state=emotional_state,
                character_relationships=character_relationships,
                goals=goals,
                internal_conflict=internal_conflict,
                node_id=node_id,
            )
            session.add(arc_point)
            session.commit()
            return arc_point

    def update_arc_point(self, arc_point_id: int, **kwargs) -> schema.ArcPoint:
        """Update an existing arc point"""
        with Session(self.engine) as session:
            arc_point = (
                session.query(schema.ArcPoint)
                .filter(schema.ArcPoint.id == arc_point_id)
                .first()
            )

            if not arc_point:
                raise ValueError(f"Arc point with ID {arc_point_id} not found")

            for key, value in kwargs.items():
                if hasattr(arc_point, key):
                    setattr(arc_point, key, value)

            session.commit()
            return arc_point

    def delete_arc_point(self, arc_point_id: int):
        """Delete an arc point"""
        with Session(self.engine) as session:
            session.query(schema.ArcPoint).filter(
                schema.ArcPoint.id == arc_point_id
            ).delete()
            session.commit()

    def create_arc_type(
        self, name: str, description: str, setting_id: int
    ) -> schema.ArcType:
        """Create a new arc type"""
        with Session(self.engine) as session:
            arc_type = schema.ArcType(
                name=name, description=description, setting_id=setting_id
            )
            session.add(arc_type)
            session.commit()
            return arc_type

    def get_arc_type(self, arc_type_id: int) -> schema.ArcType:
        """Get a specific arc type by ID"""
        with Session(self.engine) as session:
            arc_type = (
                session.query(schema.ArcType)
                .filter(schema.ArcType.id == arc_type_id)
                .first()
            )

            if not arc_type:
                raise ValueError(f"Arc type with ID {arc_type_id} not found")
            return arc_type

    def update_arc_type(
        self, arc_type_id: int, name: str | None = None, description: str | None = None
    ) -> schema.ArcType:
        """Update an existing arc type"""
        with Session(self.engine) as session:
            arc_type = (
                session.query(schema.ArcType)
                .filter(schema.ArcType.id == arc_type_id)
                .first()
            )

            if not arc_type:
                raise ValueError(f"Arc type with ID {arc_type_id} not found")

            if name is not None:
                arc_type.name = name
            if description is not None:
                arc_type.description = description

            session.commit()
            return arc_type

    def delete_arc_type(self, arc_type_id: int):
        """Delete an arc type and all character arcs using it"""
        with Session(self.engine) as session:
            # First delete all arc points for arcs using this type
            session.query(schema.ArcPoint).filter(
                schema.ArcPoint.arc_id.in_(
                    session.query(schema.LitographyArc.id).filter(
                        schema.LitographyArc.arc_type_id == arc_type_id
                    )
                )
            ).delete(synchronize_session=False)

            # Delete actor links for arcs using this type
            session.query(schema.ArcToActor).filter(
                schema.ArcToActor.arc_id.in_(
                    session.query(schema.LitographyArc.id).filter(
                        schema.LitographyArc.arc_type_id == arc_type_id
                    )
                )
            ).delete(synchronize_session=False)

            # Delete character arcs using this type
            session.query(schema.LitographyArc).filter(
                schema.LitographyArc.arc_type_id == arc_type_id
            ).delete()

            # Delete the arc type
            session.query(schema.ArcType).filter(
                schema.ArcType.id == arc_type_id
            ).delete()

            session.commit()

    def get_nodes_for_storyline(self, storyline_id: int) -> list[schema.LitographyNode]:
        """Get all nodes for a storyline"""
        with Session(self.engine) as session:
            return (
                session.query(schema.LitographyNode)
                .options(joinedload(schema.LitographyNode.storyline))
                .filter(schema.LitographyNode.storyline_id == storyline_id)
                .order_by(schema.LitographyNode.id)
                .all()
            )

    def get_actors_for_setting(self, setting_id: int) -> list[schema.Actor]:
        """Get all actors for a setting"""
        with Session(self.engine) as session:
            return (
                session.query(schema.Actor)
                .options(
                    joinedload(schema.Actor.setting),
                    joinedload(schema.Actor.background),
                    joinedload(schema.Actor.alignment)
                )
                .filter(schema.Actor.setting_id == setting_id)
                .order_by(schema.Actor.first_name, schema.Actor.last_name)
                .all()
            )
