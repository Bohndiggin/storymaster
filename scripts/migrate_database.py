#!/usr/bin/env python3
"""
Database Migration Script for Storymaster

This script adds the new name and description columns to existing litography_node tables.
Run this to update existing databases without losing data.
"""

import os
import sqlite3
from pathlib import Path


def migrate_database():
    """Add name and description columns to litography_node table"""
    # Find the database file
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster") 
    db_path = os.path.join(db_dir, "storymaster.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Please run 'python init_database.py' first to create a new database.")
        return False
    
    print(f"📦 Migrating database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(litography_node)")
        columns = [row[1] for row in cursor.fetchall()]
        
        changes_made = False
        
        # Add name column if it doesn't exist
        if 'name' not in columns:
            print("➕ Adding 'name' column to litography_node table...")
            cursor.execute("""
                ALTER TABLE litography_node 
                ADD COLUMN name TEXT NOT NULL DEFAULT 'Untitled Node'
            """)
            changes_made = True
        else:
            print("✅ 'name' column already exists")
        
        # Add description column if it doesn't exist  
        if 'description' not in columns:
            print("➕ Adding 'description' column to litography_node table...")
            cursor.execute("""
                ALTER TABLE litography_node 
                ADD COLUMN description TEXT NULL
            """)
            changes_made = True
        else:
            print("✅ 'description' column already exists")
        
        if changes_made:
            # Update existing nodes with meaningful names based on their type
            print("📝 Updating existing nodes with default names...")
            cursor.execute("""
                UPDATE litography_node 
                SET name = 'New ' || node_type || ' Node'
                WHERE name = 'Untitled Node' OR name IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"📝 Updated {rows_updated} nodes with default names")
            
            # Commit changes
            conn.commit()
            print("✅ Database migration completed successfully!")
        else:
            print("✅ Database is already up to date - no migration needed")
            
        # Close connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False


def backup_database():
    """Create a backup of the database before migration"""
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
    db_path = os.path.join(db_dir, "storymaster.db")
    backup_path = os.path.join(db_dir, "storymaster_backup_before_migration.db")
    
    if os.path.exists(db_path):
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
            return False
    return False


if __name__ == "__main__":
    print("🚀 Starting Storymaster Database Migration")
    print("=" * 50)
    
    # Create backup first
    backup_database()
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed! You can now use the updated Storymaster.")
        print("📝 Nodes now have editable names and descriptions in the litographer.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        exit(1)