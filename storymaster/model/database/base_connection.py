"""Holds base connection and engine"""

import os

from sqlalchemy import Engine, create_engine

# Use the same database path as initialization
home_dir = os.path.expanduser("~")
db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, "storymaster.db")
test_db_path = os.path.join(db_dir, "test_storymaster.db")

# Check if database exists, if not create it
if not os.path.exists(db_path):
    from storymaster.model.database.schema.base import BaseTable

    temp_engine = create_engine(f"sqlite:///{db_path}")
    BaseTable.metadata.create_all(temp_engine)
    temp_engine.dispose()

engine = create_engine(f"sqlite:///{db_path}")
test_engine = create_engine(f"sqlite:///{test_db_path}")

# Idempotently create any tables introduced after the DB was first
# initialized (e.g. SyncConflict). create_all skips existing tables, so this
# is safe to run on every startup.
from storymaster.model.database.schema.base import BaseTable as _BaseTable  # noqa: E402

_BaseTable.metadata.create_all(engine)


def get_test_engine(_) -> Engine:
    """returns the test engine"""
    return test_engine
