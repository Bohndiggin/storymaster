"""Contains queries that are needed frequently"""

from sqlalchemy import sql

from storymaster.model.database import schema


def get_storyline_ids_for_user(user_id: int) -> sql.Executable:
    """Gets all the storyline ids for a specific user

    Args:
        user_id: the id of the user in question

    Returns:
        a sql executable
    """

    return sql.select(schema.Storyline.id).where(schema.Storyline.user_id == user_id)


def get_setting_ids_for_storyline(storyline_id: int) -> sql.Executable:
    """Gets all setting ids for a storyline

    Args:
        storyline_id: the id of the targeted storyline

    Returns:
        sql executable
    """

    return (
        sql.select(schema.Setting.id)
        .join(schema.StorylineToSetting)
        .where(schema.StorylineToSetting.storyline_id == storyline_id)
    )


def get_lorekeeper_classes_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper class from a group id

    Args:
        setting_id: the id of the setting related to the classes

    Returns:
        sql executable
    """

    return sql.select(schema.Class_).where(schema.Class_.setting_id == setting_id)


def get_lorekeeper_backgrounds_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper background from a group id

    Args:
        setting_id: the id of the setting related to the backgrounds

    Returns:
        sql executable
    """

    return sql.select(schema.Background).where(
        schema.Background.setting_id == setting_id
    )


def get_lorekeeper_races_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper race from a group id

    Args:
        setting_id: the id of the setting related to the races

    Returns:
        sql executable
    """

    return sql.select(schema.Race).where(schema.Race.setting_id == setting_id)


def get_lorekeeper_sub_races_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper sub_race from a group id

    Args:
        setting_id: the id of the setting related to the sub_races

    Returns:
        sql executable
    """

    return sql.select(schema.SubRace).where(schema.SubRace.setting_id == setting_id)


def get_lorekeeper_actors_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper actors from a group id

    Args:
        setting_id: the id of the setting related to the actors

    Returns:
        sql executable
    """

    return sql.select(schema.Actor).where(schema.Actor.setting_id == setting_id)


def get_single_actor(actor: schema.Actor) -> sql.Executable:
    """Gets all related data for a single actor

    Args:
        actor: the actor in question

    Returns:
        sql executable
    """

    return sql.select(schema.ActorAOnBRelations).where(
        schema.ActorAOnBRelations.actor_a == actor
    )


def get_lorekeeper_factions_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper factions from a group id

    Args:
        setting_id: the id of the setting related to the factions

    Returns:
        sql executable
    """

    return sql.select(schema.Faction).where(schema.Faction.setting_id == setting_id)


def get_lorekeeper_locations_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper locations from a group id

    Args:
        setting_id: the id of the setting related to the locations

    Returns:
        sql executable
    """
    return sql.select(schema.Location).where(schema.Location.setting_id == setting_id)


def get_lorekeeper_history_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper history from a group id

    Args:
        setting_id: the id of the setting related to the history

    Returns:
        sql executable
    """
    return sql.select(schema.History).where(schema.History.setting_id == setting_id)


def get_lorekeeper_objects_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper objects from a group id

    Args:
        setting_id: the id of the setting related to the objects

    Returns:
        sql executable
    """
    return sql.select(schema.Object_).where(schema.Object_.setting_id == setting_id)


def get_lorekeeper_world_data_from_setting(setting_id: int) -> sql.Executable:
    """Gets lorekeeper world data from a group id

    Args:
        setting_id: the id of the setting related to the world data

    Returns:
        sql executable
    """
    return sql.select(schema.WorldData).where(schema.WorldData.setting_id == setting_id)
