#!/usr/bin/env python3
"""
Database Migration Script for Storymaster - Arc Type Constraint Fix

This script fixes the arc_type table constraint to allow the same arc type name
in different settings. Changes the unique constraint from just 'name' to
composite 'name + setting_id'.

Run this to update existing databases without losing data.
"""

import os
import sqlite3
from pathlib import Path


def check_arc_type_constraint(cursor):
    """
    Check if arc_type table has the old unique constraint on name only.
    Returns True if migration is needed.
    """
    # Get the CREATE TABLE statement for arc_type
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='arc_type'")
    result = cursor.fetchone()

    if not result:
        print("⚠️  arc_type table does not exist")
        return False

    create_statement = result[0]

    # Check if there's a UNIQUE constraint on name column only
    # Old schema: name TEXT NOT NULL UNIQUE
    # New schema: CONSTRAINT uq_arc_type_name_setting UNIQUE (name, setting_id)
    has_old_constraint = (
        "UNIQUE" in create_statement and "uq_arc_type_name_setting" not in create_statement
    )

    return has_old_constraint


def migrate_arc_type_table(cursor):
    """
    Migrate arc_type table to use composite unique constraint.

    SQLite doesn't support dropping constraints, so we need to:
    1. Create new table with correct constraint
    2. Copy data from old table
    3. Drop old table
    4. Rename new table
    """
    print("🔧 Recreating arc_type table with composite unique constraint...")

    # Step 1: Create new table with correct constraint
    cursor.execute(
        """
        CREATE TABLE arc_type_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            setting_id INTEGER NOT NULL,
            CONSTRAINT uq_arc_type_name_setting UNIQUE (name, setting_id),
            FOREIGN KEY (setting_id) REFERENCES setting(id)
        )
    """
    )
    print("✅ Created new arc_type table with composite constraint")

    # Step 2: Copy data from old table (only unique name+setting_id combinations)
    cursor.execute(
        """
        INSERT INTO arc_type_new (id, name, description, setting_id)
        SELECT id, name, description, setting_id
        FROM arc_type
    """
    )

    rows_copied = cursor.rowcount
    print(f"✅ Copied {rows_copied} rows from old table")

    # Step 3: Drop old table
    cursor.execute("DROP TABLE arc_type")
    print("✅ Dropped old arc_type table")

    # Step 4: Rename new table
    cursor.execute("ALTER TABLE arc_type_new RENAME TO arc_type")
    print("✅ Renamed arc_type_new to arc_type")

    return True


def migrate_database():
    """Fix arc_type unique constraint to allow same name in different settings"""
    # Find the database file
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
    db_path = os.path.join(db_dir, "storymaster.db")

    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Please run 'python init_database.py' first to create a new database.")
        return False

    print(f"📦 Checking database: {db_path}")

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if migration is needed
        needs_migration = check_arc_type_constraint(cursor)

        if not needs_migration:
            print("✅ Database is already up to date - no migration needed")
            print("   arc_type table already has the composite unique constraint")
            conn.close()
            return True

        print("⚠️  Old schema detected - migration required")
        print("   Current: UNIQUE constraint on 'name' only")
        print("   Target:  UNIQUE constraint on 'name + setting_id'")
        print()

        # Perform migration
        migrate_arc_type_table(cursor)

        # Commit changes
        conn.commit()
        print()
        print("✅ Database migration completed successfully!")
        print("   Arc types can now have the same name in different settings")

        # Close connection
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ SQLite error during migration: {e}")
        if "conn" in locals():
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        if "conn" in locals():
            conn.rollback()
            conn.close()
        return False


def backup_database():
    """Create a backup of the database before migration"""
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
    db_path = os.path.join(db_dir, "storymaster.db")

    # Create backup with timestamp
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(db_dir, f"storymaster_backup_arc_type_{timestamp}.db")

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
    print("🚀 Starting Storymaster Arc Type Constraint Migration")
    print("=" * 60)
    print()

    # Create backup first
    backup_database()
    print()

    # Run migration
    success = migrate_database()

    if success:
        print()
        print("🎉 Migration completed successfully!")
        print("   You can now import arc types with the same name to different settings.")
    else:
        print()
        print("💥 Migration failed. Please check the error messages above.")
        exit(1)
