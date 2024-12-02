"""Holds base database datatypes for Lorekeeper"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseTable(DeclarativeBase):
    __abstract__ = True

    def as_dict(self):
        """
        Converts the instance into a dictionary.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class User(BaseTable):
    """Class to represent the users table"""

    __tablename__ = "user"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    username = mapped_column(String(150), nullable=False, name="username")


class Project(BaseTable):
    """Class to represent the project table"""

    __tablename__ = "project"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    name = mapped_column(String(120), nullable=True, name="name")
    description = mapped_column(Text, nullable=True, name="description")
    user_id = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, name="user_id"
    )

    user = relationship("User", foreign_keys=[user_id])


class LorekeeperGroup(BaseTable):
    """Class to represent the lorekeeper_group table

    This table is meant to keep lorekeeper tables together.
    """

    __tablename__ = "lorekeeper_group"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    name = mapped_column(String(120), nullable=True, name="name")
    description = mapped_column(Text, nullable=True, name="description")
    user_id = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, name="user_id"
    )

    user = relationship("User", foreign_keys=[user_id])
    project_to_group = relationship("ProjectToGroup", back_populates="group")


class ProjectToGroup(BaseTable):
    """Class to represent the project_to_group table

    Table is here so that projects can have many groups and groups can have many projects

    """

    __tablename__ = "project_to_group"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    project_id = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    project = relationship("Project", foreign_keys=[project_id])
    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


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


class LitographyNode(BaseTable):
    """Represents litography_node table"""

    __tablename__ = "litography_node"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    node_type = mapped_column(Enum(NodeType), nullable=False, name="node_type")
    node_height = mapped_column(Float, nullable=False, name="node_height")
    previous_node = mapped_column(Integer, nullable=True, name="previous_node")
    next_node = mapped_column(Integer, nullable=True, name="next_node")
    project_id = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyNotes(BaseTable):
    """Represents litography_notes table"""

    __tablename__ = "litography_notes"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    linked_node = mapped_column(
        Integer, ForeignKey("litography_node.id"), nullable=False, name="linked_node"
    )
    title = mapped_column(String(250), nullable=False, name="title")
    description = mapped_column(Text, nullable=True, name="description")
    project_id = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyPlot(BaseTable):
    """Represents litography_plot table"""

    __tablename__ = "litography_plot"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    project_id = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class LitographyPlotSection(BaseTable):
    """Represents litography_plot_section table"""

    __tablename__ = "litography_plot_section"

    id = mapped_column(Integer, nullable=False, primary_key=True, name="id")
    section_type = mapped_column(
        Enum(PlotSectionType), nullable=False, name="plot_section_type"
    )
    section_plot_id = mapped_column(
        Integer,
        ForeignKey("litography_plot.id"),
        nullable=False,
        name="section_plot_id",
    )

    section_plot = relationship("LitographyPlot", foreign_keys=[section_plot_id])


class LitographyArc(BaseTable):
    """Represents the litography_arc table"""

    __tablename__ = "litography_arc"

    id = mapped_column(Integer, nullable=True, primary_key=True, name="id")
    project_id = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project = relationship("Project", foreign_keys=[project_id])


class Class_(BaseTable):
    __tablename__ = "class"

    id = mapped_column(Integer, primary_key=True, name="id")
    class_name = mapped_column(String(255), name="class_name")
    class_description = mapped_column(Text, name="class_description")
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class Background(BaseTable):
    __tablename__ = "background"

    id = mapped_column(Integer, primary_key=True)
    background_name = mapped_column(String(255))
    background_description = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class Race(BaseTable):
    __tablename__ = "race"

    id = mapped_column(Integer, primary_key=True)
    race_name = mapped_column(String(255))
    race_description = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    sub_race = relationship("SubRace", back_populates="race")


class SubRace(BaseTable):
    __tablename__ = "sub_race"

    id = mapped_column(Integer, primary_key=True)
    parent_race_id = mapped_column(Integer, ForeignKey("race.id"))
    sub_race_name = mapped_column(String(255))
    sub_race_description = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    race = relationship("Race", back_populates="sub_race")


class Actor(BaseTable):
    __tablename__ = "actor"

    id = mapped_column(Integer, primary_key=True, nullable=False, name="id")
    first_name = mapped_column(Text, nullable=True, name="first_name")
    middle_name = mapped_column(Text, nullable=True, name="middle_name")
    last_name = mapped_column(Text, nullable=True, name="last_name")
    title = mapped_column(Text, nullable=True, name="title")
    actor_age = mapped_column(Integer, nullable=True, name="actor_age")
    class_id = mapped_column(
        Integer, ForeignKey("class.id"), nullable=True, name="class_id"
    )
    actor_level = mapped_column(Integer, nullable=True, name="actor_level")
    background_id = mapped_column(
        Integer, ForeignKey("background.id"), nullable=True, name="background_id"
    )
    job = mapped_column(Text, nullable=True, name="job")
    actor_role = mapped_column(Text, nullable=True, name="actor_role")
    race_id = mapped_column(
        Integer, ForeignKey("race.id"), nullable=True, name="race_id"
    )
    sub_race_id = mapped_column(
        Integer, ForeignKey("sub_race.id"), nullable=True, name="sub_race_id"
    )
    alignment = mapped_column(String(2), nullable=True, name="alignment")
    strength = mapped_column(Integer, nullable=True, name="strength")
    dexterity = mapped_column(Integer, nullable=True, name="dexterity")
    constitution = mapped_column(Integer, nullable=True, name="constitution")
    intelligence = mapped_column(Integer, nullable=True, name="intelligence")
    wisdom = mapped_column(Integer, nullable=True, name="wisdom")
    charisma = mapped_column(Integer, nullable=True, name="charisma")
    ideal = mapped_column(Text, nullable=True, name="ideal")
    bond = mapped_column(Text, nullable=True, name="bond")
    flaw = mapped_column(Text, nullable=True, name="flaw")
    appearance = mapped_column(Text, nullable=True, name="appearance")
    strengths = mapped_column(Text, nullable=True, name="strengths")
    weaknesses = mapped_column(Text, nullable=True, name="weaknesses")
    notes = mapped_column(Text, nullable=True, name="notes")
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    class_ = relationship("Class_", foreign_keys=[class_id])
    background = relationship("Background", foreign_keys=[background_id])
    race = relationship("Race", foreign_keys=[race_id])
    sub_race = relationship("SubRace", foreign_keys=[sub_race_id])


class ActorAOnBRelations(BaseTable):
    __tablename__ = "actor_a_on_b_relations"

    id = mapped_column(Integer, primary_key=True)
    actor_a_id = mapped_column(Integer, ForeignKey("actor.id"))
    actor_b_id = mapped_column(Integer, ForeignKey("actor.id"))
    overall = mapped_column(String)
    economically = mapped_column(String)
    power_dynamic = mapped_column(String)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    actor_a = relationship("Actor", foreign_keys=[actor_a_id])
    actor_b = relationship("Actor", foreign_keys=[actor_b_id])


class Skills(BaseTable):
    __tablename__ = "skills"

    id = mapped_column(Integer, primary_key=True)
    skill_name = mapped_column(String(255))
    skill_description = mapped_column(Text)
    skill_trait = mapped_column(String(255))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class ActorToSkills(BaseTable):
    __tablename__ = "actor_to_skills"

    id = mapped_column(Integer, primary_key=True)
    actor_id = mapped_column(Integer, ForeignKey("actor.id"))
    skill_id = mapped_column(Integer, ForeignKey("skills.id"))
    skill_level = mapped_column(Integer)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class Faction(BaseTable):
    __tablename__ = "faction"

    id = mapped_column(Integer, primary_key=True)
    faction_name = mapped_column(String(255))
    faction_description = mapped_column(Text)
    goals = mapped_column(Text)
    faction_values = mapped_column(Text)
    faction_income_sources = mapped_column(Text)
    faction_expenses = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class FactionAOnBRelations(BaseTable):
    __tablename__ = "faction_a_on_b_relations"

    id = mapped_column(Integer, primary_key=True)
    faction_a_id = mapped_column(Integer, ForeignKey("faction.id"))
    faction_b_id = mapped_column(Integer, ForeignKey("faction.id"))
    overall = mapped_column(Text)
    economically = mapped_column(Text)
    politically = mapped_column(Text)
    opinion = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    faction_a = relationship("Faction", foreign_keys=[faction_a_id])
    faction_b = relationship("Faction", foreign_keys=[faction_b_id])


class FactionMembers(BaseTable):
    __tablename__ = "faction_members"

    id = mapped_column(Integer, primary_key=True)
    actor_id = mapped_column(Integer, ForeignKey("actor.id"))
    faction_id = mapped_column(Integer, ForeignKey("faction.id"))
    actor_role = mapped_column(String(255))
    relative_power = mapped_column(Integer)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    actor = relationship("Actor", foreign_keys=[actor_id])
    faction = relationship("Faction", foreign_keys=[faction_id])
    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class Location(BaseTable):
    __tablename__ = "location_"

    id = mapped_column(Integer, primary_key=True)
    location_name = mapped_column(String(255))
    location_type = mapped_column(String(255))
    location_description = mapped_column(Text)
    sights = mapped_column(Text)
    smells = mapped_column(Text)
    sounds = mapped_column(Text)
    feels = mapped_column(Text)
    tastes = mapped_column(Text)
    coordinates = mapped_column(String(255))
    location_flora_fauna = relationship(
        "LocationFloraFauna", back_populates="location_"
    )
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class LocationToFaction(BaseTable):
    __tablename__ = "location_to_faction"

    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    faction_id = mapped_column(Integer, ForeignKey("faction.id"))
    faction_presence = mapped_column(Float)
    faction_power = mapped_column(Float)
    notes = mapped_column(Text)

    location = relationship("Location", foreign_keys=[location_id])
    faction = relationship("Faction", foreign_keys=[faction_id])
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class LocationDungeon(BaseTable):
    __tablename__ = "location_dungeon"

    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    dangers = mapped_column(Text)
    traps = mapped_column(Text)
    secrets = mapped_column(Text)

    location = relationship("Location", foreign_keys=[location_id])
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class LocationCity(BaseTable):
    __tablename__ = "location_city"

    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    government = mapped_column(Text)

    location = relationship("Location", foreign_keys=[location_id])
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class LocationCityDistricts(BaseTable):
    __tablename__ = "location_city_districts"

    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    district_id = mapped_column(Integer, ForeignKey("location_.id"))

    location = relationship("Location", foreign_keys=[location_id])
    district = relationship("Location", foreign_keys=[district_id])
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class Resident(BaseTable):
    __tablename__ = "residents"

    id = mapped_column(Integer, primary_key=True)
    actor_id = mapped_column(Integer, ForeignKey("actor.id"))
    location_id = mapped_column(Integer, ForeignKey("location_.id"))

    actor = relationship("Actor", foreign_keys=[actor_id])
    location = relationship("Location", foreign_keys=[location_id])
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class LocationFloraFauna(BaseTable):
    __tablename__ = "location_flora_fauna"

    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    living_name = mapped_column(String(255))
    living_description = mapped_column(Text)
    living_type = mapped_column(Text)

    location_ = relationship("Location", back_populates="location_flora_fauna")
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class History(BaseTable):
    __tablename__ = "history"

    id = mapped_column(Integer, primary_key=True)
    event_name = mapped_column(String(255))
    event_year = mapped_column(Integer)
    event_description = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class HistoryActor(BaseTable):
    __tablename__ = "history_actor"

    id = mapped_column(Integer, primary_key=True)
    history_id = mapped_column(Integer, ForeignKey("history.id"))
    actor_id = mapped_column(Integer, ForeignKey("actor.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    history = relationship("History", foreign_keys=[history_id])
    actor = relationship("Actor", foreign_keys=[actor_id])
    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class HistoryLocation(BaseTable):
    __tablename__ = "history_location"

    id = mapped_column(Integer, primary_key=True)
    history_id = mapped_column(Integer, ForeignKey("history.id"))
    location_id = mapped_column(Integer, ForeignKey("location_.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    history = relationship("History", foreign_keys=[history_id])
    location = relationship("Location", foreign_keys=[location_id])


class HistoryFaction(BaseTable):
    __tablename__ = "history_faction"

    id = mapped_column(Integer, primary_key=True)
    history_id = mapped_column(Integer, ForeignKey("history.id"))
    faction_id = mapped_column(Integer, ForeignKey("faction.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    history = relationship("History", foreign_keys=[history_id])
    faction = relationship("Faction", foreign_keys=[faction_id])


class Object_(BaseTable):
    __tablename__ = "object_"

    id = mapped_column(Integer, primary_key=True)
    object_name = mapped_column(String(255))
    object_description = mapped_column(Text)
    object_value = mapped_column(Integer)
    rarity = mapped_column(String(255))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class HistoryObject(BaseTable):
    __tablename__ = "history_object"

    id = mapped_column(Integer, primary_key=True)
    history_id = mapped_column(Integer, ForeignKey("history.id"))
    object_id = mapped_column(Integer, ForeignKey("object_.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    history = relationship("History", foreign_keys=[history_id])
    object = relationship("Object_", foreign_keys=[object_id])


class ObjectToOwner(BaseTable):
    __tablename__ = "object_to_owner"

    id = mapped_column(Integer, primary_key=True)
    object_id = mapped_column(Integer, ForeignKey("object_.id"))
    actor_id = mapped_column(Integer, ForeignKey("actor.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    object = relationship("Object_", foreign_keys=[object_id])
    actor = relationship("Actor", foreign_keys=[actor_id])


class WorldData(BaseTable):
    __tablename__ = "world_data"

    id = mapped_column(Integer, primary_key=True)
    data_name = mapped_column(String(255))
    data_description = mapped_column(Text)
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])


class HistoryWorldData(BaseTable):
    __tablename__ = "history_world_data"

    id = mapped_column(Integer, primary_key=True)
    history_id = mapped_column(Integer, ForeignKey("history.id"))
    world_data_id = mapped_column(Integer, ForeignKey("world_data.id"))
    group_id = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group = relationship("LorekeeperGroup", foreign_keys=[group_id])
    history = relationship("History", foreign_keys=[history_id])
    world_data = relationship("WorldData", foreign_keys=[world_data_id])


class LitographyNoteToActor(BaseTable):
    """Represents litography_note_to_actor table"""

    __tablename__ = "litography_note_to_actor"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    actor_id = Column(Integer, ForeignKey("actor.id"), name="actor_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToBackground(BaseTable):
    """Represents litography_note_to_background table"""

    __tablename__ = "litography_note_to_background"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    background_id = Column(Integer, ForeignKey("background.id"), name="background_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToFaction(BaseTable):
    """Represents litography_note_to_faction table"""

    __tablename__ = "litography_note_to_faction"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    faction_id = Column(Integer, ForeignKey("faction.id"), name="faction_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToLocation(BaseTable):
    """Represents litography_note_to_location table"""

    __tablename__ = "litography_note_to_location"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    location_id = Column(Integer, ForeignKey("location_.id"), name="location_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToHistory(BaseTable):
    """Represents litography_note_to_history table"""

    __tablename__ = "litography_note_to_history"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    history_id = Column(Integer, ForeignKey("history.id"), name="history_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToObject(BaseTable):
    """Represents litography_note_to_object table"""

    __tablename__ = "litography_note_to_object"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    object_id = Column(Integer, ForeignKey("object_.id"), name="object_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNoteToWorldData(BaseTable):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_note_to_world_data"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    note_id = Column(Integer, ForeignKey("litography_notes.id"), name="note_id")
    world_data_id = Column(Integer, ForeignKey("world_data.id"), name="world_data_id")

    note = relationship("LitographyNotes", foreign_keys=[note_id])


class LitographyNodeToPlotSection(BaseTable):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_node_to_plot_section"

    id = Column(Integer, nullable=False, primary_key=True, name="id")
    node_id = Column(Integer, ForeignKey("litography_node.id"), name="node_id")
    litography_plot_section_id = Column(
        Integer,
        ForeignKey("litography_plot_section.id"),
        name="litography_plot_section_id",
    )

    node = relationship("LitographyNode", foreign_keys=[node_id])


class ArcToNode(BaseTable):
    """Represents the arc_to_node table"""

    __tablename__ = "arc_to_node"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    node_id = Column(Integer, ForeignKey("litography_node.id"), name="node_id")
    arc_id = Column(Integer, ForeignKey("litography_arc.id"), name="arc_id")

    node = relationship("LitographyNode", foreign_keys=[node_id])
    arc = relationship("LitographyArc", foreign_keys=[arc_id])


class ArcToActor(BaseTable):
    """Represents the arc_to_actor table"""

    __tablename__ = "arc_to_actor"

    id = Column(Integer, nullable=True, primary_key=True, name="id")
    actor_id = Column(Integer, ForeignKey("actor.id"), nullable=False, name="actor_id")
    arc_id = Column(Integer, ForeignKey("arc.id"), nullable=False, name="arc_id")

    actor = relationship("Actor", foreign_keys=[actor_id])
