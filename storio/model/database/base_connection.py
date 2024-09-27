"""Holds base connection and engine"""

import os

from dotenv import load_dotenv
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session

from storio.model.database import common_queries

load_dotenv()


engine = create_engine(os.getenv("DATABASE_CONNECTION"))

with Session(engine) as session:
    classes = session.execute(
        common_queries.get_lorekeeper_classes_from_group(1)
    ).scalar()
    print(classes)
