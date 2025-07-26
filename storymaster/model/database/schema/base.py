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

    storylines: Mapped[list["Storyline"]] = relationship(back_populates="user")
    settings: Mapped[list["Setting"]] = relationship(back_populates="user")


class Storyline(BaseTable):
    """Class to represent the storyline table"""

    __tablename__ = "storyline"

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

    user: Mapped["User"] = relationship(back_populates="storylines")
    storyline_to_settings: Mapped[list["StorylineToSetting"]] = relationship(
        back_populates="storyline"
    )
    litography_nodes: Mapped[list["LitographyNode"]] = relationship(
        back_populates="storyline"
    )
    litography_notes: Mapped[list["LitographyNotes"]] = relationship(
        back_populates="storyline"
    )
    litography_plots: Mapped[list["LitographyPlot"]] = relationship(
        back_populates="storyline"
    )
    litography_arcs: Mapped[list["LitographyArc"]] = relationship(
        back_populates="storyline"
    )


class Setting(BaseTable):
    """Class to represent the setting table"""

    __tablename__ = "setting"

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

    user: Mapped["User"] = relationship(back_populates="settings")
    storyline_to_setting: Mapped[list["StorylineToSetting"]] = relationship(
        back_populates="setting"
    )
    classes: Mapped[list["Class_"]] = relationship(back_populates="setting")
    backgrounds: Mapped[list["Background"]] = relationship(back_populates="setting")
    races: Mapped[list["Race"]] = relationship(back_populates="setting")
    sub_races: Mapped[list["SubRace"]] = relationship(back_populates="setting")
    actors: Mapped[list["Actor"]] = relationship(back_populates="setting")
    actor_relations: Mapped[list["ActorAOnBRelations"]] = relationship(
        back_populates="setting"
    )
    skills: Mapped[list["Skills"]] = relationship(back_populates="setting")
    actor_to_skills: Mapped[list["ActorToSkills"]] = relationship(
        back_populates="setting"
    )
    alignments: Mapped[list["Alignment"]] = relationship(back_populates="setting")
    stats: Mapped[list["Stat"]] = relationship(back_populates="setting")
    actor_to_races: Mapped[list["ActorToRace"]] = relationship(back_populates="setting")
    actor_to_classes: Mapped[list["ActorToClass"]] = relationship(
        back_populates="setting"
    )
    actor_to_stats: Mapped[list["ActorToStat"]] = relationship(back_populates="setting")
    factions: Mapped[list["Faction"]] = relationship(back_populates="setting")
    faction_relations: Mapped[list["FactionAOnBRelations"]] = relationship(
        back_populates="setting"
    )
    faction_members: Mapped[list["FactionMembers"]] = relationship(
        back_populates="setting"
    )
    locations: Mapped[list["Location"]] = relationship(back_populates="setting")
    location_to_factions: Mapped[list["LocationToFaction"]] = relationship(
        back_populates="setting"
    )
    location_dungeons: Mapped[list["LocationDungeon"]] = relationship(
        back_populates="setting"
    )
    location_cities: Mapped[list["LocationCity"]] = relationship(
        back_populates="setting"
    )
    location_city_districts: Mapped[list["LocationCityDistricts"]] = relationship(
        back_populates="setting"
    )
    residents: Mapped[list["Resident"]] = relationship(back_populates="setting")
    location_flora_fauna: Mapped[list["LocationFloraFauna"]] = relationship(
        back_populates="setting"
    )
    histories: Mapped[list["History"]] = relationship(back_populates="setting")
    history_actors: Mapped[list["HistoryActor"]] = relationship(
        back_populates="setting"
    )
    history_locations: Mapped[list["HistoryLocation"]] = relationship(
        back_populates="setting"
    )
    history_factions: Mapped[list["HistoryFaction"]] = relationship(
        back_populates="setting"
    )
    objects: Mapped[list["Object_"]] = relationship(back_populates="setting")
    history_objects: Mapped[list["HistoryObject"]] = relationship(
        back_populates="setting"
    )
    object_owners: Mapped[list["ObjectToOwner"]] = relationship(
        back_populates="setting"
    )
    world_data: Mapped[list["WorldData"]] = relationship(back_populates="setting")
    history_world_data: Mapped[list["HistoryWorldData"]] = relationship(
        back_populates="setting"
    )
    arc_types: Mapped[list["ArcType"]] = relationship(back_populates="setting")


class StorylineToSetting(BaseTable):
    """Class to represent the storyline_to_setting table"""

    __tablename__ = "storyline_to_setting"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    storyline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("storyline.id"), nullable=False, name="storyline_id"
    )
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    storyline: Mapped["Storyline"] = relationship(
        back_populates="storyline_to_settings"
    )
    setting: Mapped["Setting"] = relationship(back_populates="storyline_to_setting")


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
    x_position: Mapped[float] = mapped_column(
        Float, nullable=False, name="x_position", default=0.0
    )
    y_position: Mapped[float] = mapped_column(
        Float, nullable=False, name="y_position", default=0.0
    )
    storyline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("storyline.id"), nullable=False, name="storyline_id"
    )

    storyline: Mapped["Storyline"] = relationship(back_populates="litography_nodes")
    notes: Mapped[list["LitographyNotes"]] = relationship(back_populates="linked_node")
    plot_sections: Mapped[list["LitographyNodeToPlotSection"]] = relationship(
        back_populates="node"
    )
    arcs: Mapped[list["ArcToNode"]] = relationship(back_populates="node")
    arc_points: Mapped[list["ArcPoint"]] = relationship(back_populates="node")
    output_connections: Mapped[list["NodeConnection"]] = relationship(
        foreign_keys="NodeConnection.output_node_id", back_populates="output_node"
    )
    input_connections: Mapped[list["NodeConnection"]] = relationship(
        foreign_keys="NodeConnection.input_node_id", back_populates="input_node"
    )


class NodeConnection(BaseTable):
    """Represents connections between nodes"""

    __tablename__ = "node_connection"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    output_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_node.id"), nullable=False, name="output_node_id"
    )
    input_node_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_node.id"), nullable=False, name="input_node_id"
    )

    output_node: Mapped["LitographyNode"] = relationship(
        foreign_keys=[output_node_id], back_populates="output_connections"
    )
    input_node: Mapped["LitographyNode"] = relationship(
        foreign_keys=[input_node_id], back_populates="input_connections"
    )


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
    storyline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("storyline.id"), nullable=False, name="storyline_id"
    )

    linked_node: Mapped["LitographyNode"] = relationship(back_populates="notes")
    storyline: Mapped["Storyline"] = relationship(back_populates="litography_notes")
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
    storyline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("storyline.id"), nullable=False, name="storyline_id"
    )

    storyline: Mapped["Storyline"] = relationship(back_populates="litography_plots")
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


class ArcType(BaseTable):
    """Represents character arc types (Growth, Fall, Flat, etc.)"""

    __tablename__ = "arc_type"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, name="name"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="arc_types")
    arcs: Mapped[list["LitographyArc"]] = relationship(back_populates="arc_type")


class LitographyArc(BaseTable):
    """Represents the litography_arc table"""

    __tablename__ = "litography_arc"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    title: Mapped[str] = mapped_column(
        String(250), nullable=False, name="title"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    arc_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("arc_type.id"), nullable=False, name="arc_type_id"
    )
    storyline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("storyline.id"), nullable=False, name="storyline_id"
    )

    storyline: Mapped["Storyline"] = relationship(back_populates="litography_arcs")
    arc_type: Mapped["ArcType"] = relationship(back_populates="arcs")
    nodes: Mapped[list["ArcToNode"]] = relationship(back_populates="arc")
    actors: Mapped[list["ArcToActor"]] = relationship(back_populates="arc")
    arc_points: Mapped[list["ArcPoint"]] = relationship(back_populates="arc")


class ArcPoint(BaseTable):
    """Represents specific moments in a character's arc progression"""

    __tablename__ = "arc_point"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    arc_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("litography_arc.id"), nullable=False, name="arc_id"
    )
    node_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("litography_node.id"), nullable=True, name="node_id"
    )
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, name="order_index", default=0
    )
    title: Mapped[str] = mapped_column(
        String(250), nullable=False, name="title"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="description"
    )
    emotional_state: Mapped[str | None] = mapped_column(
        String(500), nullable=True, name="emotional_state"
    )
    character_relationships: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="character_relationships"
    )
    goals: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="goals"
    )
    internal_conflict: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="internal_conflict"
    )

    arc: Mapped["LitographyArc"] = relationship(back_populates="arc_points")
    node: Mapped["LitographyNode"] = relationship(back_populates="arc_points")


class Class_(BaseTable):
    __tablename__ = "class"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, name="id"
    )
    name: Mapped[str | None] = mapped_column(String(255), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description")
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="classes")
    actors: Mapped[list["ActorToClass"]] = relationship(back_populates="class_")
    notes_to: Mapped[list["LitographyNoteToClass"]] = relationship(
        back_populates="class_"
    )


class Background(BaseTable):
    __tablename__ = "background"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="backgrounds")
    actors: Mapped[list["Actor"]] = relationship(back_populates="background")
    notes_to: Mapped[list["LitographyNoteToBackground"]] = relationship(
        back_populates="background"
    )


class Race(BaseTable):
    __tablename__ = "race"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="races")
    sub_races: Mapped[list["SubRace"]] = relationship(back_populates="race")
    actors: Mapped[list["ActorToRace"]] = relationship(back_populates="race")
    notes_to: Mapped[list["LitographyNoteToRace"]] = relationship(back_populates="race")


class SubRace(BaseTable):
    __tablename__ = "sub_race"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_race_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("race.id"))
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="sub_races")
    race: Mapped["Race"] = relationship(back_populates="sub_races")
    actors: Mapped[list["ActorToRace"]] = relationship(back_populates="sub_race")
    notes_to: Mapped[list["LitographyNoteToSubRace"]] = relationship(
        back_populates="sub_race"
    )


class Alignment(BaseTable):
    __tablename__ = "alignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="alignments")
    actors: Mapped[list["Actor"]] = relationship(back_populates="alignment")


class Stat(BaseTable):
    __tablename__ = "stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="stats")
    actors: Mapped[list["ActorToStat"]] = relationship(back_populates="stat")


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
    background_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("background.id"), nullable=True, name="background_id"
    )
    job: Mapped[str | None] = mapped_column(Text, nullable=True, name="job")
    actor_role: Mapped[str | None] = mapped_column(
        Text, nullable=True, name="actor_role"
    )
    alignment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("alignment.id"), nullable=True, name="alignment_id"
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
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actors")
    background: Mapped["Background"] = relationship(back_populates="actors")
    alignment: Mapped["Alignment"] = relationship(back_populates="actors")
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
    races: Mapped[list["ActorToRace"]] = relationship(back_populates="actor")
    classes: Mapped[list["ActorToClass"]] = relationship(back_populates="actor")
    stats: Mapped[list["ActorToStat"]] = relationship(back_populates="actor")


class ActorAOnBRelations(BaseTable):
    __tablename__ = "actor_a_on_b_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_a_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    actor_b_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    overall: Mapped[str | None] = mapped_column(String)
    economically: Mapped[str | None] = mapped_column(String)
    power_dynamic: Mapped[str | None] = mapped_column(String)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actor_relations")
    actor_a: Mapped["Actor"] = relationship(
        foreign_keys=[actor_a_id], back_populates="actor_a_relations"
    )
    actor_b: Mapped["Actor"] = relationship(
        foreign_keys=[actor_b_id], back_populates="actor_b_relations"
    )


class Skills(BaseTable):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    skill_trait: Mapped[str | None] = mapped_column(String(255))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="skills")
    actors: Mapped[list["ActorToSkills"]] = relationship(back_populates="skill")
    notes_to: Mapped[list["LitographyNoteToSkills"]] = relationship(
        back_populates="skill"
    )


class ActorToSkills(BaseTable):
    __tablename__ = "actor_to_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    skill_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("skills.id"))
    skill_level: Mapped[int | None] = mapped_column(Integer)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actor_to_skills")
    actor: Mapped["Actor"] = relationship(back_populates="skills")
    skill: Mapped["Skills"] = relationship(back_populates="actors")


class ActorToRace(BaseTable):
    __tablename__ = "actor_to_race"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    race_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("race.id"))
    sub_race_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sub_race.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actor_to_races")
    actor: Mapped["Actor"] = relationship(back_populates="races")
    race: Mapped["Race"] = relationship(back_populates="actors")
    sub_race: Mapped["SubRace"] = relationship(back_populates="actors")


class ActorToClass(BaseTable):
    __tablename__ = "actor_to_class"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    class_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("class.id"))
    level: Mapped[int | None] = mapped_column(Integer)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actor_to_classes")
    actor: Mapped["Actor"] = relationship(back_populates="classes")
    class_: Mapped["Class_"] = relationship(back_populates="actors")


class ActorToStat(BaseTable):
    __tablename__ = "actor_to_stat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    stat_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("stat.id"))
    stat_value: Mapped[int | None] = mapped_column(Integer)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="actor_to_stats")
    actor: Mapped["Actor"] = relationship(back_populates="stats")
    stat: Mapped["Stat"] = relationship(back_populates="actors")


class Faction(BaseTable):
    __tablename__ = "faction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[str | None] = mapped_column(Text)
    faction_values: Mapped[str | None] = mapped_column(Text)
    faction_income_sources: Mapped[str | None] = mapped_column(Text)
    faction_expenses: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="factions")
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    faction_a_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    faction_b_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    overall: Mapped[str | None] = mapped_column(Text)
    economically: Mapped[str | None] = mapped_column(Text)
    politically: Mapped[str | None] = mapped_column(Text)
    opinion: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="faction_relations")
    faction_a: Mapped["Faction"] = relationship(
        foreign_keys=[faction_a_id], back_populates="faction_a_relations"
    )
    faction_b: Mapped["Faction"] = relationship(
        foreign_keys=[faction_b_id], back_populates="faction_b_relations"
    )


class FactionMembers(BaseTable):
    __tablename__ = "faction_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    actor_role: Mapped[str | None] = mapped_column(String(255))
    relative_power: Mapped[int | None] = mapped_column(Integer)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    actor: Mapped["Actor"] = relationship(back_populates="faction_memberships")
    faction: Mapped["Faction"] = relationship(back_populates="members")
    setting: Mapped["Setting"] = relationship(back_populates="faction_members")


class Location(BaseTable):
    __tablename__ = "location_"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    location_type: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    sights: Mapped[str | None] = mapped_column(Text)
    smells: Mapped[str | None] = mapped_column(Text)
    sounds: Mapped[str | None] = mapped_column(Text)
    feels: Mapped[str | None] = mapped_column(Text)
    tastes: Mapped[str | None] = mapped_column(Text)
    coordinates: Mapped[str | None] = mapped_column(String(255))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location_flora_fauna: Mapped[list["LocationFloraFauna"]] = relationship(
        back_populates="location_"
    )
    setting: Mapped["Setting"] = relationship(back_populates="locations")
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    faction_presence: Mapped[float | None] = mapped_column(Float)
    faction_power: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location: Mapped["Location"] = relationship(back_populates="factions")
    faction: Mapped["Faction"] = relationship(back_populates="locations")
    setting: Mapped["Setting"] = relationship(back_populates="location_to_factions")


class LocationDungeon(BaseTable):
    __tablename__ = "location_dungeon"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    dangers: Mapped[str | None] = mapped_column(Text)
    traps: Mapped[str | None] = mapped_column(Text)
    secrets: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location: Mapped["Location"] = relationship(back_populates="dungeons")
    setting: Mapped["Setting"] = relationship(back_populates="location_dungeons")


class LocationCity(BaseTable):
    __tablename__ = "location_city"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    government: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location: Mapped["Location"] = relationship(back_populates="cities")
    setting: Mapped["Setting"] = relationship(back_populates="location_cities")


class LocationCityDistricts(BaseTable):
    __tablename__ = "location_city_districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    district_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location: Mapped["Location"] = relationship(
        foreign_keys=[location_id], back_populates="city_districts"
    )
    district: Mapped["Location"] = relationship(
        foreign_keys=[district_id], back_populates="districts_in_city"
    )
    setting: Mapped["Setting"] = relationship(back_populates="location_city_districts")


class Resident(BaseTable):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    actor: Mapped["Actor"] = relationship(back_populates="residences")
    location: Mapped["Location"] = relationship(back_populates="residents")
    setting: Mapped["Setting"] = relationship(back_populates="residents")


class LocationFloraFauna(BaseTable):
    __tablename__ = "location_flora_fauna"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    living_type: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    location_: Mapped["Location"] = relationship(back_populates="location_flora_fauna")
    setting: Mapped["Setting"] = relationship(back_populates="location_flora_fauna")


class History(BaseTable):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    event_year: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="histories")
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    history: Mapped["History"] = relationship(back_populates="actors")
    actor: Mapped["Actor"] = relationship(back_populates="history")
    setting: Mapped["Setting"] = relationship(back_populates="history_actors")


class HistoryLocation(BaseTable):
    __tablename__ = "history_location"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location_.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="history_locations")
    history: Mapped["History"] = relationship(back_populates="locations")
    location: Mapped["Location"] = relationship(back_populates="history")


class HistoryFaction(BaseTable):
    __tablename__ = "history_faction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    faction_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("faction.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="history_factions")
    history: Mapped["History"] = relationship(back_populates="factions")
    faction: Mapped["Faction"] = relationship(back_populates="history")


class Object_(BaseTable):
    __tablename__ = "object_"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    object_value: Mapped[int | None] = mapped_column(Integer)
    rarity: Mapped[str | None] = mapped_column(String(255))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="objects")
    history: Mapped[list["HistoryObject"]] = relationship(back_populates="object")
    owners: Mapped[list["ObjectToOwner"]] = relationship(back_populates="object")
    notes_to: Mapped[list["LitographyNoteToObject"]] = relationship(
        back_populates="object"
    )


class HistoryObject(BaseTable):
    __tablename__ = "history_object"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    object_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("object_.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="history_objects")
    history: Mapped["History"] = relationship(back_populates="objects")
    object: Mapped["Object_"] = relationship(back_populates="history")


class ObjectToOwner(BaseTable):
    __tablename__ = "object_to_owner"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    object_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("object_.id"))
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("actor.id"))
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="object_owners")
    object: Mapped["Object_"] = relationship(back_populates="owners")
    actor: Mapped["Actor"] = relationship(back_populates="objects")


class WorldData(BaseTable):
    __tablename__ = "world_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="world_data")
    history: Mapped[list["HistoryWorldData"]] = relationship(
        back_populates="world_data"
    )
    notes_to: Mapped[list["LitographyNoteToWorldData"]] = relationship(
        back_populates="world_data"
    )


class HistoryWorldData(BaseTable):
    __tablename__ = "history_world_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    history_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("history.id"))
    world_data_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("world_data.id")
    )
    setting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("setting.id"), nullable=False, name="setting_id"
    )

    setting: Mapped["Setting"] = relationship(back_populates="history_world_data")
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
