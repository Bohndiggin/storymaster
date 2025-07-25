#!/usr/bin/env python3
"""
SQLite Database Initialization Script for Storymaster

This script initializes a new SQLite database with the proper schema.
Run this before using the application for the first time.
"""

from sqlalchemy import create_engine

from storymaster.model.database.schema.base import BaseTable


def init_database():
    """Initialize SQLite database with schema"""
    # Use SQLite database in the data directory
    db_connection = "sqlite:///data/storymaster.db"

    print(f"Initializing database: {db_connection}")

    # Create engine
    engine = create_engine(db_connection)

    # Create all tables
    print("Creating database tables...")
    BaseTable.metadata.create_all(engine)

    print("✅ Database initialization complete!")
    print(f"Database file created at: {db_connection.replace('sqlite:///', '')}")

    return engine


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        exit(1)
