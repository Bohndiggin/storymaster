"""Contains queries that are needed frequently"""

from sqlalchemy import sql

from storio.model.database import schema


def get_project_ids_for_user(user_id: int) -> sql.Executable:
    """Gets all the project ids for a specific user

    Args:
        user_id: the id of the user in question

    Returns:
        a sql executable
    """

    return sql.select(schema.Project.id).where(schema.Project.user_id == user_id)


def get_group_ids_for_project(project_id: int) -> sql.Executable:
    """Gets all group ids for a project

    Args:
        project_id: the id of the targeted project

    Returns:
        sql executable
    """


def get_lorekeeper_all_from_group(group_id: int) -> sql.Executable:
    """Gets a lorekeeper db from a group_id

    Args:
        group_id: the id of the group of the lorekeeper data

    """

    return sql.select(
        schema.Actor,
        schema.Faction,
        schema.Location,
        schema.History,
        schema.Object_,
        schema.WorldData,
    ).where(
        schema.Actor.group_id == group_id,
        schema.Faction.group_id == group_id,
        schema.Location.group_id == group_id,
        schema.History.group_id == group_id,
        schema.Object_.group_id == group_id,
        schema.WorldData.group_id == group_id,
    )


def get_lorekeeper_classes_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper class from a group id

    Args:
        group_id: the id of the group related to the actors
    """

    return sql.select(schema.Class_).where(schema.Class_.group_id == group_id)


def get_lorekeeper_backgrounds_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper background from a group id

    Args:
        group_id: the id of the group related to the actors
    """

    return sql.select(schema.Background).where(schema.Background.group_id == group_id)


def get_lorekeeper_races_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper race from a group id

    Args:
        group_id: the id of the group related to the actors
    """

    return sql.select(schema.Race).where(schema.Race.group_id == group_id)


def get_lorekeeper_sub_races_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper sub_race from a group id

    Args:
        group_id: the id of the group related to the actors
    """

    return sql.select(schema.SubRace).where(schema.SubRace.group_id == group_id)


def get_lorekeeper_actors_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper actors from a group id

    Args:
        group_id: the id of the group related to the actors
    """

    return sql.select(schema.Actor).where(schema.Actor.group_id == group_id)


def get_lorekeeper_factions_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper factions from a group id

    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_locations_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper locations from a group id

    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_history_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper history from a group id

    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_objects_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper objects from a group id

    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_world_data_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper actors from a group id

    Args:
        group_id: the id of the group related to the actors
    """
