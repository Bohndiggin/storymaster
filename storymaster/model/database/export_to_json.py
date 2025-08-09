#!/usr/bin/env python3
"""
Setting Export System for Storymaster

This script exports an entire setting and all related world-building data
to a JSON file that can be imported back into Storymaster.

Usage:
    python export_to_json.py <setting_id> <output_file_path>
    python export_to_json.py 1 my_setting_export.json

Or programmatically:
    from export_to_json import export_setting_to_json
    success = export_setting_to_json(setting_id, output_path)
"""

import json
import os
import sys
from typing import Dict, List, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import schema directly from the same package
from . import schema
from .schema.base import BaseTable

# Database configuration
database_url = (
    f"sqlite:///{os.path.expanduser('~/.local/share/storymaster/storymaster.db')}"
)
engine = create_engine(database_url)

# Table name to SQLAlchemy class mapping (from import script)
TABLE_CLASS_MAP = {
    "setting": schema.Setting,
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

# Reverse mapping for export
CLASS_TO_TABLE_MAP = {v: k for k, v in TABLE_CLASS_MAP.items()}

# Export order - designed to match import dependency order
EXPORT_ORDER = [
    "setting",
    "alignment",
    "background",
    "class",
    "race",
    "sub_race",
    "stat",
    "skills",
    "actor",
    "actor_a_on_b_relations",
    "actor_to_skills",
    "actor_to_race",
    "actor_to_class",
    "actor_to_stat",
    "faction",
    "faction_a_on_b_relations",
    "faction_members",
    "location_",
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
    "history",
    "history_actor",
    "history_location",
    "history_faction",
    "object_",
    "history_object",
    "object_to_owner",
    "world_data",
    "history_world_data",
    "arc_type",
]


def convert_instance_to_dict(instance) -> Dict[str, Any]:
    """Convert SQLAlchemy instance to dictionary with proper field handling"""
    result = {}

    for column in instance.__table__.columns:
        value = getattr(instance, column.name)

        # Convert None to empty string for consistency with import
        if value is None:
            result[column.name] = ""
        else:
            result[column.name] = value

    # Handle special field mappings (reverse of import logic)
    if hasattr(instance, "linked_node_id") and instance.linked_node_id is not None:
        result["linked_node"] = instance.linked_node_id
        result.pop("linked_node_id", None)

    return result


def export_table_data(
    session: Session, table_name: str, setting_id: int
) -> List[Dict[str, Any]]:
    """Export all records for a specific table related to the setting"""
    if table_name not in TABLE_CLASS_MAP:
        print(f"⚠️  Unknown table: {table_name}, skipping...")
        return []

    table_class = TABLE_CLASS_MAP[table_name]
    exported_data = []

    try:
        if table_name == "setting":
            # Export only the specific setting
            instances = session.query(table_class).filter_by(id=setting_id).all()
        elif hasattr(table_class, "setting_id"):
            # Export all records belonging to this setting
            instances = (
                session.query(table_class).filter_by(setting_id=setting_id).all()
            )
        else:
            # Skip tables that don't belong to settings
            print(f"ℹ️  Table {table_name} has no setting relationship, skipping...")
            return []

        for instance in instances:
            # Skip empty records (similar to import logic)
            instance_dict = convert_instance_to_dict(instance)

            # Check if this is essentially an empty record
            non_empty_values = [
                v
                for v in instance_dict.values()
                if v not in ["", 0, 1, 0.0, 1.0, False, True, None]
            ]

            if non_empty_values:
                exported_data.append(instance_dict)

        return exported_data

    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")
        return []


def validate_setting_exists(session: Session, setting_id: int) -> bool:
    """Check if the setting exists and get its details"""
    setting = session.query(schema.Setting).filter_by(id=setting_id).first()
    if not setting:
        print(f"❌ Setting with ID {setting_id} not found")
        return False

    print(f"📋 Found setting: '{setting.name}' (ID: {setting_id})")
    print(f"👤 Owner: User ID {setting.user_id}")
    return True


def export_setting_to_json(setting_id: int, output_path: str) -> bool:
    """Main export function"""

    print(f"🔄 Starting export of setting {setting_id} to {output_path}")

    with Session(engine) as session:
        # Validate setting exists
        if not validate_setting_exists(session, setting_id):
            return False

        export_data = {}
        total_exported = 0

        # Export each table in the correct order
        for table_name in EXPORT_ORDER:
            table_data = export_table_data(session, table_name, setting_id)

            if table_data:
                export_data[table_name] = table_data
                print(f"✅ Exported {len(table_data)} records from {table_name}")
                total_exported += len(table_data)
            else:
                # Still include empty tables for import compatibility
                export_data[table_name] = []

        # Write to JSON file
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"🎉 Successfully exported {total_exported} total records!")
            print(f"📁 Export saved to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error writing export file: {e}")
            return False


def main():
    """CLI entry point"""
    if len(sys.argv) != 3:
        print("Usage: python export_to_json.py <setting_id> <output_file_path>")
        print("Example: python export_to_json.py 1 my_setting_export.json")
        sys.exit(1)

    try:
        setting_id = int(sys.argv[1])
    except ValueError:
        print("❌ Setting ID must be a valid integer")
        sys.exit(1)

    output_path = sys.argv[2]

    # Add .json extension if not present
    if not output_path.lower().endswith(".json"):
        output_path += ".json"

    success = export_setting_to_json(setting_id, output_path)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
