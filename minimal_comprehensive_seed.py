#!/usr/bin/env python3
"""
Minimal Comprehensive Database Seeding Script for Storymaster

This script creates one minimal valid entry for every table in the database schema.
Uses minimal required fields to ensure successful creation.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from storymaster.model.database import schema
from storymaster.model.database.schema.base import BaseTable, NodeConnection

# Database configuration
database_url = (
    f"sqlite:///{os.path.expanduser('~/.local/share/storymaster/storymaster.db')}"
)
engine = create_engine(database_url)


def clear_database(session: Session) -> Session:
    """Completely drops and recreates all tables"""
    BaseTable.metadata.drop_all(engine)
    BaseTable.metadata.create_all(engine)
    return session


def main():
    """Main comprehensive seeding function - minimal entries for all tables"""
    with Session(engine) as session:
        print("🔄 Clearing database...")
        session = clear_database(session)
        session.commit()

        print("📚 Creating minimal test data for ALL tables...")

        # Core system tables
        user = schema.User(id=1, username="test_user")
        session.add(user)

        storyline = schema.Storyline(id=1, user_id=1, name="Test Story")
        session.add(storyline)

        setting = schema.Setting(id=1, name="Test Setting", user_id=1)
        session.add(setting)

        session.add(schema.StorylineToSetting(storyline_id=1, setting_id=1))
        session.commit()
        print("✅ Core tables: User, Storyline, Setting, StorylineToSetting")

        # Character system tables
        alignment = schema.Alignment(id=1, name="Neutral", setting_id=1)
        session.add(alignment)

        race = schema.Race(id=1, name="Human", setting_id=1)
        session.add(race)

        subrace = schema.SubRace(id=1, name="Variant", parent_race_id=1, setting_id=1)
        session.add(subrace)

        class_ = schema.Class_(id=1, name="Fighter", setting_id=1)
        session.add(class_)

        background = schema.Background(id=1, name="Soldier", setting_id=1)
        session.add(background)

        skill = schema.Skills(id=1, name="Athletics", setting_id=1)
        session.add(skill)

        stat = schema.Stat(id=1, name="Strength", setting_id=1)
        session.add(stat)

        actor1 = schema.Actor(id=1, first_name="Test", last_name="Hero", setting_id=1)
        session.add(actor1)

        actor2 = schema.Actor(id=2, first_name="Test", last_name="NPC", setting_id=1)
        session.add(actor2)

        session.commit()
        print(
            "✅ Character system: Alignment, Race, SubRace, Class_, Background, Skills, Stat, Actor"
        )

        # Character relationship tables
        session.add(schema.ActorAOnBRelations(actor_a_id=1, actor_b_id=2, setting_id=1))
        session.add(schema.ActorToSkills(actor_id=1, skill_id=1, setting_id=1))
        session.add(schema.ActorToRace(actor_id=1, race_id=1, setting_id=1))
        session.add(schema.ActorToClass(actor_id=1, class_id=1, setting_id=1))
        session.add(schema.ActorToStat(actor_id=1, stat_id=1, setting_id=1))
        session.commit()
        print(
            "✅ Character relationships: ActorAOnBRelations, ActorToSkills, ActorToRace, ActorToClass, ActorToStat"
        )

        # Faction system tables
        faction1 = schema.Faction(id=1, name="Test Guild", setting_id=1)
        session.add(faction1)

        faction2 = schema.Faction(id=2, name="Test Order", setting_id=1)
        session.add(faction2)

        session.add(
            schema.FactionAOnBRelations(faction_a_id=1, faction_b_id=2, setting_id=1)
        )
        session.add(schema.FactionMembers(actor_id=1, faction_id=1, setting_id=1))
        session.commit()
        print("✅ Faction system: Faction, FactionAOnBRelations, FactionMembers")

        # Location system tables
        location1 = schema.Location(id=1, name="Test City", setting_id=1)
        session.add(location1)

        location2 = schema.Location(id=2, name="Test Dungeon", setting_id=1)
        session.add(location2)

        # Third location for district
        location3 = schema.Location(id=3, name="Test District", setting_id=1)
        session.add(location3)

        session.add(schema.LocationToFaction(location_id=1, faction_id=1, setting_id=1))
        session.add(schema.LocationDungeon(location_id=2, setting_id=1))
        session.add(schema.LocationCity(location_id=1, setting_id=1))
        session.add(
            schema.LocationCityDistricts(location_id=1, district_id=3, setting_id=1)
        )
        session.add(schema.Resident(actor_id=1, location_id=1, setting_id=1))
        session.add(
            schema.LocationFloraFauna(location_id=1, name="Test Plant", setting_id=1)
        )
        session.commit()
        print(
            "✅ Location system: Location, LocationToFaction, LocationDungeon, LocationCity, LocationCityDistricts, Resident, LocationFloraFauna"
        )

        # Object system tables
        object1 = schema.Object_(id=1, name="Test Sword", setting_id=1)
        session.add(object1)

        session.add(schema.ObjectToOwner(object_id=1, actor_id=1, setting_id=1))
        session.commit()
        print("✅ Object system: Object_, ObjectToOwner")

        # History system tables
        history1 = schema.History(id=1, name="Test War", setting_id=1)
        session.add(history1)

        session.add(schema.HistoryActor(history_id=1, actor_id=1, setting_id=1))
        session.add(schema.HistoryLocation(history_id=1, location_id=1, setting_id=1))
        session.add(schema.HistoryFaction(history_id=1, faction_id=1, setting_id=1))
        session.add(schema.HistoryObject(history_id=1, object_id=1, setting_id=1))
        session.commit()
        print(
            "✅ History system: History, HistoryActor, HistoryLocation, HistoryFaction, HistoryObject"
        )

        # World data system tables
        world_data1 = schema.WorldData(id=1, name="Test Lore", setting_id=1)
        session.add(world_data1)

        session.add(
            schema.HistoryWorldData(history_id=1, world_data_id=1, setting_id=1)
        )
        session.commit()
        print("✅ World data system: WorldData, HistoryWorldData")

        # Story plotting system tables
        plot1 = schema.LitographyPlot(id=1, title="Test Plot", storyline_id=1)
        session.add(plot1)

        plot_section1 = schema.LitographyPlotSection(
            id=1, plot_section_type=schema.PlotSectionType.RISING, plot_id=1
        )
        session.add(plot_section1)

        node1 = schema.LitographyNode(
            id=1,
            node_type=schema.NodeType.EXPOSITION,
            x_position=0.0,
            y_position=0.0,
            storyline_id=1,
        )
        session.add(node1)

        node2 = schema.LitographyNode(
            id=2,
            node_type=schema.NodeType.ACTION,
            x_position=100.0,
            y_position=0.0,
            storyline_id=1,
        )
        session.add(node2)

        session.add(NodeConnection(output_node_id=1, input_node_id=2))
        session.add(
            schema.LitographyNodeToPlotSection(node_id=1, litography_plot_section_id=1)
        )

        note1 = schema.LitographyNotes(
            id=1,
            title="Test Note",
            note_type=schema.NoteType.OTHER,
            linked_node=node1,
            storyline_id=1,
        )
        session.add(note1)

        session.commit()
        print(
            "✅ Story plotting: LitographyPlot, LitographyPlotSection, LitographyNode, NodeConnection, LitographyNodeToPlotSection, LitographyNotes"
        )

        # Character arc system tables
        arc_type1 = schema.ArcType(id=1, name="Test Arc Type", setting_id=1)
        session.add(arc_type1)

        arc1 = schema.LitographyArc(
            id=1, title="Test Arc", arc_type_id=1, storyline_id=1
        )
        session.add(arc1)

        arc_point1 = schema.ArcPoint(
            id=1, arc_id=1, node_id=1, order_index=1, title="Test Point"
        )
        session.add(arc_point1)

        session.add(schema.ArcToNode(arc_id=1, node_id=1))
        session.add(schema.ArcToActor(actor_id=1, arc_id=1))
        session.commit()
        print(
            "✅ Character arc system: ArcType, LitographyArc, ArcPoint, ArcToNode, ArcToActor"
        )

        # Note linking system tables
        session.add(schema.LitographyNoteToActor(note_id=1, actor_id=1))
        session.add(schema.LitographyNoteToBackground(note_id=1, background_id=1))
        session.add(schema.LitographyNoteToFaction(note_id=1, faction_id=1))
        session.add(schema.LitographyNoteToLocation(note_id=1, location_id=1))
        session.add(schema.LitographyNoteToHistory(note_id=1, history_id=1))
        session.add(schema.LitographyNoteToObject(note_id=1, object_id=1))
        session.add(schema.LitographyNoteToWorldData(note_id=1, world_data_id=1))
        session.add(schema.LitographyNoteToClass(note_id=1, class_id=1))
        session.add(schema.LitographyNoteToRace(note_id=1, race_id=1))
        session.add(schema.LitographyNoteToSubRace(note_id=1, sub_race_id=1))
        session.add(schema.LitographyNoteToSkills(note_id=1, skill_id=1))
        session.commit()
        print("✅ Note linking system: All LitographyNoteTo* tables")

        print(f"\n🎉 MINIMAL COMPREHENSIVE DATABASE SEEDING COMPLETED!")
        print(f"📊 Successfully created minimal data for ALL database tables!")
        print(f"✨ Every table now has at least one test record!")
        print(f"🚀 The application is ready for comprehensive testing!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error during minimal comprehensive seeding: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
