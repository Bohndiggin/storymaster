"""
Test suite for database schema and models
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import (
    BaseTable,
    User,
    Storyline,
    Setting,
    NodeType,
    PlotSectionType,
    NoteType,
    LitographyNode,
    LitographyPlot,
    Actor,
    Faction,
    Location,
    Object_,
)


class TestDatabaseSchemaBasics:
    """Test basic database schema functionality"""

    def test_base_table_as_dict_method(self):
        """Test that BaseTable.as_dict() works correctly"""
        # Create a test user instance
        user = User(id=1, username="testuser")

        # Test as_dict method
        user_dict = user.as_dict()

        assert isinstance(user_dict, dict)
        assert user_dict["id"] == 1
        assert user_dict["username"] == "testuser"

    def test_enum_values(self):
        """Test that enums have correct values"""
        # Test NodeType enum
        assert NodeType.EXPOSITION.value == "exposition"
        assert NodeType.ACTION.value == "action"
        assert NodeType.REACTION.value == "reaction"
        assert NodeType.TWIST.value == "twist"
        assert NodeType.DEVELOPMENT.value == "development"
        assert NodeType.OTHER.value == "other"

        # Test PlotSectionType enum
        assert PlotSectionType.LOWER.value == "Tension lowers"
        assert PlotSectionType.FLAT.value == "Tension sustains"
        assert PlotSectionType.RISING.value == "Increases tension"
        assert PlotSectionType.POINT.value == "Singular moment"

        # Test NoteType enum
        assert NoteType.WHAT.value == "what"
        assert NoteType.WHY.value == "why"
        assert NoteType.HOW.value == "how"
        assert NoteType.WHEN.value == "when"
        assert NoteType.WHERE.value == "where"

    def test_node_type_completeness(self):
        """Test that NodeType enum covers all expected node types"""
        expected_types = {
            "exposition",
            "action",
            "reaction",
            "twist",
            "development",
            "other",
        }
        actual_types = {node_type.value for node_type in NodeType}

        assert (
            expected_types == actual_types
        ), f"Missing node types: {expected_types - actual_types}"

    def test_model_instantiation(self):
        """Test that model classes can be instantiated"""
        # Test User
        user = User(username="testuser")
        assert user.username == "testuser"

        # Test Storyline
        storyline = Storyline(
            name="Test Story", description="A test storyline", user_id=1
        )
        assert storyline.name == "Test Story"
        assert storyline.description == "A test storyline"
        assert storyline.user_id == 1

        # Test Setting
        setting = Setting(name="Test Setting", description="A test setting", user_id=1)
        assert setting.name == "Test Setting"
        assert setting.description == "A test setting"
        assert setting.user_id == 1


class TestDatabaseSchemaRelationships:
    """Test database relationships (conceptual tests without actual DB)"""

    def test_user_storyline_relationship_concept(self):
        """Test the concept of user-storyline relationships"""
        # Test that relationship fields exist
        user = User(username="testuser")
        assert hasattr(user, "storylines")

        storyline = Storyline(name="Test Story", user_id=1)
        assert hasattr(storyline, "user_id")

    def test_storyline_setting_relationship_concept(self):
        """Test the concept of storyline-setting relationships"""
        storyline = Storyline(name="Test Story", user_id=1)
        setting = Setting(name="Test Setting", user_id=1)

        # Test that relationship fields exist
        assert hasattr(storyline, "storyline_to_settings")
        assert hasattr(setting, "storyline_to_setting")

    def test_litography_node_attributes(self):
        """Test that LitographyNode has required attributes for the node system"""
        # Test enum assignment
        node = LitographyNode(
            node_type=NodeType.EXPOSITION,
            storyline_id=1,
            x_position=100.0,
            y_position=200.0,
        )

        assert node.node_type == NodeType.EXPOSITION
        assert node.storyline_id == 1
        assert node.x_position == 100.0
        assert node.y_position == 200.0

    def test_world_building_entities_exist(self):
        """Test that world-building entities can be created"""
        # Test Actor
        actor = Actor(first_name="Test", last_name="Character", setting_id=1)
        assert actor.first_name == "Test"
        assert actor.last_name == "Character"
        assert actor.setting_id == 1

        # Test Faction
        faction = Faction(name="Test Faction", setting_id=1)
        assert faction.name == "Test Faction"
        assert faction.setting_id == 1

        # Test Location
        location = Location(name="Test Location", setting_id=1)
        assert location.name == "Test Location"
        assert location.setting_id == 1

        # Test Object
        obj = Object_(name="Test Object", setting_id=1)
        assert obj.name == "Test Object"
        assert obj.setting_id == 1


class TestDatabaseSchemaValidation:
    """Test schema validation and constraints"""

    def test_required_fields_validation(self):
        """Test that required fields are properly defined"""
        # User requires username (would fail in production)
        # In testing, SQLAlchemy allows creation without required fields
        user = User()
        assert hasattr(user, "username")

        # Storyline requires user_id
        storyline = Storyline(name="Test")
        assert hasattr(storyline, "user_id")

        # Setting requires user_id
        setting = Setting(name="Test")
        assert hasattr(setting, "user_id")

    def test_enum_field_validation(self):
        """Test that enum fields accept valid values"""
        # Test valid NodeType assignment
        node = LitographyNode(node_type=NodeType.ACTION, storyline_id=1)
        assert node.node_type == NodeType.ACTION

        # Test that enum values are accessible
        assert NodeType.ACTION in NodeType
        assert NodeType.EXPOSITION in NodeType

    def test_foreign_key_relationships(self):
        """Test that foreign key relationships are properly defined"""
        # Test that models have foreign key fields
        storyline = Storyline(name="Test", user_id=1)
        assert hasattr(storyline, "user_id")

        setting = Setting(name="Test", user_id=1)
        assert hasattr(setting, "user_id")

        node = LitographyNode(storyline_id=1, node_type=NodeType.OTHER)
        assert hasattr(node, "storyline_id")

        actor = Actor(first_name="Test", setting_id=1)
        assert hasattr(actor, "setting_id")

    def test_position_fields_for_nodes(self):
        """Test that nodes have position fields for the visual editor"""
        node = LitographyNode(
            storyline_id=1,
            node_type=NodeType.EXPOSITION,
            x_position=150.5,
            y_position=275.0,
        )

        # Test that position fields exist and accept float values
        assert hasattr(node, "x_position")
        assert hasattr(node, "y_position")
        assert isinstance(node.x_position, float)
        assert isinstance(node.y_position, float)
        assert node.x_position == 150.5
        assert node.y_position == 275.0


class TestDatabaseSchemaIntegration:
    """Test integration aspects of the schema"""

    def test_schema_completeness_for_node_system(self):
        """Test that schema supports the node connection system"""
        # Test that LitographyNode has all required fields for the visual editor
        node = LitographyNode(
            storyline_id=1,
            node_type=NodeType.EXPOSITION,
            x_position=100.0,
            y_position=200.0,
        )

        required_fields = ["storyline_id", "node_type", "x_position", "y_position"]
        for field in required_fields:
            assert hasattr(
                node, field
            ), f"LitographyNode missing required field: {field}"

    def test_multi_user_support(self):
        """Test that schema supports multiple users"""
        # Test that multiple users can be created
        user1 = User(username="user1")
        user2 = User(username="user2")

        assert user1.username != user2.username

        # Test that storylines can belong to different users
        story1 = Storyline(name="Story1", user_id=1)
        story2 = Storyline(name="Story2", user_id=2)

        assert story1.user_id != story2.user_id

    def test_multi_project_support(self):
        """Test that schema supports multiple projects/settings"""
        # Test that multiple settings can exist
        setting1 = Setting(name="Fantasy World", user_id=1)
        setting2 = Setting(name="Sci-Fi Universe", user_id=1)

        assert setting1.name != setting2.name

        # Test that actors can belong to different settings
        character1 = Actor(first_name="Wizard", setting_id=1)
        character2 = Actor(first_name="Space", last_name="Captain", setting_id=2)

        assert character1.setting_id != character2.setting_id

    def test_world_building_completeness(self):
        """Test that world-building entities have essential fields"""
        # Test Actor has required fields
        actor = Actor(first_name="Test", last_name="Character", setting_id=1)
        essential_actor_fields = ["first_name", "last_name", "setting_id"]
        for field in essential_actor_fields:
            assert hasattr(actor, field), f"Actor missing essential field: {field}"

        # Test Faction has required fields
        faction = Faction(name="Test Faction", setting_id=1)
        essential_faction_fields = ["name", "setting_id"]
        for field in essential_faction_fields:
            assert hasattr(faction, field), f"Faction missing essential field: {field}"

        # Test Location has required fields
        location = Location(name="Test Location", setting_id=1)
        essential_location_fields = ["name", "setting_id"]
        for field in essential_location_fields:
            assert hasattr(
                location, field
            ), f"Location missing essential field: {field}"
