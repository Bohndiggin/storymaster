"""
Test suite for character arc schema additions
"""

import pytest
from storymaster.model.database.schema.base import (
    LitographyArc, ArcType, ArcPoint, ArcToActor, Setting, Actor, Storyline
)


class TestCharacterArcSchema:
    """Test character arc schema components"""

    def test_arc_type_model_creation(self):
        """Test that ArcType models can be created"""
        arc_type = ArcType(
            name="Hero's Journey",
            description="The classic hero's journey arc",
            setting_id=1
        )
        
        assert arc_type.name == "Hero's Journey"
        assert arc_type.description == "The classic hero's journey arc"
        assert arc_type.setting_id == 1

    def test_litography_arc_model_creation(self):
        """Test that LitographyArc models can be created"""
        arc = LitographyArc(
            title="Character Growth",
            description="A character's journey of personal growth",
            arc_type_id=1,
            storyline_id=1
        )
        
        assert arc.title == "Character Growth"
        assert arc.description == "A character's journey of personal growth"
        assert arc.arc_type_id == 1
        assert arc.storyline_id == 1

    def test_arc_point_model_creation(self):
        """Test that ArcPoint models can be created"""
        point = ArcPoint(
            arc_id=1,
            title="Moment of Change",
            order_index=1,
            description="The character realizes they must change",
            emotional_state="Conflicted",
            character_relationships="Strained with mentor",
            goals="Learn the truth",
            internal_conflict="Fear vs. duty",
            node_id=1
        )
        
        assert point.arc_id == 1
        assert point.title == "Moment of Change"
        assert point.order_index == 1
        assert point.description == "The character realizes they must change"
        assert point.emotional_state == "Conflicted"
        assert point.character_relationships == "Strained with mentor"
        assert point.goals == "Learn the truth"
        assert point.internal_conflict == "Fear vs. duty"
        assert point.node_id == 1

    def test_arc_to_actor_relationship_creation(self):
        """Test that ArcToActor relationship models can be created"""
        arc_to_actor = ArcToActor(
            arc_id=1,
            actor_id=1
        )
        
        assert arc_to_actor.arc_id == 1
        assert arc_to_actor.actor_id == 1

    def test_character_arc_required_fields(self):
        """Test that character arc models have required fields"""
        # Test ArcType required fields
        arc_type = ArcType(name="Test Type", setting_id=1)
        required_arc_type_fields = ['name', 'setting_id']
        for field in required_arc_type_fields:
            assert hasattr(arc_type, field), f"ArcType missing required field: {field}"

        # Test LitographyArc required fields
        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        required_arc_fields = ['title', 'arc_type_id', 'storyline_id']
        for field in required_arc_fields:
            assert hasattr(arc, field), f"LitographyArc missing required field: {field}"

        # Test ArcPoint required fields
        point = ArcPoint(arc_id=1, title="Test Point", order_index=1)
        required_point_fields = ['arc_id', 'title', 'order_index']
        for field in required_point_fields:
            assert hasattr(point, field), f"ArcPoint missing required field: {field}"

    def test_character_arc_optional_fields(self):
        """Test that character arc models have optional fields"""
        # Test ArcType optional fields
        arc_type = ArcType(name="Test Type", setting_id=1)
        optional_arc_type_fields = ['description']
        for field in optional_arc_type_fields:
            assert hasattr(arc_type, field), f"ArcType missing optional field: {field}"

        # Test LitographyArc optional fields
        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        optional_arc_fields = ['description']
        for field in optional_arc_fields:
            assert hasattr(arc, field), f"LitographyArc missing optional field: {field}"

        # Test ArcPoint optional fields
        point = ArcPoint(arc_id=1, title="Test Point", order_index=1)
        optional_point_fields = [
            'description', 'emotional_state', 'character_relationships',
            'goals', 'internal_conflict', 'node_id'
        ]
        for field in optional_point_fields:
            assert hasattr(point, field), f"ArcPoint missing optional field: {field}"

    def test_character_arc_foreign_key_relationships(self):
        """Test that foreign key relationships are properly defined"""
        # Test ArcType relationship to Setting
        arc_type = ArcType(name="Test Type", setting_id=1)
        assert hasattr(arc_type, 'setting_id')

        # Test LitographyArc relationships
        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        assert hasattr(arc, 'arc_type_id')
        assert hasattr(arc, 'storyline_id')

        # Test ArcPoint relationships
        point = ArcPoint(arc_id=1, title="Test Point", order_index=1, node_id=1)
        assert hasattr(point, 'arc_id')
        assert hasattr(point, 'node_id')

        # Test ArcToActor relationship
        arc_to_actor = ArcToActor(arc_id=1, actor_id=1)
        assert hasattr(arc_to_actor, 'arc_id')
        assert hasattr(arc_to_actor, 'actor_id')

    def test_character_arc_relationship_attributes(self):
        """Test that relationship attributes exist"""
        # Test that models have relationship attributes defined
        arc_type = ArcType(name="Test Type", setting_id=1)
        assert hasattr(arc_type, 'setting')

        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        assert hasattr(arc, 'arc_type')
        assert hasattr(arc, 'storyline')
        assert hasattr(arc, 'actors')
        assert hasattr(arc, 'arc_points')

        point = ArcPoint(arc_id=1, title="Test Point", order_index=1)
        assert hasattr(point, 'arc')
        assert hasattr(point, 'node')

        arc_to_actor = ArcToActor(arc_id=1, actor_id=1)
        assert hasattr(arc_to_actor, 'arc')
        assert hasattr(arc_to_actor, 'actor')

    def test_character_arc_data_types(self):
        """Test that character arc fields have correct data types"""
        # Create instances with different data types
        arc_type = ArcType(name="Test Type", description="Test desc", setting_id=1)
        assert isinstance(arc_type.name, str)
        assert arc_type.description is None or isinstance(arc_type.description, str)
        assert isinstance(arc_type.setting_id, int)

        arc = LitographyArc(title="Test Arc", description="Test desc", arc_type_id=1, storyline_id=1)
        assert isinstance(arc.title, str)
        assert arc.description is None or isinstance(arc.description, str)
        assert isinstance(arc.arc_type_id, int)
        assert isinstance(arc.storyline_id, int)

        point = ArcPoint(arc_id=1, title="Test Point", order_index=1, node_id=1)
        assert isinstance(point.arc_id, int)
        assert isinstance(point.title, str)
        assert isinstance(point.order_index, int)
        assert point.node_id is None or isinstance(point.node_id, int)

    def test_character_arc_table_names(self):
        """Test that character arc tables have correct names"""
        assert ArcType.__tablename__ == "arc_type"
        assert LitographyArc.__tablename__ == "litography_arc"
        assert ArcPoint.__tablename__ == "arc_point"
        assert ArcToActor.__tablename__ == "arc_to_actor"

    def test_character_arc_schema_completeness(self):
        """Test that character arc schema supports all required functionality"""
        # Test that we can create a complete character arc structure
        
        # Arc type
        arc_type = ArcType(name="Hero's Journey", setting_id=1)
        essential_arc_type_fields = ['id', 'name', 'description', 'setting_id']
        for field in essential_arc_type_fields:
            assert hasattr(arc_type, field), f"ArcType missing essential field: {field}"

        # Character arc
        arc = LitographyArc(title="Character Growth", arc_type_id=1, storyline_id=1)
        essential_arc_fields = ['id', 'title', 'description', 'arc_type_id', 'storyline_id']
        for field in essential_arc_fields:
            assert hasattr(arc, field), f"LitographyArc missing essential field: {field}"

        # Arc point with all tracking fields
        point = ArcPoint(
            arc_id=1, title="Test Point", order_index=1,
            emotional_state="Happy", character_relationships="Strong",
            goals="Save world", internal_conflict="Self-doubt"
        )
        essential_point_fields = [
            'id', 'arc_id', 'title', 'order_index', 'description',
            'emotional_state', 'character_relationships', 'goals', 
            'internal_conflict', 'node_id'
        ]
        for field in essential_point_fields:
            assert hasattr(point, field), f"ArcPoint missing essential field: {field}"

        # Relationship junction table
        arc_to_actor = ArcToActor(arc_id=1, actor_id=1)
        essential_relationship_fields = ['id', 'arc_id', 'actor_id']
        for field in essential_relationship_fields:
            assert hasattr(arc_to_actor, field), f"ArcToActor missing essential field: {field}"

    def test_character_arc_integration_with_existing_schema(self):
        """Test that character arc schema integrates with existing schema"""
        # Test that character arcs reference existing entities correctly
        
        # Arc types reference settings
        arc_type = ArcType(name="Test Type", setting_id=1)
        assert hasattr(arc_type, 'setting_id')
        
        # Arcs reference storylines and arc types
        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        assert hasattr(arc, 'arc_type_id')
        assert hasattr(arc, 'storyline_id')
        
        # Arc points can reference story nodes
        point = ArcPoint(arc_id=1, title="Test Point", order_index=1, node_id=1)
        assert hasattr(point, 'node_id')
        
        # Junction table references arcs and actors
        arc_to_actor = ArcToActor(arc_id=1, actor_id=1)
        assert hasattr(arc_to_actor, 'arc_id')
        assert hasattr(arc_to_actor, 'actor_id')


class TestCharacterArcSchemaValidation:
    """Test character arc schema validation and constraints"""

    def test_arc_point_order_index_constraint(self):
        """Test that arc points have proper order index handling"""
        point1 = ArcPoint(arc_id=1, title="First Point", order_index=1)
        point2 = ArcPoint(arc_id=1, title="Second Point", order_index=2)
        
        assert point1.order_index < point2.order_index
        assert isinstance(point1.order_index, int)
        assert isinstance(point2.order_index, int)

    def test_character_arc_text_field_lengths(self):
        """Test that text fields can handle reasonable content lengths"""
        # Test that description fields can handle longer text
        long_description = "A" * 1000  # 1000 character description
        
        arc_type = ArcType(name="Test", description=long_description, setting_id=1)
        assert len(arc_type.description) == 1000
        
        arc = LitographyArc(title="Test", description=long_description, arc_type_id=1, storyline_id=1)
        assert len(arc.description) == 1000
        
        point = ArcPoint(
            arc_id=1, title="Test", order_index=1,
            description=long_description,
            emotional_state="Complex emotional state with detailed description",
            character_relationships="Detailed relationship dynamics",
            goals="Comprehensive list of character goals",
            internal_conflict="Deep internal psychological conflict"
        )
        assert len(point.description) == 1000

    def test_character_arc_none_handling(self):
        """Test that optional fields handle None values correctly"""
        # Test ArcType with minimal fields
        arc_type = ArcType(name="Test Type", setting_id=1)
        assert arc_type.description is None
        
        # Test LitographyArc with minimal fields  
        arc = LitographyArc(title="Test Arc", arc_type_id=1, storyline_id=1)
        assert arc.description is None
        
        # Test ArcPoint with minimal fields
        point = ArcPoint(arc_id=1, title="Test Point", order_index=1)
        assert point.description is None
        assert point.emotional_state is None
        assert point.character_relationships is None
        assert point.goals is None
        assert point.internal_conflict is None
        assert point.node_id is None

    def test_character_arc_id_fields(self):
        """Test that ID fields are properly configured"""
        # All character arc models should have ID fields
        arc_type = ArcType(name="Test", setting_id=1)
        assert hasattr(arc_type, 'id')
        
        arc = LitographyArc(title="Test", arc_type_id=1, storyline_id=1)
        assert hasattr(arc, 'id')
        
        point = ArcPoint(arc_id=1, title="Test", order_index=1)
        assert hasattr(point, 'id')
        
        arc_to_actor = ArcToActor(arc_id=1, actor_id=1)
        assert hasattr(arc_to_actor, 'id')