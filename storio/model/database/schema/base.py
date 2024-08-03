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
    name = Column(String(120), nullable=True, name="name")
    description = Column(Text, nullable=True, name="description")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, name="user_id")

    user = relationship("User", foreign_keys=[user_id])


class LorekeeperGroup(Base):
    """Class to represent the lorekeeper_group table

    This table is meant to keep lorekeeper tables together.
    """

    __tablename__ = "lorekeeper_group"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, name="user_id")

    user = relationship("User", foreign_keys=[user_id])


class ProjectToGroup(Base):
    """Class to represent the project_to_group table

    Table is here so that projects can have many groups and groups can have many projects

    """

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    project_id = Column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False, name="group_id")

    project = relationship("Project", foreign_keys=[project_id])
    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
