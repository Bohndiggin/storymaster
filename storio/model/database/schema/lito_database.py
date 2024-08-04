"""Holds base database datatypes for Litographer"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

from storio.model.database.base_connection import Base

class PlotSectionType(enum.Enum):
    """Enum of different Types of Plot Section"""

    LOWER = "Tension lowers"
    FLAT = "Tension sustains"
    RISING = "Increases tension"
    POINT = "Singular moment"


class NodeType(enum.Enum):
    """Different types of story Nodes"""

    EXPOSITION = "exposition"
    ACTION = "action"
    REACTION = "reaction"
    TWIST = "twist"
    DEVELOPMENT = "development"


class NoteType(enum.Enum):
    """Types of notes that can be added to nodes"""

    WHAT = "what"
    WHY = "why"
    HOW = "how"
    WHEN = "when"
    WHERE = "where"
    OTHER = "other"


class LitographyNode(Base):
    """Represents litography_node table"""

    __tablename__ = "litography_node"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    node_type = Column(Enum(NodeType), nullable=False, name="node_type")
    node_height = Column(Float, nullable=False, name="node_height")
    previous_node = Column(Integer, nullable=True, name="previous_node")
    next_node = Column(Integer, nullable=True, name="next_node")
    project_id = Column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyNotes(Base):
    """Represents litography_notes table"""

    __tablename__ = "litography_notes"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    linked_node = Column(
        Integer, ForeignKey("litography_node.id"), nullable=False, name="linked_node"
    )
    title = Column(String(250), nullable=False, name="title")
    description = Column(Text, nullable=True, name="description")
    project_id = Column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyPlot(Base):
    """Represents litography_plot table"""

    __tablename__ = "litography_plot"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    project_id = Column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyPlotSection(Base):
    """Represents litography_plot_section table"""

    __tablename__ = "litography_plot_section"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    section_type = Column(
        Enum(PlotSectionType), nullable=False, name="plot_section_type"
    )
    section_plot_id = Column(
        Integer,
        ForeignKey("litography_plot.id"),
        nullable=False,
        name="section_plot_id",
    )

    section_plot = relationship("LitographyPlot", foreign_keys=[section_plot_id])


class LitographyArc(Base):
    """Represents the litography_arc table"""

    __tablename__ = "litography_arc"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    project_id = Column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])
