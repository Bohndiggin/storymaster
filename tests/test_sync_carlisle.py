#!/usr/bin/env python3
"""Test to check what data Sir Carlisle returns"""

import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import Actor


def test_carlisle_data():
    """Check what as_dict() returns for Sir Carlisle"""
    home_dir = os.path.expanduser("~")
    db_path = os.path.join(home_dir, ".local", "share", "storymaster", "storymaster.db")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        # Get Sir Carlisle
        stmt = select(Actor).where(Actor.id == 42)
        carlisle = session.execute(stmt).scalar_one_or_none()

        if carlisle:
            print(f"Found: {carlisle.first_name} {carlisle.last_name} - {carlisle.title}")
            print(f"Version: {carlisle.version}")
            print(f"Updated at: {carlisle.updated_at}")
            print("\nFull as_dict() output:")
            data = carlisle.as_dict()
            import json
            print(json.dumps(data, indent=2, default=str))
        else:
            print("Sir Carlisle not found!")


if __name__ == "__main__":
    test_carlisle_data()
