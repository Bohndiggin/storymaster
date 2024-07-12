"""Holds base database datatypes for Lorekeeper"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    """Class to represent the users table"""


class Projects(Base):
    """Class to represent the projects table"""
