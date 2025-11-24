#!/usr/bin/env python3
"""
Database Migration Script for Storymaster Sync Feature

This script adds timestamp tracking fields (created_at, updated_at, deleted_at, version)
to all existing tables and creates new sync-related tables (SyncDevice, SyncLog).
Run this to update existing databases for mobile sync support.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path


def get_all_table_names(cursor):
    """Get all table names from the database"""
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """
    )
    return [row[0] for row in cursor.fetchall()]


def migrate_database():
    """Add sync tracking fields to all tables and create new sync tables"""
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

        # Get all existing tables
        all_tables = get_all_table_names(cursor)
        print(f"📋 Found {len(all_tables)} tables to migrate")

        changes_made = False
        current_timestamp = datetime.now().isoformat()

        # Add sync fields to each existing table
        for table_name in all_tables:
            # Check existing columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            table_changes = False

            # Add created_at if it doesn't exist
            if "created_at" not in columns:
                print(f"  ➕ Adding 'created_at' to {table_name}...")
                cursor.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT '{current_timestamp}'
                """
                )
                table_changes = True

            # Add updated_at if it doesn't exist
            if "updated_at" not in columns:
                print(f"  ➕ Adding 'updated_at' to {table_name}...")
                cursor.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT '{current_timestamp}'
                """
                )
                table_changes = True

            # Add deleted_at if it doesn't exist
            if "deleted_at" not in columns:
                print(f"  ➕ Adding 'deleted_at' to {table_name}...")
                cursor.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN deleted_at TIMESTAMP NULL
                """
                )
                table_changes = True

            # Add version if it doesn't exist
            if "version" not in columns:
                print(f"  ➕ Adding 'version' to {table_name}...")
                cursor.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN version INTEGER NOT NULL DEFAULT 1
                """
                )
                table_changes = True

            if table_changes:
                changes_made = True
                print(f"  ✅ {table_name} migrated")

        # Create SyncDevice table if it doesn't exist
        if "sync_device" not in all_tables:
            print("➕ Creating 'sync_device' table...")
            cursor.execute(
                """
                CREATE TABLE sync_device (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id VARCHAR(255) UNIQUE NOT NULL,
                    device_name VARCHAR(255) NOT NULL,
                    auth_token VARCHAR(255) UNIQUE NOT NULL,
                    last_sync_at TIMESTAMP NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
            """
            )
            changes_made = True
            print("  ✅ sync_device table created")

        # Create SyncLog table if it doesn't exist
        if "sync_log" not in all_tables:
            print("➕ Creating 'sync_log' table...")
            cursor.execute(
                """
                CREATE TABLE sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    entity_type VARCHAR(100) NOT NULL,
                    entity_id INTEGER NOT NULL,
                    operation VARCHAR(20) NOT NULL,
                    synced_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (device_id) REFERENCES sync_device (id)
                )
            """
            )
            changes_made = True
            print("  ✅ sync_log table created")

        if changes_made:
            # Commit changes
            conn.commit()
            print("\n✅ Database migration completed successfully!")
            print("📱 Database is now ready for mobile sync!")
        else:
            print("\n✅ Database is already up to date - no migration needed")

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

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(db_dir, f"storymaster_backup_sync_migration_{timestamp}.db")

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
    print("🚀 Starting Storymaster Sync Migration")
    print("=" * 50)
    print("This migration will add sync tracking fields to all tables")
    print("and create new sync tables for mobile app synchronization.")
    print()

    # Create backup first
    print("Step 1: Creating backup...")
    backup_database()
    print()

    # Run migration
    print("Step 2: Running migration...")
    success = migrate_database()

    if success:
        print("\n🎉 Migration completed successfully!")
        print("📱 Your database is now ready for mobile sync.")
        print("🔄 You can now start the sync server and pair mobile devices.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        print("💾 Your original database backup is available if needed.")
        exit(1)
