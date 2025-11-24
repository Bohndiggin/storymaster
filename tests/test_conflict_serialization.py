#!/usr/bin/env python3
"""Test conflict serialization"""

import os
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import Actor
from storymaster.sync_server.models import ConflictInfo, EntityChange


def test_conflict_serialization():
    """Test how conflicts are serialized"""
    home_dir = os.path.expanduser("~")
    db_path = os.path.join(home_dir, ".local", "share", "storymaster", "storymaster.db")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        # Get Sir Carlisle
        stmt = select(Actor).where(Actor.id == 42)
        carlisle = session.execute(stmt).scalar_one_or_none()

        if not carlisle:
            print("Sir Carlisle not found!")
            return

        # Simulate mobile data (version 2 with Jones)
        mobile_data = {
            "id": 42,
            "first_name": "Carlisle",
            "middle_name": None,
            "last_name": "Jones",  # Mobile added this
            "title": "Sir",
            "actor_age": None,
            "setting_id": 1,
            "version": 2,
            "updated_at": "2025-11-24T20:55:34",
        }

        # Desktop data (current database state)
        desktop_data = carlisle.as_dict()

        print("Desktop data from database:")
        print(json.dumps(desktop_data, indent=2, default=str))
        print("\n" + "="*60 + "\n")

        # Create a conflict
        conflict = ConflictInfo(
            entity_type="actor",
            entity_id=42,
            mobile_version=2,
            desktop_version=1,
            mobile_updated_at=datetime.now(timezone.utc),
            desktop_updated_at=datetime.now(timezone.utc),
            mobile_data=mobile_data,
            desktop_data=desktop_data,
            resolution="merge",
        )

        print("Conflict object created successfully")
        print("\nConflict as JSON:")
        # Convert to dict and then to JSON to see what gets sent
        conflict_dict = conflict.model_dump()
        print(json.dumps(conflict_dict, indent=2, default=str))


if __name__ == "__main__":
    test_conflict_serialization()
