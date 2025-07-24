"""Holds base connection and engine"""

import os

from sqlalchemy import Engine, create_engine

# Default database connections - can be overridden by environment variables
DATABASE_CONNECTION = os.getenv("DATABASE_CONNECTION", "sqlite:///storymaster.db")
TEST_DATABASE_CONNECTION = os.getenv("TEST_DATABASE_CONNECTION", "sqlite:///test_storymaster.db")

engine = create_engine(DATABASE_CONNECTION)
test_engine = create_engine(TEST_DATABASE_CONNECTION)


def get_test_engine(_) -> Engine:
    """returns the test engine"""
    return test_engine
