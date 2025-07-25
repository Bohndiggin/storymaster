"""Holds base connection and engine"""

import os
from sqlalchemy import Engine, create_engine


engine = create_engine("sqlite:///storymaster.db")
test_engine = create_engine("sqlite:///test_storymaster.db")


def get_test_engine(_) -> Engine:
    """returns the test engine"""
    return test_engine
