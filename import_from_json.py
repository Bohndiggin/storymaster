#!/usr/bin/env python3
"""
Universal JSON Story Import System for Storymaster

This script imports story data from a JSON file into the Storymaster database.
The JSON should follow the schema template format with proper foreign key ordering.

Usage:
    python import_from_json.py <json_file_path>
    python import_from_json.py story_data.json
"""

import json
import os
import sys
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
    'user': schema.User,
    'setting': schema.Setting,
    'storyline': schema.Storyline,
    'storyline_to_setting': schema.StorylineToSetting,
    'alignment': schema.Alignment,
    'background': schema.Background,
    'class': schema.Class_,
    'race': schema.Race,
    'sub_race': schema.SubRace,
    'stat': schema.Stat,
    'skills': schema.Skills,
    'actor': schema.Actor,
    'actor_a_on_b_relations': schema.ActorAOnBRelations,
    'actor_to_skills': schema.ActorToSkills,
    'actor_to_race': schema.ActorToRace,
    'actor_to_class': schema.ActorToClass,
    'actor_to_stat': schema.ActorToStat,
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
    'location_a_on_b_relations': schema.LocationAOnBRelations,
    'location_geographic_relations': schema.LocationGeographicRelations,
    'location_political_relations': schema.LocationPoliticalRelations,
    'location_economic_relations': schema.LocationEconomicRelations,
    'location_hierarchy': schema.LocationHierarchy,
    'history': schema.History,
    'history_actor': schema.HistoryActor,
    'history_location': schema.HistoryLocation,
    'history_faction': schema.HistoryFaction,
    'object_': schema.Object_,
    'history_object': schema.HistoryObject,
    'object_to_owner': schema.ObjectToOwner,
    'world_data': schema.WorldData,
    'history_world_data': schema.HistoryWorldData,
    'arc_type': schema.ArcType,
    'litography_node': schema.LitographyNode,
    'node_connection': schema.NodeConnection,
    'litography_notes': schema.LitographyNotes,
    'litography_plot': schema.LitographyPlot,
    'litography_plot_section': schema.LitographyPlotSection,
    'litography_node_to_plot_section': schema.LitographyNodeToPlotSection,
    'litography_arc': schema.LitographyArc,
    'arc_point': schema.ArcPoint,
    'arc_to_node': schema.ArcToNode,
    'arc_to_actor': schema.ArcToActor,
    'litography_note_to_actor': schema.LitographyNoteToActor,
    'litography_note_to_background': schema.LitographyNoteToBackground,
    'litography_note_to_faction': schema.LitographyNoteToFaction,
    'litography_note_to_location': schema.LitographyNoteToLocation,
    'litography_note_to_history': schema.LitographyNoteToHistory,
    'litography_note_to_object': schema.LitographyNoteToObject,
    'litography_note_to_world_data': schema.LitographyNoteToWorldData,
    'litography_note_to_class': schema.LitographyNoteToClass,
    'litography_note_to_race': schema.LitographyNoteToRace,
    'litography_note_to_sub_race': schema.LitographyNoteToSubRace,
    'litography_note_to_skills': schema.LitographyNoteToSkills,
}

def clear_database(session: Session) -> Session:
    """Completely drops and recreates all tables"""
    print("🔄 Clearing database...")
    BaseTable.metadata.drop_all(engine)
    BaseTable.metadata.create_all(engine)
    return session

def filter_valid_fields(table_class, data_dict):
    """Filter data dictionary to only include valid fields for the table class"""
    if not hasattr(table_class, '__table__'):
        return data_dict
    
    valid_columns = {col.name for col in table_class.__table__.columns}
    filtered_data = {k: v for k, v in data_dict.items() if k in valid_columns}
    
    # Handle special field mappings
    if 'linked_node' in data_dict and 'linked_node_id' in valid_columns:
        filtered_data['linked_node_id'] = data_dict['linked_node']
        filtered_data.pop('linked_node', None)
    
    return filtered_data

def import_table_data(session: Session, table_name: str, table_data: list):
    """Import data for a specific table"""
    if table_name not in TABLE_CLASS_MAP:
        print(f"⚠️  Unknown table: {table_name}, skipping...")
        return 0
    
    table_class = TABLE_CLASS_MAP[table_name]
    imported_count = 0
    
    for row_data in table_data:
        # Skip empty rows (rows with all empty/default values)
        if not any(v for v in row_data.values() if v not in ["", 0, 1, 0.0, 1.0, False, True]):
            continue
            
        try:
            # Filter to only valid fields for this table
            filtered_data = filter_valid_fields(table_class, row_data)
            
            # Remove empty strings and convert to None for nullable fields
            for key, value in list(filtered_data.items()):
                if value == "":
                    filtered_data[key] = None
            
            # Create and add the instance
            instance = table_class(**filtered_data)
            session.add(instance)
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Error creating {table_name} with data {row_data}: {e}")
            continue
    
    return imported_count

def import_from_json(json_file_path: str, clear_db: bool = True):
    """Main import function"""
    
    # Validate file exists
    if not os.path.exists(json_file_path):
        print(f"❌ JSON file not found: {json_file_path}")
        return False
    
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            story_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return False
    
    # Validate JSON structure
    if not isinstance(story_data, dict):
        print("❌ JSON must be a dictionary with table names as keys")
        return False
    
    print(f"📚 Importing story data from: {json_file_path}")
    
    with Session(engine) as session:
        if clear_db:
            session = clear_database(session)
            session.commit()
        
        total_imported = 0
        
        # Import data table by table in dependency order
        # The JSON template is ordered correctly for foreign keys
        for table_name, table_data in story_data.items():
            if not isinstance(table_data, list):
                print(f"⚠️  Table data for '{table_name}' must be a list, skipping...")
                continue
            
            imported_count = import_table_data(session, table_name, table_data)
            if imported_count > 0:
                print(f"✅ Imported {imported_count} rows into {table_name}")
                total_imported += imported_count
            
            # Commit after each table to handle foreign key constraints
            try:
                session.commit()
            except Exception as e:
                print(f"❌ Error committing {table_name}: {e}")
                session.rollback()
                return False
        
        print(f"🎉 Successfully imported {total_imported} total rows!")
        return True

def main():
    """CLI entry point"""
    if len(sys.argv) != 2:
        print("Usage: python import_from_json.py <json_file_path>")
        print("Example: python import_from_json.py my_story.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    success = import_from_json(json_file_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()