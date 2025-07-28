"""
Test suite for node positioning and scene redraw functionality
"""

import pytest
from tests.test_qt_utils import QT_AVAILABLE, QPointF, QApplication, QGraphicsScene

# Skip all tests in this module if Qt is not available
pytestmark = pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt6 not available in headless environment")

from storymaster.controller.common.main_page_controller import (
    CircleNodeItem,
    RectangleNodeItem,
    create_node_item,
)


class MockNodeData:
    """Mock node data class for testing"""

    def __init__(self, id_val, x_pos=100, y_pos=200, node_type_name="EXPOSITION"):
        self.id = id_val
        self.x_position = x_pos
        self.y_position = y_pos
        self.node_type = MockNodeType(node_type_name)


class MockNodeType:
    """Mock node type class"""

    def __init__(self, name):
        self.name = name


class MockController:
    """Mock controller for testing"""

    def __init__(self):
        self.node_scene = QGraphicsScene()


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_controller():
    """Create mock controller with scene"""
    return MockController()


@pytest.fixture
def graphics_scene():
    """Create graphics scene"""
    return QGraphicsScene()


class TestNodePositioning:
    """Test node positioning functionality"""

    def test_multiple_nodes_have_separate_connection_points(
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

        # Verify initial positions
        assert node1.pos().x() == 100
        assert node1.pos().y() == 100
        assert node2.pos().x() == 300
        assert node2.pos().y() == 100

        # Verify they're different objects
        assert id(node1.input_point) != id(
            node2.input_point
        ), "Input points are shared!"
        assert id(node1.output_point) != id(
            node2.output_point
        ), "Output points are shared!"

        # Get initial connection positions for node2
        node2_initial_input = node2.get_input_connection_pos()
        node2_initial_output = node2.get_output_connection_pos()

        # Move node1 and verify node2's connections don't move
        node1.setPos(200, 200)

        node2_after_input = node2.get_input_connection_pos()
        node2_after_output = node2.get_output_connection_pos()

        # Node 2's positions should be unchanged
        assert (
            abs(node2_after_input.x() - node2_initial_input.x()) < 1.0
        ), "Node 2 input moved!"
        assert (
            abs(node2_after_input.y() - node2_initial_input.y()) < 1.0
        ), "Node 2 input moved!"
        assert (
            abs(node2_after_output.x() - node2_initial_output.x()) < 1.0
        ), "Node 2 output moved!"
        assert (
            abs(node2_after_output.y() - node2_initial_output.y()) < 1.0
        ), "Node 2 output moved!"

    def test_node_recreation_preserves_position(
        self, qapp, graphics_scene, mock_controller
    ):
        """Test that node recreation (simulating scene.clear() + redraw) preserves position"""
        # Create initial node
        node_data = MockNodeData(1)
        node = RectangleNodeItem(0, 0, 80, 80, node_data, mock_controller)
        graphics_scene.addItem(node)
        node.setPos(100, 100)

        # Get initial connection positions
        initial_input = node.get_input_connection_pos()
        initial_output = node.get_output_connection_pos()

        # Simulate scene.clear() and recreate node
        graphics_scene.clear()

        # Recreate the same node at same position
        node_recreated = RectangleNodeItem(0, 0, 80, 80, node_data, mock_controller)
        graphics_scene.addItem(node_recreated)
        node_recreated.setPos(100, 100)  # Set to same position

        # Get connection positions after recreation
        recreated_input = node_recreated.get_input_connection_pos()
        recreated_output = node_recreated.get_output_connection_pos()

        # Positions should be the same
        assert (
            abs(recreated_input.x() - initial_input.x()) < 1.0
        ), "Input position changed after recreation"
        assert (
            abs(recreated_input.y() - initial_input.y()) < 1.0
        ), "Input position changed after recreation"
        assert (
            abs(recreated_output.x() - initial_output.x()) < 1.0
        ), "Output position changed after recreation"
        assert (
            abs(recreated_output.y() - initial_output.y()) < 1.0
        ), "Output position changed after recreation"

    def test_real_workflow_node_creation(self, qapp, mock_controller):
        """Test the real application workflow for node creation"""
        scene = mock_controller.node_scene

        # Create mock database nodes (simulating database records)
        nodes = [
            MockNodeData(1, 100, 100, "EXPOSITION"),  # Rectangle
            MockNodeData(2, 300, 150, "REACTION"),  # Circle
        ]

        # Simulate load_and_draw_nodes workflow
        def simulate_load_and_draw_nodes(nodes_to_draw):
            scene.clear()
            node_items = []

            for node in nodes_to_draw:
                x_pos = getattr(node, "x_position", 100 + (node.id * 150))
                y_pos = getattr(node, "y_position", 200)

                # Create node at origin then position (the fixed approach)
                node_item = create_node_item(0, 0, 80, 80, node, mock_controller)
                scene.addItem(node_item)
                node_item.setPos(x_pos, y_pos)

                node_items.append(node_item)

            return node_items

        # Initial load
        node_items = simulate_load_and_draw_nodes(nodes)

        # Verify initial positions
        assert len(node_items) == 2
        assert node_items[0].pos().x() == 100
        assert node_items[0].pos().y() == 100
        assert node_items[1].pos().x() == 300
        assert node_items[1].pos().y() == 150

        # Get connection positions before adding new node
        initial_connections = [
            (item.get_input_connection_pos(), item.get_output_connection_pos())
            for item in node_items
        ]

        # Add a new node (this triggers the redraw)
        new_node = MockNodeData(3, 500, 200, "ACTION")
        nodes.append(new_node)

        # Redraw all nodes (this is what happens in the real app)
        node_items = simulate_load_and_draw_nodes(nodes)

        # Verify all connection points are still correct
        for i, node_item in enumerate(node_items[:-1]):  # Skip the new node
            expected_x = nodes[i].x_position
            expected_y = nodes[i].y_position

            input_pos = node_item.get_input_connection_pos()
            output_pos = node_item.get_output_connection_pos()

            # Check if connection points are near expected positions
            input_expected_x = expected_x - 5  # Left of node
            output_expected_x = expected_x + 85  # Right of node
            expected_y_center = expected_y + 40  # Middle of node

            assert (
                abs(input_pos.x() - input_expected_x) < 10
            ), f"Node {i+1} input position incorrect"
            assert (
                abs(input_pos.y() - expected_y_center) < 10
            ), f"Node {i+1} input position incorrect"
            assert (
                abs(output_pos.x() - output_expected_x) < 10
            ), f"Node {i+1} output position incorrect"
            assert (
                abs(output_pos.y() - expected_y_center) < 10
            ), f"Node {i+1} output position incorrect"

    def test_get_node_ui_position_method(self, qapp, mock_controller):
        """Test the get_node_ui_position helper method"""
        scene = mock_controller.node_scene

        # Add the method to our mock controller for testing
        def get_node_ui_position(node_id):
            """Get the current UI position of a node from the graphics scene"""
            for item in scene.items():
                if hasattr(item, "node_data") and item.node_data.id == node_id:
                    pos = item.pos()
                    return float(pos.x()), float(pos.y())
            # Fallback
            return 100.0, 200.0

        mock_controller.get_node_ui_position = get_node_ui_position

        # Create a test node at a specific position
        node_data = MockNodeData(1, 150, 250, "EXPOSITION")
        node_item = create_node_item(0, 0, 80, 80, node_data, mock_controller)
        scene.addItem(node_item)
        node_item.setPos(150, 250)

        # Test getting position
        ui_x, ui_y = mock_controller.get_node_ui_position(1)
        assert abs(ui_x - 150) < 1, "get_node_ui_position returned wrong x"
        assert abs(ui_y - 250) < 1, "get_node_ui_position returned wrong y"

        # Simulate moving the node (but not saving to database)
        node_item.setPos(300, 400)

        # Test that method returns new position
        ui_x_moved, ui_y_moved = mock_controller.get_node_ui_position(1)
        assert abs(ui_x_moved - 300) < 1, "get_node_ui_position doesn't track movement"
        assert abs(ui_y_moved - 400) < 1, "get_node_ui_position doesn't track movement"

        # Test with non-existent node
        fallback_x, fallback_y = mock_controller.get_node_ui_position(999)
        assert fallback_x == 100.0, "Fallback position incorrect"
        assert fallback_y == 200.0, "Fallback position incorrect"
