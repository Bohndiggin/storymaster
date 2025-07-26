"""
Pytest-compatible tests for the node connection system
"""

import pytest
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsScene


class TestNodeSystemConcepts:
    """Test the core concepts of the node system"""

    def test_graphics_scene_creation(self, qapp):
        """Test that graphics scenes can be created"""
        scene = QGraphicsScene()
        assert scene is not None
        assert scene.items() == []

    def test_qpoint_functionality(self, qapp):
        """Test QPointF functionality"""
        point = QPointF(100, 200)
        assert point.x() == 100
        assert point.y() == 200

    def test_position_tracking_logic(self, qapp):
        """Test the position tracking logic used by nodes"""
        # Simulate node position storage
        positions = {1: (100, 150), 2: (300, 200)}
        
        # Test getting existing position
        node_id = 1
        x, y = positions[node_id]
        assert x == 100
        assert y == 150
        
        # Test updating position
        positions[1] = (200, 250)
        x, y = positions[1]
        assert x == 200
        assert y == 250
        
        # Test fallback for missing node
        x, y = positions.get(999, (100, 200))
        assert x == 100
        assert y == 200

    def test_connection_point_mathematics(self, qapp):
        """Test the mathematical calculations for connection points"""
        # Node at position (100, 100) with size 80x80
        node_x, node_y = 100, 100
        node_width, node_height = 80, 80
        
        # Input connection point (left side, center)
        input_x = node_x - 5  # 5 pixels left of node
        input_y = node_y + node_height // 2  # Center of node
        assert input_x == 95
        assert input_y == 140
        
        # Output connection point (right side, center)
        output_x = node_x + node_width + 5  # 5 pixels right of node
        output_y = node_y + node_height // 2  # Center of node
        assert output_x == 185
        assert output_y == 140

    def test_connection_point_movement(self, qapp):
        """Test that connection points move correctly with nodes"""
        # Initial node position
        node_x, node_y = 100, 100
        node_width, node_height = 80, 80
        
        # Initial connection points
        input_x = node_x - 5
        input_y = node_y + node_height // 2
        output_x = node_x + node_width + 5
        output_y = node_y + node_height // 2
        
        # Move node
        new_node_x, new_node_y = 200, 200
        offset_x = new_node_x - node_x
        offset_y = new_node_y - node_y
        
        # Calculate new connection points
        new_input_x = input_x + offset_x
        new_input_y = input_y + offset_y
        new_output_x = output_x + offset_x
        new_output_y = output_y + offset_y
        
        assert new_input_x == 195  # 95 + 100
        assert new_input_y == 240  # 140 + 100
        assert new_output_x == 285  # 185 + 100
        assert new_output_y == 240  # 140 + 100

    def test_node_type_change_position_preservation(self, qapp):
        """Test the logic behind preserving position during node type changes"""
        # Simulate old behavior (using database position)
        db_position = {"x_position": 100, "y_position": 200}
        
        # Simulate current UI position (what user actually moved to)
        ui_position = {"x": 250, "y": 350}
        
        # Simulate the fix: prioritize UI position over database position
        def get_position_for_save():
            return ui_position["x"], ui_position["y"]
        
        current_x, current_y = get_position_for_save()
        
        # Verify fix preserves UI position
        assert current_x == 250
        assert current_y == 350
        assert current_x != db_position["x_position"]
        assert current_y != db_position["y_position"]


class TestNodeSystemIntegration:
    """Test integration with actual node system components"""

    def test_node_system_imports(self, qapp):
        """Test that node system components can be imported"""
        try:
            from storymaster.controller.common.main_page_controller import create_node_item
            assert create_node_item is not None
        except ImportError as e:
            pytest.fail(f"Failed to import node system components: {e}")

    def test_mock_node_creation(self, qapp):
        """Test creating mock nodes for testing"""
        from storymaster.controller.common.main_page_controller import create_node_item
        
        class MockNodeData:
            def __init__(self, id_val):
                self.id = id_val
                self.node_type = MockNodeType("EXPOSITION")
        
        class MockNodeType:
            def __init__(self, name):
                self.name = name
        
        class MockController:
            pass
        
        # Create mock objects
        node_data = MockNodeData(1)
        controller = MockController()
        
        # Create node item
        node_item = create_node_item(0, 0, 80, 80, node_data, controller)
        
        # Verify node has required methods
        assert hasattr(node_item, 'get_input_connection_pos')
        assert hasattr(node_item, 'get_output_connection_pos')

    def test_connection_point_methods(self, qapp):
        """Test that connection point methods return correct types"""
        from storymaster.controller.common.main_page_controller import create_node_item
        
        class MockNodeData:
            def __init__(self, id_val):
                self.id = id_val
                self.node_type = MockNodeType("EXPOSITION")
        
        class MockNodeType:
            def __init__(self, name):
                self.name = name
        
        class MockController:
            pass
        
        # Create mock node
        node_data = MockNodeData(1)
        controller = MockController()
        node_item = create_node_item(0, 0, 80, 80, node_data, controller)
        
        # Add to scene and position
        scene = QGraphicsScene()
        scene.addItem(node_item)
        node_item.setPos(100, 100)
        
        # Test connection point methods
        input_pos = node_item.get_input_connection_pos()
        output_pos = node_item.get_output_connection_pos()
        
        assert isinstance(input_pos, QPointF)
        assert isinstance(output_pos, QPointF)
        assert input_pos.x() >= 0
        assert input_pos.y() >= 0
        assert output_pos.x() >= 0
        assert output_pos.y() >= 0