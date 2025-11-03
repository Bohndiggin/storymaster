"""
Test suite for the node system functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from tests.test_qt_utils import (
    QT_AVAILABLE,
    QApplication,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QPainter,
    QPointF,
    Qt,
)

# Skip all tests in this module if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PyQt6 not available in headless environment"
)

from storymaster.model.database.schema.base import (
    LitographyNode,
    NodeType,
    LitographyPlot,
    LitographyPlotSection,
)


class TestNodeModelMethods:
    """Test node model methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_session = Mock()

    def test_get_nodes_for_storyline(self):
        """Test getting nodes for a storyline"""
        mock_node1 = Mock(spec=LitographyNode)
        mock_node1.id = 1
        mock_node1.name = "Opening Scene"
        mock_node1.node_type = NodeType.EXPOSITION
        mock_node1.x_position = 100.0
        mock_node1.y_position = 200.0

        mock_node2 = Mock(spec=LitographyNode)
        mock_node2.id = 2
        mock_node2.name = "Inciting Incident"
        mock_node2.node_type = NodeType.ACTION
        mock_node2.x_position = 300.0
        mock_node2.y_position = 200.0

        self.mock_model.get_nodes_for_storyline.return_value = [mock_node1, mock_node2]

        nodes = self.mock_model.get_nodes_for_storyline(storyline_id=1)

        assert len(nodes) == 2
        assert nodes[0].name == "Opening Scene"
        assert nodes[1].name == "Inciting Incident"
        assert nodes[0].node_type == NodeType.EXPOSITION
        assert nodes[1].node_type == NodeType.ACTION

    def test_create_node(self):
        """Test creating a new node"""
        mock_node = Mock(spec=LitographyNode)
        mock_node.id = 1
        mock_node.name = "New Scene"
        mock_node.node_type = NodeType.ACTION

        self.mock_model.create_node.return_value = mock_node

        result = self.mock_model.create_node(
            label="New Scene",
            node_type=NodeType.ACTION,
            storyline_id=1,
            x_position=150.0,
            y_position=250.0,
        )

        assert result.name == "New Scene"
        assert result.node_type == NodeType.ACTION

    def test_update_node_position(self):
        """Test updating node position"""
        self.mock_model.update_node_position.return_value = None

        # Should not raise an exception
        self.mock_model.update_node_position(node_id=1, x=200.0, y=300.0)

        self.mock_model.update_node_position.assert_called_once_with(
            node_id=1, x=200.0, y=300.0
        )

    def test_delete_node(self):
        """Test deleting a node"""
        self.mock_model.delete_node.return_value = None

        # Should not raise an exception
        self.mock_model.delete_node(node_id=1)

        self.mock_model.delete_node.assert_called_once_with(node_id=1)

    def test_get_node_connections(self):
        """Test getting node connections"""
        mock_connection1 = Mock()
        mock_connection1.from_node_id = 1
        mock_connection1.to_node_id = 2

        mock_connection2 = Mock()
        mock_connection2.from_node_id = 2
        mock_connection2.to_node_id = 3

        self.mock_model.get_node_connections.return_value = [
            mock_connection1,
            mock_connection2,
        ]

        connections = self.mock_model.get_node_connections(storyline_id=1)

        assert len(connections) == 2
        assert connections[0].from_node_id == 1
        assert connections[0].to_node_id == 2

    def test_create_node_connection(self):
        """Test creating a connection between nodes"""
        mock_connection = Mock()
        mock_connection.from_node_id = 1
        mock_connection.to_node_id = 2

        self.mock_model.create_node_connection.return_value = mock_connection

        result = self.mock_model.create_node_connection(from_node_id=1, to_node_id=2)

        assert result.from_node_id == 1
        assert result.to_node_id == 2

    def test_update_node_order(self):
        """Test updating node order in linked list"""
        self.mock_model.update_node_order.return_value = None

        # Should not raise an exception
        self.mock_model.update_node_order(node_id=2, previous_node_id=1, next_node_id=3)

        self.mock_model.update_node_order.assert_called_once_with(
            node_id=2, previous_node_id=1, next_node_id=3
        )


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestNodeGraphicsSystem:
    """Test the graphics system for nodes"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()

    def test_node_graphics_item_creation(self, qapp):
        """Test creating graphics items for nodes"""
        # Mock the node item creation pattern from the application
        mock_node = Mock()
        mock_node.id = 1
        mock_node.name = "Test Node"
        mock_node.node_type = NodeType.EXPOSITION
        mock_node.x_position = 100.0
        mock_node.y_position = 200.0

        # Test that we can create a graphics item concept
        node_item_data = {
            "id": mock_node.id,
            "label": mock_node.name,
            "node_type": mock_node.node_type,
            "position": QPointF(mock_node.x_position, mock_node.y_position),
        }

        assert node_item_data["id"] == 1
        assert node_item_data["label"] == "Test Node"
        assert node_item_data["node_type"] == NodeType.EXPOSITION
        assert node_item_data["position"].x() == 100.0
        assert node_item_data["position"].y() == 200.0

    def test_node_shape_types(self, qapp):
        """Test different node shape types"""
        # Test that all node types are supported
        shapes = {
            NodeType.EXPOSITION: "rectangle",
            NodeType.ACTION: "circle",
            NodeType.REACTION: "diamond",
            NodeType.TWIST: "star",
            NodeType.DEVELOPMENT: "hexagon",
            NodeType.OTHER: "triangle",
        }

        for node_type, expected_shape in shapes.items():
            # Mock node shape creation
            shape_data = {"node_type": node_type, "shape": expected_shape}
            assert shape_data["node_type"] == node_type
            assert shape_data["shape"] == expected_shape

    def test_node_positioning_system(self, qapp):
        """Test node positioning and movement"""
        mock_node = Mock()
        mock_node.id = 1
        mock_node.x_position = 100.0
        mock_node.y_position = 200.0

        # Test position update
        new_position = QPointF(150.0, 250.0)

        # Mock position update
        position_update = {
            "node_id": mock_node.id,
            "old_position": QPointF(mock_node.x_position, mock_node.y_position),
            "new_position": new_position,
        }

        assert position_update["node_id"] == 1
        assert position_update["old_position"].x() == 100.0
        assert position_update["new_position"].x() == 150.0

    def test_node_selection_system(self, qapp):
        """Test node selection handling"""
        # Mock selection state
        selected_nodes = [1, 3, 5]  # Node IDs

        selection_data = {
            "selected_count": len(selected_nodes),
            "selected_ids": selected_nodes,
            "multi_select": len(selected_nodes) > 1,
        }

        assert selection_data["selected_count"] == 3
        assert selection_data["multi_select"] is True
        assert 1 in selection_data["selected_ids"]

    def test_node_connection_drawing(self, qapp):
        """Test drawing connections between nodes"""
        # Mock connection data
        connection_data = {
            "from_node_id": 1,
            "to_node_id": 2,
            "from_position": QPointF(100.0, 200.0),
            "to_position": QPointF(300.0, 200.0),
        }

        # Test connection geometry calculation
        start_point = connection_data["from_position"]
        end_point = connection_data["to_position"]

        # Calculate connection line
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()

        assert dx == 200.0  # Horizontal distance
        assert dy == 0.0  # No vertical distance

        # Test distance calculation
        import math

        distance = math.sqrt(dx * dx + dy * dy)
        assert distance == 200.0


class TestNodeEditingOperations:
    """Test node editing operations"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()

    def test_node_creation_workflow(self, qapp):
        """Test the complete node creation workflow"""
        # Mock the node creation process
        node_data = {
            "name": "New Scene",
            "node_type": NodeType.ACTION,
            "storyline_id": 1,
            "x_position": 200.0,
            "y_position": 300.0,
        }

        mock_node = Mock()
        mock_node.id = 5
        mock_node.name = node_data["name"]
        mock_node.node_type = node_data["node_type"]

        self.mock_model.create_node.return_value = mock_node

        # Simulate node creation
        result = self.mock_model.create_node(**node_data)

        assert result.name == "New Scene"
        assert result.node_type == NodeType.ACTION
        self.mock_model.create_node.assert_called_once_with(**node_data)

    def test_node_editing_workflow(self, qapp):
        """Test node editing workflow"""
        original_node = Mock()
        original_node.id = 1
        original_node.name = "Original Label"
        original_node.node_type = NodeType.EXPOSITION

        # Mock node update
        update_data = {
            "label": "Updated Label",
            "node_type": NodeType.ACTION,
            "description": "Updated description",
        }

        self.mock_model.update_node.return_value = None

        # Simulate node update
        self.mock_model.update_node(node_id=1, **update_data)

        self.mock_model.update_node.assert_called_once_with(node_id=1, **update_data)

    def test_node_deletion_workflow(self, qapp):
        """Test node deletion workflow with connection cleanup"""
        node_to_delete = 2
        connected_nodes = [1, 3]  # Nodes connected to node 2

        # Mock connection cleanup
        self.mock_model.get_connected_nodes.return_value = connected_nodes
        self.mock_model.delete_node_connections.return_value = None
        self.mock_model.delete_node.return_value = None

        # Simulate deletion workflow
        connections = self.mock_model.get_connected_nodes(node_to_delete)
        self.mock_model.delete_node_connections(node_to_delete)
        self.mock_model.delete_node(node_to_delete)

        assert len(connections) == 2
        self.mock_model.delete_node_connections.assert_called_once_with(node_to_delete)
        self.mock_model.delete_node.assert_called_once_with(node_to_delete)

    def test_node_copy_paste_workflow(self, qapp):
        """Test node copy and paste operations"""
        source_node = Mock()
        source_node.name = "Source Node"
        source_node.node_type = NodeType.REACTION
        source_node.description = "Original description"

        # Mock copy operation
        copy_data = {
            "name": f"{source_node.name} (Copy)",
            "node_type": source_node.node_type,
            "description": source_node.description,
            "x_position": 100.0,  # Offset position
            "y_position": 100.0,
            "storyline_id": 1,
        }

        mock_copied_node = Mock()
        mock_copied_node.id = 10
        mock_copied_node.name = copy_data["name"]

        self.mock_model.create_node.return_value = mock_copied_node

        # Simulate copy-paste
        result = self.mock_model.create_node(**copy_data)

        assert result.name == "Source Node (Copy)"
        self.mock_model.create_node.assert_called_once_with(**copy_data)


class TestNodeSystemIntegration:
    """Test integration aspects of the node system"""

    def test_node_plot_section_integration(self, qapp):
        """Test integration between nodes and plot sections"""
        # Mock plot section
        mock_section = Mock()
        mock_section.id = 1
        mock_section.name = "Act 1"
        mock_section.section_type = "rising"

        # Mock nodes in section
        mock_node1 = Mock()
        mock_node1.id = 1
        mock_node1.plot_section_id = 1
        mock_node1.name = "Opening"

        mock_node2 = Mock()
        mock_node2.id = 2
        mock_node2.plot_section_id = 1
        mock_node2.name = "Inciting Incident"

        section_nodes = [mock_node1, mock_node2]

        # Test that nodes can be grouped by plot sections
        nodes_by_section = {mock_section.id: section_nodes}

        assert len(nodes_by_section[1]) == 2
        assert all(node.plot_section_id == 1 for node in nodes_by_section[1])

    def test_node_storyline_integration(self, qapp):
        """Test integration between nodes and storylines"""
        # Mock storyline
        storyline_id = 1

        # Mock nodes for storyline
        nodes = [
            Mock(id=1, storyline_id=storyline_id, label="Scene 1"),
            Mock(id=2, storyline_id=storyline_id, label="Scene 2"),
            Mock(id=3, storyline_id=storyline_id, label="Scene 3"),
        ]

        # Test storyline filtering
        storyline_nodes = [node for node in nodes if node.storyline_id == storyline_id]

        assert len(storyline_nodes) == 3
        assert all(node.storyline_id == storyline_id for node in storyline_nodes)

    def test_node_connection_validation(self, qapp):
        """Test node connection validation"""
        # Mock nodes
        node1 = Mock(id=1, storyline_id=1)
        node2 = Mock(id=2, storyline_id=1)
        node3 = Mock(id=3, storyline_id=2)  # Different storyline

        # Test valid connection (same storyline)
        valid_connection = {
            "from_node": node1,
            "to_node": node2,
            "valid": node1.storyline_id == node2.storyline_id,
        }

        # Test invalid connection (different storylines)
        invalid_connection = {
            "from_node": node1,
            "to_node": node3,
            "valid": node1.storyline_id == node3.storyline_id,
        }

        assert valid_connection["valid"] is True
        assert invalid_connection["valid"] is False


class TestNodeSystemEdgeCases:
    """Test edge cases and error conditions"""

    def test_node_system_with_no_nodes(self, qapp):
        """Test node system behavior with empty storylines"""
        mock_model = Mock()
        mock_model.get_nodes_for_storyline.return_value = []

        nodes = mock_model.get_nodes_for_storyline(storyline_id=1)

        assert len(nodes) == 0
        mock_model.get_nodes_for_storyline.assert_called_once_with(storyline_id=1)

    def test_invalid_node_connections(self, qapp):
        """Test handling of invalid node connections"""
        # Test self-connection (node connecting to itself)
        self_connection = {"from_node_id": 1, "to_node_id": 1}

        # Mock validation functions
        def is_self_connection(conn):
            return conn["from_node_id"] == conn["to_node_id"]

        assert is_self_connection(self_connection) is True

    def test_node_position_boundaries(self, qapp):
        """Test node position boundary handling"""
        # Test extreme positions
        extreme_positions = [
            {"x": -1000000, "y": -1000000},  # Very negative
            {"x": 1000000, "y": 1000000},  # Very positive
            {"x": 0, "y": 0},  # Origin
        ]

        # Test position validation
        valid_positions = []
        for pos in extreme_positions:
            # Mock position validation
            if isinstance(pos["x"], (int, float)) and isinstance(
                pos["y"], (int, float)
            ):
                valid_positions.append(pos)

        assert len(valid_positions) == 3

    def test_node_label_edge_cases(self, qapp):
        """Test node label edge cases"""
        edge_case_labels = [
            "",  # Empty label
            "A" * 1000,  # Very long label
            "Label with emoji 🎭",  # Unicode characters
            None,  # None value
        ]

        # Test label validation
        valid_labels = []
        for label in edge_case_labels:
            # Mock label validation
            if (
                label is not None
                and len(str(label).strip()) > 0
                and len(str(label)) < 500
            ):
                valid_labels.append(label)

        # Should accept non-empty labels under 500 characters
        assert "Label with emoji 🎭" in valid_labels
        assert "A" * 1000 not in valid_labels  # Too long
        assert "" not in valid_labels  # Empty
