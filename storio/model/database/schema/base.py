"""Holds base database datatypes for Lorekeeper"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class Users(Base):
    """Class to represent the users table"""


class Projects(Base):
    """Class to represent the projects table"""
