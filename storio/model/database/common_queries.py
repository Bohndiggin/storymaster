"""Contains queries that are needed frequently"""

from sqlalchemy.orm import Session
from sqlalchemy import sql
from storio.model.database import schema


def get_lorekeeper_all_from_group(group_id: int) -> sql.Executable:
    """Gets a lorekeeper db from a group_id
    
    Args:
        group_id: the id of the group of the lorekeeper data
    
    """

    return sql.select(
        schema.Actor,
        schema.ActorAOnBRelations,
        schema.ActorToSkills,
        schema.Background,
        schema.Class_,
        schema.Faction,
        schema.FactionAOnBRelations,
        schema.FactionMembers,
        schema.History
    )

def get_lorekeeper_classes_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper class from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_backgrounds_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper background from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_races_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper race from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_sub_races_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper sub_race from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """


def get_lorekeeper_actors_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper actors from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """


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


def get_lorekeeper_world_data_from_group(group_id: int) -> sql.Executable:
    """Gets lorekeeper world data from a group id
    
    Args:
        group_id: the id of the group related to the actors
    """

