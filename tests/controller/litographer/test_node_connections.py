"""
Test suite for the Blender-style node connection system
"""

import pytest
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsScene

from storymaster.controller.common.main_page_controller import (
    CircleNodeItem,
    DiamondNodeItem,
    HexagonNodeItem,
    RectangleNodeItem,
    StarNodeItem,
    TriangleNodeItem,
)


class MockNodeData:
    """Mock node data class for testing"""

    def __init__(self, id_val):
        self.id = id_val


class MockController:
    """Mock controller for testing"""

    def __init__(self):
        pass


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here as other tests might need it


@pytest.fixture
def mock_controller():
    """Create mock controller"""
    return MockController()


@pytest.fixture
def mock_node_data():
    """Create mock node data"""
    return MockNodeData(1)


@pytest.fixture
def graphics_scene():
    """Create graphics scene"""
    return QGraphicsScene()


class TestNodeConnectionPoints:
    """Test node connection point functionality"""

    @pytest.mark.parametrize(
        "node_name,node_class",
        [
            ("Rectangle", RectangleNodeItem),
            ("Circle", CircleNodeItem),
            ("Diamond", DiamondNodeItem),
            ("Star", StarNodeItem),
            ("Hexagon", HexagonNodeItem),
            ("Triangle", TriangleNodeItem),
        ],
    )
    def test_node_has_connection_methods(
        self, qapp, node_name, node_class, mock_node_data, mock_controller
    ):
        """Test that all node types have proper connection point methods"""
        # Create test node
        node = node_class(0, 0, 80, 80, mock_node_data, mock_controller)

        # Test connection point methods exist
        assert hasattr(
            node, "get_input_connection_pos"
        ), f"{node_name} missing get_input_connection_pos"
        assert hasattr(
            node, "get_output_connection_pos"
        ), f"{node_name} missing get_output_connection_pos"

    @pytest.mark.parametrize(
        "node_name,node_class",
        [
            ("Rectangle", RectangleNodeItem),
            ("Circle", CircleNodeItem),
            ("Diamond", DiamondNodeItem),
            ("Star", StarNodeItem),
            ("Hexagon", HexagonNodeItem),
            ("Triangle", TriangleNodeItem),
        ],
    )
    def test_node_connection_points_work(
        self,
        qapp,
        graphics_scene,
        node_name,
        node_class,
        mock_node_data,
        mock_controller,
    ):
        """Test that connection point methods return valid positions"""
        # Create test node
        node = node_class(0, 0, 80, 80, mock_node_data, mock_controller)
        graphics_scene.addItem(node)
        node.setPos(100, 100)

        # Test connection point methods work
        input_pos = node.get_input_connection_pos()
        output_pos = node.get_output_connection_pos()

        assert isinstance(input_pos, QPointF), f"{node_name} input_pos not QPointF"
        assert isinstance(output_pos, QPointF), f"{node_name} output_pos not QPointF"

        # Positions should be reasonable (not at origin unless that's expected)
        assert input_pos.x() >= 0, f"{node_name} input position negative x"
        assert input_pos.y() >= 0, f"{node_name} input position negative y"
        assert output_pos.x() >= 0, f"{node_name} output position negative x"
        assert output_pos.y() >= 0, f"{node_name} output position negative y"

    @pytest.mark.parametrize(
        "node_name,node_class",
        [
            ("Rectangle", RectangleNodeItem),
            ("Circle", CircleNodeItem),
            ("Diamond", DiamondNodeItem),
            ("Star", StarNodeItem),
            ("Hexagon", HexagonNodeItem),
            ("Triangle", TriangleNodeItem),
        ],
    )
    def test_connection_points_have_child_items(
        self,
        qapp,
        graphics_scene,
        node_name,
        node_class,
        mock_node_data,
        mock_controller,
    ):
        """Test that connection points exist as child items"""
        # Create test node
        node = node_class(0, 0, 80, 80, mock_node_data, mock_controller)
        graphics_scene.addItem(node)

        # Test that connection points exist as child items
        assert hasattr(node, "input_point"), f"{node_name} missing input_point"
        assert hasattr(node, "output_point"), f"{node_name} missing output_point"

        # Test relative positions exist
        assert hasattr(
            node.input_point, "relative_x"
        ), f"{node_name} input_point missing relative_x"
        assert hasattr(
            node.input_point, "relative_y"
        ), f"{node_name} input_point missing relative_y"
        assert hasattr(
            node.output_point, "relative_x"
        ), f"{node_name} output_point missing relative_x"
        assert hasattr(
            node.output_point, "relative_y"
        ), f"{node_name} output_point missing relative_y"

    def test_connection_points_move_with_node(
        self, qapp, graphics_scene, mock_node_data, mock_controller
    ):
        """Test that connection points move when node is moved"""
        # Create test node (using Rectangle as example)
        node = RectangleNodeItem(0, 0, 80, 80, mock_node_data, mock_controller)
        graphics_scene.addItem(node)
        node.setPos(100, 100)

        # Get initial positions
        initial_input = node.get_input_connection_pos()
        initial_output = node.get_output_connection_pos()

        # Move node
        node.setPos(150, 150)

        # Get new positions
        new_input = node.get_input_connection_pos()
        new_output = node.get_output_connection_pos()

        # Positions should have moved by 50 pixels in both directions
        assert (
            abs(new_input.x() - initial_input.x() - 50) < 1
        ), "Input connection didn't move correctly"
        assert (
            abs(new_input.y() - initial_input.y() - 50) < 1
        ), "Input connection didn't move correctly"
        assert (
            abs(new_output.x() - initial_output.x() - 50) < 1
        ), "Output connection didn't move correctly"
        assert (
            abs(new_output.y() - initial_output.y() - 50) < 1
        ), "Output connection didn't move correctly"

    def test_different_nodes_have_separate_connection_points(
        self, qapp, graphics_scene, mock_controller
    ):
        """Test that multiple nodes have separate connection points"""
        # Create two different nodes
        node1_data = MockNodeData(1)
        node2_data = MockNodeData(2)

        node1 = RectangleNodeItem(0, 0, 80, 80, node1_data, mock_controller)
        node2 = CircleNodeItem(0, 0, 80, 80, node2_data, mock_controller)

        graphics_scene.addItem(node1)
        graphics_scene.addItem(node2)

        node1.setPos(100, 100)
        node2.setPos(300, 100)

        # Verify they're different objects
        assert id(node1.input_point) != id(
            node2.input_point
        ), "Input points are shared!"
        assert id(node1.output_point) != id(
            node2.output_point
        ), "Output points are shared!"

        # Move node1 and verify node2's connections don't move
        node1.setPos(200, 200)

        node2_input = node2.get_input_connection_pos()
        node2_output = node2.get_output_connection_pos()

        # Node 2's positions should still be around (300, 100) + offsets
        assert (
            abs(node2_input.x() - 295.0) < 10.0
        ), "Node 2 connection moved incorrectly"
        assert (
            abs(node2_input.y() - 140.0) < 10.0
        ), "Node 2 connection moved incorrectly"
