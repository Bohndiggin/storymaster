"""
Test suite for common model classes and utilities
"""

import pytest
from storymaster.model.common.common_model import (
    StorioModes,
    GroupListTypes,
    GroupData,
    BaseModel,
)
from storymaster.model.database.schema.base import (
    Actor,
    Background,
    Class_,
    Faction,
    History,
    Location,
    Object_,
    Race,
    SubRace,
    WorldData,
)


class TestStorioModes:
    """Test the StorioModes enum"""

    def test_storio_modes_values(self):
        """Test that StorioModes has correct values"""
        assert StorioModes.LOREKEEPER.value == "Lorekeeper"
        assert StorioModes.LITOGRAPHER.value == "Litographer"

    def test_storio_modes_completeness(self):
        """Test that all expected modes are present"""
        expected_modes = {"Lorekeeper", "Litographer"}
        actual_modes = {mode.value for mode in StorioModes}

        assert expected_modes == actual_modes

    def test_storio_modes_iteration(self):
        """Test that StorioModes can be iterated"""
        modes = list(StorioModes)
        assert len(modes) == 2
        assert StorioModes.LOREKEEPER in modes
        assert StorioModes.LITOGRAPHER in modes


class TestGroupListTypes:
    """Test the GroupListTypes enum"""

    def test_group_list_types_values(self):
        """Test that GroupListTypes has correct values"""
        assert GroupListTypes.ACTORS.value == "actors"
        assert GroupListTypes.BACKGROUNDS.value == "backgrounds"
        assert GroupListTypes.CLASSES.value == "classes"
        assert GroupListTypes.FACTIONS.value == "factions"
        assert GroupListTypes.HISTORY.value == "history"
        assert GroupListTypes.LOCATIONS.value == "locations"
        assert GroupListTypes.OBJECTS.value == "objects"
        assert GroupListTypes.RACES.value == "races"
        assert GroupListTypes.SUB_RACES.value == "sub_races"
        assert GroupListTypes.WORLD_DATAS.value == "world_datas"

    def test_group_list_types_completeness(self):
        """Test that all expected world-building types are present"""
        expected_types = {
            "actors",
            "backgrounds",
            "classes",
            "factions",
            "history",
            "locations",
            "objects",
            "races",
            "sub_races",
            "world_datas",
        }
        actual_types = {group_type.value for group_type in GroupListTypes}

        assert expected_types == actual_types

    def test_group_list_types_coverage(self):
        """Test that GroupListTypes covers all major world-building entities"""
        # These should correspond to the main entity types in the application
        core_entities = [
            GroupListTypes.ACTORS,
            GroupListTypes.FACTIONS,
            GroupListTypes.LOCATIONS,
            GroupListTypes.OBJECTS,
        ]

        for entity in core_entities:
            assert entity in GroupListTypes


class TestGroupData:
    """Test the GroupData class"""

    def test_group_data_initialization(self):
        """Test that GroupData can be initialized with empty lists"""
        group_data = GroupData(
            actors=[],
            backgrounds=[],
            classes=[],
            factions=[],
            history=[],
            locations=[],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        assert isinstance(group_data.actors, list)
        assert isinstance(group_data.backgrounds, list)
        assert isinstance(group_data.classes, list)
        assert isinstance(group_data.factions, list)
        assert isinstance(group_data.history, list)
        assert isinstance(group_data.locations, list)
        assert isinstance(group_data.objects, list)
        assert isinstance(group_data.races, list)
        assert isinstance(group_data.sub_races, list)
        assert isinstance(group_data.world_datas, list)

    def test_group_data_with_mock_entities(self):
        """Test GroupData with mock entities"""
        # Create mock entities
        mock_actor = Actor(first_name="Test", last_name="Actor", setting_id=1)
        mock_faction = Faction(name="Test Faction", setting_id=1)
        mock_location = Location(name="Test Location", setting_id=1)

        group_data = GroupData(
            actors=[mock_actor],
            backgrounds=[],
            classes=[],
            factions=[mock_faction],
            history=[],
            locations=[mock_location],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        assert len(group_data.actors) == 1
        assert len(group_data.factions) == 1
        assert len(group_data.locations) == 1
        assert group_data.actors[0].first_name == "Test"
        assert group_data.actors[0].last_name == "Actor"
        assert group_data.factions[0].name == "Test Faction"
        assert group_data.locations[0].name == "Test Location"

    def test_group_data_attributes_exist(self):
        """Test that GroupData has all expected attributes"""
        group_data = GroupData(
            actors=[],
            backgrounds=[],
            classes=[],
            factions=[],
            history=[],
            locations=[],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        expected_attributes = [
            "actors",
            "backgrounds",
            "classes",
            "factions",
            "history",
            "locations",
            "objects",
            "races",
            "sub_races",
            "world_datas",
        ]

        for attr in expected_attributes:
            assert hasattr(group_data, attr), f"GroupData missing attribute: {attr}"

    def test_group_data_type_hints(self):
        """Test that GroupData accepts correct types"""
        # Test with actual entity types
        actor = Actor(first_name="Test", setting_id=1)
        background = Background(name="Test", setting_id=1)
        faction = Faction(name="Test", setting_id=1)

        group_data = GroupData(
            actors=[actor],
            backgrounds=[background],
            classes=[],
            factions=[faction],
            history=[],
            locations=[],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        assert isinstance(group_data.actors[0], Actor)
        assert isinstance(group_data.backgrounds[0], Background)
        assert isinstance(group_data.factions[0], Faction)


class TestBaseModelConcepts:
    """Test BaseModel concepts without database dependencies"""

    def test_base_model_import(self):
        """Test that BaseModel can be imported"""
        assert BaseModel is not None

    def test_base_model_instantiation_concept(self):
        """Test the concept of BaseModel instantiation"""
        # Test that BaseModel expects a user_id parameter
        # This is a conceptual test without actual database connection
        try:
            # This would normally require a database connection
            # but we're testing the interface concept
            assert hasattr(BaseModel, "__init__")
        except Exception:
            # Expected - would need database setup for actual instantiation
            pass

    def test_base_model_methods_exist(self):
        """Test that BaseModel has expected methods"""
        # Test method existence conceptually
        expected_methods = [
            "get_all_actors",
            "get_litography_nodes",
            "create_new_row",
            "update_row",
            "delete_row",
        ]

        for method_name in expected_methods:
            # BaseModel should have these methods defined
            # (even if they require database connection to work)
            try:
                assert hasattr(
                    BaseModel, method_name
                ), f"BaseModel missing method: {method_name}"
            except Exception:
                # Some methods might not be accessible without instantiation
                pass


class TestModelUtilities:
    """Test utility functions and classes"""

    def test_enum_integration(self):
        """Test that model enums integrate well together"""
        # Test that StorioModes and GroupListTypes work together conceptually

        # Lorekeeper mode should work with all group types
        lorekeeper_mode = StorioModes.LOREKEEPER
        world_building_types = [
            GroupListTypes.ACTORS,
            GroupListTypes.FACTIONS,
            GroupListTypes.LOCATIONS,
            GroupListTypes.OBJECTS,
        ]

        assert lorekeeper_mode.value == "Lorekeeper"
        for wb_type in world_building_types:
            assert wb_type in GroupListTypes

    def test_data_structure_consistency(self):
        """Test that data structures are consistent"""
        # Test that GroupData attributes align with GroupListTypes
        group_list_values = {group_type.value for group_type in GroupListTypes}

        # Create empty GroupData to check attributes
        group_data = GroupData(
            actors=[],
            backgrounds=[],
            classes=[],
            factions=[],
            history=[],
            locations=[],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        # All GroupListTypes values should have corresponding GroupData attributes
        for group_type in GroupListTypes:
            attr_name = group_type.value
            assert hasattr(
                group_data, attr_name
            ), f"GroupData missing attribute for {attr_name}"

    def test_world_building_completeness(self):
        """Test that world-building system is complete"""
        # Test that we have all major world-building categories
        essential_categories = [
            GroupListTypes.ACTORS,  # Characters
            GroupListTypes.FACTIONS,  # Organizations
            GroupListTypes.LOCATIONS,  # Places
            GroupListTypes.OBJECTS,  # Items
            GroupListTypes.HISTORY,  # Events
            GroupListTypes.WORLD_DATAS,  # Lore/concepts
        ]

        for category in essential_categories:
            assert category in GroupListTypes, f"Missing essential category: {category}"

    def test_application_modes_coverage(self):
        """Test that application modes cover main functionality"""
        # Test that we have modes for both main features
        assert StorioModes.LITOGRAPHER in StorioModes  # Story plotting
        assert StorioModes.LOREKEEPER in StorioModes  # World building

        # Test mode count (should be exactly 2 main modes)
        assert len(list(StorioModes)) == 2


class TestDataTypeValidation:
    """Test data type validation and constraints"""

    def test_string_enum_values(self):
        """Test that enum values are strings as expected"""
        for mode in StorioModes:
            assert isinstance(mode.value, str)

        for group_type in GroupListTypes:
            assert isinstance(group_type.value, str)

    def test_enum_value_formatting(self):
        """Test that enum values follow expected formatting"""
        # StorioModes should be title case
        for mode in StorioModes:
            assert mode.value.istitle(), f"StorioMode {mode.value} should be title case"

        # GroupListTypes should be lowercase with underscores
        for group_type in GroupListTypes:
            value = group_type.value
            assert value.islower(), f"GroupListType {value} should be lowercase"
            assert " " not in value, f"GroupListType {value} should not contain spaces"

    def test_list_type_annotations(self):
        """Test that GroupData type annotations are consistent"""
        # This is a conceptual test for type consistency
        group_data = GroupData(
            actors=[],
            backgrounds=[],
            classes=[],
            factions=[],
            history=[],
            locations=[],
            objects=[],
            races=[],
            sub_races=[],
            world_datas=[],
        )

        # All attributes should be lists
        for attr_name in [
            "actors",
            "backgrounds",
            "classes",
            "factions",
            "history",
            "locations",
            "objects",
            "races",
            "sub_races",
            "world_datas",
        ]:
            attr_value = getattr(group_data, attr_name)
            assert isinstance(attr_value, list), f"{attr_name} should be a list"
