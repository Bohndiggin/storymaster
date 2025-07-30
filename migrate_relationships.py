#!/usr/bin/env python3
"""
Database migration script for relationship table enhancements.
Adds comprehensive relationship fields to all relationship tables.
"""

import os
import sys
from pathlib import Path

# Add the storymaster directory to the Python path
current_dir = Path(__file__).parent
storymaster_dir = current_dir / "storymaster"
sys.path.insert(0, str(storymaster_dir))

try:
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.exc import OperationalError
    
    # Load environment variables
    
    def get_database_url():
        """Get the database URL from environment or default"""
        db_url = None
        if not db_url:
            # Use the same path as seed.py
            db_path = os.path.expanduser('~/.local/share/storymaster/storymaster.db')
            db_url = f"sqlite:///{db_path}"
        elif not db_url.startswith("sqlite:///") and not os.path.isabs(db_url.replace("sqlite:///", "")):
            # Make relative SQLite paths absolute
            db_file = db_url.replace("sqlite:///", "")
            db_path = current_dir / db_file
            db_url = f"sqlite:///{db_path}"
        return db_url
    
    def column_exists(inspector, table_name, column_name):
        """Check if a column exists in a table"""
        try:
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
        except Exception:
            return False
    
    def table_exists(inspector, table_name):
        """Check if a table exists"""
        try:
            return table_name in inspector.get_table_names()
        except Exception:
            return False
    
    def add_column_if_not_exists(engine, table_name, column_name, column_definition):
        """Add a column to a table if it doesn't exist"""
        inspector = inspect(engine)
        
        if not table_exists(inspector, table_name):
            print(f"  Table {table_name} does not exist, skipping...")
            return False
            
        if column_exists(inspector, table_name, column_name):
            print(f"  Column {column_name} already exists in {table_name}")
            return False
        
        try:
            with engine.connect() as conn:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✓ Added {column_name} to {table_name}")
                return True
        except Exception as e:
            print(f"  ✗ Failed to add {column_name} to {table_name}: {e}")
            return False
    
    def migrate_relationship_tables():
        """Migrate all relationship tables with new fields"""
        print("Starting relationship table migration...")
        
        # Get database connection
        db_url = get_database_url()
        print(f"Using database: {db_url}")
        
        engine = create_engine(db_url)
        
        # Define migrations for each relationship table
        migrations = {
            "faction_members": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Membership-specific fields
                ("how_joined", "TEXT"),
                ("reputation_within", "INTEGER"),
                ("personal_goals", "TEXT"),
                ("conflicts", "TEXT"),
            ],
            "location_to_faction": [
                # Basic relationship fields (notes already exists)
                ("description", "TEXT"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Territory-specific fields
                ("local_opposition", "TEXT"),
                ("key_supporters", "TEXT"),
                ("control_mechanisms", "TEXT"),
            ],
            "residents": [
                # Basic relationship fields (notes and is_public_knowledge already exist)
                ("description", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                # Residency-specific fields
                ("reason_for_living", "TEXT"),
                ("living_conditions", "TEXT"),
                ("relationships_neighbors", "TEXT"),
                ("future_plans", "TEXT"),
            ],
            "object_to_owner": [
                # Basic relationship fields (notes and is_public_knowledge already exist)
                ("description", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                # Ownership-specific fields
                ("item_condition", "VARCHAR(100)"),
                ("usage_frequency", "VARCHAR(100)"),
                ("storage_location", "TEXT"),
                ("acquisition_story", "TEXT"),
            ],
            "actor_to_skills": [
                # Basic relationship fields (notes already exists)
                ("description", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Skill-specific fields
                ("practice_frequency", "VARCHAR(100)"),
                ("skill_applications", "TEXT"),
                ("learning_goals", "TEXT"),
            ],
            "actor_to_race": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Heritage-specific fields
                ("heritage_pride", "INTEGER"),
                ("cultural_connection", "TEXT"),
                ("racial_experiences", "TEXT"),
            ],
            "actor_to_class": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Class-specific fields
                ("training_location", "TEXT"),
                ("mentors", "TEXT"),
                ("class_goals", "TEXT"),
                ("advancement_plans", "TEXT"),
            ],
            "actor_to_stat": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Stat-specific fields
                ("how_developed", "TEXT"),
                ("training_methods", "TEXT"),
                ("stat_goals", "TEXT"),
            ],
            "history_actor": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Historical involvement fields (some may already exist)
                ("role_in_event", "TEXT"),
                ("involvement_level", "VARCHAR(100)"),
                ("impact_on_actor", "TEXT"),
                ("actor_perspective", "TEXT"),
                ("consequences", "TEXT"),
            ],
            "history_location": [
                # Basic relationship fields
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Historical location fields
                ("role_in_event", "TEXT"),
                ("location_impact", "TEXT"),
                ("physical_changes", "TEXT"),
                ("ongoing_effects", "TEXT"),
            ],
            "history_faction": [
                # Basic relationship fields (some may already exist)
                ("description", "TEXT"),
                ("notes", "TEXT"),
                ("status", "VARCHAR(50)"),
                ("strength", "INTEGER"),
                ("is_public", "BOOLEAN DEFAULT 1"),
                # Historical faction fields may already exist, check first
            ],
        }
        
        total_added = 0
        
        for table_name, columns in migrations.items():
            print(f"\nMigrating table: {table_name}")
            
            for column_name, column_def in columns:
                if add_column_if_not_exists(engine, table_name, column_name, column_def):
                    total_added += 1
        
        print(f"\n✅ Migration completed! Added {total_added} new columns.")
        print("Relationship dialogs will now have much richer data fields.")
        
        return True
    
    def main():
        """Main migration function"""
        print("🚀 Storymaster Relationship Database Migration")
        print("=" * 50)
        
        try:
            success = migrate_relationship_tables()
            if success:
                print("\n🎉 All relationship tables have been successfully enhanced!")
                print("You can now use the relationship dialogs with full data persistence.")
            else:
                print("\n❌ Migration encountered some issues.")
                return 1
                
        except Exception as e:
            print(f"\n💥 Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        return 0
    
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install the required packages:")
    print("pip install sqlalchemy python-dotenv")
    sys.exit(1)