#!/usr/bin/env python3
"""
Database Migration Script for Storymaster - Fix PlotSectionType Capitalization

This script updates plot_section_type values in the litography_plot_sections table
to match the new capitalized PlotSectionType enum definition.

Migrations:
- "Tension lowers" → "Tension Lowers"
- "Tension sustains" → "Tension Sustains"
- "Increases tension" → "Tension Increases"
- "Singular moment" → "Singular Moment"

Run this to fix existing databases with old capitalization.
"""

import os
import sqlite3
from pathlib import Path


def migrate_plot_section_type():
    """Fix plot_section_type values to match new capitalization"""
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

        # Check if table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='litography_plot_section'
        """
        )
        if not cursor.fetchone():
            print("✅ Table litography_plot_section does not exist yet - skipping migration")
            conn.close()
            return True

        # Check if there are any values needing migration
        cursor.execute(
            """
            SELECT COUNT(*) FROM litography_plot_section
            WHERE plot_section_type IN (
                'Tension lowers',
                'Tension sustains',
                'Increases tension',
                'Singular moment'
            )
        """
        )
        old_values_count = cursor.fetchone()[0]

        if old_values_count == 0:
            print("✅ Database is already up to date - plot_section_type values use correct capitalization")
            conn.close()
            return True

        print(f"⚠️  Found {old_values_count} plot sections with old capitalization")
        print("   Updating to match PlotSectionType enum...")

        # Update all old values to new capitalization
        updates = [
            ("Tension lowers", "Tension Lowers"),
            ("Tension sustains", "Tension Sustains"),
            ("Increases tension", "Tension Increases"),
            ("Singular moment", "Singular Moment"),
        ]

        total_updated = 0
        for old_value, new_value in updates:
            cursor.execute(
                """
                UPDATE litography_plot_section
                SET plot_section_type = ?
                WHERE plot_section_type = ?
            """,
                (new_value, old_value),
            )
            rows_updated = cursor.rowcount
            if rows_updated > 0:
                print(f"   ✓ Updated {rows_updated} records: '{old_value}' → '{new_value}'")
                total_updated += rows_updated

        # Commit changes
        conn.commit()
        print()
        print(f"✅ Database migration completed successfully!")
        print(f"   Updated {total_updated} plot_section_type values")

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
    backup_path = os.path.join(
        db_dir, f"storymaster_backup_plot_section_{timestamp}.db"
    )

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
    print("🚀 Starting Storymaster PlotSectionType Migration")
    print("=" * 60)
    print()

    # Create backup first
    backup_database()
    print()

    # Run migration
    success = migrate_plot_section_type()

    if success:
        print()
        print("🎉 Migration completed successfully!")
        print("   Plot sections will now load without enum errors.")
    else:
        print()
        print("💥 Migration failed. Please check the error messages above.")
        exit(1)
