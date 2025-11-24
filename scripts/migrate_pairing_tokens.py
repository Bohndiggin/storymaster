#!/usr/bin/env python3
"""
Database Migration Script for Storymaster

This script adds the `sync_pairing_tokens` table to the database.
"""

import os
import sqlite3
from datetime import datetime


def migrate_database():
    """Create the sync_pairing_tokens table"""
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

        # Check if table already exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='sync_pairing_tokens'
        """
        )
        table_exists = cursor.fetchone()

        if table_exists:
            print("✅ 'sync_pairing_tokens' table already exists - no migration needed")
            conn.close()
            return True

        # Create SyncPairingToken table
        print("➕ Creating 'sync_pairing_tokens' table...")
        cursor.execute(
            """
            CREATE TABLE sync_pairing_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                version INTEGER NOT NULL DEFAULT 1,
                expires_at TIMESTAMP NOT NULL
            )
        """
        )
        print("  ✅ sync_pairing_tokens table created")

        # Commit changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")

        # Close connection
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ SQLite error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Storymaster Pairing Token Migration")
    print("=" * 50)
    print("This migration will add the `sync_pairing_tokens` table.")
    print()

    success = migrate_database()

    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        exit(1)
