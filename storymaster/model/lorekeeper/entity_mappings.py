"""User-friendly entity type mappings for Lorekeeper

This module provides mappings between database table names and user-friendly
creative writing terminology, along with field groupings for intuitive UI sections.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FieldSection:
    """Represents a logical grouping of fields for UI display"""

    name: str
    display_name: str
    fields: List[str]
    description: Optional[str] = None


@dataclass
class EntityMapping:
    """Maps database entities to user-friendly creative writing concepts"""

    table_name: str
    display_name: str
    plural_name: str
    icon: str
    description: str
    sections: List[FieldSection]
    relationships: Dict[str, str]  # relationship_table -> display_name


# Entity type mappings
ENTITY_MAPPINGS = {
    "actor": EntityMapping(
        table_name="actor",
        display_name="Character",
        plural_name="Characters",
        icon="👤",
        description="People who inhabit your world - heroes, villains, allies, and everyone in between",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Basic Information",
                fields=["first_name", "middle_name", "last_name", "title", "actor_age"],
                description="Core character details",
            ),
            FieldSection(
                name="appearance",
                display_name="Appearance & Personality",
                fields=["appearance", "strengths", "weaknesses"],
                description="How they look and what defines them",
            ),
            FieldSection(
                name="background",
                display_name="Background & Role",
                fields=["background_id", "job", "actor_role"],
                description="Their history and place in the world",
            ),
            FieldSection(
                name="character_traits",
                display_name="Character Traits",
                fields=["alignment_id", "ideal", "bond", "flaw"],
                description="What drives and motivates them",
            ),
            FieldSection(
                name="notes",
                display_name="Additional Notes",
                fields=["notes"],
                description="Miscellaneous information and story notes",
            ),
        ],
        relationships={
            "actor_a_on_b_relations": "Relationships with Others",
            "faction_members": "Organization Memberships",
            "residents": "Places They Live",
            "actor_to_skills": "Skills & Abilities",
            "actor_to_race": "Heritage",
            "actor_to_class": "Classes & Professions",
            "actor_to_stat": "Statistics",
            "object_to_owner": "Possessions",
            "history_actor": "Historical Events",
            "arc_to_actor": "Character Arcs",
        },
    ),
    "faction": EntityMapping(
        table_name="faction",
        display_name="Organization",
        plural_name="Organizations",
        icon="🏛️",
        description="Groups, guilds, kingdoms, companies, and other collective entities",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Overview",
                fields=["name", "description"],
                description="What this organization is about",
            ),
            FieldSection(
                name="purpose",
                display_name="Purpose & Values",
                fields=["goals", "faction_values"],
                description="What they want to achieve and what they believe in",
            ),
            FieldSection(
                name="resources",
                display_name="Resources & Finances",
                fields=["faction_income_sources", "faction_expenses"],
                description="How they make and spend money",
            ),
        ],
        relationships={
            "faction_members": "Members",
            "faction_a_on_b_relations": "Relations with Other Organizations",
            "location_to_faction": "Territories & Influence",
            "history_faction": "Historical Events",
        },
    ),
    "location_": EntityMapping(
        table_name="location_",
        display_name="Place",
        plural_name="Places",
        icon="🗺️",
        description="Cities, dungeons, regions, buildings, and other locations in your world",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Overview",
                fields=["name", "location_type", "description"],
                description="Basic information about this place",
            ),
            FieldSection(
                name="sensory",
                display_name="Atmosphere",
                fields=["sights", "smells", "sounds", "feels", "tastes"],
                description="What it's like to be there - the sensory experience",
            ),
            FieldSection(
                name="geography",
                display_name="Geography",
                fields=["coordinates"],
                description="Where this place is located",
            ),
        ],
        relationships={
            "residents": "Who Lives Here",
            "location_to_faction": "Controlling Organizations",
            "location_dungeon": "Dungeon Details",
            "location_city": "City Details",
            "location_city_districts": "Districts & Neighborhoods",
            "location_flora_fauna": "Local Wildlife",
            "history_location": "Historical Events",
        },
    ),
    "object_": EntityMapping(
        table_name="object_",
        display_name="Item",
        plural_name="Items",
        icon="⚔️",
        description="Weapons, artifacts, treasures, tools, and other important objects",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Overview",
                fields=["name", "description"],
                description="What this item is",
            ),
            FieldSection(
                name="properties",
                display_name="Properties",
                fields=["object_value", "rarity"],
                description="Important characteristics and value",
            ),
        ],
        relationships={
            "object_to_owner": "Current Owner",
            "history_object": "Historical Events",
        },
    ),
    "history": EntityMapping(
        table_name="history",
        display_name="Event",
        plural_name="Events",
        icon="📜",
        description="Important happenings, timeline events, and historical moments",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Event Details",
                fields=["name", "event_year", "description"],
                description="What happened and when",
            )
        ],
        relationships={
            "history_actor": "Characters Involved",
            "history_location": "Places Involved",
            "history_faction": "Organizations Involved",
            "history_object": "Items Involved",
            "history_world_data": "Lore Elements",
        },
    ),
    "world_data": EntityMapping(
        table_name="world_data",
        display_name="Lore",
        plural_name="Lore",
        icon="📚",
        description="Cultures, customs, rules, knowledge, and other world-building elements",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Details",
                fields=["name", "description"],
                description="Information about this lore element",
            )
        ],
        relationships={"history_world_data": "Related Historical Events"},
    ),
}

# Supporting entity mappings (background tables)
SUPPORTING_MAPPINGS = {
    "background": EntityMapping(
        table_name="background",
        display_name="Background",
        plural_name="Backgrounds",
        icon="🎭",
        description="Character backgrounds and origins",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Details",
                fields=["name", "description"],
                description="Background information",
            )
        ],
        relationships={},
    ),
    "race": EntityMapping(
        table_name="race",
        display_name="Heritage",
        plural_name="Heritage Types",
        icon="🧬",
        description="Character races and heritage types",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Details",
                fields=["name", "description"],
                description="Heritage information",
            )
        ],
        relationships={"sub_races": "Sub-types"},
    ),
    "class": EntityMapping(
        table_name="class",
        display_name="Profession",
        plural_name="Professions",
        icon="⚔️",
        description="Character classes and professions",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Details",
                fields=["name", "description"],
                description="Profession information",
            )
        ],
        relationships={},
    ),
    "skills": EntityMapping(
        table_name="skills",
        display_name="Skill",
        plural_name="Skills",
        icon="🎯",
        description="Character skills and abilities",
        sections=[
            FieldSection(
                name="basic_info",
                display_name="Details",
                fields=["name", "description", "skill_trait"],
                description="Skill information",
            )
        ],
        relationships={},
    ),
}

# Main navigation categories
MAIN_CATEGORIES = ["actor", "faction", "location_", "object_", "history", "world_data"]
SUPPORTING_CATEGORIES = ["background", "race", "class", "skills"]


def get_entity_mapping(table_name: str) -> Optional[EntityMapping]:
    """Get the entity mapping for a given table name"""
    return ENTITY_MAPPINGS.get(table_name) or SUPPORTING_MAPPINGS.get(table_name)


def get_display_name(table_name: str) -> str:
    """Get the user-friendly display name for a table"""
    mapping = get_entity_mapping(table_name)
    return mapping.display_name if mapping else table_name.replace("_", " ").title()


def get_plural_name(table_name: str) -> str:
    """Get the plural display name for a table"""
    mapping = get_entity_mapping(table_name)
    return mapping.plural_name if mapping else get_display_name(table_name) + "s"


def get_entity_icon(table_name: str) -> str:
    """Get the icon for an entity type"""
    mapping = get_entity_mapping(table_name)
    return mapping.icon if mapping else "📄"


def get_relationship_display_name(table_name: str, relationship_table: str) -> str:
    """Get the user-friendly name for a relationship"""
    mapping = get_entity_mapping(table_name)
    if mapping and relationship_table in mapping.relationships:
        return mapping.relationships[relationship_table]
    return relationship_table.replace("_", " ").title()
