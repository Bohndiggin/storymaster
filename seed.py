import csv
import os

from sqlalchemy import Connection, create_engine, sql
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from storymaster.model.database import schema
from storymaster.model.database.schema.base import BaseTable


database_url = f"sqlite:///{os.path.expanduser('~/.local/share/storymaster/storymaster.db')}"
engine = create_engine(database_url)

def load_from_csv(path: str, setting_id: int) -> list[dict[str, str | int]]:
    """loads the csv based on path and returns a list of dictionaries"""

    with open(path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        result_list = []
        for row in reader:
            # Convert string "null" to None for nullable columns
            processed_row = {}
            for key, value in row.items():
                if value == 'null' or value == '':
                    processed_row[key] = None
                else:
                    processed_row[key] = value
            processed_row['setting_id'] = setting_id
            result_list.append(processed_row)
    
    return result_list

def clear_database(session: Session) -> Session:
    """Completely drops and recreates all tables"""
    # Drop all tables
    BaseTable.metadata.drop_all(engine)
    # Recreate all tables
    BaseTable.metadata.create_all(engine)
    return session

def load_csv_if_exists(path: str, setting_id: int) -> list[dict[str, str | int]]:
    """Load CSV if file exists, otherwise return empty list"""
    if os.path.exists(path):
        return load_from_csv(path, setting_id)
    else:
        print(f"Warning: CSV file not found: {path}")
        return []

def load_csv_raw(path: str) -> list[dict[str, str | int]]:
    """Load CSV without adding group_id - for litography tables"""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            result_list = []
            for row in reader:
                # Convert string "null" to None for nullable columns
                processed_row = {}
                for key, value in row.items():
                    if value == 'null' or value == '':
                        processed_row[key] = None
                    else:
                        processed_row[key] = value
                result_list.append(processed_row)
            return result_list
    else:
        print(f"Warning: CSV file not found: {path}")
        return []

    


def main():
    """Main seeding function"""
    with Session(engine) as session:
        print("Clearing database...")
        session = clear_database(session)
        session.commit()
        
        # Core entities - Create default user and example data
        print("Creating core entities...")
        
        # Create default user
        default_user = schema.User(id=1, username='demo_user')
        session.add(default_user)
        session.commit()
        print("   Created demo user")

        # Create storyline
        storyline = schema.Storyline(
            id=1, 
            user_id=1, 
            name="Fantasy Adventure", 
            description="A sample fantasy storyline with heroes, magic, and adventure"
        )
        session.add(storyline)
        session.commit()
        print("   Created storyline")

        # Create setting
        setting = schema.Setting(
            id=1, 
            name="Mystical Realm", 
            description="A fantasy world filled with magic, diverse races, and ancient mysteries", 
            user_id=1
        )
        session.add(setting)
        session.commit()
        print("   Created setting")
        
        # Link storyline to setting
        session.add(schema.StorylineToSetting(storyline_id=1, setting_id=1))
        session.commit()
        print("   Linked storyline to setting")

        # Create basic lookup data programmatically
        print("Creating basic lookup entities...")
        try:
            # Create some basic races
            races = [
                schema.Race(id=1, name="Human", description="Versatile and adaptable humanoids", setting_id=1),
                schema.Race(id=2, name="Elf", description="Graceful and long-lived forest dwellers", setting_id=1),
                schema.Race(id=3, name="Dwarf", description="Sturdy mountain folk skilled in crafts", setting_id=1),
                schema.Race(id=4, name="Halfling", description="Small, peaceful folk who love comfort", setting_id=1),
            ]
            session.add_all(races)
            session.commit()
            print(f"   Created {len(races)} races")

            # Create some basic classes
            classes = [
                schema.Class_(id=1, name="Warrior", description="Skilled in combat and warfare", setting_id=1),
                schema.Class_(id=2, name="Mage", description="Master of arcane arts and magic", setting_id=1),
                schema.Class_(id=3, name="Rogue", description="Stealthy and skilled in subterfuge", setting_id=1),
                schema.Class_(id=4, name="Cleric", description="Divine spellcaster and healer", setting_id=1),
            ]
            session.add_all(classes)
            session.commit()
            print(f"   Created {len(classes)} classes")

            # Create some basic backgrounds
            backgrounds = [
                schema.Background(id=1, name="Noble", description="Born to privilege and power", setting_id=1),
                schema.Background(id=2, name="Commoner", description="Ordinary folk of the realm", setting_id=1),
                schema.Background(id=3, name="Scholar", description="Devoted to learning and knowledge", setting_id=1),
                schema.Background(id=4, name="Soldier", description="Trained in military service", setting_id=1),
            ]
            session.add_all(backgrounds)
            session.commit()
            print(f"   Created {len(backgrounds)} backgrounds")
            
        except Exception as e:
            print(f"   Warning: Error creating lookup entities: {e}")

        # Create sample world entities
        print("Creating sample world entities...")
        try:
            # Create sample actors
            actors = [
                schema.Actor(
                    id=1, first_name="Eldara", last_name="Moonwhisper", title="Archmage",
                    actor_age=150, job="Court Wizard", actor_role="Mentor",
                    background_id=3, setting_id=1
                ),
                schema.Actor(
                    id=2, first_name="Thorgan", last_name="Ironforge", title="Captain",
                    actor_age=45, job="City Guard Captain", actor_role="Authority Figure",
                    background_id=4, setting_id=1
                ),
                schema.Actor(
                    id=3, first_name="Pip", last_name="Lightfingers", title="",
                    actor_age=25, job="Thief", actor_role="Ally",
                    background_id=2, setting_id=1
                ),
            ]
            session.add_all(actors)
            session.commit()
            print(f"   Created {len(actors)} actors")

            # Create sample factions
            factions = [
                schema.Faction(
                    id=1, name="The Mage's Guild", description="Organization of magical practitioners",
                    setting_id=1
                ),
                schema.Faction(
                    id=2, name="City Watch", description="Law enforcement organization",
                    setting_id=1
                ),
                schema.Faction(
                    id=3, name="Thieves' Guild", description="Underground criminal organization",
                    setting_id=1
                ),
            ]
            session.add_all(factions)
            session.commit()
            print(f"   Created {len(factions)} factions")

            # Create sample locations
            locations = [
                schema.Location(
                    id=1, name="Crystalport", description="Major trading city by the sea",
                    setting_id=1
                ),
                schema.Location(
                    id=2, name="Whispering Woods", description="Ancient forest filled with magic",
                    setting_id=1
                ),
                schema.Location(
                    id=3, name="Ironhold Mountains", description="Rugged mountain range rich in minerals",
                    setting_id=1
                ),
            ]
            session.add_all(locations)
            session.commit()
            print(f"   Created {len(locations)} locations")
            
        except Exception as e:
            print(f"   Warning: Error creating world entities: {e}")

        # Create sample story plotting data
        print("Creating sample story plotting data...")
        try:
            # Create a plot
            plot = schema.LitographyPlot(
                id=1, 
                title="The Crystal of Eternal Light", 
                description="Heroes must recover an ancient artifact to save the realm",
                storyline_id=1
            )
            session.add(plot)
            session.commit()
            print("   Created sample plot")
            
            # Create plot sections
            plot_sections = [
                schema.LitographyPlotSection(id=1, plot_section_type=schema.PlotSectionType.RISING, plot_id=1),
                schema.LitographyPlotSection(id=2, plot_section_type=schema.PlotSectionType.POINT, plot_id=1),
                schema.LitographyPlotSection(id=3, plot_section_type=schema.PlotSectionType.LOWER, plot_id=1),
            ]
            session.add_all(plot_sections)
            session.commit()
            print(f"   Created {len(plot_sections)} plot sections")

            # Create sample story nodes
            nodes = [
                schema.LitographyNode(
                    id=1, 
                    node_type=schema.NodeType.EXPOSITION, 
                    x_position=100.0, 
                    y_position=100.0, 
                    storyline_id=1
                ),
                schema.LitographyNode(
                    id=2, 
                    node_type=schema.NodeType.ACTION, 
                    x_position=300.0, 
                    y_position=100.0, 
                    storyline_id=1
                ),
                schema.LitographyNode(
                    id=3, 
                    node_type=schema.NodeType.TWIST, 
                    x_position=500.0, 
                    y_position=100.0, 
                    storyline_id=1
                ),
            ]
            session.add_all(nodes)
            session.commit()
            print(f"   Created {len(nodes)} story nodes")
            
        except Exception as e:
            print(f"   Warning: Error creating plotting data: {e}")

        print("\nDatabase seeding completed successfully!")
        print("Sample data created:")
        print("  - Demo user account")
        print("  - Fantasy storyline and setting")
        print("  - Basic races, classes, and backgrounds")
        print("  - Sample characters, factions, and locations")
        print("  - Example story plot with tension-based sections")
        print("\nYou can now launch the application and explore the sample data!")

if __name__ == "__main__":
    main()


    
