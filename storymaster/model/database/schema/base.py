"""Holds base database datatypes for Lorekeeper"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseTable(DeclarativeBase):
    __abstract__ = True

    def as_dict(self):
        """
        Converts the instance into a dictionary. Used for display only.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class User(BaseTable):
    """Class to represent the users table"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    username: Mapped[str] = mapped_column(String(150), nullable=False, name="username")

    projects: Mapped[list["Project"]] = relationship(back_populates="user")
    lorekeeper_groups: Mapped[list["LorekeeperGroup"]] = relationship(
        back_populates="user"
    )


class Project(BaseTable):
    """Class to represent the project table"""

    __tablename__ = "project"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    name: Mapped[str | None] = mapped_column(String(120), nullable=True, name="name")
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, name="user_id"
    )

    user: Mapped["User"] = relationship(back_populates="projects")
    project_to_groups: Mapped[list["ProjectToGroup"]] = relationship(
        back_populates="project"
    )
    litography_nodes: Mapped[list["LitographyNode"]] = relationship(
        back_populates="project"
    )
    litography_notes: Mapped[list["LitographyNotes"]] = relationship(
        back_populates="project"
    )
    litography_plots: Mapped[list["LitographyPlot"]] = relationship(
        back_populates="project"
    )
    litography_arcs: Mapped[list["LitographyArc"]] = relationship(
        back_populates="project"
    )


class LorekeeperGroup(BaseTable):
    """Class to represent the lorekeeper_group table"""

    __tablename__ = "lorekeeper_group"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    name: Mapped[str | None] = mapped_column(String(120), nullable=True, name="name")
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, name="user_id"
    )

    user: Mapped["User"] = relationship(back_populates="lorekeeper_groups")
    project_to_group: Mapped[list["ProjectToGroup"]] = relationship(
        back_populates="group"
    )
    classes: Mapped[list["Class_"]] = relationship(back_populates="group")
    backgrounds: Mapped[list["Background"]] = relationship(back_populates="group")
    races: Mapped[list["Race"]] = relationship(back_populates="group")
    sub_races: Mapped[list["SubRace"]] = relationship(back_populates="group")
    actors: Mapped[list["Actor"]] = relationship(back_populates="group")
    actor_relations: Mapped[list["ActorAOnBRelations"]] = relationship(
        back_populates="group"
    )
    skills: Mapped[list["Skills"]] = relationship(back_populates="group")
    actor_to_skills: Mapped[list["ActorToSkills"]] = relationship(
        back_populates="group"
    )
    factions: Mapped[list["Faction"]] = relationship(back_populates="group")
    faction_relations: Mapped[list["FactionAOnBRelations"]] = relationship(
        back_populates="group"
    )
    faction_members: Mapped[list["FactionMembers"]] = relationship(
        back_populates="group"
    )
    locations: Mapped[list["Location"]] = relationship(back_populates="group")
    location_to_factions: Mapped[list["LocationToFaction"]] = relationship(
        back_populates="group"
    )
    location_dungeons: Mapped[list["LocationDungeon"]] = relationship(
        back_populates="group"
    )
    location_cities: Mapped[list["LocationCity"]] = relationship(back_populates="group")
    location_city_districts: Mapped[list["LocationCityDistricts"]] = relationship(
        back_populates="group"
    )
    residents: Mapped[list["Resident"]] = relationship(back_populates="group")
    location_flora_fauna: Mapped[list["LocationFloraFauna"]] = relationship(
        back_populates="group"
    )
    histories: Mapped[list["History"]] = relationship(back_populates="group")
    history_actors: Mapped[list["HistoryActor"]] = relationship(back_populates="group")
    history_locations: Mapped[list["HistoryLocation"]] = relationship(
        back_populates="group"
    )
    history_factions: Mapped[list["HistoryFaction"]] = relationship(
        back_populates="group"
    )
    objects: Mapped[list["Object_"]] = relationship(back_populates="group")
    history_objects: Mapped[list["HistoryObject"]] = relationship(
        back_populates="group"
    )
    object_owners: Mapped[list["ObjectToOwner"]] = relationship(back_populates="group")
    world_data: Mapped[list["WorldData"]] = relationship(back_populates="group")
    history_world_data: Mapped[list["HistoryWorldData"]] = relationship(
        back_populates="group"
    )


class ProjectToGroup(BaseTable):
    """Class to represent the project_to_group table"""

    __tablename__ = "project_to_group"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    project: Mapped["Project"] = relationship(back_populates="project_to_groups")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="project_to_group")


class PlotSectionType(enum.Enum):
    LOWER = "Tension lowers"
    FLAT = "Tension sustains"
    RISING = "Increases tension"
    POINT = "Singular moment"


class NodeType(enum.Enum):
    EXPOSITION = "exposition"
    ACTION = "action"
    REACTION = "reaction"
    TWIST = "twist"
    DEVELOPMENT = "development"
    OTHER = "other"


class NoteType(enum.Enum):
    WHAT = "what"
    WHY = "why"
    HOW = "how"
    WHEN = "when"
    WHERE = "where"
    OTHER = "other"


class LitographyNode(BaseTable):
    """Represents litography_node table"""

    __tablename__ = "litography_node"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    node_type: Mapped[NodeType] = mapped_column(
        Enum(NodeType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        name="node_type",
    )
    node_height: Mapped[float] = mapped_column(
        Float, nullable=False, name="node_height"
    )
    previous_node: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="previous_node"
    )
    next_node: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="next_node"
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project: Mapped["Project"] = relationship(back_populates="litography_nodes")
    notes: Mapped[list["LitographyNotes"]] = relationship(back_populates="linked_node")
    plot_sections: Mapped[list["LitographyNodeToPlotSection"]] = relationship(
        back_populates="node"
    )
    arcs: Mapped[list["ArcToNode"]] = relationship(back_populates="node")


class LitographyNotes(BaseTable):
    """Represents litography_notes table"""

    __tablename__ = "litography_notes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False, name="title")
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    note_type: Mapped[NoteType] = mapped_column(
        Enum(NoteType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        name="note_type",
    )
    linked_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_node.id"), nullable=False, name="linked_node"
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    linked_node: Mapped["LitographyNode"] = relationship(back_populates="notes")
    project: Mapped["Project"] = relationship(back_populates="litography_notes")
    actors: Mapped[list["LitographyNoteToActor"]] = relationship(back_populates="note")
    backgrounds: Mapped[list["LitographyNoteToBackground"]] = relationship(
        back_populates="note"
    )
    factions: Mapped[list["LitographyNoteToFaction"]] = relationship(
        back_populates="note"
    )
    locations: Mapped[list["LitographyNoteToLocation"]] = relationship(
        back_populates="note"
    )
    histories: Mapped[list["LitographyNoteToHistory"]] = relationship(
        back_populates="note"
    )
    objects: Mapped[list["LitographyNoteToObject"]] = relationship(
        back_populates="note"
    )
    world_data: Mapped[list["LitographyNoteToWorldData"]] = relationship(
        back_populates="note"
    )
    classes: Mapped[list["LitographyNoteToClass"]] = relationship(back_populates="note")
    races: Mapped[list["LitographyNoteToRace"]] = relationship(back_populates="note")
    sub_races: Mapped[list["LitographyNoteToSubRace"]] = relationship(
        back_populates="note"
    )
    skills: Mapped[list["LitographyNoteToSkills"]] = relationship(back_populates="note")


class LitographyPlot(BaseTable):
    """Represents litography_plot table"""

    __tablename__ = "litography_plot"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False, name="title")
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project: Mapped["Project"] = relationship(back_populates="litography_plots")
    plot_sections: Mapped[list["LitographyPlotSection"]] = relationship(
        back_populates="section_plot"
    )


class LitographyPlotSection(BaseTable):
    """Represents litography_plot_section table"""

    __tablename__ = "litography_plot_section"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    plot_section_type: Mapped[PlotSectionType] = mapped_column(
        Enum(PlotSectionType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        name="plot_section_type",
    )
    plot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_plot.id"), nullable=False, name="plot_id"
    )

    section_plot: Mapped["LitographyPlot"] = relationship(
        back_populates="plot_sections"
    )
    nodes: Mapped[list["LitographyNodeToPlotSection"]] = relationship(
        back_populates="plot_section"
    )


class LitographyNodeToPlotSection(BaseTable):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_node_to_plot_section"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    node_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_node.id"), name="node_id"
    )
    litography_plot_section_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("litography_plot_section.id"),
        name="litography_plot_section_id",
    )

    node: Mapped["LitographyNode"] = relationship(back_populates="plot_sections")
    plot_section: Mapped["LitographyPlotSection"] = relationship(back_populates="nodes")


class LitographyArc(BaseTable):
    """Represents the litography_arc table"""

    __tablename__ = "litography_arc"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("project.id"), nullable=False, name="project_id"
    )

    project: Mapped["Project"] = relationship(back_populates="litography_arcs")
    nodes: Mapped[list["ArcToNode"]] = relationship(back_populates="arc")
    actors: Mapped[list["ArcToActor"]] = relationship(back_populates="arc")


class Class_(BaseTable):
    __tablename__ = "class"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    class_name: Mapped[str | None] = mapped_column(String(255), name="class_name")
    class_description: Mapped[str | None] = mapped_column(
        Text, name="class_description"
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="classes")
    actors: Mapped[list["Actor"]] = relationship(back_populates="class_")
    notes_to: Mapped[list["LitographyNoteToClass"]] = relationship(
        back_populates="class_"
    )


class Background(BaseTable):
    __tablename__ = "background"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    background_name: Mapped[str | None] = mapped_column(String(255))
    background_description: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="backgrounds")
    actors: Mapped[list["Actor"]] = relationship(back_populates="background")
    notes_to: Mapped[list["LitographyNoteToBackground"]] = relationship(
        back_populates="background"
    )


class Race(BaseTable):
    __tablename__ = "race"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    race_name: Mapped[str | None] = mapped_column(String(255))
    race_description: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="races")
    sub_races: Mapped[list["SubRace"]] = relationship(back_populates="race")
    actors: Mapped[list["Actor"]] = relationship(back_populates="race")
    notes_to: Mapped[list["LitographyNoteToRace"]] = relationship(back_populates="race")


class SubRace(BaseTable):
    __tablename__ = "sub_race"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    parent_race_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("race.id"))
    sub_race_name: Mapped[str | None] = mapped_column(String(255))
    sub_race_description: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="sub_races")
    race: Mapped["Race"] = relationship(back_populates="sub_races")
    actors: Mapped[list["Actor"]] = relationship(back_populates="sub_race")
    notes_to: Mapped[list["LitographyNoteToSubRace"]] = relationship(
        back_populates="sub_race"
    )


class Actor(BaseTable):
    __tablename__ = "actor"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    first_name: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="first_name"
    )
    middle_name: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="middle_name"
    )
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True, name="last_name")
    title: Mapped[str | None] = mapped_column(Text, nullable=True, name="title")
    actor_age: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="actor_age"
    )
    class_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("class.id"), nullable=True, name="class_id"
    )
    actor_level: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="actor_level"
    )
    background_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("background.id"), nullable=True, name="background_id"
    )
    job: Mapped[str | None] = mapped_column(Text, nullable=True, name="job")
    actor_role: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="actor_role"
    )
    race_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("race.id"), nullable=True, name="race_id"
    )
    sub_race_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sub_race.id"), nullable=True, name="sub_race_id"
    )
    alignment: Mapped[str | None] = mapped_column(
        String(2), nullable=True, name="alignment"
    )
    strength: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="strength"
    )
    dexterity: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="dexterity"
    )
    constitution: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="constitution"
    )
    intelligence: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="intelligence"
    )
    wisdom: Mapped[int | None] = mapped_column(Integer, nullable=True, name="wisdom")
    charisma: Mapped[int | None] = mapped_column(
        Integer, nullable=True, name="charisma"
    )
    ideal: Mapped[str | None] = mapped_column(Text, nullable=True, name="ideal")
    bond: Mapped[str | None] = mapped_column(Text, nullable=True, name="bond")
    flaw: Mapped[str | None] = mapped_column(Text, nullable=True, name="flaw")
    appearance: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="appearance"
    )
    strengths: Mapped[str | None] = mapped_column(Text, nullable=True, name="strengths")
    weaknesses: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="weaknesses"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, name="notes")
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="actors")
    class_: Mapped["Class_"] = relationship(back_populates="actors")
    background: Mapped["Background"] = relationship(back_populates="actors")
    race: Mapped["Race"] = relationship(back_populates="actors")
    sub_race: Mapped["SubRace"] = relationship(back_populates="actors")
    actor_a_relations: Mapped[list["ActorAOnBRelations"]] = relationship(
        foreign_keys="ActorAOnBRelations.actor_a_id", back_populates="actor_a"
    )
    actor_b_relations: Mapped[list["ActorAOnBRelations"]] = relationship(
        foreign_keys="ActorAOnBRelations.actor_b_id", back_populates="actor_b"
    )
    skills: Mapped[list["ActorToSkills"]] = relationship(back_populates="actor")
    faction_memberships: Mapped[list["FactionMembers"]] = relationship(
        back_populates="actor"
    )
    residences: Mapped[list["Resident"]] = relationship(back_populates="actor")
    history: Mapped[list["HistoryActor"]] = relationship(back_populates="actor")
    objects: Mapped[list["ObjectToOwner"]] = relationship(back_populates="actor")
    notes_to: Mapped[list["LitographyNoteToActor"]] = relationship(
        back_populates="actor"
    )
    arcs: Mapped[list["ArcToActor"]] = relationship(back_populates="actor")


class ActorAOnBRelations(BaseTable):
    __tablename__ = "actor_a_on_b_relations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    actor_a_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    actor_b_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    overall: Mapped[str | None] = mapped_column(String)
    economically: Mapped[str | None] = mapped_column(String)
    power_dynamic: Mapped[str | None] = mapped_column(String)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="actor_relations")
    actor_a: Mapped["Actor"] = relationship(
        foreign_keys=[actor_a_id], back_populates="actor_a_relations"
    )
    actor_b: Mapped["Actor"] = relationship(
        foreign_keys=[actor_b_id], back_populates="actor_b_relations"
    )


class Skills(BaseTable):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    skill_name: Mapped[str | None] = mapped_column(String(255))
    skill_description: Mapped[str | None] = mapped_column(Text)
    skill_trait: Mapped[str | None] = mapped_column(String(255))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="skills")
    actors: Mapped[list["ActorToSkills"]] = relationship(back_populates="skill")
    notes_to: Mapped[list["LitographyNoteToSkills"]] = relationship(
        back_populates="skill"
    )


class ActorToSkills(BaseTable):
    __tablename__ = "actor_to_skills"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    skill_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("skills.id"))
    skill_level: Mapped[int | None] = mapped_column(Integer)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="actor_to_skills")
    actor: Mapped["Actor"] = relationship(back_populates="skills")
    skill: Mapped["Skills"] = relationship(back_populates="actors")


class Faction(BaseTable):
    __tablename__ = "faction"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    faction_name: Mapped[str | None] = mapped_column(String(255))
    faction_description: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[str | None] = mapped_column(Text)
    faction_values: Mapped[str | None] = mapped_column(Text)
    faction_income_sources: Mapped[str | None] = mapped_column(Text)
    faction_expenses: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="factions")
    faction_a_relations: Mapped[list["FactionAOnBRelations"]] = relationship(
        foreign_keys="FactionAOnBRelations.faction_a_id", back_populates="faction_a"
    )
    faction_b_relations: Mapped[list["FactionAOnBRelations"]] = relationship(
        foreign_keys="FactionAOnBRelations.faction_b_id", back_populates="faction_b"
    )
    members: Mapped[list["FactionMembers"]] = relationship(back_populates="faction")
    locations: Mapped[list["LocationToFaction"]] = relationship(
        back_populates="faction"
    )
    history: Mapped[list["HistoryFaction"]] = relationship(back_populates="faction")
    notes_to: Mapped[list["LitographyNoteToFaction"]] = relationship(
        back_populates="faction"
    )


class FactionAOnBRelations(BaseTable):
    __tablename__ = "faction_a_on_b_relations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    faction_a_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    faction_b_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    overall: Mapped[str | None] = mapped_column(Text)
    economically: Mapped[str | None] = mapped_column(Text)
    politically: Mapped[str | None] = mapped_column(Text)
    opinion: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="faction_relations")
    faction_a: Mapped["Faction"] = relationship(
        foreign_keys=[faction_a_id], back_populates="faction_a_relations"
    )
    faction_b: Mapped["Faction"] = relationship(
        foreign_keys=[faction_b_id], back_populates="faction_b_relations"
    )


class FactionMembers(BaseTable):
    __tablename__ = "faction_members"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    actor_role: Mapped[str | None] = mapped_column(String(255))
    relative_power: Mapped[int | None] = mapped_column(Integer)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    actor: Mapped["Actor"] = relationship(back_populates="faction_memberships")
    faction: Mapped["Faction"] = relationship(back_populates="members")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="faction_members")


class Location(BaseTable):
    __tablename__ = "location_"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_name: Mapped[str | None] = mapped_column(String(255))
    location_type: Mapped[str | None] = mapped_column(String(255))
    location_description: Mapped[str | None] = mapped_column(Text)
    sights: Mapped[str | None] = mapped_column(Text)
    smells: Mapped[str | None] = mapped_column(Text)
    sounds: Mapped[str | None] = mapped_column(Text)
    feels: Mapped[str | None] = mapped_column(Text)
    tastes: Mapped[str | None] = mapped_column(Text)
    coordinates: Mapped[str | None] = mapped_column(String(255))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location_flora_fauna: Mapped[list["LocationFloraFauna"]] = relationship(
        back_populates="location_"
    )
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="locations")
    factions: Mapped[list["LocationToFaction"]] = relationship(
        back_populates="location"
    )
    dungeons: Mapped[list["LocationDungeon"]] = relationship(back_populates="location")
    cities: Mapped[list["LocationCity"]] = relationship(back_populates="location")
    city_districts: Mapped[list["LocationCityDistricts"]] = relationship(
        foreign_keys="LocationCityDistricts.location_id", back_populates="location"
    )
    districts_in_city: Mapped[list["LocationCityDistricts"]] = relationship(
        foreign_keys="LocationCityDistricts.district_id", back_populates="district"
    )
    residents: Mapped[list["Resident"]] = relationship(back_populates="location")
    history: Mapped[list["HistoryLocation"]] = relationship(back_populates="location")
    notes_to: Mapped[list["LitographyNoteToLocation"]] = relationship(
        back_populates="location"
    )


class LocationToFaction(BaseTable):
    __tablename__ = "location_to_faction"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    faction_presence: Mapped[float | None] = mapped_column(Float)
    faction_power: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location: Mapped["Location"] = relationship(back_populates="factions")
    faction: Mapped["Faction"] = relationship(back_populates="locations")
    group: Mapped["LorekeeperGroup"] = relationship(
        back_populates="location_to_factions"
    )


class LocationDungeon(BaseTable):
    __tablename__ = "location_dungeon"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    dangers: Mapped[str | None] = mapped_column(Text)
    traps: Mapped[str | None] = mapped_column(Text)
    secrets: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location: Mapped["Location"] = relationship(back_populates="dungeons")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="location_dungeons")


class LocationCity(BaseTable):
    __tablename__ = "location_city"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    government: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location: Mapped["Location"] = relationship(back_populates="cities")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="location_cities")


class LocationCityDistricts(BaseTable):
    __tablename__ = "location_city_districts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    district_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location: Mapped["Location"] = relationship(
        foreign_keys=[location_id], back_populates="city_districts"
    )
    district: Mapped["Location"] = relationship(
        foreign_keys=[district_id], back_populates="districts_in_city"
    )
    group: Mapped["LorekeeperGroup"] = relationship(
        back_populates="location_city_districts"
    )


class Resident(BaseTable):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    actor: Mapped["Actor"] = relationship(back_populates="residences")
    location: Mapped["Location"] = relationship(back_populates="residents")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="residents")


class LocationFloraFauna(BaseTable):
    __tablename__ = "location_flora_fauna"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    living_name: Mapped[str | None] = mapped_column(String(255))
    living_description: Mapped[str | None] = mapped_column(Text)
    living_type: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    location_: Mapped["Location"] = relationship(back_populates="location_flora_fauna")
    group: Mapped["LorekeeperGroup"] = relationship(
        back_populates="location_flora_fauna"
    )


class History(BaseTable):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    event_name: Mapped[str | None] = mapped_column(String(255))
    event_year: Mapped[int | None] = mapped_column(Integer)
    event_description: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="histories")
    actors: Mapped[list["HistoryActor"]] = relationship(back_populates="history")
    locations: Mapped[list["HistoryLocation"]] = relationship(back_populates="history")
    factions: Mapped[list["HistoryFaction"]] = relationship(back_populates="history")
    objects: Mapped[list["HistoryObject"]] = relationship(back_populates="history")
    world_data: Mapped[list["HistoryWorldData"]] = relationship(
        back_populates="history"
    )
    notes_to: Mapped[list["LitographyNoteToHistory"]] = relationship(
        back_populates="history"
    )


class HistoryActor(BaseTable):
    __tablename__ = "history_actor"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    history: Mapped["History"] = relationship(back_populates="actors")
    actor: Mapped["Actor"] = relationship(back_populates="history")
    group: Mapped["LorekeeperGroup"] = relationship(back_populates="history_actors")


class HistoryLocation(BaseTable):
    __tablename__ = "history_location"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="history_locations")
    history: Mapped["History"] = relationship(back_populates="locations")
    location: Mapped["Location"] = relationship(back_populates="history")


class HistoryFaction(BaseTable):
    __tablename__ = "history_faction"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="history_factions")
    history: Mapped["History"] = relationship(back_populates="factions")
    faction: Mapped["Faction"] = relationship(back_populates="history")


class Object_(BaseTable):
    __tablename__ = "object_"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    object_name: Mapped[str | None] = mapped_column(String(255))
    object_description: Mapped[str | None] = mapped_column(Text)
    object_value: Mapped[int | None] = mapped_column(Integer)
    rarity: Mapped[str | None] = mapped_column(String(255))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="objects")
    history: Mapped[list["HistoryObject"]] = relationship(back_populates="object")
    owners: Mapped[list["ObjectToOwner"]] = relationship(back_populates="object")
    notes_to: Mapped[list["LitographyNoteToObject"]] = relationship(
        back_populates="object"
    )


class HistoryObject(BaseTable):
    __tablename__ = "history_object"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    object_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("object_.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="history_objects")
    history: Mapped["History"] = relationship(back_populates="objects")
    object: Mapped["Object_"] = relationship(back_populates="history")


class ObjectToOwner(BaseTable):
    __tablename__ = "object_to_owner"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    object_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("object_.id"))
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="object_owners")
    object: Mapped["Object_"] = relationship(back_populates="owners")
    actor: Mapped["Actor"] = relationship(back_populates="objects")


class WorldData(BaseTable):
    __tablename__ = "world_data"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    data_name: Mapped[str | None] = mapped_column(String(255))
    data_description: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="world_data")
    history: Mapped[list["HistoryWorldData"]] = relationship(
        back_populates="world_data"
    )
    notes_to: Mapped[list["LitographyNoteToWorldData"]] = relationship(
        back_populates="world_data"
    )


class HistoryWorldData(BaseTable):
    __tablename__ = "history_world_data"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    world_data_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("world_data.id")
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lorekeeper_group.id"), nullable=False, name="group_id"
    )

    group: Mapped["LorekeeperGroup"] = relationship(back_populates="history_world_data")
    history: Mapped["History"] = relationship(back_populates="world_data")
    world_data: Mapped["WorldData"] = relationship(back_populates="history")


class LitographyNoteToActor(BaseTable):
    """Represents litography_note_to_actor table"""

    __tablename__ = "litography_note_to_actor"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    actor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("actor.id"), name="actor_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    actor: Mapped["Actor"] = relationship(back_populates="notes_to")


class LitographyNoteToBackground(BaseTable):
    """Represents litography_note_to_background table"""

    __tablename__ = "litography_note_to_background"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    background_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("background.id"), name="background_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    background: Mapped["Background"] = relationship()


class LitographyNoteToFaction(BaseTable):
    """Represents litography_note_to_faction table"""

    __tablename__ = "litography_note_to_faction"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    faction_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("faction.id"), name="faction_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    faction: Mapped["Faction"] = relationship(back_populates="notes_to")


class LitographyNoteToLocation(BaseTable):
    """Represents litography_note_to_location table"""

    __tablename__ = "litography_note_to_location"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    location_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("location_.id"), name="location_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    location: Mapped["Location"] = relationship(back_populates="notes_to")


class LitographyNoteToHistory(BaseTable):
    """Represents litography_note_to_history table"""

    __tablename__ = "litography_note_to_history"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    history_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("history.id"), name="history_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    history: Mapped["History"] = relationship(back_populates="notes_to")


class LitographyNoteToObject(BaseTable):
    """Represents litography_note_to_object table"""

    __tablename__ = "litography_note_to_object"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    object_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("object_.id"), name="object_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    object: Mapped["Object_"] = relationship(back_populates="notes_to")


class LitographyNoteToWorldData(BaseTable):
    """Represents litography_note_to_world_data table"""

    __tablename__ = "litography_note_to_world_data"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    world_data_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("world_data.id"), name="world_data_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    world_data: Mapped["WorldData"] = relationship(back_populates="notes_to")


class LitographyNoteToClass(BaseTable):
    """Represents litography_note_to_class table"""

    __tablename__ = "litography_note_to_class"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    class_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("class.id"), name="class_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    class_: Mapped["Class_"] = relationship(back_populates="notes_to")


class LitographyNoteToRace(BaseTable):
    """Represents litography_note_to_race table"""

    __tablename__ = "litography_note_to_race"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    race_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("race.id"), name="race_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    race: Mapped["Race"] = relationship(back_populates="notes_to")


class LitographyNoteToSubRace(BaseTable):
    """Represents litography_note_to_sub_race table"""

    __tablename__ = "litography_note_to_sub_race"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    sub_race_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sub_race.id"), name="sub_race_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    sub_race: Mapped["SubRace"] = relationship(back_populates="notes_to")


class LitographyNoteToSkills(BaseTable):
    """Represents litography_note_to_skills table"""

    __tablename__ = "litography_note_to_skills"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, name="id"
    )
    note_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_notes.id"), name="note_id"
    )
    skill_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("skills.id"), name="skill_id"
    )

    note: Mapped["LitographyNotes"] = relationship()
    skill: Mapped["Skills"] = relationship(back_populates="notes_to")


class ArcToNode(BaseTable):
    """Represents the arc_to_node table"""

    __tablename__ = "arc_to_node"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    node_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_node.id"), name="node_id"
    )
    arc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_arc.id"), name="arc_id"
    )

    node: Mapped["LitographyNode"] = relationship(back_populates="arcs")
    arc: Mapped["LitographyArc"] = relationship(back_populates="nodes")


class ArcToActor(BaseTable):
    """Represents the arc_to_actor table"""

    __tablename__ = "arc_to_actor"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    actor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("actor.id"), nullable=False, name="actor_id"
    )
    arc_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_arc.id"), nullable=False, name="arc_id"
    )

    actor: Mapped["Actor"] = relationship(back_populates="arcs")
    arc: Mapped["LitographyArc"] = relationship(back_populates="actors")
