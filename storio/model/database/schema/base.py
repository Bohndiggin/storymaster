"""Holds base database datatypes for Lorekeeper"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    """Class to represent the users table"""

    __tablename__ = "users"

    id = Column(Integer, nullable=False, primary_key=True, name="id")


class Project(Base):
    """Class to represent the project table"""

    __tablename__ = "project"

    id = Column(Integer, nullable=False, primary_key=True, name="id")


