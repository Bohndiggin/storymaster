#!/usr/bin/env python3
"""
Adds sync_uuid column to every table and backfills a UUID for each existing row.

This is required for multi-device sync: integer auto-increment primary keys are
local to each database, so they collide when two devices both create new rows
independently. sync_uuid is the canonical cross-device identity.

Idempotent: re-running on a migrated DB is a no-op.
"""

import os
import shutil
import sqlite3
import sys
import uuid
from datetime import datetime


def get_db_path() -> str:
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
    return os.path.join(db_dir, "storymaster.db")


def get_all_table_names(cursor) -> list[str]:
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cursor.fetchall()]


def column_names(cursor, table: str) -> list[str]:
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def backup_database(db_path: str) -> None:
    if not os.path.exists(db_path):
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.replace(
        ".db", f"_backup_sync_uuid_{timestamp}.db"
    )
    shutil.copy2(db_path, backup)
    print(f"Backup written to {backup}")


def migrate(db_path: str) -> bool:
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}; run init_database.py first.")
        return False

    print(f"Migrating {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        tables = get_all_table_names(cursor)

        for table in tables:
            cols = column_names(cursor, table)
            has_sync_uuid = "sync_uuid" in cols
            has_id = "id" in cols

            if not has_sync_uuid:
                print(f"  Adding sync_uuid to {table}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN sync_uuid TEXT")

            if not has_id:
                # No PK to iterate by — skip backfill. This shouldn't happen
                # in the current schema but guard anyway.
                print(f"  {table} has no 'id' column; skipping backfill")
                continue

            cursor.execute(
                f"SELECT id FROM {table} WHERE sync_uuid IS NULL OR sync_uuid = ''"
            )
            rows = cursor.fetchall()
            if rows:
                print(f"  Backfilling {len(rows)} rows in {table}")
                cursor.executemany(
                    f"UPDATE {table} SET sync_uuid = ? WHERE id = ?",
                    [(str(uuid.uuid4()), row[0]) for row in rows],
                )

            # Create the unique index if it's missing. Named consistently so
            # repeat runs are no-ops.
            index_name = f"ix_{table}_sync_uuid_unique"
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                (index_name,),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    f"CREATE UNIQUE INDEX {index_name} ON {table}(sync_uuid)"
                )

        conn.commit()
        print("Migration complete.")
        return True

    except sqlite3.Error as e:
        conn.rollback()
        print(f"SQLite error: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = get_db_path()
    backup_database(db_path)
    ok = migrate(db_path)
    sys.exit(0 if ok else 1)
