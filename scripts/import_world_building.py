#!/usr/bin/env python3
"""
World Building Package Import System for Storymaster

This script imports world-building data from JSON packages into an existing setting.
It automatically updates setting_id references to match the target setting.

Usage:
    from import_world_building import import_world_building_package
    success = import_world_building_package(json_file_path, target_setting_id)
"""

import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from storymaster.model.database import schema
from storymaster.model.database.schema.base import BaseTable

# Database configuration
database_url = (
    f"sqlite:///{os.path.expanduser('~/.local/share/storymaster/storymaster.db')}"
)
engine = create_engine(database_url)

# Table name to SQLAlchemy class mapping
TABLE_CLASS_MAP = {
    "alignment": schema.Alignment,
    "background": schema.Background,
    "class": schema.Class_,
    "race": schema.Race,
    "sub_race": schema.SubRace,
    "stat": schema.Stat,
    "skills": schema.Skills,
    "actor": schema.Actor,
    "actor_a_on_b_relations": schema.ActorAOnBRelations,
    "actor_to_skills": schema.ActorToSkills,
    "actor_to_race": schema.ActorToRace,
    "actor_to_class": schema.ActorToClass,
    "actor_to_stat": schema.ActorToStat,
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
    "location_a_on_b_relations": schema.LocationAOnBRelations,
    "location_geographic_relations": schema.LocationGeographicRelations,
    "location_political_relations": schema.LocationPoliticalRelations,
    "location_economic_relations": schema.LocationEconomicRelations,
    "location_hierarchy": schema.LocationHierarchy,
    "history": schema.History,
    "history_actor": schema.HistoryActor,
    "history_location": schema.HistoryLocation,
    "history_faction": schema.HistoryFaction,
    "object_": schema.Object_,
    "history_object": schema.HistoryObject,
    "object_to_owner": schema.ObjectToOwner,
    "world_data": schema.WorldData,
    "history_world_data": schema.HistoryWorldData,
    "arc_type": schema.ArcType,
}

# Tables that should be skipped (core system tables)
SKIP_TABLES = {
    "user",
    "setting",
    "storyline",
    "storyline_to_setting",
    "litography_node",
    "node_connection",
    "litography_notes",
    "litography_plot",
    "litography_plot_section",
    "litography_node_to_plot_section",
    "litography_arc",
    "arc_point",
    "arc_to_node",
    "arc_to_actor",
    "litography_note_to_actor",
    "litography_note_to_background",
    "litography_note_to_faction",
    "litography_note_to_location",
    "litography_note_to_history",
    "litography_note_to_object",
    "litography_note_to_world_data",
    "litography_note_to_class",
    "litography_note_to_race",
    "litography_note_to_sub_race",
    "litography_note_to_skills",
}


def filter_valid_fields(table_class, data_dict):
    """Filter data dictionary to only include valid fields for the table class"""
    if not hasattr(table_class, "__table__"):
        return data_dict

    valid_columns = {col.name for col in table_class.__table__.columns}
    filtered_data = {k: v for k, v in data_dict.items() if k in valid_columns}

    return filtered_data


def update_setting_id(row_data: dict, target_setting_id: int) -> dict:
    """Update setting_id in row data to match target setting"""
    updated_data = row_data.copy()
    if "setting_id" in updated_data:
        updated_data["setting_id"] = target_setting_id
    return updated_data


def get_next_available_id(session: Session, table_class) -> int:
    """Get the next available ID for a table"""
    try:
        max_id = session.query(table_class.id).order_by(table_class.id.desc()).first()
        return (max_id[0] + 1) if max_id else 1
    except Exception:
        return 1


def check_duplicate_entry(
    session: Session, table_class, filtered_data: dict, target_setting_id: int
) -> bool:
    """Check if an entry with the same unique fields already exists in the setting"""
    # Check for name-based uniqueness within setting
    if "name" in filtered_data and "setting_id" in filtered_data:
        existing = (
            session.query(table_class)
            .filter(
                table_class.name == filtered_data["name"],
                table_class.setting_id == target_setting_id,
            )
            .first()
        )
        if existing:
            return True

    return False


def import_table_data(
    session: Session,
    table_name: str,
    table_data: list,
    target_setting_id: int,
    id_mapping: dict,
):
    """Import data for a specific table with setting ID updates"""
    if table_name in SKIP_TABLES:
        return 0

    if table_name not in TABLE_CLASS_MAP:
        print(f"⚠️  Unknown table: {table_name}, skipping...")
        return 0

    table_class = TABLE_CLASS_MAP[table_name]
    imported_count = 0
    skipped_count = 0

    # Track ID mappings for foreign keys
    if table_name not in id_mapping:
        id_mapping[table_name] = {}

    for row_data in table_data:
        # Skip empty rows
        if not any(
            v
            for v in row_data.values()
            if v not in ["", 0, 1, 0.0, 1.0, False, True, None]
        ):
            continue

        try:
            # Update setting_id to target setting
            updated_row = update_setting_id(row_data, target_setting_id)

            # Get original ID for mapping
            original_id = updated_row.get("id")

            # Generate new ID to avoid conflicts
            new_id = get_next_available_id(session, table_class)
            updated_row["id"] = new_id

            # Update foreign key references using ID mapping
            updated_row = update_foreign_keys(updated_row, id_mapping, table_name)

            # Filter to only valid fields for this table
            filtered_data = filter_valid_fields(table_class, updated_row)

            # Remove empty strings and convert to None for nullable fields
            for key, value in list(filtered_data.items()):
                if value == "":
                    filtered_data[key] = None

            # Check for duplicates before inserting
            if check_duplicate_entry(
                session, table_class, filtered_data, target_setting_id
            ):
                print(
                    f"⚠️  Skipping duplicate {table_name}: {filtered_data.get('name', 'unnamed')}"
                )
                skipped_count += 1
                # Still store ID mapping for consistency
                if original_id is not None:
                    # Find existing record to get its ID
                    existing = (
                        session.query(table_class)
                        .filter(
                            table_class.name == filtered_data["name"],
                            table_class.setting_id == target_setting_id,
                        )
                        .first()
                    )
                    if existing:
                        id_mapping[table_name][original_id] = existing.id
                continue

            # Create and add the instance
            instance = table_class(**filtered_data)
            session.add(instance)

            # Store ID mapping for foreign key references
            if original_id is not None:
                id_mapping[table_name][original_id] = new_id

            imported_count += 1

        except Exception as e:
            print(f"❌ Error creating {table_name} with data {row_data}: {e}")
            continue

    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} duplicate entries in {table_name}")

    return imported_count


def update_foreign_keys(row_data: dict, id_mapping: dict, current_table: str) -> dict:
    """Update foreign key references using ID mapping"""
    updated_data = row_data.copy()

    # Common foreign key patterns
    fk_patterns = {
        "actor_id": "actor",
        "faction_id": "faction",
        "location_id": "location_",
        "race_id": "race",
        "sub_race_id": "sub_race",
        "parent_race_id": "race",
        "class_id": "class",
        "skill_id": "skills",
        "stat_id": "stat",
        "background_id": "background",
        "alignment_id": "alignment",
        "history_id": "history",
        "object_id": "object_",
        "world_data_id": "world_data",
        "arc_type_id": "arc_type",
    }

    for fk_field, ref_table in fk_patterns.items():
        if fk_field in updated_data and updated_data[fk_field] is not None:
            original_fk_id = updated_data[fk_field]
            if ref_table in id_mapping and original_fk_id in id_mapping[ref_table]:
                updated_data[fk_field] = id_mapping[ref_table][original_fk_id]

    return updated_data


def import_world_building_package(json_file_path: str, target_setting_id: int) -> bool:
    """
    Import a world building package into the specified setting.

    Args:
        json_file_path: Path to the JSON package file
        target_setting_id: ID of the setting to import into

    Returns:
        bool: True if successful, False otherwise
    """

    # Validate file exists
    if not os.path.exists(json_file_path):
        print(f"❌ JSON file not found: {json_file_path}")
        return False

    # Load JSON data
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            package_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return False

    # Validate JSON structure
    if not isinstance(package_data, dict):
        print("❌ JSON must be a dictionary with table names as keys")
        return False

    # Get package info if available
    package_info = package_data.get("_package_info", {})
    package_name = package_info.get("display_name", os.path.basename(json_file_path))

    print(f"📦 Importing world building package: {package_name}")
    print(f"🎯 Target setting ID: {target_setting_id}")

    with Session(engine) as session:
        total_imported = 0
        id_mapping = {}  # Track ID mappings for foreign keys

        # Import data table by table in dependency order
        table_order = [
            "alignment",
            "background",
            "class",
            "race",
            "sub_race",
            "stat",
            "skills",
            "actor",
            "faction",
            "location_",
            "history",
            "object_",
            "world_data",
            "arc_type",
            "actor_a_on_b_relations",
            "actor_to_skills",
            "actor_to_race",
            "actor_to_class",
            "actor_to_stat",
            "faction_a_on_b_relations",
            "faction_members",
            "location_to_faction",
            "location_dungeon",
            "location_city",
            "location_city_districts",
            "residents",
            "location_flora_fauna",
            "location_a_on_b_relations",
            "location_geographic_relations",
            "location_political_relations",
            "location_economic_relations",
            "location_hierarchy",
            "history_actor",
            "history_location",
            "history_faction",
            "history_object",
            "object_to_owner",
            "history_world_data",
        ]

        # Process tables in dependency order
        for table_name in table_order:
            if table_name in package_data:
                table_data = package_data[table_name]
                if isinstance(table_data, list) and table_data:
                    imported_count = import_table_data(
                        session, table_name, table_data, target_setting_id, id_mapping
                    )
                    if imported_count > 0:
                        print(f"✅ Imported {imported_count} rows into {table_name}")
                        total_imported += imported_count

        # Process any remaining tables not in the ordered list
        for table_name, table_data in package_data.items():
            if table_name.startswith("_"):  # Skip metadata
                continue
            if (
                table_name not in table_order
                and isinstance(table_data, list)
                and table_data
            ):
                imported_count = import_table_data(
                    session, table_name, table_data, target_setting_id, id_mapping
                )
                if imported_count > 0:
                    print(f"✅ Imported {imported_count} rows into {table_name}")
                    total_imported += imported_count

        # Commit all changes
        try:
            session.commit()
            print(
                f"🎉 Successfully imported {total_imported} total rows from {package_name}!"
            )
            return True
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
            session.rollback()
            return False


def main():
    """CLI entry point for testing"""
    import sys

    if len(sys.argv) != 3:
        print(
            "Usage: python import_world_building.py <json_file_path> <target_setting_id>"
        )
        print("Example: python import_world_building.py fantasy_skills.json 1")
        sys.exit(1)

    json_file_path = sys.argv[1]
    try:
        target_setting_id = int(sys.argv[2])
    except ValueError:
        print("❌ Target setting ID must be a number")
        sys.exit(1)

    success = import_world_building_package(json_file_path, target_setting_id)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
