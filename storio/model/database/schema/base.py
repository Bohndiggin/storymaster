"""Holds base database datatypes for Lorekeeper"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Class to represent the users table"""

    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    username = Column(String(150), nullable=False, name="username")


class Project(Base):
    """Class to represent the project table"""

    __tablename__ = "project"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, name="user_id")
    
    user = relationship("User", foreign_keys=[user_id])


