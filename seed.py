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
                    is_city=True, setting_id=1
                ),
                schema.Location(
                    id=2, name="Whispering Woods", description="Ancient forest filled with magic",
                    setting_id=1
                ),
                schema.Location(
                    id=3, name="Ironhold Mountains", description="Rugged mountain range rich in minerals",
                    setting_id=1
                ),
                schema.Location(
                    id=4, name="Shadow Caverns", description="Dark underground network of caves and tunnels",
                    is_dungeon=True, setting_id=1
                ),
                schema.Location(
                    id=5, name="Harbor District", description="Bustling docks with merchant warehouses, taverns, and the famous Crystal Market",
                    setting_id=1
                ),
                schema.Location(
                    id=6, name="Mage Quarter", description="Elegant district housing the Mage's Guild and various magical academies",
                    setting_id=1
                ),
            ]
            session.add_all(locations)
            session.commit()
            print(f"   Created {len(locations)} locations")
            
        except Exception as e:
            print(f"   Warning: Error creating world entities: {e}")

        # Create character arc types
        print("Creating character arc types...")
        try:
            arc_types = [
                schema.ArcType(
                    id=1, name="Hero's Journey", 
                    description="The classic hero transformation from ordinary to extraordinary",
                    setting_id=1
                ),
                schema.ArcType(
                    id=2, name="Character Growth", 
                    description="Character learns and develops throughout the story",
                    setting_id=1
                ),
                schema.ArcType(
                    id=3, name="Redemption Arc", 
                    description="Character seeks to make amends for past mistakes",
                    setting_id=1
                ),
                schema.ArcType(
                    id=4, name="Fall from Grace", 
                    description="Character's moral decline throughout the story",
                    setting_id=1
                ),
                schema.ArcType(
                    id=5, name="Romance Arc", 
                    description="Character's romantic relationship development",
                    setting_id=1
                ),
            ]
            session.add_all(arc_types)
            session.commit()
            print(f"   Created {len(arc_types)} arc types")
            
            # Create sample character arcs
            character_arcs = [
                schema.LitographyArc(
                    id=1, title="Kael's Hero Journey", 
                    description="Kael transforms from farm boy to legendary hero",
                    arc_type_id=1, storyline_id=1
                ),
                schema.LitographyArc(
                    id=2, title="Luna's Magic Growth", 
                    description="Luna learns to control her powerful magic abilities",
                    arc_type_id=2, storyline_id=1
                ),
                schema.LitographyArc(
                    id=3, title="Thorin's Redemption", 
                    description="Thorin seeks to redeem himself for past failures",
                    arc_type_id=3, storyline_id=1
                ),
            ]
            session.add_all(character_arcs)
            session.commit()
            print(f"   Created {len(character_arcs)} character arcs")
            
            # Link arcs to actors
            arc_to_actors = [
                schema.ArcToActor(actor_id=1, arc_id=1),  # Kael -> Hero's Journey
                schema.ArcToActor(actor_id=2, arc_id=2),  # Luna -> Magic Growth
                schema.ArcToActor(actor_id=3, arc_id=3),  # Thorin -> Redemption
            ]
            session.add_all(arc_to_actors)
            session.commit()
            print("   Linked arcs to characters")
            
        except Exception as e:
            print(f"   Warning: Error creating character arcs: {e}")

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
            
            # Create sample arc points
            arc_points = [
                # Kael's Hero Journey arc points
                schema.ArcPoint(
                    id=1, arc_id=1, node_id=1, order_index=1,
                    title="Call to Adventure", 
                    description="Kael discovers the ancient prophecy",
                    emotional_state="Curious but reluctant",
                    goals="Understand the prophecy",
                    internal_conflict="Doubts his ability to be a hero"
                ),
                schema.ArcPoint(
                    id=2, arc_id=1, node_id=2, order_index=2,
                    title="First Trial",
                    description="Kael faces his first real challenge",
                    emotional_state="Determined but afraid",
                    goals="Prove himself worthy",
                    internal_conflict="Fear of failure"
                ),
                schema.ArcPoint(
                    id=3, arc_id=1, node_id=3, order_index=3,
                    title="Transformation",
                    description="Kael embraces his destiny",
                    emotional_state="Confident and resolved",
                    goals="Save the realm",
                    internal_conflict="Accepts the burden of leadership"
                ),
                # Luna's Magic Growth arc points
                schema.ArcPoint(
                    id=4, arc_id=2, node_id=1, order_index=1,
                    title="Power Awakening",
                    description="Luna's magic manifests uncontrollably",
                    emotional_state="Frightened and confused",
                    goals="Control her powers",
                    internal_conflict="Fear of hurting others"
                ),
                schema.ArcPoint(
                    id=5, arc_id=2, node_id=2, order_index=2,
                    title="Learning Control",
                    description="Luna begins formal magic training",
                    emotional_state="Focused but struggling",
                    goals="Master basic techniques",
                    internal_conflict="Impatience with slow progress"
                ),
            ]
            session.add_all(arc_points)
            session.commit()
            print(f"   Created {len(arc_points)} arc points")
            
        except Exception as e:
            print(f"   Warning: Error creating plotting data: {e}")

        # Add creative content to fill out all relationship tables
        print("Creating additional creative content...")
        try:
            # Create stats
            stats = [
                schema.Stat(id=1, name="Strength", description="Physical power and muscle", setting_id=1),
                schema.Stat(id=2, name="Intelligence", description="Reasoning and memory", setting_id=1),
                schema.Stat(id=3, name="Charisma", description="Force of personality", setting_id=1),
                schema.Stat(id=4, name="Wisdom", description="Perception and insight", setting_id=1),
            ]
            session.add_all(stats)
            session.commit()
            print(f"   Created {len(stats)} stats")

            # Create skills
            skills = [
                schema.Skills(id=1, name="Arcane Lore", description="Knowledge of magical theory", setting_id=1),
                schema.Skills(id=2, name="Stealth", description="Moving silently and unseen", setting_id=1),
                schema.Skills(id=3, name="Swordplay", description="Combat with bladed weapons", setting_id=1),
                schema.Skills(id=4, name="Diplomacy", description="Negotiation and persuasion", setting_id=1),
            ]
            session.add_all(skills)
            session.commit()
            print(f"   Created {len(skills)} skills")

            # Create objects (including the wizard's staff!)
            objects = [
                schema.Object_(
                    id=1, name="Staff of Eldara", 
                    description="An ancient crystalline staff that pulses with arcane energy. Carved from moonwood and topped with a star-sapphire, it amplifies magical power.",
                    rarity="Legendary", object_value=5000, setting_id=1
                ),
                schema.Object_(
                    id=2, name="Captain's Badge", 
                    description="A silver badge of office marking Thorgan as Captain of the City Guard",
                    rarity="Uncommon", object_value=100, setting_id=1
                ),
                schema.Object_(
                    id=3, name="Lockpick Set", 
                    description="Pip's prized set of masterwork lockpicks, worn smooth from use",
                    rarity="Common", object_value=25, setting_id=1
                ),
                schema.Object_(
                    id=4, name="Ancient Tome of Secrets", 
                    description="A leather-bound book containing forbidden knowledge",
                    rarity="Rare", object_value=1200, setting_id=1
                ),
            ]
            session.add_all(objects)
            session.commit()
            print(f"   Created {len(objects)} objects")

            # Create historical events
            histories = [
                schema.History(
                    id=1, name="The Great Mage War", event_year=1150,
                    description="A devastating conflict between rival magical schools that reshaped the realm",
                    setting_id=1
                ),
                schema.History(
                    id=2, name="The Founding of Crystalport", event_year=1200,
                    description="The establishment of the great trading city at the confluence of three rivers",
                    setting_id=1
                ),
                schema.History(
                    id=3, name="The Thieves' Guild Uprising", event_year=1250,
                    description="When the criminal underworld challenged the established order",
                    setting_id=1
                ),
            ]
            session.add_all(histories)
            session.commit()
            print(f"   Created {len(histories)} historical events")

            # Create world data (lore)
            world_data = [
                schema.WorldData(
                    id=1, name="The Art of Crystal Magic", 
                    description="The unique magical tradition of focusing arcane energy through specially prepared crystals",
                    setting_id=1
                ),
                schema.WorldData(
                    id=2, name="The Code of the Watch", 
                    description="The moral and legal principles that guide the City Guard",
                    setting_id=1
                ),
                schema.WorldData(
                    id=3, name="Thieves' Cant", 
                    description="The secret language and symbols used by criminals",
                    setting_id=1
                ),
            ]
            session.add_all(world_data)
            session.commit()
            print(f"   Created {len(world_data)} lore entries")

            # Create relationships
            print("Creating sample relationships...")
            
            # Character relationships
            actor_relations = [
                schema.ActorAOnBRelations(
                    id=1, actor_a_id=1, actor_b_id=2, setting_id=1,
                    description="Professional colleagues who respect each other",
                    relationship_type="Professional", status="Active", strength=7, trust_level=8,
                    is_mutual=True, is_public=True,
                    how_met="Met during a joint investigation of magical crimes",
                    current_status="Cooperative allies"
                ),
            ]
            session.add_all(actor_relations)
            
            # Faction memberships
            faction_members = [
                schema.FactionMembers(
                    id=1, actor_id=1, faction_id=1, setting_id=1,
                    role="Archmage", rank=10, membership_status="Leadership",
                    loyalty=9, responsibilities="Leading magical research and teaching apprentices"
                ),
                schema.FactionMembers(
                    id=2, actor_id=2, faction_id=2, setting_id=1,
                    role="Captain", rank=8, membership_status="Active Member",
                    loyalty=8, responsibilities="Leading city patrols and crime prevention"
                ),
            ]
            session.add_all(faction_members)
            
            # Faction relationships
            faction_relations = [
                schema.FactionAOnBRelations(
                    id=1, faction_a_id=1, faction_b_id=2, setting_id=1,
                    description="The Mage's Guild works closely with the City Watch to prevent magical crimes",
                    relationship_type="Alliance", status="Active", strength=8, trust_level=7,
                    is_mutual=True, is_public=True,
                    how_met="Formed during the Great Mage War to maintain order",
                    current_status="Strong cooperative partnership",
                    # Legacy fields for compatibility
                    overall="The Mage's Guild works closely with the City Watch to prevent magical crimes",
                    economically="Share resources for magical crime investigation",
                    politically="Strong alliance with formal cooperation agreements",
                    opinion="Mutual respect and trust between organizations"
                ),
                schema.FactionAOnBRelations(
                    id=2, faction_a_id=2, faction_b_id=3, setting_id=1,
                    description="The City Watch and Thieves' Guild maintain an uneasy truce",
                    relationship_type="Rivalry", status="Tense", strength=3, trust_level=2,
                    is_mutual=False, is_public=False,
                    how_met="Years of cat-and-mouse enforcement vs evasion",
                    current_status="Cold war with occasional cooperation",
                    # Legacy fields for compatibility
                    overall="The City Watch and Thieves' Guild maintain an uneasy truce",
                    economically="Occasional bribes and information trading",
                    politically="Cold war with careful boundaries",
                    opinion="Wary antagonism with grudging professional respect"
                ),
            ]
            session.add_all(faction_relations)

            # Object ownership (the wizard's staff!)
            object_owners = [
                schema.ObjectToOwner(
                    id=1, actor_id=1, object_id=1, setting_id=1,
                    ownership_type="Owned", ownership_status="Current",
                    acquisition_method="Inherited from previous Archmage",
                    notes="The staff chooses its wielder and has been passed down for generations"
                ),
                schema.ObjectToOwner(
                    id=2, actor_id=2, object_id=2, setting_id=1,
                    ownership_type="Owned", ownership_status="Current",
                    acquisition_method="Awarded upon promotion",
                    notes="Symbol of authority and responsibility"
                ),
            ]
            session.add_all(object_owners)

            # Residences
            residents = [
                schema.Resident(
                    id=1, actor_id=1, location_id=1, setting_id=1,
                    residency_type="Permanent", residency_status="Current",
                    housing_type="Mage Tower", notes="Lives in the Guild's grand tower overlooking the harbor"
                ),
                schema.Resident(
                    id=2, actor_id=2, location_id=1, setting_id=1,
                    residency_type="Permanent", residency_status="Current",
                    housing_type="Guard Barracks", notes="Lives in the officers' quarters near the city center"
                ),
            ]
            session.add_all(residents)

            # Skills
            actor_skills = [
                schema.ActorToSkills(
                    id=1, actor_id=1, skill_id=1, setting_id=1,
                    skill_level=10, proficiency_level=10, experience_years=100,
                    how_learned="Decades of study and magical practice",
                    specialty="Crystal magic and enchantment"
                ),
                schema.ActorToSkills(
                    id=2, actor_id=3, skill_id=2, setting_id=1,
                    skill_level=8, proficiency_level=8, experience_years=10,
                    how_learned="Street training and natural talent",
                    specialty="Urban infiltration"
                ),
            ]
            session.add_all(actor_skills)

            # Character stats
            actor_stats = [
                schema.ActorToStat(
                    id=1, actor_id=1, stat_id=2, setting_id=1,
                    stat_value=18, base_value=16, modifier=2,
                    notes="Enhanced by magical study and ancient wisdom"
                ),
                schema.ActorToStat(
                    id=2, actor_id=2, stat_id=1, setting_id=1,
                    stat_value=16, base_value=15, modifier=1,
                    notes="Built through years of military training"
                ),
            ]
            session.add_all(actor_stats)

            # Race assignments
            actor_races = [
                schema.ActorToRace(
                    id=1, actor_id=1, race_id=2, setting_id=1,
                    heritage_strength=9, cultural_upbringing="Raised in elven magical traditions",
                    community_standing="Highly respected elder"
                ),
                schema.ActorToRace(
                    id=2, actor_id=2, race_id=3, setting_id=1,
                    heritage_strength=8, cultural_upbringing="Traditional dwarven clan values",
                    community_standing="Honored warrior"
                ),
            ]
            session.add_all(actor_races)

            # Class assignments
            actor_classes = [
                schema.ActorToClass(
                    id=1, actor_id=1, class_id=2, setting_id=1,
                    level=15, current_level=15, experience_points=225000,
                    specialization="Enchantment and Divination",
                    training_location="The Great Library of Arcane Arts",
                    mentor="Archmage Celestine the Wise"
                ),
            ]
            session.add_all(actor_classes)

            # Historical involvement
            history_actors = [
                schema.HistoryActor(
                    id=1, history_id=1, actor_id=1, setting_id=1,
                    role_in_event="Peace Negotiator", involvement_level="Central Figure",
                    impact_on_character="Shaped her philosophy of magical responsibility",
                    character_perspective="Magic should unite, not divide the realm",
                    consequences="Became the youngest Archmage in history"
                ),
            ]
            session.add_all(history_actors)
            
            # Faction historical involvement
            history_factions = [
                schema.HistoryFaction(
                    id=1, history_id=1, faction_id=1, setting_id=1,
                    role_in_event="Primary Combatant", involvement_level="Central Figure",
                    impact_on_faction="Led to stricter magical regulations and guild oversight",
                    faction_perspective="Magic must be regulated to prevent future conflicts",
                    consequences="Gained authority over magical practice in the realm"
                ),
                schema.HistoryFaction(
                    id=2, history_id=2, faction_id=2, setting_id=1,
                    role_in_event="Security Providers", involvement_level="Supporting Role",
                    impact_on_faction="Established the City Watch as the primary law enforcement",
                    faction_perspective="Order and safety are the foundation of civilization",
                    consequences="Gained permanent jurisdiction over city law enforcement"
                ),
            ]
            session.add_all(history_factions)
            
            # Location relationship data
            from storymaster.model.database.schema.base import (
                LocationAOnBRelations, LocationGeographicRelations, 
                LocationPoliticalRelations, LocationEconomicRelations
            )
            
            location_relations = [
                LocationAOnBRelations(
                    id=1, location_a_id=1, location_b_id=2, setting_id=1,
                    description="Crystalport serves as the gateway to the mystical Whispering Woods",
                    relationship_type="Cultural", status="Active", strength=6,
                    is_mutual=True, is_public=True,
                    established_date="Ancient times", 
                    current_status="The city depends on the woods for magical components while the woods are protected by city laws"
                ),
            ]
            session.add_all(location_relations)
            
            # Geographic relationships
            location_geographic = [
                LocationGeographicRelations(
                    id=1, location_a_id=1, location_b_id=2, setting_id=1,
                    geographic_type="borders", distance="5 miles",
                    travel_time="1 hour on foot", travel_difficulty="Easy",
                    travel_method="Well-maintained road",
                    description="Crystalport's eastern gate opens directly onto the ancient road that leads into the Whispering Woods"
                ),
                LocationGeographicRelations(
                    id=2, location_a_id=1, location_b_id=3, setting_id=1,
                    geographic_type="distant", distance="100 miles",
                    travel_time="5 days by caravan", travel_difficulty="Moderate",
                    travel_method="Mountain pass road",
                    description="The Ironhold Mountains loom on the northern horizon, accessible via the Trader's Pass"
                ),
            ]
            session.add_all(location_geographic)
            
            # Political relationships
            location_political = [
                LocationPoliticalRelations(
                    id=1, location_a_id=1, location_b_id=3, setting_id=1,
                    political_type="allied", treaty_name="Crystal-Iron Trade Compact",
                    treaty_date="1245", status="Active",
                    description="Crystalport and the Ironhold mining settlements maintain a crucial trade alliance for magical crystals and rare metals"
                ),
            ]
            session.add_all(location_political)
            
            # Economic relationships
            location_economic = [
                LocationEconomicRelations(
                    id=1, location_a_id=1, location_b_id=3, setting_id=1,
                    economic_type="trade_route", 
                    trade_goods="Crystalport exports: magical components, enchanted items, luxury goods. Ironhold exports: rare metals, gems, dwarven crafts",
                    trade_volume="High", trade_frequency="Weekly caravans",
                    trade_value="Thousands of gold pieces monthly",
                    description="The primary trade route between the coastal city and mountain settlements"
                ),
            ]
            session.add_all(location_economic)
            
            # Location detail data
            location_dungeons = [
                schema.LocationDungeon(
                    id=1, location_id=4, setting_id=1,
                    dangers="Unstable ceiling, poisonous gas pockets, territorial undead",
                    traps="Collapsing floor sections, dart traps in narrow passages",
                    secrets="Hidden chamber containing ancient dwarven artifacts, secret passage to surface"
                ),
            ]
            session.add_all(location_dungeons)
            
            location_cities = [
                schema.LocationCity(
                    id=1, location_id=1, setting_id=1,
                    government="Merchant Council - elected representatives from major trading houses"
                ),
            ]
            session.add_all(location_cities)
            
            location_flora_fauna = [
                schema.LocationFloraFauna(
                    id=1, location_id=2, setting_id=1,
                    name="Ancient Treants",
                    description="Massive tree beings that have guarded the forest for millennia",
                    living_type="Sentient Plant"
                ),
                schema.LocationFloraFauna(
                    id=2, location_id=2, setting_id=1,
                    name="Silver Stags",
                    description="Ethereal deer with silver antlers that glow in moonlight",
                    living_type="Magical Beast"
                ),
                schema.LocationFloraFauna(
                    id=3, location_id=2, setting_id=1,
                    name="Whispering Willows",
                    description="Mystical trees whose leaves carry messages on the wind",
                    living_type="Enchanted Flora"
                ),
            ]
            session.add_all(location_flora_fauna)
            
            # Create city-district relationships
            location_districts = [
                schema.LocationCityDistricts(
                    id=1, location_id=1, district_id=5, setting_id=1  # Crystalport -> Harbor District
                ),
                schema.LocationCityDistricts(
                    id=2, location_id=1, district_id=6, setting_id=1  # Crystalport -> Mage Quarter
                ),
            ]
            session.add_all(location_districts)

            session.commit()
            print("   Created sample relationships and location details connecting all the entities")
            
        except Exception as e:
            print(f"   Warning: Error creating additional content: {e}")

        print("\nDatabase seeding completed successfully!")
        print("Sample data created:")
        print("  - Demo user account")
        print("  - Fantasy storyline and setting")
        print("  - Basic races, classes, and backgrounds")
        print("  - Sample characters, factions, and locations")
        print("  - Character arc types and sample character arcs")
        print("  - Example story plot with tension-based sections")
        print("  - Arc points linking character development to story beats")
        print("  - Stats, skills, objects (including Eldara's magical staff!)")
        print("  - Historical events and world lore")
        print("  - Rich relationships connecting all entities")
        print("\nYou can now launch the application and explore the sample data!")

if __name__ == "__main__":
    main()


    
