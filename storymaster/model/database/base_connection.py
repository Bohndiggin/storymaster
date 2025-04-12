"""Holds base connection and engine"""

import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

load_dotenv()


engine = create_engine(os.getenv("DATABASE_CONNECTION"))
test_engine = create_engine(os.getenv("TEST_DATABASE_CONNECTION"))


def get_test_engine(_) -> Engine:
    """returns the test engine"""
    return test_engine
