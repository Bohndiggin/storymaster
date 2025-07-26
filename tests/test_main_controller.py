"""
Test suite for main controller integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMessageBox
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QAction

from storymaster.controller.common.main_page_controller import MainWindowController
from storymaster.model.database.schema.base import (
    User, Storyline, Setting, LitographyNode, LitographyPlot, 
    NodeType, Actor, LitographyArc
)


@pytest.fixture
def qapp():
    """Create QApplication for GUI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestMainControllerInitialization:
    """Test main controller initialization"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()

    def test_controller_initialization(self, qapp):
        """Test that controller initializes properly"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel') as mock_base_model:
            mock_base_model.return_value = self.mock_model
            
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                assert controller.model == self.mock_model
                assert controller.view == self.mock_view

    def test_controller_startup_user_check(self, qapp):
        """Test controller startup user validation"""
        with patch('storymaster.controller.common.main_page_controller.get_startup_user_id') as mock_get_user:
            with patch('storymaster.controller.common.main_page_controller.BaseModel') as mock_base_model:
                mock_get_user.return_value = 42
                mock_base_model.return_value = self.mock_model
                
                with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                    mock_view_class.return_value = self.mock_view
                    
                    controller = MainWindowController()
                    
                    mock_get_user.assert_called_once()
                    mock_base_model.assert_called_with(42)

    def test_controller_scene_setup(self, qapp):
        """Test that graphics scenes are set up properly"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                # Mock graphics view
                mock_graphics_view = Mock()
                self.mock_view.ui.graphicsView = mock_graphics_view
                
                controller = MainWindowController()
                
                # Should set up scene
                assert hasattr(controller, 'node_scene')

    def test_controller_signal_connections(self, qapp):
        """Test that UI signals are connected"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                # Mock UI elements
                mock_action_new_node = Mock(spec=QAction)
                mock_action_delete_node = Mock(spec=QAction)
                mock_storyline_combo = Mock()
                
                self.mock_view.ui.actionNewNode = mock_action_new_node
                self.mock_view.ui.actionDeleteNode = mock_action_delete_node
                self.mock_view.ui.storylineComboBox = mock_storyline_combo
                
                controller = MainWindowController()
                
                # Should connect signals
                mock_action_new_node.triggered.connect.assert_called()
                mock_action_delete_node.triggered.connect.assert_called()


class TestMainControllerNodeOperations:
    """Test node operations through the main controller"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # Mock UI elements
        self.mock_view.ui.graphicsView = Mock()
        self.mock_view.ui.storylineComboBox = Mock()
        self.mock_view.ui.actionNewNode = Mock()
        self.mock_view.ui.actionDeleteNode = Mock()
        self.mock_view.ui.statusbar = Mock()

    def test_create_node_operation(self, qapp):
        """Test creating a new node through the controller"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock node creation
                mock_node = Mock(spec=LitographyNode)
                mock_node.id = 10
                mock_node.label = "New Scene"
                mock_node.node_type = NodeType.ACTION
                
                self.mock_model.create_node.return_value = mock_node
                
                with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                    with patch('storymaster.view.common.new_node_dialog.NewNodeDialog') as mock_dialog:
                        mock_dialog_instance = Mock()
                        mock_dialog_instance.exec.return_value = 1  # Accepted
                        mock_dialog_instance.get_node_data.return_value = {
                            'label': 'New Scene',
                            'node_type': NodeType.ACTION,
                            'description': 'Test description'
                        }
                        mock_dialog.return_value = mock_dialog_instance
                        
                        controller.create_new_node()
                        
                        self.mock_model.create_node.assert_called_once()
                        mock_load_draw.assert_called_once()

    def test_delete_node_operation(self, qapp):
        """Test deleting a node through the controller"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.selected_node_id = 5
                
                with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                    with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
                        mock_question.return_value = QMessageBox.StandardButton.Yes
                        
                        controller.delete_selected_node()
                        
                        self.mock_model.delete_node.assert_called_once_with(5)
                        mock_load_draw.assert_called_once()

    def test_update_node_position(self, qapp):
        """Test updating node position through the controller"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Mock node position update
                node_id = 3
                new_x = 150.0
                new_y = 250.0
                
                controller.update_node_position(node_id, new_x, new_y)
                
                self.mock_model.update_node_position.assert_called_once_with(
                    node_id, new_x, new_y
                )

    def test_load_and_draw_nodes(self, qapp):
        """Test loading and drawing nodes on the graphics scene"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock scene
                mock_scene = Mock()
                controller.node_scene = mock_scene
                
                # Mock nodes
                mock_node1 = Mock(spec=LitographyNode)
                mock_node1.id = 1
                mock_node1.label = "Opening"
                mock_node1.node_type = NodeType.EXPOSITION
                mock_node1.x_position = 100.0
                mock_node1.y_position = 200.0
                
                mock_node2 = Mock(spec=LitographyNode)
                mock_node2.id = 2
                mock_node2.label = "Climax"
                mock_node2.node_type = NodeType.ACTION
                mock_node2.x_position = 300.0
                mock_node2.y_position = 200.0
                
                self.mock_model.get_nodes_for_storyline.return_value = [mock_node1, mock_node2]
                
                with patch.object(controller, 'create_node_item') as mock_create_item:
                    controller.load_and_draw_nodes()
                    
                    self.mock_model.get_nodes_for_storyline.assert_called_once_with(1)
                    mock_scene.clear.assert_called_once()
                    assert mock_create_item.call_count == 2

    def test_validate_ui_database_sync(self, qapp):
        """Test UI/database synchronization validation"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock scene items
                mock_scene = Mock()
                mock_item1 = Mock()
                mock_item1.node_id = 1
                mock_item2 = Mock()
                mock_item2.node_id = 2
                mock_scene.items.return_value = [mock_item1, mock_item2]
                controller.node_scene = mock_scene
                
                # Mock database nodes
                mock_db_node1 = Mock()
                mock_db_node1.id = 1
                mock_db_node2 = Mock()
                mock_db_node2.id = 2
                self.mock_model.get_nodes_for_storyline.return_value = [mock_db_node1, mock_db_node2]
                
                # Should return True when synced
                with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                    result = controller.validate_ui_database_sync()
                    
                    # Since IDs match, should not reload
                    assert mock_load_draw.call_count == 0


class TestMainControllerPlotOperations:
    """Test plot operations through the main controller"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # Mock UI elements
        self.mock_view.ui.graphicsView = Mock()
        self.mock_view.ui.storylineComboBox = Mock()
        self.mock_view.ui.actionNewPlot = Mock()
        self.mock_view.ui.actionSwitchPlot = Mock()
        self.mock_view.ui.actionDeletePlot = Mock()
        self.mock_view.ui.statusbar = Mock()

    def test_create_new_plot(self, qapp):
        """Test creating a new plot through the controller"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock plot creation
                mock_plot = Mock(spec=LitographyPlot)
                mock_plot.id = 5
                mock_plot.title = "New Adventure"
                
                self.mock_model.create_plot.return_value = mock_plot
                
                with patch('PyQt6.QtWidgets.QInputDialog.getText') as mock_input:
                    mock_input.return_value = ("New Adventure", True)
                    
                    with patch.object(controller, 'refresh_plots') as mock_refresh:
                        controller.create_new_plot()
                        
                        self.mock_model.create_plot.assert_called_once()
                        mock_refresh.assert_called_once()

    def test_switch_plot(self, qapp):
        """Test switching between plots"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                controller.current_plot_id = 1
                
                # Mock available plots
                mock_plot1 = Mock(spec=LitographyPlot)
                mock_plot1.id = 1
                mock_plot1.title = "Main Plot"
                
                mock_plot2 = Mock(spec=LitographyPlot)
                mock_plot2.id = 2
                mock_plot2.title = "Side Plot"
                
                self.mock_model.get_plots_for_storyline.return_value = [mock_plot1, mock_plot2]
                
                with patch('storymaster.view.common.plot_manager_dialog.PlotManagerDialog') as mock_dialog:
                    mock_dialog_instance = Mock()
                    mock_dialog_instance.exec.return_value = 1  # Accepted
                    mock_dialog_instance.action = "switch"
                    mock_dialog_instance.selected_plot_id = 2
                    mock_dialog.return_value = mock_dialog_instance
                    
                    with patch.object(controller, 'switch_to_plot') as mock_switch:
                        controller.manage_plots()
                        
                        mock_switch.assert_called_once_with(2)

    def test_delete_plot(self, qapp):
        """Test deleting a plot"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                controller.current_plot_id = 1
                
                # Mock available plots
                mock_plot1 = Mock(spec=LitographyPlot)
                mock_plot1.id = 1
                mock_plot1.title = "Main Plot"
                
                mock_plot2 = Mock(spec=LitographyPlot)
                mock_plot2.id = 2
                mock_plot2.title = "Side Plot"
                
                self.mock_model.get_plots_for_storyline.return_value = [mock_plot1, mock_plot2]
                
                with patch('storymaster.view.common.plot_manager_dialog.PlotManagerDialog') as mock_dialog:
                    mock_dialog_instance = Mock()
                    mock_dialog_instance.exec.return_value = 1  # Accepted
                    mock_dialog_instance.action = "delete"
                    mock_dialog_instance.selected_plot_id = 2
                    mock_dialog.return_value = mock_dialog_instance
                    
                    with patch.object(controller, 'refresh_plots') as mock_refresh:
                        controller.manage_plots()
                        
                        self.mock_model.delete_plot.assert_called_once_with(2)
                        mock_refresh.assert_called_once()


class TestMainControllerStorylineOperations:
    """Test storyline operations through the main controller"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # Mock UI elements
        self.mock_view.ui.storylineComboBox = Mock()
        self.mock_view.ui.statusbar = Mock()

    def test_load_storylines(self, qapp):
        """Test loading storylines into combo box"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Mock storylines
                mock_storyline1 = Mock(spec=Storyline)
                mock_storyline1.id = 1
                mock_storyline1.name = "Epic Fantasy"
                
                mock_storyline2 = Mock(spec=Storyline)
                mock_storyline2.id = 2
                mock_storyline2.name = "Space Opera"
                
                self.mock_model.get_all_storylines.return_value = [mock_storyline1, mock_storyline2]
                
                controller.load_storylines()
                
                self.mock_model.get_all_storylines.assert_called_once()
                # Should populate combo box
                assert self.mock_view.ui.storylineComboBox.addItem.call_count == 2

    def test_storyline_changed(self, qapp):
        """Test handling storyline change events"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Mock combo box selection
                self.mock_view.ui.storylineComboBox.currentData.return_value = 2
                
                with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                    with patch.object(controller, 'refresh_plots') as mock_refresh_plots:
                        controller.on_storyline_changed()
                        
                        assert controller.current_storyline_id == 2
                        mock_load_draw.assert_called_once()
                        mock_refresh_plots.assert_called_once()


class TestMainControllerCharacterArcIntegration:
    """Test character arc integration with main controller"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()

    def test_character_arc_widget_integration(self, qapp):
        """Test that character arc widget is properly integrated"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                # Mock character arc widget
                mock_arc_widget = Mock()
                self.mock_view.character_arc_widget = mock_arc_widget
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Should refresh arcs when storyline changes
                with patch.object(controller, 'refresh_character_arcs') as mock_refresh:
                    controller.on_storyline_changed()
                    mock_refresh.assert_called_once()

    def test_refresh_character_arcs(self, qapp):
        """Test refreshing character arcs"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                # Mock character arc widget
                mock_arc_widget = Mock()
                self.mock_view.character_arc_widget = mock_arc_widget
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                controller.refresh_character_arcs()
                
                mock_arc_widget.refresh_arcs.assert_called_once_with(1)


class TestMainControllerErrorHandling:
    """Test error handling in main controller"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # Mock UI elements
        self.mock_view.ui.statusbar = Mock()

    def test_database_error_handling(self, qapp):
        """Test handling of database errors"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock database error
                self.mock_model.get_nodes_for_storyline.side_effect = Exception("Database error")
                
                with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                    controller.load_and_draw_nodes()
                    
                    mock_critical.assert_called_once()

    def test_node_creation_error_handling(self, qapp):
        """Test handling of node creation errors"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock node creation error
                self.mock_model.create_node.side_effect = Exception("Creation failed")
                
                with patch('storymaster.view.common.new_node_dialog.NewNodeDialog') as mock_dialog:
                    mock_dialog_instance = Mock()
                    mock_dialog_instance.exec.return_value = 1  # Accepted
                    mock_dialog_instance.get_node_data.return_value = {
                        'label': 'New Scene',
                        'node_type': NodeType.ACTION
                    }
                    mock_dialog.return_value = mock_dialog_instance
                    
                    with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                        controller.create_new_node()
                        
                        mock_critical.assert_called_once()

    def test_invalid_storyline_handling(self, qapp):
        """Test handling of invalid storyline selection"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Mock invalid storyline ID
                self.mock_view.ui.storylineComboBox.currentData.return_value = None
                
                with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                    controller.on_storyline_changed()
                    
                    # Should handle None storyline gracefully
                    assert controller.current_storyline_id is None


class TestMainControllerEdgeCases:
    """Test edge cases and complex scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_model = Mock()
        self.mock_view = Mock()

    def test_empty_storyline_handling(self, qapp):
        """Test handling of empty storylines"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock empty storyline
                self.mock_model.get_nodes_for_storyline.return_value = []
                self.mock_model.get_plots_for_storyline.return_value = []
                
                # Should handle empty data gracefully
                controller.load_and_draw_nodes()
                controller.refresh_plots()
                
                # Should not crash
                assert controller.current_storyline_id == 1

    def test_concurrent_modification_handling(self, qapp):
        """Test handling of concurrent modifications"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock scene with outdated data
                mock_scene = Mock()
                mock_item = Mock()
                mock_item.node_id = 999  # Non-existent node
                mock_scene.items.return_value = [mock_item]
                controller.node_scene = mock_scene
                
                # Mock current database state
                self.mock_model.get_nodes_for_storyline.return_value = []  # No nodes
                
                with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                    # Should detect sync issue and reload
                    controller.validate_ui_database_sync()
                    mock_load_draw.assert_called_once()

    def test_memory_management_large_scenes(self, qapp):
        """Test memory management with large scenes"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                controller.current_storyline_id = 1
                
                # Mock large number of nodes
                large_node_count = 1000
                mock_nodes = []
                
                for i in range(large_node_count):
                    mock_node = Mock(spec=LitographyNode)
                    mock_node.id = i + 1
                    mock_node.label = f"Node {i + 1}"
                    mock_node.node_type = NodeType.OTHER
                    mock_node.x_position = (i % 50) * 100
                    mock_node.y_position = (i // 50) * 100
                    mock_nodes.append(mock_node)
                
                self.mock_model.get_nodes_for_storyline.return_value = mock_nodes
                
                # Mock scene
                mock_scene = Mock()
                controller.node_scene = mock_scene
                
                with patch.object(controller, 'create_node_item') as mock_create_item:
                    controller.load_and_draw_nodes()
                    
                    # Should handle large number of nodes
                    assert mock_create_item.call_count == large_node_count
                    mock_scene.clear.assert_called_once()

    def test_rapid_storyline_switching(self, qapp):
        """Test rapid storyline switching"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Mock rapid switching
                storyline_ids = [1, 2, 3, 1, 2]
                
                for storyline_id in storyline_ids:
                    self.mock_view.ui.storylineComboBox.currentData.return_value = storyline_id
                    
                    with patch.object(controller, 'load_and_draw_nodes') as mock_load_draw:
                        controller.on_storyline_changed()
                        
                        assert controller.current_storyline_id == storyline_id
                        mock_load_draw.assert_called_once()

    def test_ui_state_persistence(self, qapp):
        """Test UI state persistence across operations"""
        with patch('storymaster.controller.common.main_page_controller.BaseModel'):
            with patch('storymaster.view.common.storymaster_main.StorymasterMain') as mock_view_class:
                mock_view_class.return_value = self.mock_view
                
                controller = MainWindowController()
                
                # Set initial state
                controller.current_storyline_id = 1
                controller.current_plot_id = 2
                controller.selected_node_id = 5
                
                # Perform operations that shouldn't affect unrelated state
                with patch.object(controller, 'load_and_draw_nodes'):
                    controller.refresh_plots()
                    
                    # State should be preserved
                    assert controller.current_storyline_id == 1
                    assert controller.current_plot_id == 2
                    assert controller.selected_node_id == 5