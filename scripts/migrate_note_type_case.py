#!/usr/bin/env python3
"""
Database Migration Script for Storymaster - Fix NoteType Case

This script fixes note_type values in the litography_notes table to be lowercase
to match the NoteType enum definition.

Run this to fix existing databases with uppercase note_type values.
"""

import os
import sqlite3
from pathlib import Path


def migrate_note_type_case():
    """Fix note_type values to be lowercase"""
    # Find the database file
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
    db_path = os.path.join(db_dir, "storymaster.db")

    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False

    print(f"📦 Checking database: {db_path}")

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if there are any uppercase note_type values
        cursor.execute(
            """
            SELECT COUNT(*) FROM litography_notes
            WHERE note_type != LOWER(note_type)
        """
        )
        uppercase_count = cursor.fetchone()[0]

        if uppercase_count == 0:
            print("✅ Database is already up to date - no uppercase note_type values")
            conn.close()
            return True

        print(f"⚠️  Found {uppercase_count} notes with uppercase note_type values")
        print("   Converting to lowercase to match NoteType enum...")

        # Fix all uppercase note_type values
        cursor.execute(
            """
            UPDATE litography_notes
            SET note_type = LOWER(note_type)
            WHERE note_type != LOWER(note_type)
        """
        )

        rows_updated = cursor.rowcount
        print(f"✅ Updated {rows_updated} note_type values to lowercase")

        # Commit changes
        conn.commit()
        print()
        print("✅ Database migration completed successfully!")
        print("   All note_type values are now lowercase")

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
    backup_path = os.path.join(db_dir, f"storymaster_backup_note_type_{timestamp}.db")

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
    print("🚀 Starting Storymaster NoteType Case Migration")
    print("=" * 60)
    print()

    # Create backup first
    backup_database()
    print()

    # Run migration
    success = migrate_note_type_case()

    if success:
        print()
        print("🎉 Migration completed successfully!")
        print("   Notes will now load without enum errors.")
    else:
        print()
        print("💥 Migration failed. Please check the error messages above.")
        exit(1)
