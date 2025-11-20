"""
Storymaster - Main Page Controller

Copyright (c) 2025 Storymaster Development Team
All rights reserved.
"""

import json

# Import export functionality
import os

from PySide6.QtCore import QPointF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainterPath,
    QPen,
    QPolygonF,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import Session

from storymaster.model.common.backup_manager import BackupManager
from storymaster.model.common.common_model import BaseModel
from storymaster.model.database.export_to_json import export_setting_to_json
from storymaster.model.database.schema.base import (
    Actor,
    Background,
    Class_,
    Faction,
    History,
    LitographyNode,
    LitographyNodeToPlotSection,
    LitographyNotes,
    LitographyNoteToActor,
    LitographyNoteToBackground,
    LitographyNoteToClass,
    LitographyNoteToFaction,
    LitographyNoteToHistory,
    LitographyNoteToLocation,
    LitographyNoteToObject,
    LitographyNoteToRace,
    LitographyNoteToSkills,
    LitographyNoteToSubRace,
    LitographyNoteToWorldData,
    LitographyPlot,
    LitographyPlotSection,
    Location,
    NodeConnection,
    NodeType,
    Object_,
    PlotSectionType,
    Race,
    Skills,
    Storyline,
    StorylineToSetting,
    SubRace,
    WorldData,
)
from storymaster.view.character_arcs.new_character_arcs_page import NewCharacterArcsPage
from storymaster.view.common.common_view import MainView
from storymaster.view.common.database_manager_dialog import DatabaseManagerDialog
from storymaster.view.common.import_lore_packages_dialog import ImportLorePackagesDialog
from storymaster.view.common.new_setting_dialog import NewSettingDialog
from storymaster.view.common.new_storyline_dialog import NewStorylineDialog
from storymaster.view.common.new_user_dialog import NewUserDialog
from storymaster.view.common.open_storyline_dialog import OpenStorylineDialog
from storymaster.view.common.plot_manager_dialog import PlotManagerDialog
from storymaster.view.common.setting_switcher_dialog import SettingSwitcherDialog
from storymaster.view.common.storyline_switcher_dialog import StorylineSwitcherDialog
from storymaster.view.common.theme import (
    COLORS,
    FONTS,
    get_button_style,
    get_group_box_style,
    get_input_style,
    get_label_style,
)
from storymaster.view.common.tooltips import apply_general_tooltips
from storymaster.view.common.user_manager_dialog import UserManagerDialog
from storymaster.view.common.user_switcher_dialog import UserSwitcherDialog

# Import the dialogs
from storymaster.view.litographer.add_node_dialog import AddNodeDialog
from storymaster.view.litographer.node_notes_dialog import NodeNotesDialog
from storymaster.view.lorekeeper.new_lorekeeper_page import NewLorekeeperPage
from storymaster.view.storyweaver.storyweaver_widget import StoryweaverWidget


class ConnectionPoint(QGraphicsEllipseItem):
    """Visual connection point on nodes for creating connections"""

    def __init__(self, x, y, is_input, node_item, parent=None):
        # Create the ellipse at origin, we'll position it after
        super().__init__(-5, -5, 10, 10, parent)
        self.is_input = is_input
        self.node_item = node_item
        self.relative_x = x
        self.relative_y = y

        # Position the connection point at the correct relative location
        self.setPos(x, y)

        self.setBrush(QBrush(QColor("#4CAF50" if is_input else "#FF5722")))
        self.setPen(QPen(QColor("#FFFFFF"), 1))
        self.setZValue(10)  # Ensure connection points are on top
        self.setAcceptHoverEvents(True)

        # Connection dragging state
        self.dragging_connection = False
        self.temp_line = None

    def get_absolute_center(self):
        """Get the absolute center position of this connection point"""
        # Since connection point is a child of the node, use its scene position
        scene_pos = self.scenePos()
        return QPointF(scene_pos.x() + 5, scene_pos.y() + 5)  # Center of the 10x10 circle

    def mousePressEvent(self, event):
        """Start connection dragging from output points"""
        if event.button() == Qt.MouseButton.LeftButton and not self.is_input:
            # Only allow dragging from output points (red ones)
            self.dragging_connection = True
            start_pos = self.get_absolute_center()

            # Create temporary line for visual feedback
            self.temp_line = QGraphicsLineItem(
                start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y()
            )
            self.temp_line.setPen(QPen(QColor("#FFFF00"), 3))  # Yellow connection line
            self.temp_line.setZValue(5)
            self.scene().addItem(self.temp_line)

            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Update temporary connection line while dragging"""
        if self.dragging_connection and self.temp_line:
            start_pos = self.get_absolute_center()
            end_pos = event.scenePos()

            self.temp_line.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Complete connection when released over a valid input point"""
        if self.dragging_connection and event.button() == Qt.MouseButton.LeftButton:
            # Clean up temporary line
            if self.temp_line:
                self.scene().removeItem(self.temp_line)
                self.temp_line = None

            # Find item under mouse
            items_under_mouse = self.scene().items(event.scenePos())
            target_connection_point = None

            for item in items_under_mouse:
                if (
                    isinstance(item, ConnectionPoint)
                    and item != self
                    and item.is_input
                    and item.node_item != self.node_item
                ):  # Can't connect to same node
                    target_connection_point = item
                    break

            if target_connection_point:
                # Create connection in database
                self.create_connection(target_connection_point)

            self.dragging_connection = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def create_connection(self, target_point):
        """Create a connection between this output point and target input point"""
        try:
            # Get controller from node
            if hasattr(self.node_item, "controller") and hasattr(
                target_point.node_item, "controller"
            ):
                controller = self.node_item.controller

                from sqlalchemy.orm import Session

                with Session(controller.model.engine) as session:
                    # Check if connection already exists
                    existing = (
                        session.query(NodeConnection)
                        .filter_by(
                            output_node_id=self.node_item.node_data.id,
                            input_node_id=target_point.node_item.node_data.id,
                        )
                        .first()
                    )

                    if not existing:
                        new_connection = NodeConnection(
                            output_node_id=self.node_item.node_data.id,
                            input_node_id=target_point.node_item.node_data.id,
                        )
                        session.add(new_connection)
                        session.commit()

                        # Refresh the display
                        controller.load_and_draw_nodes()
                    else:
                        pass  # Connection already exists

        except Exception as e:
            print(f"❌ Error creating connection: {e}")

    def hoverEnterEvent(self, event):
        """Highlight connection point on hover"""
        self.setPen(QPen(QColor("#FFFFFF"), 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Remove highlight when not hovering"""
        self.setPen(QPen(QColor("#FFFFFF"), 1))
        super().hoverLeaveEvent(event)


class NodeMixin:
    """Mixin class that adds connection functionality to node items"""

    def init_node_data(self, x, y, width, height, node_data, controller):
        """Initialize node data and connection points"""
        self.node_data = node_data
        self.controller = controller
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Store all connection lines for updates
        self.connection_lines = []

        # Add connection points
        self.add_connection_points()

        # Setup drag handlers (pass 'self' which is the graphics item)
        self.setup_drag_handlers(self)

    def add_connection_points(self):
        """Add input and output connection points to the node"""
        # Special positioning for triangle nodes (lower connection points)
        if hasattr(self, "__class__") and "Triangle" in self.__class__.__name__:
            input_y = int(self.height * 0.75)  # Lower position for triangles
            output_y = int(self.height * 0.75)
        else:
            input_y = self.height // 2  # Center vertically for other shapes
            output_y = self.height // 2

        # Input connection point (left side, green) - relative to node
        input_x = -5  # Left edge
        self.input_point = ConnectionPoint(input_x, input_y, True, self, self)

        # Output connection point (right side, red) - relative to node
        output_x = self.width + 5  # Right edge
        self.output_point = ConnectionPoint(output_x, output_y, False, self, self)

    def get_input_connection_pos(self):
        """Get absolute position of input connection point"""
        if hasattr(self, "input_point"):
            return self.input_point.get_absolute_center()
        # Fallback for compatibility
        node_pos = self.pos()
        return QPointF(node_pos.x() - 5, node_pos.y() + self.height // 2)

    def get_output_connection_pos(self):
        """Get absolute position of output connection point"""
        if hasattr(self, "output_point"):
            return self.output_point.get_absolute_center()
        # Fallback for compatibility
        node_pos = self.pos()
        return QPointF(node_pos.x() + self.width + 5, node_pos.y() + self.height // 2)

    def setup_drag_handlers(self, graphics_item):
        """Setup drag event handlers for the graphics item"""
        # Store original events
        original_mouse_release = graphics_item.mouseReleaseEvent
        original_mouse_move = graphics_item.mouseMoveEvent

        def mouse_move_handler(event):
            """Handle mouse move to update connections while dragging"""
            # Call original move event first
            original_mouse_move(event)

            # Update all connection lines during drag
            if hasattr(self, "controller"):
                self.controller.update_all_connections()

        def mouse_release_handler(event):
            """Handle mouse release to save new position after dragging"""
            if hasattr(self, "node_data") and hasattr(self, "controller"):
                # Get the new position
                new_pos = graphics_item.pos()

                # Update the database with the new position
                try:
                    update_data = {
                        "id": self.node_data.id,
                        "x_position": float(new_pos.x()),
                        "y_position": float(new_pos.y()),
                        "storyline_id": self.controller.current_storyline_id,
                    }
                    self.controller.model.update_row("litography_node", update_data)

                    # Update all connections after move
                    self.controller.update_all_connections()

                except Exception as e:
                    print(f"Error saving node position: {e}")

            # Call the original mouse release event
            original_mouse_release(event)

        # Assign the new handlers
        graphics_item.mouseMoveEvent = mouse_move_handler
        graphics_item.mouseReleaseEvent = mouse_release_handler


class BaseNodeItem:
    """Base class for all node shapes"""

    def __init__(self, x, y, width, height, node_data, controller):
        self.node_data = node_data
        self.controller = controller
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def setup_flags(self, item):
        """Setup common flags for all node items"""
        item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)

    def setup_mouse_events(self, item):
        """Setup mouse event handling"""
        original_mouse_press = item.mousePressEvent

        def mouse_press_event(event):
            original_mouse_press(event)
            self.controller.on_node_clicked(self.node_data)

        item.mousePressEvent = mouse_press_event


class RectangleNodeItem(QGraphicsRectItem, NodeMixin):
    """Rectangle node for EXPOSITION"""

    def __init__(self, x, y, width, height, node_data, controller):
        super().__init__(x, y, width, height)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class CircleNodeItem(QGraphicsEllipseItem, NodeMixin):
    """Circle node for REACTION"""

    def __init__(self, x, y, width, height, node_data, controller):
        super().__init__(x, y, width, height)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class DiamondNodeItem(QGraphicsPolygonItem, NodeMixin):
    """Diamond node for ACTION"""

    def __init__(self, x, y, width, height, node_data, controller):
        # Create diamond shape points
        center_x = x + width / 2
        center_y = y + height / 2
        diamond = QPolygonF(
            [
                QPointF(center_x, y),  # Top
                QPointF(x + width, center_y),  # Right
                QPointF(center_x, y + height),  # Bottom
                QPointF(x, center_y),  # Left
            ]
        )
        super().__init__(diamond)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsMovable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class StarNodeItem(QGraphicsPolygonItem, NodeMixin):
    """Star node for TWIST"""

    def __init__(self, x, y, width, height, node_data, controller):
        # Create 5-pointed star
        import math

        center_x = x + width / 2
        center_y = y + height / 2
        outer_radius = min(width, height) / 2 * 0.9
        inner_radius = outer_radius * 0.4

        points = []
        for i in range(10):  # 5 outer points + 5 inner points
            angle = (i * math.pi / 5) - (math.pi / 2)  # Start from top
            if i % 2 == 0:  # Outer points
                radius = outer_radius
            else:  # Inner points
                radius = inner_radius

            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append(QPointF(px, py))

        star = QPolygonF(points)
        super().__init__(star)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsMovable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class HexagonNodeItem(QGraphicsPolygonItem, NodeMixin):
    """Hexagon node for DEVELOPMENT"""

    def __init__(self, x, y, width, height, node_data, controller):
        # Create hexagon shape
        import math

        center_x = x + width / 2
        center_y = y + height / 2
        radius = min(width, height) / 2 * 0.9

        points = []
        for i in range(6):
            angle = i * math.pi / 3  # 60 degrees each
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append(QPointF(px, py))

        hexagon = QPolygonF(points)
        super().__init__(hexagon)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsMovable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class TriangleNodeItem(QGraphicsPolygonItem, NodeMixin):
    """Triangle node for OTHER"""

    def __init__(self, x, y, width, height, node_data, controller):
        # Create triangle shape
        triangle = QPolygonF(
            [
                QPointF(x + width / 2, y),  # Top
                QPointF(x + width, y + height),  # Bottom right
                QPointF(x, y + height),  # Bottom left
            ]
        )
        super().__init__(triangle)
        self.init_node_data(x, y, width, height, node_data, controller)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsMovable, True)

    def get_input_connection_pos(self):
        """Get absolute position of input connection point for triangle"""
        node_pos = self.pos()
        # Left side of triangle (approximate)
        return QPointF(node_pos.x() - 5, node_pos.y() + self.height * 0.75)  # Lower left

    def get_output_connection_pos(self):
        """Get absolute position of output connection point for triangle"""
        node_pos = self.pos()
        # Right side of triangle (approximate)
        return QPointF(
            node_pos.x() + self.width + 5, node_pos.y() + self.height * 0.75
        )  # Lower right

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


def create_node_item(x, y, width, height, node_data, controller):
    """Factory function to create the appropriate node shape based on node type"""
    node_type = node_data.node_type.name

    node_shapes = {
        "EXPOSITION": RectangleNodeItem,
        "ACTION": DiamondNodeItem,
        "REACTION": CircleNodeItem,
        "TWIST": StarNodeItem,
        "DEVELOPMENT": HexagonNodeItem,
        "OTHER": TriangleNodeItem,
    }

    node_class = node_shapes.get(node_type, RectangleNodeItem)
    return node_class(x, y, width, height, node_data, controller)


class SectionEditDialog(QDialog):
    """Dialog for editing plot section properties"""

    def __init__(self, parent, section_id, model, plot_id):
        super().__init__(parent)
        self.section_id = section_id
        self.model = model
        self.plot_id = plot_id

        self.setWindowTitle("Edit Section Type")
        self.setFixedSize(300, 150)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2e2e2e;
                color: #dcdcdc;
            }
            QLabel {
                color: #dcdcdc;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: #dcdcdc;
                border: 1px solid #424242;
                padding: 4px;
            }
            QPushButton {
                background-color: #5c4a8e;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6b5bb3;
            }
        """
        )

        layout = QVBoxLayout(self)

        # Section type selection
        type_label = QLabel(f"Section {section_id} Type:")
        layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.populate_types()
        layout.addWidget(self.type_combo)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def populate_types(self):
        """Populate the section type combo box"""
        try:

            # Add all section types
            for section_type in PlotSectionType:
                self.type_combo.addItem(f"{section_type.value}", section_type)

            # Get current section type and set it
            with Session(self.model.engine) as session:
                section = session.query(LitographyPlotSection).filter_by(id=self.section_id).first()
                if section:
                    for i in range(self.type_combo.count()):
                        if hasattr(self.type_combo, "itemData"):
                            if self.type_combo.itemData(i) == section.plot_section_type:
                                self.type_combo.setCurrentIndex(i)
                                break
                        else:
                            # Fallback for PyQt6 compatibility
                            combo_type = list(PlotSectionType)[i]
                            if combo_type == section.plot_section_type:
                                self.type_combo.setCurrentIndex(i)
                                break

        except Exception as e:
            print(f"Error populating section types: {e}")

    def save_changes(self):
        """Save the section type changes"""
        try:

            # Get selected type
            if hasattr(self.type_combo, "itemData"):
                new_type = self.type_combo.itemData(self.type_combo.currentIndex())
            else:
                # Fallback for PyQt6 compatibility
                type_index = self.type_combo.currentIndex()
                new_type = list(PlotSectionType)[type_index]

            with Session(self.model.engine) as session:
                section = session.query(LitographyPlotSection).filter_by(id=self.section_id).first()
                if section:
                    section.plot_section_type = new_type
                    session.commit()
                    self.accept()

        except Exception as e:
            print(f"Error saving section changes: {e}")
            self.reject()


class AddNodeButton(QGraphicsPathItem):
    """Clickable '+' symbol for adding nodes"""

    def __init__(self, x, y, controller, position_type, reference_node_id=None):
        super().__init__()
        self.controller = controller
        self.position_type = position_type  # 'before' or 'after'
        self.reference_node_id = reference_node_id

        # Create '+' symbol using QPainterPath
        path = QPainterPath()
        # Horizontal bar
        path.addRect(x + 5, y + 10, 15, 5)
        # Vertical bar
        path.addRect(x + 10, y + 5, 5, 15)

        self.setPath(path)
        self.setBrush(QBrush(QColor("#4CAF50")))  # Green
        self.setPen(QPen(QColor("#2E7D32"), 1))
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.controller.on_add_node_button_clicked(self.position_type, self.reference_node_id)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("#66BB6A")))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("#4CAF50")))
        super().hoverLeaveEvent(event)


class DeleteNodeButton(QGraphicsPathItem):
    """Clickable '×' symbol for deleting nodes"""

    def __init__(self, x, y, controller, node_id):
        super().__init__()
        self.controller = controller
        self.node_id = node_id

        # Create '×' symbol using QPainterPath
        path = QPainterPath()
        # First diagonal line (top-left to bottom-right)
        path.moveTo(x + 3, y + 3)
        path.lineTo(x + 17, y + 17)
        # Second diagonal line (top-right to bottom-left)
        path.moveTo(x + 17, y + 3)
        path.lineTo(x + 3, y + 17)

        self.setPath(path)
        self.setPen(QPen(QColor("#F44336"), 4))  # Red, thick lines
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.controller.on_delete_node_button_clicked(self.node_id)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor("#EF5350"), 4))  # Lighter red on hover
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor("#F44336"), 4))  # Back to normal red
        super().hoverLeaveEvent(event)


class MainWindowController:
    """Controller for the main window"""

    def __init__(self, view: MainView, model: BaseModel):
        self.view = view
        self.model = model
        # Initialize storyline and setting IDs based on user's data
        self.current_storyline_id = self._get_default_storyline_id()
        self.current_setting_id = self._get_default_setting_id()
        self.current_table_name = None
        self.current_row_data = None
        self.current_foreign_keys = {}
        self.current_column_types = {}
        self.edit_form_widgets = {}
        self.add_form_widgets = {}
        self.connection_lines = []  # Store connection lines for updates

        # Table visibility management
        self.visible_tables = None  # None means show all available tables
        self.load_table_visibility_preferences()

        # --- Set up Lorekeeper models (deprecated components removed) ---
        # Database tree and table views removed - using new Lorekeeper interface

        # --- Set up Litographer scene ---
        self.node_scene = QGraphicsScene()
        self.view.ui.nodeGraphView.setScene(self.node_scene)

        # Enable context menu on graphics view
        self.view.ui.nodeGraphView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.ui.nodeGraphView.customContextMenuRequested.connect(
            self.on_litographer_context_menu
        )

        # --- Set up node editing side panel ---
        self.setup_node_editing_panel()
        self.selected_node = None
        self.current_plot_section_id = None
        self.current_plot_id = 1  # Default to first plot
        self.section_tab_ids = []  # Store section IDs corresponding to tab indices

        # --- Set up backup system ---
        import os

        # Use the same database path as base_connection.py
        home_dir = os.path.expanduser("~")
        db_dir = os.path.join(home_dir, ".local", "share", "storymaster")
        database_path = os.path.join(db_dir, "storymaster.db")
        self.backup_manager = BackupManager(database_path)

        # Connect backup signals
        self.backup_manager.backup_created.connect(self.on_backup_created)
        self.backup_manager.backup_failed.connect(self.on_backup_failed)

        # Start automatic backups
        self.backup_manager.start_automatic_backups()

        # Initialize character arc page
        self.character_arc_page = NewCharacterArcsPage(self.model, self.view)

        # Add the character arc page to the character arcs container
        character_arcs_layout = QVBoxLayout(self.view.ui.characterArcsContainer)
        character_arcs_layout.setContentsMargins(0, 0, 0, 0)
        character_arcs_layout.addWidget(self.character_arc_page)

        # Initialize new Lorekeeper page
        self.new_lorekeeper_widget = None  # Will be initialized when needed

        # Initialize Storyweaver page
        self.storyweaver_widget = StoryweaverWidget(
            model=self.model,
            current_storyline_id=self.current_storyline_id or 1,
            current_setting_id=self.current_setting_id or 1,
            parent=self.view
        )

        # Entity cache for Storyweaver (key: setting_id, value: entity list)
        self._entity_cache = {}

        # Entity details cache (key: (entity_type, entity_id), value: (name, details))
        self._entity_details_cache = {}

        # Add the Storyweaver widget to the storyweaver page
        storyweaver_layout = QVBoxLayout(self.view.ui.storyweaverPage)
        storyweaver_layout.setContentsMargins(0, 0, 0, 0)
        storyweaver_layout.addWidget(self.storyweaver_widget)

        # Connect Storyweaver signals
        self.storyweaver_widget.entity_search_requested.connect(self._on_storyweaver_entity_search)
        self.storyweaver_widget.entity_hover_requested.connect(self._on_storyweaver_entity_hover)
        self.storyweaver_widget.entity_navigation_requested.connect(self._on_entity_card_clicked)
        self.storyweaver_widget.editor.alias_add_requested.connect(self._on_alias_add_requested)

        self.connect_signals()
        self.on_litographer_selected()  # Start on the litographer page
        self.update_status_indicators()  # Initialize status indicators

    def _get_default_storyline_id(self) -> int | None:
        """Get the first available storyline ID for the current user, or None if none exist."""
        try:
            storylines = self.model.get_all_storylines()
            return storylines[0].id if storylines else None
        except Exception:
            return None

    def _get_default_setting_id(self) -> int | None:
        """Get the first available setting ID for the current user, or None if none exist."""
        try:
            settings = self.model.get_all_settings()
            return settings[0].id if settings else None
        except Exception:
            return None

    def _get_current_storyline_nodes(self):
        """Safely get litography nodes for the current storyline."""
        if self.current_storyline_id is not None:
            return self.model.get_litography_nodes(storyline_id=self.current_storyline_id)
        return []

    def validate_ui_database_sync(self):
        """Check if UI and database are in sync and force refresh if not"""
        try:
            # Get current database state
            db_nodes = self._get_current_storyline_nodes()
            db_ids = set(n.id for n in db_nodes)

            # Get UI state by examining scene items
            ui_node_ids = set()
            for item in self.node_scene.items():
                if isinstance(item, DeleteNodeButton):
                    ui_node_ids.add(item.node_id)

            # Check for discrepancies
            if ui_node_ids != db_ids:
                self.load_and_draw_nodes()
                return False
            return True
        except Exception as e:
            return False

    def setup_node_editing_panel(self):
        """Create the node editing side panel"""
        # Get the existing layout and use it to add our splitter
        current_layout = self.view.ui.litographerPage.layout()

        # If there's an existing layout, we'll work with it
        if current_layout:
            # Create horizontal splitter
            splitter = QSplitter(Qt.Orientation.Horizontal)

            # Left side: Graph view container
            graph_container = QWidget()
            graph_layout = QVBoxLayout(graph_container)

            # Add plot section selector at the top
            self.setup_plot_section_selector(graph_layout)

            graph_layout.addWidget(self.view.ui.litographerToolbar)
            graph_layout.addWidget(self.view.ui.nodeGraphView)
            graph_layout.setContentsMargins(0, 0, 0, 0)

            # Right side: Node editing panel
            self.node_panel = QWidget()
            self.node_panel.setFixedWidth(300)
            self.node_panel.setStyleSheet(
                f"""
                background-color: {COLORS['bg_main']}; 
                border-left: 1px solid {COLORS['border_main']};
            """
            )

            panel_layout = QVBoxLayout(self.node_panel)

            # Node info section
            node_info_group = QGroupBox("Node Information")
            node_info_layout = QFormLayout(node_info_group)

            self.node_name_edit = QLineEdit()
            self.node_name_edit.setStyleSheet(get_input_style())
            self.node_description_edit = QTextEdit()
            self.node_description_edit.setStyleSheet(get_input_style())
            self.node_description_edit.setMaximumHeight(80)  # Keep it compact
            self.node_type_combo = QComboBox()

            node_info_layout.addRow("Name:", self.node_name_edit)
            node_info_layout.addRow("Description:", self.node_description_edit)
            node_info_layout.addRow("Node Type:", self.node_type_combo)

            # Plot section selector
            section_group = QGroupBox("Plot Section")
            section_layout = QFormLayout(section_group)
            self.section_combo = QComboBox()
            section_layout.addRow("Section:", self.section_combo)

            # Keep the old combos for backward compatibility with existing save logic
            self.previous_node_combo = QComboBox()
            self.next_node_combo = QComboBox()
            self.previous_node_combo.hide()  # Hide them from UI
            self.next_node_combo.hide()

            # Notes section
            notes_group = QGroupBox("Notes")
            notes_layout = QVBoxLayout(notes_group)

            # Notes list
            self.notes_list = QListWidget()
            self.notes_list.setMaximumHeight(120)
            self.notes_list.itemSelectionChanged.connect(self.on_note_selected)
            notes_layout.addWidget(self.notes_list)

            # Notes controls
            notes_controls_layout = QHBoxLayout()
            self.add_note_btn = QPushButton("Add Note")
            self.edit_note_btn = QPushButton("Edit")
            self.delete_note_btn = QPushButton("Delete")
            self.edit_note_btn.setEnabled(False)
            self.delete_note_btn.setEnabled(False)

            self.add_note_btn.clicked.connect(self.on_add_note)
            self.edit_note_btn.clicked.connect(self.on_edit_note)
            self.delete_note_btn.clicked.connect(self.on_delete_note)

            notes_controls_layout.addWidget(self.add_note_btn)
            notes_controls_layout.addWidget(self.edit_note_btn)
            notes_controls_layout.addWidget(self.delete_note_btn)
            notes_layout.addLayout(notes_controls_layout)

            # Buttons (only delete, save is now automatic)
            button_layout = QHBoxLayout()
            self.delete_node_btn = QPushButton("Delete Node")
            self.delete_node_btn.setStyleSheet(get_button_style("danger"))

            button_layout.addWidget(self.delete_node_btn)

            # Add to panel
            panel_layout.addWidget(node_info_group)
            panel_layout.addWidget(section_group)
            panel_layout.addWidget(notes_group)
            panel_layout.addLayout(button_layout)
            panel_layout.addStretch()

            # Add to splitter
            splitter.addWidget(graph_container)
            splitter.addWidget(self.node_panel)
            splitter.setSizes([800, 300])  # Initial sizes

            # Add the splitter to the existing layout
            current_layout.addWidget(splitter)

            # Connect signals for autosave
            self.node_name_edit.editingFinished.connect(self.on_save_node_changes)
            self.node_description_edit.textChanged.connect(self._schedule_autosave)
            self.node_type_combo.currentIndexChanged.connect(self.on_save_node_changes)
            self.section_combo.currentIndexChanged.connect(self.on_save_node_changes)

            # Connect delete button
            self.delete_node_btn.clicked.connect(self.on_delete_node)

            # Initialize autosave timer for description field
            self._autosave_timer = QTimer()
            self._autosave_timer.setSingleShot(True)
            self._autosave_timer.timeout.connect(self.on_save_node_changes)
            self._autosave_timer.setInterval(1000)  # 1 second delay

            # Initially hide the panel
            self.node_panel.hide()

    def setup_plot_section_selector(self, parent_layout):
        """Create the plot section selector UI at the top"""
        # Section selector container
        section_container = QWidget()
        section_container.setFixedHeight(60)
        section_container.setStyleSheet(
            f"""
            background-color: {COLORS['bg_main']}; 
            border-bottom: 1px solid {COLORS['border_main']};
        """
        )

        section_layout = QHBoxLayout(section_container)
        section_layout.setContentsMargins(10, 10, 10, 10)

        # Label
        section_label = QLabel("Plot Sections:")
        section_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold;")
        section_layout.addWidget(section_label)

        # Tab widget for sections
        self.section_tabs = QTabWidget()
        self.section_tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border_main']};
                background-color: {COLORS['bg_secondary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['border_light']};
            }}
        """
        )
        self.section_tabs.currentChanged.connect(self.on_section_changed)

        # Enable context menu on tabs
        self.section_tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.section_tabs.customContextMenuRequested.connect(self.on_section_context_menu)

        section_layout.addWidget(self.section_tabs)

        # Add section button
        add_section_btn = QPushButton("+ Add Section")
        add_section_btn.setStyleSheet(get_button_style("primary"))
        add_section_btn.clicked.connect(self.on_add_section_clicked)
        section_layout.addWidget(add_section_btn)

        parent_layout.addWidget(section_container)

    def on_section_changed(self, index):
        """Handle plot section tab change"""
        if index >= 0 and index < len(self.section_tab_ids):
            self.current_plot_section_id = self.section_tab_ids[index]
            self.load_and_draw_nodes()

    def on_add_section_clicked(self):
        """Handle adding a new plot section"""
        try:
            # Import the PlotSectionType enum

            # Create a new plot section
            new_section_data = {
                "plot_section_type": PlotSectionType.FLAT.value,  # Default to FLAT
                "plot_id": self.current_plot_id,
            }

            # Add to database - first need to check if there's a method for this
            # For now, let's use direct SQLAlchemy

            with Session(self.model.engine) as session:
                new_section = LitographyPlotSection(
                    plot_section_type=PlotSectionType.FLAT, plot_id=self.current_plot_id
                )
                session.add(new_section)
                session.commit()
                session.refresh(new_section)

                self.view.ui.statusbar.showMessage(f"Added new plot section {new_section.id}", 3000)
                self.load_plot_sections()
                # Switch to the new section
                self.current_plot_section_id = new_section.id

        except Exception as e:
            print(f"Error adding plot section: {e}")
            self.view.ui.statusbar.showMessage(f"Error adding section: {e}", 5000)

    def on_section_context_menu(self, position):
        """Handle right-click on section tabs"""
        # Get the tab that was right-clicked
        tab_bar = self.section_tabs.tabBar()
        clicked_index = tab_bar.tabAt(position)

        if clicked_index >= 0:
            menu = QMenu(self.section_tabs)

            edit_action = menu.addAction("Edit Section Type")
            delete_action = menu.addAction("Delete Section")

            action = menu.exec(self.section_tabs.mapToGlobal(position))

            if action == edit_action:
                self.edit_section_type(clicked_index)
            elif action == delete_action:
                self.delete_section(clicked_index)

    def edit_section_type(self, tab_index):
        """Open dialog to edit section type"""
        if tab_index < len(self.section_tab_ids):
            section_id = self.section_tab_ids[tab_index]
            dialog = SectionEditDialog(self.view, section_id, self.model, self.current_plot_id)
            if dialog.exec():
                # Refresh sections after edit
                self.load_plot_sections()

    def delete_section(self, tab_index):
        """Delete a section"""
        if tab_index < len(self.section_tab_ids):
            section_id = self.section_tab_ids[tab_index]

            # Check if section has nodes
            nodes_in_section = self.get_nodes_in_section(section_id)
            if nodes_in_section:
                self.view.ui.statusbar.showMessage(
                    f"Cannot delete section with {len(nodes_in_section)} nodes", 5000
                )
                return

            try:

                with Session(self.model.engine) as session:
                    section = session.query(LitographyPlotSection).filter_by(id=section_id).first()
                    if section:
                        session.delete(section)
                        session.commit()
                        self.view.ui.statusbar.showMessage("Section deleted", 3000)
                        self.load_plot_sections()

            except Exception as e:
                print(f"Error deleting section: {e}")
                self.view.ui.statusbar.showMessage(f"Error deleting section: {e}", 5000)

    def on_node_clicked(self, node_data):
        """Handle node click - show editing panel"""
        self.selected_node = node_data
        self.populate_node_panel(node_data)
        self.node_panel.show()

    def populate_node_panel(self, node_data):
        """Populate the editing panel with node data"""
        # Temporarily disconnect autosave signals to prevent triggering during population
        self._disconnect_autosave_signals()

        try:
            # Populate node type combo
            self.node_type_combo.clear()
            for node_type in NodeType:
                self.node_type_combo.addItem(node_type.value, node_type)

            # Set current values
            self.node_name_edit.setText(node_data.name or "Untitled Node")
            self.node_description_edit.setPlainText(node_data.description or "")
            self.node_type_combo.setCurrentText(node_data.node_type.value)

            # Populate connection combos (hidden, for save logic compatibility)
            self.populate_connection_combos(node_data)

            # Populate section combo
            self.populate_section_combo(node_data)

            # Load notes for this node
            self.load_notes_for_node(node_data.id)
        finally:
            # Reconnect autosave signals
            self._connect_autosave_signals()

    def populate_connection_combos(self, current_node):
        """Update hidden connection combos for backward compatibility with save logic"""
        # Get all nodes for reference
        all_nodes = self.model.get_litography_nodes(storyline_id=self.current_storyline_id)
        nodes_dict = {node.id: node for node in all_nodes}

        # Get current connections from database
        with Session(self.model.engine) as session:
            # Get input connections (where this node is the input)
            input_connections = (
                session.query(NodeConnection).filter_by(input_node_id=current_node.id).all()
            )

            # Get output connections (where this node is the output)
            output_connections = (
                session.query(NodeConnection).filter_by(output_node_id=current_node.id).all()
            )

            # Update hidden combos for backward compatibility with save logic
            self.previous_node_combo.clear()
            self.next_node_combo.clear()
            self.previous_node_combo.addItem("None", None)
            self.next_node_combo.addItem("None", None)

            # Add all other nodes to hidden combos
            for node in all_nodes:
                if node.id != current_node.id:
                    display_text = f"Node {node.id} ({node.node_type.value})"
                    self.previous_node_combo.addItem(display_text, node.id)
                    self.next_node_combo.addItem(display_text, node.id)

            # Set first connection in hidden combos for compatibility
            if input_connections:
                first_input = input_connections[0].output_node_id
                for i in range(self.previous_node_combo.count()):
                    if self.previous_node_combo.itemData(i) == first_input:
                        self.previous_node_combo.setCurrentIndex(i)
                        break

            if output_connections:
                first_output = output_connections[0].input_node_id
                for i in range(self.next_node_combo.count()):
                    if self.next_node_combo.itemData(i) == first_output:
                        self.next_node_combo.setCurrentIndex(i)
                        break

    def populate_section_combo(self, current_node):
        """Populate the plot section combo box"""
        try:

            # Clear combo
            self.section_combo.clear()

            with Session(self.model.engine) as session:
                # Get all sections for current plot
                sections = (
                    session.query(LitographyPlotSection)
                    .filter_by(plot_id=self.current_plot_id)
                    .order_by(LitographyPlotSection.id)
                    .all()
                )

                # Add sections to combo (store section objects for easy access)
                self.section_combo_sections = sections
                for section in sections:
                    display_text = f"Section {section.id} ({section.plot_section_type.value})"
                    self.section_combo.addItem(display_text)

                # Find current section for this node
                current_section = (
                    session.query(LitographyNodeToPlotSection)
                    .filter_by(node_id=current_node.id)
                    .first()
                )

                if current_section:
                    # Set current selection by finding the section in the combo
                    for i, section in enumerate(self.section_combo_sections):
                        if section.id == current_section.litography_plot_section_id:
                            self.section_combo.setCurrentIndex(i)
                            break

        except Exception as e:
            print(f"Error populating section combo: {e}")

    def get_node_ui_position(self, node_id):
        """Get the current UI position of a node from the graphics scene"""
        for item in self.node_scene.items():
            if hasattr(item, "node_data") and item.node_data.id == node_id:
                pos = item.pos()
                return float(pos.x()), float(pos.y())
        # Fallback to database position
        return getattr(self.selected_node, "x_position", 100), getattr(
            self.selected_node, "y_position", 200
        )

    def _disconnect_autosave_signals(self):
        """Temporarily disconnect autosave signals (used during panel population)"""
        try:
            self.node_name_edit.editingFinished.disconnect(self.on_save_node_changes)
            self.node_description_edit.textChanged.disconnect(self._schedule_autosave)
            self.node_type_combo.currentIndexChanged.disconnect(self.on_save_node_changes)
            self.section_combo.currentIndexChanged.disconnect(self.on_save_node_changes)
        except:
            pass  # Ignore if already disconnected

    def _connect_autosave_signals(self):
        """Reconnect autosave signals after panel population"""
        try:
            self.node_name_edit.editingFinished.connect(self.on_save_node_changes)
            self.node_description_edit.textChanged.connect(self._schedule_autosave)
            self.node_type_combo.currentIndexChanged.connect(self.on_save_node_changes)
            self.section_combo.currentIndexChanged.connect(self.on_save_node_changes)
        except:
            pass  # Ignore if already connected

    def _schedule_autosave(self):
        """Schedule an autosave after a short delay (for text fields)"""
        if hasattr(self, "_autosave_timer"):
            self._autosave_timer.stop()
            self._autosave_timer.start()

    def on_save_node_changes(self):
        """Save changes to the selected node (autosave)"""
        if not self.selected_node:
            return

        try:
            # Get values from the form
            new_name = self.node_name_edit.text().strip() or "Untitled Node"
            new_description = self.node_description_edit.toPlainText().strip() or None
            new_type = self.node_type_combo.currentData()

            # Track if node type changed (requires full redraw)
            node_type_changed = new_type and (
                not hasattr(self.selected_node, "node_type")
                or new_type.value != self.selected_node.node_type.value
            )

            # Get section ID from combo index
            section_index = self.section_combo.currentIndex()
            new_section = (
                self.section_combo_sections[section_index].id
                if section_index >= 0
                and hasattr(self, "section_combo_sections")
                and section_index < len(self.section_combo_sections)
                else None
            )

            # Get current UI position to preserve it
            current_x, current_y = self.get_node_ui_position(self.selected_node.id)

            # Update the node with new schema (no previous_node/next_node)
            update_data = {
                "id": self.selected_node.id,
                "name": new_name,
                "description": new_description,
                "x_position": current_x,
                "y_position": current_y,
                "storyline_id": self.current_storyline_id,
            }

            # Only update node_type if we have a valid value (it's required/NOT NULL)
            if new_type:
                update_data["node_type"] = new_type.value

            self.model.update_row("litography_node", update_data)

            # NOTE: We don't modify connections during autosave - connections are
            # managed through the graph UI (drag-and-drop connections between nodes)
            # The old previous_node_combo and next_node_combo are hidden and not used

            # Handle section change if needed
            if new_section:
                self.move_node_to_section(self.selected_node.id, new_section)

            self.view.ui.statusbar.showMessage("Node autosaved", 2000)

            # Only refresh graph if node type changed (affects visual appearance)
            # For name/description changes, just update the text label in place
            if node_type_changed:
                self.load_and_draw_nodes()
            else:
                # Update just the node label without full redraw
                self._update_node_label(self.selected_node.id, new_name)

        except Exception as e:
            print(f"Error autosaving node: {e}")
            self.view.ui.statusbar.showMessage(f"Error autosaving node: {e}", 5000)

    def _update_node_label(self, node_id, new_name):
        """Update a node's label text without redrawing the entire graph"""
        try:
            for item in self.node_scene.items():
                if hasattr(item, "node_id") and item.node_id == node_id:
                    # Find the text child item and update it
                    for child in item.childItems():
                        if isinstance(child, QGraphicsTextItem):
                            child.setPlainText(new_name)
                            break
                    break
        except Exception as e:
            print(f"Error updating node label: {e}")

    def on_delete_node(self):
        """Delete the selected node"""
        if not self.selected_node:
            return

        try:
            # Delete the node and its notes using SQLAlchemy directly since BaseModel doesn't have delete_row

            with Session(self.model.engine) as session:
                node_id = self.selected_node.id

                # First delete all connections involving this node
                session.query(NodeConnection).filter(
                    (NodeConnection.output_node_id == node_id)
                    | (NodeConnection.input_node_id == node_id)
                ).delete()

                # Delete all notes associated with this node
                notes_to_delete = (
                    session.query(LitographyNotes)
                    .filter_by(
                        linked_node_id=node_id,
                        storyline_id=self.current_storyline_id,
                    )
                    .all()
                )

                for note in notes_to_delete:
                    session.delete(note)

                # Then find and delete the node
                node_to_delete = (
                    session.query(LitographyNode)
                    .filter_by(id=node_id, storyline_id=self.current_storyline_id)
                    .first()
                )

                if node_to_delete:
                    session.delete(node_to_delete)
                    session.commit()
                    self.view.ui.statusbar.showMessage(
                        "Node, connections, and associated notes deleted successfully",
                        3000,
                    )
                else:
                    self.view.ui.statusbar.showMessage("Node not found", 3000)

            # Hide the panel and refresh
            self.node_panel.hide()
            self.selected_node = None
            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error deleting node: {e}")
            self.view.ui.statusbar.showMessage(f"Error deleting node: {e}", 5000)

    def on_add_node_button_clicked(self, position_type, reference_node_id):
        """Handle clicking '+' button to add a node (simplified for new Blender-style system)"""
        try:
            # In the new Blender-style system, nodes are added independently
            # and connected via visual connection points later

            # Determine position based on reference node or default
            x_pos = 100.0
            y_pos = 200.0

            if reference_node_id:
                # Find the reference node to position near it
                all_nodes = self.model.get_litography_nodes(storyline_id=self.current_storyline_id)
                reference_node = next((n for n in all_nodes if n.id == reference_node_id), None)

                if reference_node:
                    ref_x = getattr(reference_node, "x_position", 100)
                    ref_y = getattr(reference_node, "y_position", 200)

                    # Position new node relative to reference
                    if position_type == "before":
                        x_pos = ref_x - 150  # To the left
                        y_pos = ref_y
                    elif position_type == "after":
                        x_pos = ref_x + 150  # To the right
                        y_pos = ref_y
                    else:  # "start" or default
                        x_pos = ref_x
                        y_pos = ref_y + 100  # Below

            # Create new node data with new schema
            new_node_data = {
                "node_type": NodeType.OTHER.value,
                "storyline_id": self.current_storyline_id,
                "x_position": x_pos,
                "y_position": y_pos,
            }

            # Add the new node to database
            self.model.add_row("litography_node", new_node_data)

            # Add to current section if we have one
            if self.current_plot_section_id:
                all_nodes_after = self.model.get_litography_nodes(
                    storyline_id=self.current_storyline_id
                )
                new_node = max(all_nodes_after, key=lambda n: n.id)
                self.add_node_to_section(new_node.id, self.current_plot_section_id)

            self.view.ui.statusbar.showMessage(
                "Added new node - use connection points to link nodes", 3000
            )
            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error adding node: {e}")
            self.view.ui.statusbar.showMessage(f"Error adding node: {e}", 5000)

    def on_node_context_menu(self, node_data, position):
        """Handle right-click context menu on nodes"""
        menu = QMenu()

        # Add notes action
        notes_action = menu.addAction("Manage Notes...")
        notes_action.triggered.connect(lambda: self.open_notes_dialog(node_data))

        # Add separator
        menu.addSeparator()

        # Add existing actions
        edit_action = menu.addAction("Edit Node")
        edit_action.triggered.connect(lambda: self.on_node_clicked(node_data))

        delete_action = menu.addAction("Delete Node")
        delete_action.triggered.connect(lambda: self.on_delete_node_button_clicked(node_data.id))

        # Show menu
        menu.exec(position)

    def on_litographer_context_menu(self, position):
        """Handle right-click context menu on litographer graphics view"""
        menu = QMenu()

        # Plot management section
        plot_menu = menu.addMenu("Plot Management")

        new_plot_action = plot_menu.addAction("New Plot")
        new_plot_action.triggered.connect(self.on_new_plot_clicked)

        switch_plot_action = plot_menu.addAction("Switch Plot")
        switch_plot_action.triggered.connect(self.on_switch_plot_clicked)

        delete_plot_action = plot_menu.addAction("Delete Plot")
        delete_plot_action.triggered.connect(self.on_delete_plot_clicked)

        menu.addSeparator()

        # Node creation (only if we're in litographer mode)
        add_node_action = menu.addAction("Add Node")
        add_node_action.triggered.connect(self.on_add_node_clicked)

        # Show menu at the clicked position
        menu.exec(self.view.ui.nodeGraphView.mapToGlobal(position))

    def update_status_indicators(self):
        """Update status bar to show current storyline, setting, and user"""
        try:
            # Get current user name
            current_user = self.model.get_current_user()
            user_name = current_user.username if current_user else "Unknown User"

            # Get current storyline name
            storyline_name = "No Storylines"
            if self.current_storyline_id is not None:
                storylines = self.model.get_all_storylines()
                storyline_name = next(
                    (s.name for s in storylines if s.id == self.current_storyline_id),
                    "Unknown",
                )

            # Get current setting name
            setting_name = "No Settings"
            if self.current_setting_id is not None:
                settings = self.model.get_all_settings()
                setting_name = next(
                    (s.name for s in settings if s.id == self.current_setting_id),
                    "Unknown",
                )

            # Update status bar with user info
            status_text = (
                f"User: {user_name} | Storyline: {storyline_name} | Setting: {setting_name}"
            )
            self.view.ui.statusbar.showMessage(status_text)

        except Exception as e:
            print(f"Error updating status indicators: {e}")

    def open_notes_dialog(self, node_data):
        """Open the notes management dialog for a node"""
        try:
            dialog = NodeNotesDialog(node_data, self, self.view)
            dialog.exec()
        except Exception as e:
            self.view.ui.statusbar.showMessage(f"Error opening notes dialog: {e}", 5000)

    def get_notes_for_node(self, node_id):
        """Get all notes for a specific node"""
        try:
            with Session(self.model.engine) as session:
                notes = (
                    session.query(LitographyNotes)
                    .filter_by(linked_node_id=node_id, storyline_id=self.current_storyline_id)
                    .all()
                )
                return notes
        except Exception as e:
            print(f"Error getting notes for node {node_id}: {e}")
            return []

    def create_note(self, node_id, title, description, note_type):
        """Create a new note linked to a node"""
        try:
            with Session(self.model.engine) as session:
                note = LitographyNotes(
                    title=title,
                    description=description,
                    note_type=note_type,
                    linked_node_id=node_id,
                    storyline_id=self.current_storyline_id,
                )
                session.add(note)
                session.commit()
                self.view.ui.statusbar.showMessage("Note created successfully", 3000)
        except Exception as e:
            print(f"Error creating note: {e}")
            raise e

    def update_note(self, note_id, title, description, note_type):
        """Update an existing note"""
        try:
            with Session(self.model.engine) as session:
                note = (
                    session.query(LitographyNotes)
                    .filter_by(id=note_id, storyline_id=self.current_storyline_id)
                    .first()
                )

                if note:
                    note.title = title
                    note.description = description
                    note.note_type = note_type
                    session.commit()
                    self.view.ui.statusbar.showMessage("Note updated successfully", 3000)
                else:
                    raise Exception("Note not found")
        except Exception as e:
            print(f"Error updating note: {e}")
            raise e

    def delete_note(self, note_id):
        """Delete a note"""
        try:
            with Session(self.model.engine) as session:
                note = (
                    session.query(LitographyNotes)
                    .filter_by(id=note_id, storyline_id=self.current_storyline_id)
                    .first()
                )

                if note:
                    session.delete(note)
                    session.commit()
                    self.view.ui.statusbar.showMessage("Note deleted successfully", 3000)
                else:
                    raise Exception("Note not found")
        except Exception as e:
            print(f"Error deleting note: {e}")
            raise e

    def node_has_notes(self, node_id):
        """Check if a node has any notes attached to it"""
        try:
            with Session(self.model.engine) as session:
                count = (
                    session.query(LitographyNotes)
                    .filter_by(linked_node_id=node_id, storyline_id=self.current_storyline_id)
                    .count()
                )
                return count > 0
        except Exception as e:
            print(f"Error checking notes for node {node_id}: {e}")
            return False

    def load_notes_for_node(self, node_id):
        """Load notes for the current node into the side panel"""
        self.notes_list.clear()
        notes = self.get_notes_for_node(node_id)

        for note in notes:
            item = QListWidgetItem(f"[{note.note_type.name}] {note.title}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

    def on_note_selected(self):
        """Handle note selection in the side panel"""
        current_item = self.notes_list.currentItem()
        if current_item:
            self.edit_note_btn.setEnabled(True)
            self.delete_note_btn.setEnabled(True)
        else:
            self.edit_note_btn.setEnabled(False)
            self.delete_note_btn.setEnabled(False)

    def on_add_note(self):
        """Add a new note from the side panel"""
        if not self.selected_node:
            return

        try:
            dialog = NodeNotesDialog(self.selected_node, self, self.view)
            dialog.exec()
            # Refresh notes list and visual indicators
            self.load_notes_for_node(self.selected_node.id)
            self.load_and_draw_nodes()
        except Exception as e:
            self.view.ui.statusbar.showMessage(f"Error opening notes dialog: {e}", 5000)

    def on_edit_note(self):
        """Edit the selected note"""
        if not self.selected_node:
            return

        current_item = self.notes_list.currentItem()
        if not current_item:
            return

        try:
            dialog = NodeNotesDialog(self.selected_node, self, self.view)
            # Pre-select the note in the dialog
            note = current_item.data(Qt.ItemDataRole.UserRole)
            dialog.current_note = note
            dialog.load_note_to_editor(note)
            dialog.set_editor_enabled(True)
            dialog.exec()
            # Refresh notes list
            self.load_notes_for_node(self.selected_node.id)
            self.load_and_draw_nodes()
        except Exception as e:
            self.view.ui.statusbar.showMessage(f"Error opening notes dialog: {e}", 5000)

    def on_delete_note(self):
        """Delete the selected note from the side panel"""
        if not self.selected_node:
            return

        current_item = self.notes_list.currentItem()
        if not current_item:
            return

        note = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            f"Are you sure you want to delete the note '{note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.delete_note(note.id)
                self.load_notes_for_node(self.selected_node.id)
                self.load_and_draw_nodes()  # Refresh visual indicators
            except Exception as e:
                self.view.ui.statusbar.showMessage(f"Error deleting note: {e}", 5000)

    # Lore entity methods for note associations
    def get_lore_entities_for_setting(self, setting_id):
        """Get all lore entities for a given setting"""
        try:
            with Session(self.model.engine) as session:
                actors = session.query(Actor).filter_by(setting_id=setting_id).all()
                backgrounds = session.query(Background).filter_by(setting_id=setting_id).all()
                classes = session.query(Class_).filter_by(setting_id=setting_id).all()
                factions = session.query(Faction).filter_by(setting_id=setting_id).all()
                histories = session.query(History).filter_by(setting_id=setting_id).all()
                locations = session.query(Location).filter_by(setting_id=setting_id).all()
                objects = session.query(Object_).filter_by(setting_id=setting_id).all()
                races = session.query(Race).filter_by(setting_id=setting_id).all()
                skills = session.query(Skills).filter_by(setting_id=setting_id).all()
                sub_races = session.query(SubRace).filter_by(setting_id=setting_id).all()
                world_data = session.query(WorldData).filter_by(setting_id=setting_id).all()

                return {
                    "actors": actors,
                    "backgrounds": backgrounds,
                    "classes": classes,
                    "factions": factions,
                    "histories": histories,
                    "locations": locations,
                    "objects": objects,
                    "races": races,
                    "skills": skills,
                    "sub_races": sub_races,
                    "world_data": world_data,
                }
        except Exception as e:
            print(f"Error getting lore entities: {e}")
            return {}

    def get_note_associations(self, note_id):
        """Get all lore entity associations for a note"""
        associations = {}
        try:
            with Session(self.model.engine) as session:
                associations["actors"] = (
                    session.query(LitographyNoteToActor).filter_by(note_id=note_id).all()
                )
                associations["backgrounds"] = (
                    session.query(LitographyNoteToBackground).filter_by(note_id=note_id).all()
                )
                associations["classes"] = (
                    session.query(LitographyNoteToClass).filter_by(note_id=note_id).all()
                )
                associations["factions"] = (
                    session.query(LitographyNoteToFaction).filter_by(note_id=note_id).all()
                )
                associations["histories"] = (
                    session.query(LitographyNoteToHistory).filter_by(note_id=note_id).all()
                )
                associations["locations"] = (
                    session.query(LitographyNoteToLocation).filter_by(note_id=note_id).all()
                )
                associations["objects"] = (
                    session.query(LitographyNoteToObject).filter_by(note_id=note_id).all()
                )
                associations["races"] = (
                    session.query(LitographyNoteToRace).filter_by(note_id=note_id).all()
                )
                associations["skills"] = (
                    session.query(LitographyNoteToSkills).filter_by(note_id=note_id).all()
                )
                associations["sub_races"] = (
                    session.query(LitographyNoteToSubRace).filter_by(note_id=note_id).all()
                )
                associations["world_data"] = (
                    session.query(LitographyNoteToWorldData).filter_by(note_id=note_id).all()
                )
        except Exception as e:
            print(f"Error getting note associations: {e}")
        return associations

    def create_note_association(self, note_id, entity_type, entity_id):
        """Create an association between a note and a lore entity"""
        try:
            with Session(self.model.engine) as session:
                association = None
                if entity_type == "actor":
                    association = LitographyNoteToActor(note_id=note_id, actor_id=entity_id)
                elif entity_type == "background":
                    association = LitographyNoteToBackground(
                        note_id=note_id, background_id=entity_id
                    )
                elif entity_type == "class":
                    association = LitographyNoteToClass(note_id=note_id, class_id=entity_id)
                elif entity_type == "faction":
                    association = LitographyNoteToFaction(note_id=note_id, faction_id=entity_id)
                elif entity_type == "history":
                    association = LitographyNoteToHistory(note_id=note_id, history_id=entity_id)
                elif entity_type == "location":
                    association = LitographyNoteToLocation(note_id=note_id, location_id=entity_id)
                elif entity_type == "object":
                    association = LitographyNoteToObject(note_id=note_id, object_id=entity_id)
                elif entity_type == "race":
                    association = LitographyNoteToRace(note_id=note_id, race_id=entity_id)
                elif entity_type == "skill":
                    association = LitographyNoteToSkills(note_id=note_id, skill_id=entity_id)
                elif entity_type == "sub_race":
                    association = LitographyNoteToSubRace(note_id=note_id, sub_race_id=entity_id)
                elif entity_type == "world_data":
                    association = LitographyNoteToWorldData(
                        note_id=note_id, world_data_id=entity_id
                    )

                if association:
                    session.add(association)
                    session.commit()
                    return True
        except Exception as e:
            print(f"Error creating note association: {e}")
        return False

    def delete_note_association(self, note_id, entity_type, entity_id):
        """Delete an association between a note and a lore entity"""
        try:
            with Session(self.model.engine) as session:
                association = None
                if entity_type == "actor":
                    association = (
                        session.query(LitographyNoteToActor)
                        .filter_by(note_id=note_id, actor_id=entity_id)
                        .first()
                    )
                elif entity_type == "background":
                    association = (
                        session.query(LitographyNoteToBackground)
                        .filter_by(note_id=note_id, background_id=entity_id)
                        .first()
                    )
                elif entity_type == "class":
                    association = (
                        session.query(LitographyNoteToClass)
                        .filter_by(note_id=note_id, class_id=entity_id)
                        .first()
                    )
                elif entity_type == "faction":
                    association = (
                        session.query(LitographyNoteToFaction)
                        .filter_by(note_id=note_id, faction_id=entity_id)
                        .first()
                    )
                elif entity_type == "history":
                    association = (
                        session.query(LitographyNoteToHistory)
                        .filter_by(note_id=note_id, history_id=entity_id)
                        .first()
                    )
                elif entity_type == "location":
                    association = (
                        session.query(LitographyNoteToLocation)
                        .filter_by(note_id=note_id, location_id=entity_id)
                        .first()
                    )
                elif entity_type == "object":
                    association = (
                        session.query(LitographyNoteToObject)
                        .filter_by(note_id=note_id, object_id=entity_id)
                        .first()
                    )
                elif entity_type == "race":
                    association = (
                        session.query(LitographyNoteToRace)
                        .filter_by(note_id=note_id, race_id=entity_id)
                        .first()
                    )
                elif entity_type == "skill":
                    association = (
                        session.query(LitographyNoteToSkills)
                        .filter_by(note_id=note_id, skill_id=entity_id)
                        .first()
                    )
                elif entity_type == "sub_race":
                    association = (
                        session.query(LitographyNoteToSubRace)
                        .filter_by(note_id=note_id, sub_race_id=entity_id)
                        .first()
                    )
                elif entity_type == "world_data":
                    association = (
                        session.query(LitographyNoteToWorldData)
                        .filter_by(note_id=note_id, world_data_id=entity_id)
                        .first()
                    )

                if association:
                    session.delete(association)
                    session.commit()
                    return True
        except Exception as e:
            print(f"Error deleting note association: {e}")
        return False

    def on_delete_node_button_clicked(self, node_id):
        """Handle clicking '-' button to delete a node"""
        try:
            # First validate UI and database are in sync
            self.validate_ui_database_sync()

            # Debug: Check what nodes actually exist in database
            all_db_nodes = self.model.get_litography_nodes(storyline_id=self.current_storyline_id)
            existing_ids = [n.id for n in all_db_nodes]

            # First verify the node exists in the database directly

            with Session(self.model.engine) as session:
                node_to_delete_db = (
                    session.query(LitographyNode)
                    .filter_by(id=node_id, storyline_id=self.current_storyline_id)
                    .first()
                )

                if not node_to_delete_db:
                    self.view.ui.statusbar.showMessage(
                        f"Node {node_id} no longer exists, refreshing...", 3000
                    )
                    # Force refresh the display since the node is gone
                    self.load_and_draw_nodes()
                    return

            # Get fresh node data to understand its connections
            all_nodes = self.model.get_litography_nodes(storyline_id=self.current_storyline_id)
            node_to_delete = next((n for n in all_nodes if n.id == node_id), None)

            if not node_to_delete:
                self.view.ui.statusbar.showMessage("Node not found in current data", 3000)
                self.load_and_draw_nodes()
                return

            # In the new schema, we just need to delete connections involving this node
            # No need to update other nodes since connections are separate entities

            # Delete the node and its associated notes from database

            with Session(self.model.engine) as session:
                # First delete all connections involving this node
                session.query(NodeConnection).filter(
                    (NodeConnection.output_node_id == node_id)
                    | (NodeConnection.input_node_id == node_id)
                ).delete()

                # Delete all notes associated with this node
                notes_to_delete = (
                    session.query(LitographyNotes)
                    .filter_by(linked_node_id=node_id, storyline_id=self.current_storyline_id)
                    .all()
                )

                for note in notes_to_delete:
                    session.delete(note)

                # Then delete the node itself
                node_to_delete_db = (
                    session.query(LitographyNode)
                    .filter_by(id=node_id, storyline_id=self.current_storyline_id)
                    .first()
                )

                if node_to_delete_db:
                    session.delete(node_to_delete_db)
                    session.commit()
                    self.view.ui.statusbar.showMessage(
                        "Node, connections, and associated notes deleted successfully",
                        3000,
                    )
                else:
                    self.view.ui.statusbar.showMessage("Node not found in database", 3000)
                    return

            # Hide the panel if this node was selected
            if self.selected_node and self.selected_node.id == node_id:
                self.node_panel.hide()
                self.selected_node = None

            # Refresh the graph
            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error deleting node via button: {e}")
            self.view.ui.statusbar.showMessage(f"Error deleting node: {e}", 5000)

    def connect_signals(self):
        """Connect all UI signals to their handler methods."""
        # --- Page Navigation ---
        self.view.ui.litographerNavButton.released.connect(self.on_litographer_selected)
        apply_general_tooltips(self.view.ui.litographerNavButton, "litographer_tab")

        self.view.ui.lorekeeperNavButton.released.connect(self.on_lorekeeper_selected)
        apply_general_tooltips(self.view.ui.lorekeeperNavButton, "lorekeeper_tab")

        self.view.ui.characterArcsNavButton.released.connect(self.on_character_arcs_selected)
        apply_general_tooltips(self.view.ui.characterArcsNavButton, "character_arcs_tab")

        self.view.ui.storyweaverNavButton.released.connect(self.on_storyweaver_selected)
        apply_general_tooltips(self.view.ui.storyweaverNavButton, "storyweaver_tab")

        # --- File Menu ---
        self.view.ui.actionOpen.triggered.connect(self.on_open_storyline_clicked)
        self.view.ui.actionImportFromJSON.triggered.connect(self.on_import_from_json_clicked)
        # self.view.ui.actionExportSettingToJSON.triggered.connect(
        #     self.on_export_setting_to_json_clicked
        # )
        # Database and backup actions
        self.view.ui.actionDatabaseManager.triggered.connect(self.on_database_manager_clicked)
        self.view.ui.actionCreateBackup.triggered.connect(self.on_create_backup_clicked)

        # --- Storyline Menu ---
        self.view.ui.actionNewStoryline.triggered.connect(self.on_new_storyline_clicked)
        self.view.ui.actionSwitchStoryline.triggered.connect(self.on_switch_storyline_clicked)

        # --- Setting Menu ---
        self.view.ui.actionNewSetting.triggered.connect(self.on_new_setting_clicked)
        self.view.ui.actionSwitchSetting.triggered.connect(self.on_switch_setting_clicked)
        self.view.ui.actionManageSetting.triggered.connect(self.on_manage_setting_clicked)

        # Add storyline settings management action programmatically if it doesn't exist
        if not hasattr(self.view.ui, "actionManageStorylineSettings"):
            from PySide6.QtGui import QAction

            self.view.ui.actionManageStorylineSettings = QAction(
                "Manage Storyline-Setting Links", self.view
            )
            self.view.ui.menuSetting.addAction(self.view.ui.actionManageStorylineSettings)

        self.view.ui.actionManageStorylineSettings.triggered.connect(
            self.on_manage_storyline_settings_clicked
        )

        # --- User Menu ---
        self.view.ui.actionNewUser.triggered.connect(self.on_new_user_clicked)
        self.view.ui.actionSwitchUser.triggered.connect(self.on_switch_user_clicked)
        self.view.ui.actionManageUsers.triggered.connect(self.on_manage_users_clicked)

        # --- Plot Actions (context menu only now) ---
        self.view.ui.actionNewPlot.triggered.connect(self.on_new_plot_clicked)
        self.view.ui.actionSwitchPlot.triggered.connect(self.on_switch_plot_clicked)
        self.view.ui.actionDeletePlot.triggered.connect(self.on_delete_plot_clicked)

        # --- Litographer Toolbar ---
        self.view.ui.actionAddNode.triggered.connect(self.on_add_node_clicked)

        # --- Help Menu ---
        self.view.ui.actionAbout.triggered.connect(self.on_about_clicked)

        # --- Lorekeeper View Signals ---
        # Database tree and table view signals removed - using new Lorekeeper interface

        # --- Lorekeeper Form Buttons (deprecated interface removed) ---
        # Form buttons and tab widget removed - using new Lorekeeper interface

    # --- Project Handling ---
    def on_open_storyline_clicked(self):
        """Opens a dialog to select a storyline."""
        dialog = OpenStorylineDialog(self.model, self.view)
        storyline_id = dialog.get_selected_storyline_id()
        if storyline_id is not None:
            self.current_storyline_id = storyline_id

            # Update setting to match the storyline's associated setting
            with Session(self.model.engine) as session:
                storyline_setting = (
                    session.query(StorylineToSetting).filter_by(storyline_id=storyline_id).first()
                )
                if storyline_setting:
                    self.current_setting_id = storyline_setting.setting_id
                    print(
                        f"DEBUG: Updated setting to ID {self.current_setting_id} for storyline {storyline_id}"
                    )
                else:
                    # No setting linked - keep current setting or use first available
                    print(
                        f"DEBUG: No setting found for storyline {storyline_id}, keeping current setting"
                    )
                    if self.current_setting_id is None:
                        # If we don't have any setting, try to get the first available one
                        settings = self.model.get_all_settings()
                        if settings:
                            self.current_setting_id = settings[0].id
                            print(
                                f"DEBUG: Using first available setting ID {self.current_setting_id}"
                            )

            # Reset to first plot of opened storyline
            self._switch_to_first_plot_of_storyline()

            # Refresh the current view with the new project's data
            if self.view.ui.pageStack.currentIndex() == 0:
                self.load_plot_sections()
                self.load_and_draw_nodes()
            else:
                self._refresh_current_table_view()

            # Update status indicators to show new storyline and setting (permanent display)
            self.update_status_indicators()

    def on_database_manager_clicked(self):
        """Opens the database and backup manager dialog."""
        dialog = DatabaseManagerDialog(
            parent=self.view,
            current_db_path=str(self.backup_manager.database_path),
            backup_manager=self.backup_manager,
        )
        dialog.database_changed.connect(self.on_database_changed)
        dialog.exec()

    def on_create_backup_clicked(self):
        """Creates a manual backup of the database."""
        backup_path = self.backup_manager.create_backup()
        if backup_path:
            self.view.ui.statusbar.showMessage("Backup created successfully", 5000)
        else:
            self.view.ui.statusbar.showMessage("Failed to create backup", 5000)

    def on_database_changed(self, new_database_path: str):
        """Handle database change - requires application restart."""
        reply = QMessageBox.information(
            self.view,
            "Database Changed",
            f"Database changed to: {new_database_path}\\n\\n"
            "The application needs to be restarted to use the new database.",
            QMessageBox.StandardButton.Ok,
        )
        # Note: Full database switching would require reinitializing the entire application
        # For now, we inform the user to restart

    def on_backup_created(self, message: str):
        """Handle backup created signal."""
        self.view.ui.statusbar.showMessage(message, 3000)

    def on_backup_failed(self, message: str):
        """Handle backup failed signal."""
        self.view.ui.statusbar.showMessage(f"Backup failed: {message}", 5000)

    def on_import_from_json_clicked(self):
        """Import storyline data from a JSON file."""
        try:
            # Open file dialog to select JSON file
            file_path, _ = QFileDialog.getOpenFileName(
                self.view,
                "Import from JSON",
                "",
                "JSON files (*.json);;All files (*.*)",
            )

            if not file_path:
                return  # User cancelled

            # Load and validate JSON file
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)

                # Handle both JSON formats: nested under 'story_data' key or direct
                if "story_data" in json_data:
                    # New format: extract story_data subsection
                    json_data = json_data["story_data"]
                    self.view.ui.statusbar.showMessage("Detected nested story_data format", 3000)

            except (json.JSONDecodeError, IOError) as e:
                QMessageBox.critical(
                    self.view, "Import Error", f"Failed to load JSON file: {str(e)}"
                )
                return

            # Basic validation - check if it has the expected structure
            if not self._validate_json_structure(json_data):
                QMessageBox.critical(
                    self.view,
                    "Import Error",
                    "The JSON file doesn't match the expected schema format. "
                    "Please ensure it follows the structure of story_schema_template.json",
                )
                return

            # Ask user whether to import to current or new storyline/setting
            choice = self._get_import_choice()
            if choice is None:
                return  # User cancelled

            # Perform the import
            success = self._import_json_data(json_data, choice)

            if success:
                self.view.ui.statusbar.showMessage("JSON import completed successfully", 5000)
                # Refresh current view
                if self.view.ui.pageStack.currentIndex() == 0:
                    self.load_and_draw_nodes()
                else:
                    self._refresh_current_table_view()
            else:
                QMessageBox.warning(
                    self.view,
                    "Import Warning",
                    "Import completed with some errors. Check the status bar for details.",
                )

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Import Error",
                f"An unexpected error occurred during import: {str(e)}",
            )

    def on_export_setting_to_json_clicked(self):
        """Export current setting and all world-building data to a JSON file."""
        try:
            # Check if we have a current setting
            current_setting_id = self.model.current_setting_id
            if not current_setting_id:
                QMessageBox.warning(
                    self.view,
                    "Export Warning",
                    "No setting is currently selected. Please select a setting first.",
                )
                return

            # Get setting name for default filename
            setting_name = "setting"
            try:
                current_setting = self.model.get_setting_by_id(current_setting_id)
                if current_setting and current_setting.name:
                    # Clean filename - remove invalid characters
                    setting_name = "".join(
                        c for c in current_setting.name if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    setting_name = setting_name.replace(" ", "_")
            except:
                pass  # Use default if we can't get setting name

            # Open file dialog to select output location
            default_filename = f"{setting_name}_export.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Export Setting to JSON",
                default_filename,
                "JSON files (*.json);;All files (*.*)",
            )

            if not file_path:
                return  # User cancelled

            # Show progress in status bar
            self.view.ui.statusbar.showMessage("Exporting setting data...", 0)

            # Perform the export
            success = export_setting_to_json(current_setting_id, file_path)

            if success:
                self.view.ui.statusbar.showMessage(
                    f"Setting exported successfully to {os.path.basename(file_path)}",
                    5000,
                )
                QMessageBox.information(
                    self.view,
                    "Export Successful",
                    f"Setting data has been exported to:\n{file_path}\n\n"
                    f"This file can be imported using 'File > Import from JSON' to restore the setting.",
                )
            else:
                self.view.ui.statusbar.showMessage(
                    "Export failed - check console for details", 5000
                )
                QMessageBox.critical(
                    self.view,
                    "Export Error",
                    "Failed to export setting data. Please check the console output for details.",
                )

        except Exception as e:
            self.view.ui.statusbar.showMessage("Export failed", 5000)
            QMessageBox.critical(
                self.view,
                "Export Error",
                f"An unexpected error occurred during export: {str(e)}",
            )

    def _validate_json_structure(self, json_data):
        """Validate that the JSON has the expected structure."""
        if not isinstance(json_data, dict):
            return False

        # Check if it has at least some database table data
        # More flexible validation - just needs to have some table-like structures
        has_table_data = False
        for key, value in json_data.items():
            if isinstance(value, list) and key not in ["_consensus_models"]:
                has_table_data = True
                break

        if not has_table_data:
            return False

        # Optional: Check for typical required keys if they exist
        typical_keys = ["user", "setting", "storyline"]
        found_typical_keys = 0
        for key in typical_keys:
            if key in json_data and isinstance(json_data[key], list):
                found_typical_keys += 1

        # If we have some typical keys, that's good. If not, still proceed if we have table data
        return has_table_data

    def _get_import_choice(self):
        """Get user choice for import destination."""
        from PySide6.QtWidgets import (
            QDialog,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QRadioButton,
            QVBoxLayout,
        )

        dialog = QDialog(self.view)
        dialog.setWindowTitle("Import Destination")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Add description
        label = QLabel("Choose where to import the JSON data:")
        layout.addWidget(label)

        # Radio buttons for choices
        current_radio = QRadioButton("Import into current storyline/setting")
        new_radio = QRadioButton("Create new storyline/setting")
        current_radio.setChecked(True)  # Default selection

        layout.addWidget(current_radio)
        layout.addWidget(new_radio)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            return "current" if current_radio.isChecked() else "new"
        return None

    def _import_json_data(self, json_data, choice):
        """Import the JSON data into the database."""
        try:
            if choice == "new":
                # Create new storyline and setting
                storyline_name = json_data.get("storyline", [{}])[0].get(
                    "name", "Imported Storyline"
                )
                setting_name = json_data.get("setting", [{}])[0].get("name", "Imported Setting")

                if not storyline_name:
                    storyline_name = "Imported Storyline"
                if not setting_name:
                    setting_name = "Imported Setting"

                # Create new setting using add_row method
                setting_data = {
                    "name": setting_name,
                    "description": json_data.get("setting", [{}])[0].get("description", ""),
                    "user_id": self.model.user_id,
                }
                self.model.add_row("setting", setting_data)

                # Get the created setting by name
                all_settings = self.model.get_all_settings()
                new_setting = None
                for setting in all_settings:
                    if setting.name == setting_name and setting.user_id == self.model.user_id:
                        new_setting = setting
                        break

                if not new_setting:
                    raise ValueError(f"Failed to create setting: {setting_name}")

                # Create new storyline using add_row method
                storyline_data = {
                    "name": storyline_name,
                    "description": json_data.get("storyline", [{}])[0].get("description", ""),
                    "user_id": self.model.user_id,
                }
                self.model.add_row("storyline", storyline_data)

                # Get the created storyline by name
                all_storylines = self.model.get_all_storylines()
                new_storyline = None
                for storyline in all_storylines:
                    if storyline.name == storyline_name and storyline.user_id == self.model.user_id:
                        new_storyline = storyline
                        break

                if not new_storyline:
                    raise ValueError(f"Failed to create storyline: {storyline_name}")

                # Link storyline to setting using add_row method
                storyline_to_setting_data = {
                    "storyline_id": new_storyline.id,
                    "setting_id": new_setting.id,
                }
                self.model.add_row("storyline_to_setting", storyline_to_setting_data)

                # Switch to new storyline and setting
                self.current_storyline_id = new_storyline.id
                self.current_setting_id = new_setting.id
            else:
                # Use current storyline and setting
                new_setting = self.model.get_setting_by_id(self.current_setting_id)
                new_storyline = self.model.get_storyline_by_id(self.current_storyline_id)

            # Import all data types
            self._import_data_by_type(json_data, new_setting.id, new_storyline.id)

            return True

        except Exception as e:
            print(f"Import error: {e}")
            return False

    def _import_data_by_type(self, json_data, setting_id, storyline_id):
        """Import different data types from JSON."""
        # Skip user, setting, storyline, and linking tables as they're handled separately
        skip_tables = {"user", "setting", "storyline", "storyline_to_setting"}

        for table_name, records in json_data.items():
            if (
                table_name in skip_tables
                or not isinstance(records, list)
                or table_name.startswith("_")
            ):
                continue

            # Get the corresponding model class
            model_class = self.model.get_table_class(table_name)
            if not model_class:
                print(f"Unknown table: {table_name}")
                continue

            # Import each record
            for record_data in records:
                if not isinstance(record_data, dict):
                    continue

                # Update foreign keys to point to current setting/storyline
                updated_record = record_data.copy()

                # Remove keys that start with _ (metadata fields like _consensus_models)
                keys_to_remove = [key for key in updated_record.keys() if key.startswith("_")]
                for key in keys_to_remove:
                    del updated_record[key]

                if "setting_id" in updated_record:
                    updated_record["setting_id"] = setting_id
                if "storyline_id" in updated_record:
                    updated_record["storyline_id"] = storyline_id

                # Remove the ID field to let the database auto-assign
                if "id" in updated_record:
                    del updated_record["id"]

                try:
                    self.model.add_row(table_name, updated_record)
                except Exception as e:
                    print(f"Failed to import {table_name} record: {e}")
                    # Continue with other records

    def on_new_storyline_clicked(self):
        """Opens a dialog to create a new storyline."""
        dialog = NewStorylineDialog(self.model, self.view)
        storyline_data = dialog.get_storyline_data()
        if storyline_data is not None:
            try:
                # Extract setting ID before creating storyline
                selected_setting_id = storyline_data.pop("_selected_setting_id", None)

                # Create the storyline
                self.model.add_row("storyline", storyline_data)

                # Get the newly created storyline ID and switch to it
                storylines = self.model.get_all_storylines()
                new_storyline = next(
                    (
                        s
                        for s in storylines
                        if s.name == storyline_data["name"]
                        and s.user_id == storyline_data["user_id"]
                    ),
                    None,
                )

                if new_storyline:
                    self.current_storyline_id = new_storyline.id

                    # Link to setting if one was selected
                    if selected_setting_id is not None:
                        try:
                            success = self.model.link_storyline_to_setting(
                                new_storyline.id, selected_setting_id
                            )
                            if success:
                                # Update current setting to the linked one
                                self.current_setting_id = selected_setting_id
                                print(
                                    f"DEBUG: Linked new storyline {new_storyline.id} to setting {selected_setting_id}"
                                )
                        except Exception as e:
                            print(f"Error linking storyline to setting: {e}")

                    # Reset to first plot of new storyline (creates default if needed)
                    self._switch_to_first_plot_of_storyline()
                    # Refresh views
                    self.load_and_draw_nodes()
                    self.load_plot_sections()
                    self.update_status_indicators()

                self.view.ui.statusbar.showMessage(
                    f"Created new storyline: {storyline_data['name']}", 5000
                )
            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Error Creating Storyline",
                    f"Failed to create storyline: {str(e)}",
                )

    def on_new_setting_clicked(self):
        """Opens a dialog to create a new setting."""
        dialog = NewSettingDialog(self.model, self.view)
        setting_data = dialog.get_setting_data()
        if setting_data is not None:
            # Extract world building packages before saving
            selected_packages = setting_data.pop("_selected_packages", [])

            try:
                # Create the setting first
                self.model.add_row("setting", setting_data)

                # Get the newly created setting ID
                settings = self.model.get_all_rows_as_dicts("setting")
                new_setting = next(
                    (
                        s
                        for s in settings
                        if s["name"] == setting_data["name"]
                        and s["user_id"] == setting_data["user_id"]
                    ),
                    None,
                )

                if new_setting and selected_packages:
                    # Import world building packages for the new setting
                    dialog.import_packages_for_setting(selected_packages, new_setting["id"])

                self.view.ui.statusbar.showMessage(
                    f"Created new setting: {setting_data['name']}", 5000
                )

                # Prompt user to create a new storyline for this setting
                if new_setting:
                    reply = QMessageBox.question(
                        self.view,
                        "Create Storyline?",
                        f"Would you like to create a new storyline for the setting '{setting_data['name']}'?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes,
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        self._create_and_switch_to_new_storyline(
                            new_setting["id"], setting_data["user_id"]
                        )

            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Error Creating Setting",
                    f"Failed to create setting: {str(e)}",
                )

    def _create_and_switch_to_new_storyline(self, setting_id: int, user_id: int):
        """
        Create a new storyline linked to the given setting and switch to it.

        Args:
            setting_id: The ID of the setting to link to
            user_id: The user ID for the new storyline
        """
        try:
            # Prompt user for storyline name
            storyline_name, ok = QInputDialog.getText(
                self.view,
                "New Storyline",
                "Enter a name for the new storyline:",
                QLineEdit.EchoMode.Normal,
                "",
            )

            if not ok or not storyline_name.strip():
                return

            # Create the storyline
            storyline_data = {
                "name": storyline_name.strip(),
                "description": "",
                "user_id": user_id,
            }
            self.model.add_row("storyline", storyline_data)

            # Get the newly created storyline
            storylines = self.model.get_all_storylines()
            new_storyline = next(
                (
                    s
                    for s in storylines
                    if s.name == storyline_data["name"] and s.user_id == storyline_data["user_id"]
                ),
                None,
            )

            if new_storyline:
                # Link to the setting
                success = self.model.link_storyline_to_setting(new_storyline.id, setting_id)
                if success:
                    self.current_setting_id = setting_id
                    print(f"DEBUG: Linked new storyline {new_storyline.id} to setting {setting_id}")

                # Switch to the new storyline
                self.current_storyline_id = new_storyline.id

                # Switch to first plot (creates default if needed)
                self._switch_to_first_plot_of_storyline()

                # Refresh views
                self.load_and_draw_nodes()
                self.load_plot_sections()
                self.update_status_indicators()

                self.view.ui.statusbar.showMessage(
                    f"Created and switched to storyline: {storyline_name}", 5000
                )
            else:
                QMessageBox.warning(
                    self.view, "Error", "Failed to retrieve the newly created storyline."
                )

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error Creating Storyline",
                f"Failed to create storyline: {str(e)}",
            )

    def on_switch_storyline_clicked(self):
        """Opens a dialog to switch between storylines."""
        dialog = StorylineSwitcherDialog(self.model, self.current_storyline_id, self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_storyline_id = dialog.get_selected_storyline_id()
            if new_storyline_id:
                try:
                    self.current_storyline_id = new_storyline_id

                    # Get storyline name for status message
                    storylines = self.model.get_all_storylines()
                    storyline_name = next(
                        (s.name for s in storylines if s.id == new_storyline_id),
                        "Unknown",
                    )

                    # Update setting to match the storyline's associated setting
                    with Session(self.model.engine) as session:
                        storyline_setting = (
                            session.query(StorylineToSetting)
                            .filter_by(storyline_id=new_storyline_id)
                            .first()
                        )
                        if storyline_setting:
                            self.current_setting_id = storyline_setting.setting_id
                        else:
                            # No setting linked - keep current setting or use first available
                            if self.current_setting_id is None:
                                settings = self.model.get_all_settings()
                                if settings:
                                    self.current_setting_id = settings[0].id

                    self.view.ui.statusbar.showMessage(
                        f"Switched to storyline: {storyline_name}", 5000
                    )

                    # Reset to first plot of new storyline
                    self._switch_to_first_plot_of_storyline()

                    # Refresh the current view with the new storyline's data
                    current_page_index = self.view.ui.pageStack.currentIndex()
                    if current_page_index == 0:
                        # Litographer view - reload plot sections and nodes
                        self.load_plot_sections()
                        self.load_and_draw_nodes()
                    elif current_page_index == 1:
                        # Lorekeeper view - refresh table view
                        self._refresh_current_table_view()
                    elif current_page_index == 2:
                        # Character Arcs view - refresh arcs for current storyline (even if None)
                        self.character_arc_page.refresh_arcs(self.current_storyline_id)

                    # Reinitialize Lorekeeper widget with potentially new setting
                    if self.new_lorekeeper_widget is not None:
                        # Remove old widget
                        self.view.ui.newLorekeeperPage.layout().removeWidget(
                            self.new_lorekeeper_widget
                        )
                        self.new_lorekeeper_widget.deleteLater()
                        self.new_lorekeeper_widget = None

                    # Recreate the Lorekeeper widget with the current setting
                    if self.current_setting_id is not None:
                        self.new_lorekeeper_widget = NewLorekeeperPage(
                            self.model, self.current_setting_id
                        )
                        # Add the widget to the new Lorekeeper page
                        if self.view.ui.newLorekeeperPage.layout() is None:
                            new_lorekeeper_layout = QVBoxLayout(self.view.ui.newLorekeeperPage)
                            new_lorekeeper_layout.setContentsMargins(0, 0, 0, 0)
                        else:
                            new_lorekeeper_layout = self.view.ui.newLorekeeperPage.layout()
                        new_lorekeeper_layout.addWidget(self.new_lorekeeper_widget)

                    self.update_status_indicators()
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Error Switching Storyline",
                        f"Failed to switch storyline: {str(e)}",
                    )

    def on_manage_storyline_settings_clicked(self):
        """Opens a dialog to manage storylines connected to settings."""
        try:
            from storymaster.view.common.setting_storylines_dialog import (
                SettingStorylinesDialog,
            )

            dialog = SettingStorylinesDialog(self.model, self.view)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to open storyline settings dialog: {str(e)}",
            )

    def on_switch_setting_clicked(self):
        """Opens a dialog to switch between settings."""
        dialog = SettingSwitcherDialog(self.model, self.current_setting_id, self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_setting_id = dialog.get_selected_setting_id()
            if new_setting_id:
                try:
                    self.current_setting_id = new_setting_id
                    # Get setting name for status message
                    settings = self.model.get_all_settings()
                    setting_name = next(
                        (s.name for s in settings if s.id == new_setting_id), "Unknown"
                    )

                    # Switch to the first storyline in this setting
                    with Session(self.model.engine) as session:
                        first_storyline_link = (
                            session.query(StorylineToSetting)
                            .filter_by(setting_id=new_setting_id)
                            .first()
                        )

                        if first_storyline_link:
                            self.current_storyline_id = first_storyline_link.storyline_id
                            # Switch to the first plot of this storyline
                            self._switch_to_first_plot_of_storyline()
                        else:
                            # No storylines linked to this setting yet
                            self.current_storyline_id = None
                            self.current_plot_id = None
                            self.current_plot_section_id = None

                    self.view.ui.statusbar.showMessage(f"Switched to setting: {setting_name}", 5000)

                    # Refresh the current view with the new setting's data
                    current_page_index = self.view.ui.pageStack.currentIndex()
                    if current_page_index == 0:
                        # Litographer view - reload plot sections and nodes
                        self.load_plot_sections()
                        self.load_and_draw_nodes()
                    elif current_page_index == 1:
                        # Lorekeeper view - refresh table view
                        self._refresh_current_table_view()
                    elif current_page_index == 2:
                        # Character Arcs view - refresh arcs for current storyline (even if None)
                        self.character_arc_page.refresh_arcs(self.current_storyline_id)

                    # Refresh lorekeeper views to show new setting data
                    # Note: db_tree_model is deprecated, using new Lorekeeper interface

                    # Reinitialize new Lorekeeper widget with new setting
                    if self.new_lorekeeper_widget is not None:
                        # Remove old widget
                        self.view.ui.newLorekeeperPage.layout().removeWidget(
                            self.new_lorekeeper_widget
                        )
                        self.new_lorekeeper_widget.deleteLater()
                        self.new_lorekeeper_widget = None

                    # Recreate the Lorekeeper widget with the new setting
                    if new_setting_id is not None:
                        self.new_lorekeeper_widget = NewLorekeeperPage(self.model, new_setting_id)
                        # Add the widget to the new Lorekeeper page
                        if self.view.ui.newLorekeeperPage.layout() is None:
                            new_lorekeeper_layout = QVBoxLayout(self.view.ui.newLorekeeperPage)
                            new_lorekeeper_layout.setContentsMargins(0, 0, 0, 0)
                        else:
                            new_lorekeeper_layout = self.view.ui.newLorekeeperPage.layout()
                        new_lorekeeper_layout.addWidget(self.new_lorekeeper_widget)

                    self.update_status_indicators()
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Error Switching Setting",
                        f"Failed to switch setting: {str(e)}",
                    )

    def on_manage_setting_clicked(self):
        """Opens the import lore packages dialog for the current setting."""
        try:
            # Check if we have a current setting
            if not hasattr(self, "current_setting_id") or not self.current_setting_id:
                QMessageBox.warning(
                    self.view,
                    "No Setting Selected",
                    "Please select or create a setting first to import lore packages.",
                )
                return

            # Get setting name
            try:
                settings = self.model.get_all_settings()
                setting_name = next(
                    (s.name for s in settings if s.id == self.current_setting_id),
                    "Unknown Setting",
                )
            except Exception:
                setting_name = "Current Setting"

            # Open import lore packages dialog
            dialog = ImportLorePackagesDialog(
                self.model, self.current_setting_id, setting_name, self.view
            )
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to open import lore packages dialog: {str(e)}",
            )

    # --- User Management Methods ---

    def on_new_user_clicked(self):
        """Opens a dialog to create a new user."""
        dialog = NewUserDialog(self.model, self.view)
        user_data = dialog.get_user_data()
        if user_data is not None:
            try:
                new_user = self.model.create_user(user_data["username"])
                self.view.ui.statusbar.showMessage(f"Created new user: {new_user.username}", 5000)
            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Error Creating User",
                    f"Failed to create user: {str(e)}",
                )

    def on_switch_user_clicked(self):
        """Opens a dialog to switch between users."""
        dialog = UserSwitcherDialog(self.model, self.model.user_id, self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_user_id = dialog.get_selected_user_id()
            if new_user_id:
                try:
                    # Switch the user in the model
                    if self.model.switch_user(new_user_id):
                        user = self.model.get_current_user()
                        user_name = user.username if user else "Unknown"

                        # Refresh all UI components for the new user
                        self.refresh_after_user_switch()

                        self.view.ui.statusbar.showMessage(f"Switched to user: {user_name}", 5000)
                    else:
                        QMessageBox.warning(
                            self.view,
                            "User Switch Failed",
                            "Could not switch to the selected user.",
                        )
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Error Switching User",
                        f"Failed to switch user: {str(e)}",
                    )

    def on_manage_users_clicked(self):
        """Opens the user management dialog."""
        dialog = UserManagerDialog(self.model, self.model.user_id, self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(dialog, "action"):
            try:
                if dialog.action == "add" and dialog.new_user_name:
                    new_user = self.model.create_user(dialog.new_user_name)
                    self.view.ui.statusbar.showMessage(
                        f"Created new user: {new_user.username}", 5000
                    )
                    # Reload the dialog to show new user
                    dialog.load_users()

                elif dialog.action == "switch" and dialog.selected_user_id:
                    # Switch the user in the model
                    if self.model.switch_user(dialog.selected_user_id):
                        user = self.model.get_current_user()
                        user_name = user.username if user else "Unknown"

                        # Refresh all UI components for the new user
                        self.refresh_after_user_switch()

                        self.view.ui.statusbar.showMessage(f"Switched to user: {user_name}", 5000)
                    else:
                        QMessageBox.warning(
                            self.view,
                            "User Switch Failed",
                            "Could not switch to the selected user.",
                        )

                elif dialog.action == "delete" and dialog.selected_user_id:
                    user = self.model.get_user_by_id(dialog.selected_user_id)
                    if user:
                        self.model.delete_user(dialog.selected_user_id)
                        self.view.ui.statusbar.showMessage(f"Deleted user: {user.username}", 5000)

            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Error Managing Users",
                    f"Failed to manage users: {str(e)}",
                )

    def refresh_after_user_switch(self):
        """
        Refreshes all UI components after switching users.
        This ensures the interface shows only data for the current user.
        """
        try:
            # Reset current storyline and setting to first available for new user
            storylines = self.model.get_all_storylines()
            settings = self.model.get_all_settings()

            # Set to first available storyline, or keep current if it exists for this user
            if storylines:
                storyline_ids = [s.id for s in storylines]
                if self.current_storyline_id not in storyline_ids:
                    self.current_storyline_id = storylines[0].id
            else:
                self.current_storyline_id = None

            # Set to first available setting, or keep current if it exists for this user
            if settings:
                setting_ids = [s.id for s in settings]
                if self.current_setting_id not in setting_ids:
                    self.current_setting_id = settings[0].id
            else:
                self.current_setting_id = None

            # Clear and refresh UI components

            # Clear Litographer scene and reload nodes
            self.node_scene.clear()
            if self.current_storyline_id:
                self.load_and_draw_nodes()

            # Refresh Lorekeeper database view
            # Note: db_tree_model is deprecated, using new Lorekeeper interface

            # Clear any selected table/row data
            self.current_table_name = None
            self.current_row_data = None
            self.current_foreign_keys = {}

            # Clear form widgets
            self.edit_form_widgets = {}
            self.add_form_widgets = {}

            # Update status indicators
            self.update_status_indicators()

        except Exception as e:
            print(f"Error refreshing UI after user switch: {str(e)}")
            QMessageBox.warning(
                self.view,
                "Refresh Warning",
                f"Some UI elements may not have refreshed properly: {str(e)}",
            )

    # --- Plot Management Methods ---

    def on_new_plot_clicked(self):
        """Handle creating a new plot in the current project."""
        try:
            with Session(self.model.engine) as session:
                plots = (
                    session.query(LitographyPlot)
                    .filter_by(storyline_id=self.current_storyline_id)
                    .all()
                )

                dialog = PlotManagerDialog(self.view)
                dialog.populate_plots(plots, self.current_plot_id)
                dialog.new_plot_input.setText("")
                dialog.new_plot_input.setFocus()

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(dialog, "action"):
                    if dialog.action == "add":
                        new_plot = LitographyPlot(
                            title=dialog.new_plot_name,
                            storyline_id=self.current_storyline_id,
                        )
                        session.add(new_plot)
                        session.commit()

                        self.view.ui.statusbar.showMessage(
                            f"Created new plot: {dialog.new_plot_name}", 5000
                        )

        except Exception as e:
            print(f"Error creating new plot: {e}")
            self.view.ui.statusbar.showMessage(f"Error creating plot: {e}", 5000)

    def on_switch_plot_clicked(self):
        """Handle switching to a different plot."""
        try:
            with Session(self.model.engine) as session:
                plots = (
                    session.query(LitographyPlot)
                    .filter_by(storyline_id=self.current_storyline_id)
                    .all()
                )

                if len(plots) <= 1:
                    self.view.ui.statusbar.showMessage(
                        "Only one plot available. Create more plots to switch.", 5000
                    )
                    return

                dialog = PlotManagerDialog(self.view)
                dialog.populate_plots(plots, self.current_plot_id)

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(dialog, "action"):
                    if dialog.action == "switch" and dialog.selected_plot_id:
                        self.current_plot_id = dialog.selected_plot_id
                        self.current_plot_section_id = (
                            None  # Reset section to avoid loading old sections
                        )

                        plot = session.query(LitographyPlot).get(self.current_plot_id)
                        plot_name = plot.title if plot else f"Plot {self.current_plot_id}"

                        self.view.ui.statusbar.showMessage(f"Switched to plot: {plot_name}", 5000)

                        # Refresh the litographer view if currently active
                        if self.view.ui.pageStack.currentIndex() == 0:
                            self.load_plot_sections()
                            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error switching plot: {e}")
            self.view.ui.statusbar.showMessage(f"Error switching plot: {e}", 5000)

    def on_delete_plot_clicked(self):
        """Handle deleting the current plot."""
        try:
            with Session(self.model.engine) as session:
                plots = (
                    session.query(LitographyPlot)
                    .filter_by(storyline_id=self.current_storyline_id)
                    .all()
                )

                if len(plots) <= 1:
                    self.view.ui.statusbar.showMessage(
                        "Cannot delete the only plot in the project.", 5000
                    )
                    return

                dialog = PlotManagerDialog(self.view)
                dialog.populate_plots(plots, self.current_plot_id)

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(dialog, "action"):
                    if dialog.action == "delete" and dialog.selected_plot_id:
                        plot_to_delete = session.query(LitographyPlot).get(dialog.selected_plot_id)
                        plot_name = (
                            plot_to_delete.title
                            if plot_to_delete
                            else f"Plot {dialog.selected_plot_id}"
                        )

                        # Delete all related data
                        sections = (
                            session.query(LitographyPlotSection)
                            .filter_by(plot_id=dialog.selected_plot_id)
                            .all()
                        )

                        for section in sections:
                            # Delete junction records
                            session.query(LitographyNodeToPlotSection).filter_by(
                                plot_section_id=section.id
                            ).delete()

                            # Delete nodes in this section
                            nodes = (
                                session.query(LitographyNode)
                                .join(LitographyNodeToPlotSection)
                                .filter(
                                    LitographyNodeToPlotSection.litography_plot_section_id
                                    == section.id
                                )
                                .all()
                            )

                            for node in nodes:
                                session.delete(node)

                            session.delete(section)

                        session.delete(plot_to_delete)
                        session.commit()

                        # If we deleted the current plot, switch to the first available plot
                        if dialog.selected_plot_id == self.current_plot_id:
                            remaining_plots = (
                                session.query(LitographyPlot)
                                .filter_by(storyline_id=self.current_storyline_id)
                                .first()
                            )

                            if remaining_plots:
                                self.current_plot_id = remaining_plots.id

                                # Refresh the view
                                if self.view.ui.pageStack.currentIndex() == 0:
                                    self.load_plot_sections()
                                    self.load_and_draw_nodes()

                        self.view.ui.statusbar.showMessage(f"Deleted plot: {plot_name}", 5000)

        except Exception as e:
            print(f"Error deleting plot: {e}")
            self.view.ui.statusbar.showMessage(f"Error deleting plot: {e}", 5000)

    # --- Litographer Methods ---

    def on_litographer_selected(self):
        """Handle switching to the Litographer page and loading nodes."""
        self.view.ui.pageStack.setCurrentIndex(0)
        self.load_plot_sections()
        self.load_and_draw_nodes()
        # Hide Storyweaver info cards when leaving
        if hasattr(self, 'storyweaver_widget') and self.storyweaver_widget:
            self.storyweaver_widget.hide_info_cards()

    def load_plot_sections(self):
        """Load plot sections and populate the tabs"""
        try:

            # Clear existing tabs and section IDs
            self.section_tabs.clear()
            self.section_tab_ids.clear()

            with Session(self.model.engine) as session:
                sections = (
                    session.query(LitographyPlotSection)
                    .filter_by(plot_id=self.current_plot_id)
                    .order_by(LitographyPlotSection.id)
                    .all()
                )

                if not sections:
                    # Create a default section if none exist
                    default_section = LitographyPlotSection(
                        plot_section_type=PlotSectionType.FLAT,
                        plot_id=self.current_plot_id,
                    )
                    session.add(default_section)
                    session.commit()
                    session.refresh(default_section)
                    sections = [default_section]

                # Add tabs for each section
                for section in sections:
                    section_name = f"Section {section.id} ({section.plot_section_type.value})"
                    tab_index = self.section_tabs.addTab(QWidget(), section_name)
                    self.section_tab_ids.append(section.id)  # Store section ID at tab index

                # Select first section by default
                if sections and self.current_plot_section_id is None:
                    self.current_plot_section_id = sections[0].id
                    self.section_tabs.setCurrentIndex(0)
                elif self.current_plot_section_id:
                    # Find and select the current section
                    try:
                        section_index = self.section_tab_ids.index(self.current_plot_section_id)
                        self.section_tabs.setCurrentIndex(section_index)
                    except ValueError:
                        # Section not found, default to first
                        if self.section_tab_ids:
                            self.current_plot_section_id = self.section_tab_ids[0]
                            self.section_tabs.setCurrentIndex(0)

        except Exception as e:
            print(f"Error loading plot sections: {e}")
            self.view.ui.statusbar.showMessage(f"Error loading sections: {e}", 5000)

    def _switch_to_first_plot_of_storyline(self):
        """Switch to the first plot of the current storyline, or create one if none exist"""
        try:
            with Session(self.model.engine) as session:
                first_plot = (
                    session.query(LitographyPlot)
                    .filter_by(storyline_id=self.current_storyline_id)
                    .first()
                )

                if first_plot:
                    self.current_plot_id = first_plot.id
                    self.current_plot_section_id = None  # Reset section selection
                else:
                    # Create a default plot for this storyline
                    default_plot = LitographyPlot(
                        title=f"Plot 1",
                        description="Default plot for storyline",
                        storyline_id=self.current_storyline_id,
                    )
                    session.add(default_plot)
                    session.commit()
                    session.refresh(default_plot)
                    self.current_plot_id = default_plot.id
                    self.current_plot_section_id = None

        except Exception as e:
            print(f"Error switching to first plot of storyline: {str(e)}")
            # Fallback to a default plot ID
            self.current_plot_id = 1
            self.current_plot_section_id = None

    def get_nodes_in_section(self, section_id):
        """Get all nodes that belong to a specific plot section"""
        try:

            with Session(self.model.engine) as session:
                # Query nodes that are linked to this section via the junction table
                nodes = (
                    session.query(LitographyNode)
                    .join(
                        LitographyNodeToPlotSection,
                        LitographyNode.id == LitographyNodeToPlotSection.node_id,
                    )
                    .filter(
                        LitographyNodeToPlotSection.litography_plot_section_id == section_id,
                        LitographyNode.storyline_id == self.current_storyline_id,
                    )
                    .all()
                )

                return nodes

        except Exception as e:
            print(f"Error getting nodes in section: {e}")
            return []

    def add_node_to_section(self, node_id, section_id):
        """Add a node to a plot section via the junction table"""
        try:

            with Session(self.model.engine) as session:
                # Check if the relationship already exists
                existing = (
                    session.query(LitographyNodeToPlotSection)
                    .filter_by(node_id=node_id, litography_plot_section_id=section_id)
                    .first()
                )

                if existing:
                    pass  # Relationship already exists
                else:
                    # Create the relationship
                    node_section_link = LitographyNodeToPlotSection(
                        node_id=node_id, litography_plot_section_id=section_id
                    )
                    session.add(node_section_link)
                    session.commit()

                # Verify the relationship was created
                verification = (
                    session.query(LitographyNodeToPlotSection)
                    .filter_by(node_id=node_id, litography_plot_section_id=section_id)
                    .first()
                )

                if verification:
                    pass  # Verification successful
                else:
                    pass  # Verification failed
        except Exception as e:
            print(f"Error adding node to section: {e}")
            import traceback

            traceback.print_exc()

    def move_node_to_section(self, node_id, new_section_id):
        """Move a node from its current section to a new section"""
        try:

            with Session(self.model.engine) as session:
                # Remove existing section relationships for this node
                existing_links = (
                    session.query(LitographyNodeToPlotSection).filter_by(node_id=node_id).all()
                )

                for link in existing_links:
                    session.delete(link)

                # Add new section relationship
                new_link = LitographyNodeToPlotSection(
                    node_id=node_id, litography_plot_section_id=new_section_id
                )
                session.add(new_link)
                session.commit()

        except Exception as e:
            print(f"Error moving node to section: {e}")

    def add_node_at_position(self, x, y, node_type):
        """Add a node at specific coordinates (for testing and programmatic use)"""
        new_node_data = {
            "name": f"New {node_type.value} Node",
            "description": None,
            "node_type": node_type,
            "x_position": x,
            "y_position": y,
            "storyline_id": self.current_storyline_id,
        }

        try:
            self.model.add_row("litography_node", new_node_data)
            self.load_and_draw_nodes()
            return True
        except Exception as e:
            print(f"Error adding node at position: {e}")
            return False

    def on_add_node_clicked(self):
        """Handles the 'Add Node' action by opening a dialog."""
        dialog = AddNodeDialog(self.view)
        new_node_data = dialog.get_data()

        if new_node_data:
            new_node_data["storyline_id"] = self.current_storyline_id
            # Add default position if not present
            if "x_position" not in new_node_data:
                new_node_data["x_position"] = 100.0
            if "y_position" not in new_node_data:
                new_node_data["y_position"] = 100.0

            try:
                self.model.add_row("litography_node", new_node_data)

                # If we have a current section, add the node to it
                if self.current_plot_section_id:
                    # Get the newly created node ID
                    all_nodes_after = self.model.get_litography_nodes(
                        storyline_id=self.current_storyline_id
                    )
                    new_node = max(all_nodes_after, key=lambda n: n.id)

                    # Add to current section
                    self.add_node_to_section(new_node.id, self.current_plot_section_id)

                self.view.ui.statusbar.showMessage("Successfully added new node.", 5000)
                self.load_and_draw_nodes()
            except Exception as e:
                print(f"Error adding new node: {e}")
                self.view.ui.statusbar.showMessage(f"Error: {e}", 5000)

    def load_and_draw_nodes(self):
        """Fetches node data from the model and draws them using stored positions."""
        self.node_scene.clear()

        # Get nodes filtered by current plot section
        if self.current_plot_section_id:
            all_nodes = self.get_nodes_in_section(self.current_plot_section_id)
        else:
            all_nodes = self.model.get_litography_nodes(storyline_id=self.current_storyline_id)

        if not all_nodes:
            return

        # Define colors for different node types
        node_colors = {
            "EXPOSITION": "#FFD700",  # Gold
            "ACTION": "#FF6B6B",  # Red
            "REACTION": "#4ECDC4",  # Teal
            "TWIST": "#FF8C42",  # Orange
            "DEVELOPMENT": "#45B7D1",  # Blue
            "OTHER": "#5c4a8e",  # Purple (default)
        }

        # Draw nodes at their stored positions
        for node in all_nodes:
            x_pos = getattr(node, "x_position", 100 + (node.id * 150))
            y_pos = getattr(node, "y_position", 200)

            # Get color based on node type
            node_color = node_colors.get(node.node_type.name, node_colors["OTHER"])

            # Create the appropriate shape based on node type
            node_item = create_node_item(0, 0, 80, 80, node, self)  # Create at origin
            node_item.setBrush(QBrush(QColor(node_color)))
            node_item.setPen(QPen(QColor("#333333"), 2))
            self.node_scene.addItem(node_item)
            node_item.setPos(x_pos, y_pos)  # Position after adding to scene

        # Draw connections using new system
        self.draw_connections(all_nodes)

    def draw_connections(self, nodes):
        """Draw connections between nodes using the new NodeConnection system"""
        try:
            # Clear existing connection lines
            self.connection_lines = []

            with Session(self.model.engine) as session:
                connections = (
                    session.query(NodeConnection)
                    .join(
                        LitographyNode,
                        NodeConnection.output_node_id == LitographyNode.id,
                    )
                    .filter(LitographyNode.storyline_id == self.current_storyline_id)
                    .all()
                )

                # Find node items in the scene
                node_items = {}
                for item in self.node_scene.items():
                    if hasattr(item, "node_data") and hasattr(item, "get_output_connection_pos"):
                        node_items[item.node_data.id] = item

                for connection in connections:
                    output_item = node_items.get(connection.output_node_id)
                    input_item = node_items.get(connection.input_node_id)

                    if output_item and input_item:
                        # Get connection points from the actual node items
                        start_pos = output_item.get_output_connection_pos()
                        end_pos = input_item.get_input_connection_pos()

                        # Create connection line
                        line_item = QGraphicsLineItem(
                            start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y()
                        )
                        line_item.setPen(QPen(QColor("#FFFFFF"), 2))
                        line_item.setZValue(1)  # Behind nodes but above background

                        # Store connection info for updates
                        line_item.output_item = output_item
                        line_item.input_item = input_item

                        self.node_scene.addItem(line_item)
                        self.connection_lines.append(line_item)

        except Exception as e:
            print(f"Error drawing connections: {e}")

    def update_all_connections(self):
        """Update all connection line positions"""
        try:
            for line_item in getattr(self, "connection_lines", []):
                if hasattr(line_item, "output_item") and hasattr(line_item, "input_item"):
                    start_pos = line_item.output_item.get_output_connection_pos()
                    end_pos = line_item.input_item.get_input_connection_pos()

                    line_item.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        except Exception as e:
            print(f"Error updating connections: {e}")

    def order_nodes_by_links(self, nodes):
        """Order nodes using new connection system (no specific order needed)."""
        # In the new system, nodes don't need specific ordering since they're positioned manually
        return nodes

    # --- Lorekeeper Methods (DEPRECATED - old database interface) ---
    # NOTE: These methods are deprecated and left for compatibility
    # The new Lorekeeper interface uses NewLorekeeperPage instead

    def populate_add_form(self):
        """Populates the 'Add New Row' tab with a blank form for the current table."""
        if not self.current_table_name:
            return

        # NOTE: Assumes get_table_data can accept a storyline_id to get correct headers
        headers, _ = self.model.get_table_data(
            self.current_table_name, storyline_id=self.current_storyline_id
        )
        blank_data = {header: "" for header in headers}
        self._populate_form(
            self.view.ui.addFormLayout,
            self.add_form_widgets,
            blank_data,
            is_add_form=True,
        )

    def _populate_form(
        self,
        layout: QWidget,
        widget_dict: dict,
        row_data: dict,
        is_add_form: bool = False,
    ):
        """Generic helper to dynamically create an editable form."""
        self._clear_layout(layout)
        widget_dict.clear()

        for key, value in row_data.items():
            # Hide ID fields from both add and edit forms
            if key.lower() == "id":
                continue
            # Hide system fields from add forms only
            if is_add_form and key.lower() in ["setting_id", "storyline_id"]:
                continue

            label = QLabel(f"{key.replace('_', ' ').title()}:")

            if key in self.current_foreign_keys:
                field = self._create_dropdown(key, value)
            else:
                field = self._create_field_by_type(key, value)

            # No need for ID readonly logic since IDs are now hidden

            layout.addRow(label, field)
            widget_dict[key] = field

    def _create_dropdown(self, key, value):
        """Helper to create and populate a QComboBox for a foreign key."""
        field = QComboBox()
        referenced_table, _ = self.current_foreign_keys[key]

        try:
            # NOTE: Assumes get_all_rows_as_dicts can be filtered by project
            dropdown_items = self.model.get_all_rows_as_dicts(
                referenced_table, storyline_id=self.current_storyline_id
            )
            field.addItem("None", None)

            current_combo_index = 0
            for i, item_dict in enumerate(dropdown_items):
                display_text = str(
                    item_dict.get("name")
                    or item_dict.get("location_name")
                    or item_dict.get("background_name")
                    or item_dict.get("first_name")
                    or item_dict.get("faction_name")
                    or item_dict.get("event_name")
                    or item_dict.get("class_name")
                    or item_dict.get("race_name")
                    or item_dict.get("sub_race_name")
                    or item_dict.get("object_name")
                    or f"ID: {item_dict['id']}"
                )
                field.addItem(display_text, item_dict["id"])
                if item_dict["id"] == value:
                    current_combo_index = i + 1

            field.setCurrentIndex(current_combo_index)
        except Exception as e:
            pass  # Could not populate dropdown
        return field

    def _create_field_by_type(self, key: str, value):
        """Helper to create appropriate input field based on column type."""
        column_type = self.current_column_types.get(key, "string")
        str_value = str(value) if value is not None else ""

        if column_type == "integer":
            field = self._create_integer_field(str_value)
        elif column_type == "float":
            field = self._create_float_field(str_value)
        elif column_type == "boolean":
            field = self._create_boolean_field(str_value)
        elif column_type == "text" or "\n" in str_value or len(str_value) > 60:
            field = QTextEdit(str_value)
            field.setMinimumHeight(80)
        else:
            # Default to string/text input
            field = QLineEdit(str_value)

        return field

    def _create_integer_field(self, str_value: str):
        """Create a QLineEdit with integer-only input validation."""
        from PySide6.QtGui import QIntValidator

        field = QLineEdit(str_value)
        validator = QIntValidator()
        field.setValidator(validator)
        field.setPlaceholderText("Enter integer...")
        return field

    def _create_float_field(self, str_value: str):
        """Create a QLineEdit with float input validation."""
        from PySide6.QtGui import QDoubleValidator

        field = QLineEdit(str_value)
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        field.setValidator(validator)
        field.setPlaceholderText("Enter number...")
        return field

    def _create_boolean_field(self, str_value: str):
        """Create a QCheckBox for boolean values."""
        from PySide6.QtWidgets import QCheckBox

        field = QCheckBox()
        # Convert string to boolean
        if str_value.lower() in ("true", "1", "yes", "on"):
            field.setChecked(True)
        elif str_value.lower() in ("false", "0", "no", "off", ""):
            field.setChecked(False)
        else:
            # Try to convert to int/bool
            try:
                field.setChecked(bool(int(str_value)))
            except (ValueError, TypeError):
                field.setChecked(False)
        return field

    def _create_text_field(self, value):
        """Helper to create a QLineEdit or QTextEdit based on content length."""
        str_value = str(value) if value is not None else ""
        if "\n" in str_value or len(str_value) > 60:
            field = QTextEdit(str_value)
            field.setMinimumHeight(80)
        else:
            field = QLineEdit(str_value)
        return field

    def on_save_changes_clicked(self):
        """Gathers data from the 'Edit' form and tells the model to save it."""
        self._save_form_data(self.edit_form_widgets, is_update=True)

    def on_add_new_row_clicked(self):
        """Gathers data from the 'Add' form and tells the model to create a new row."""
        self._save_form_data(self.add_form_widgets, is_update=False)

    def _save_form_data(self, widget_dict: dict, is_update: bool):
        """Generic helper to gather data from a form and call the model."""
        if not self.current_table_name or not widget_dict:
            return

        form_data = {}
        has_non_empty_data = False

        for key, widget in widget_dict.items():
            if isinstance(widget, QComboBox):
                form_data[key] = widget.currentData()
                if widget.currentData() is not None:
                    has_non_empty_data = True
            elif isinstance(widget, QLineEdit):
                form_data[key] = widget.text()
                if widget.text().strip():
                    has_non_empty_data = True
            elif isinstance(widget, QTextEdit):
                form_data[key] = widget.toPlainText()
                if widget.toPlainText().strip():
                    has_non_empty_data = True
            elif hasattr(widget, "isChecked"):  # QCheckBox
                form_data[key] = widget.isChecked()
                has_non_empty_data = True  # Checkbox always has a value

        # For new rows, check if at least one field has meaningful data
        if not is_update and not has_non_empty_data:
            self.view.ui.statusbar.showMessage(
                "Cannot create empty row. Please fill in at least one field.", 5000
            )
            return

        try:
            if is_update:
                # The ID is already in the form_data for updates
                self.model.update_row(self.current_table_name, form_data)

                # Invalidate cache for this entity
                if 'id' in form_data:
                    self.invalidate_entity_cache(self.current_table_name, form_data['id'])

                self.view.ui.statusbar.showMessage(
                    f"Successfully saved changes to '{self.current_table_name}'.", 5000
                )
            else:
                # Pass the current setting ID directly for lorekeeper data
                self.model.add_row(
                    self.current_table_name,
                    form_data,
                    setting_id=self.current_setting_id,
                )
                self.view.ui.statusbar.showMessage(
                    f"Successfully added new row to '{self.current_table_name}'.", 5000
                )
                self.populate_add_form()

            self._refresh_current_table_view()
        except Exception as e:
            print(f"Error saving data: {e}")
            self.view.ui.statusbar.showMessage(f"Error saving data: {e}", 5000)

    def on_lorekeeper_selected(self):
        """Handle switching to the Lorekeeper page."""
        # Hide Storyweaver info cards when leaving
        if hasattr(self, 'storyweaver_widget') and self.storyweaver_widget:
            self.storyweaver_widget.hide_info_cards()

        # Initialize the new Lorekeeper widget if not already done
        if self.new_lorekeeper_widget is None and self.current_setting_id is not None:
            self.new_lorekeeper_widget = NewLorekeeperPage(self.model, self.current_setting_id)

            # Add the widget to the new Lorekeeper page
            if self.view.ui.newLorekeeperPage.layout() is None:
                new_lorekeeper_layout = QVBoxLayout(self.view.ui.newLorekeeperPage)
                new_lorekeeper_layout.setContentsMargins(0, 0, 0, 0)
            else:
                new_lorekeeper_layout = self.view.ui.newLorekeeperPage.layout()
            new_lorekeeper_layout.addWidget(self.new_lorekeeper_widget)

        # Switch to the new Lorekeeper page (index 1 - after litographer)
        if self.new_lorekeeper_widget is not None:
            self.view.ui.pageStack.setCurrentWidget(self.view.ui.newLorekeeperPage)
        else:
            # Fallback: if no widget is initialized, still switch to the lorekeeper page
            self.view.ui.pageStack.setCurrentIndex(1)

        # Update bottom navigation button state
        if hasattr(self.view.ui, 'lorekeeperNavButton') and hasattr(self.view.ui.lorekeeperNavButton, 'setChecked'):
            self.view.ui.lorekeeperNavButton.setChecked(True)

    def on_character_arcs_selected(self):
        """Handle switching to the Character Arcs page."""
        self.view.ui.pageStack.setCurrentIndex(
            2
        )  # Updated index for character arcs page (after removing old lorekeeper)

        # Hide Storyweaver info cards when leaving
        if hasattr(self, 'storyweaver_widget') and self.storyweaver_widget:
            self.storyweaver_widget.hide_info_cards()

        # Only refresh if we have a storyline selected
        if self.current_storyline_id is not None:
            self.character_arc_page.refresh_arcs(self.current_storyline_id)
        else:
            # No storyline selected - show empty state
            pass

    def on_storyweaver_selected(self):
        """Handle switching to the Storyweaver page."""
        self.view.ui.pageStack.setCurrentIndex(3)  # Storyweaver is the 4th tab (index 3)

        # Update project context if storyline/setting changed
        if self.current_storyline_id is not None and self.current_setting_id is not None:
            self.storyweaver_widget.update_project_context(
                self.current_storyline_id,
                self.current_setting_id
            )
            # Preload entities for faster autocomplete
            self.storyweaver_widget.preload_entities()

    def _on_storyweaver_entity_search(self, query: str, storyline_id: int, setting_id: int):
        """
        Handle entity search request from Storyweaver widget.

        Args:
            query: Search query string (empty string for all entities)
            storyline_id: Current storyline ID for filtering
            setting_id: Current setting ID for filtering
        """
        try:
            # Check cache for this setting if no query (full list)
            if not query and setting_id in self._entity_cache:
                # Use cached entities and return immediately
                self.storyweaver_widget.set_entity_list(self._entity_cache[setting_id])
                return

            with Session(self.model.engine) as session:
                entities = []

                # Query Actors (characters)
                actors = session.query(Actor).filter(
                    Actor.setting_id == setting_id
                )
                if query:
                    # Search across first_name, middle_name, and last_name
                    actors = actors.filter(
                        (Actor.first_name.ilike(f"%{query}%")) |
                        (Actor.middle_name.ilike(f"%{query}%")) |
                        (Actor.last_name.ilike(f"%{query}%"))
                    )
                actors = actors.all()

                for actor in actors:
                    # Construct full name from name components
                    name_parts = []
                    if actor.first_name:
                        name_parts.append(actor.first_name)
                    if actor.middle_name:
                        name_parts.append(actor.middle_name)
                    if actor.last_name:
                        name_parts.append(actor.last_name)

                    full_name = " ".join(name_parts) if name_parts else f"Actor {actor.id}"

                    entities.append({
                        "id": f"actor_{actor.id}",
                        "name": full_name,
                        "type": "character"
                    })

                # Query Locations
                from storymaster.model.database.schema.base import Location
                locations = session.query(Location).filter(
                    Location.setting_id == setting_id
                )
                if query:
                    locations = locations.filter(Location.name.ilike(f"%{query}%"))
                locations = locations.all()

                for location in locations:
                    entities.append({
                        "id": f"location_{location.id}",
                        "name": location.name,
                        "type": "location"
                    })

                # Query Factions
                factions = session.query(Faction).filter(
                    Faction.setting_id == setting_id
                )
                if query:
                    factions = factions.filter(Faction.name.ilike(f"%{query}%"))
                factions = factions.all()

                for faction in factions:
                    entities.append({
                        "id": f"faction_{faction.id}",
                        "name": faction.name,
                        "type": "faction"
                    })

                # Sort by name
                entities.sort(key=lambda x: x["name"])

                # Add aliases from the current document if available
                current_doc = self.storyweaver_widget.get_current_document()
                if current_doc:
                    for entity in entities:
                        entity_id = entity["id"]
                        aliases = current_doc.get_aliases(entity_id)
                        if aliases:
                            entity["aliases"] = aliases

                # Cache full entity list (no query) for this setting
                if not query:
                    self._entity_cache[setting_id] = entities

                # Update the Storyweaver widget with the entity list
                self.storyweaver_widget.set_entity_list(entities)

        except Exception as e:
            print(f"[Storyweaver] Error searching entities: {e}")
            self.storyweaver_widget.set_entity_list([])

    def _on_alias_add_requested(self, entity_id: str, entity_name: str, alias: str):
        """
        Handle request to add an alias for an entity.

        Args:
            entity_id: The entity ID
            entity_name: The entity's canonical name
            alias: The alias to add
        """
        try:
            current_doc = self.storyweaver_widget.get_current_document()
            if not current_doc:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self.view, "No Document",
                    "No document is currently open. Aliases are stored per-document."
                )
                return

            # Add the alias to the document
            if current_doc.add_alias(entity_id, alias):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.view, "Alias Added",
                    f"Added alias '{alias}' for {entity_name}"
                )

                # Refresh the entity list to show the new alias
                self._on_storyweaver_entity_search(
                    "",
                    self.storyweaver_widget.current_storyline_id,
                    self.storyweaver_widget.current_setting_id
                )
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.view, "Alias Not Added",
                    f"Alias '{alias}' already exists or is the same as the canonical name."
                )

        except Exception as e:
            print(f"[Storyweaver] Error adding alias: {e}")
            import traceback
            traceback.print_exc()

    def _on_entity_card_clicked(self, entity_id: str, entity_type: str, storyline_id: int = None, setting_id: int = None):
        """
        Handle click on entity name in info card - navigate to Lorekeeper.

        Args:
            entity_id: The entity ID (e.g., "actor_13")
            entity_type: The entity type ("character", "location", "faction")
            storyline_id: The storyline ID (optional, not used)
            setting_id: The setting ID (optional, not used)
        """
        try:
            # Extract numeric ID from entity_id
            numeric_id = int(entity_id.split('_')[1]) if '_' in entity_id else None
            if not numeric_id:
                return

            # Switch to Lorekeeper page
            self.on_lorekeeper_selected()

            # Map entity type to table name for Lorekeeper
            table_map = {
                "character": "actor",
                "location": "location_",
                "faction": "faction"
            }
            table_name = table_map.get(entity_type, entity_type)

            # Navigate to the specific entity in Lorekeeper
            if self.new_lorekeeper_widget:
                self.new_lorekeeper_widget.navigate_to_entity(table_name, numeric_id)
                self.view.ui.statusbar.showMessage(f"Viewing {entity_type}: {entity_id}", 3000)
            else:
                self.view.ui.statusbar.showMessage(f"Lorekeeper not initialized", 3000)

        except Exception as e:
            print(f"[Storyweaver] Error navigating to entity: {e}")
            import traceback
            traceback.print_exc()

    def invalidate_entity_cache(self, table_name: str, entity_id: int):
        """
        Invalidate cached entity details for a specific entity.

        Args:
            table_name: Database table name (e.g., 'actor', 'location', 'faction')
            entity_id: Numeric ID of the entity
        """
        # Map table names to entity types
        table_to_type = {
            'actor': 'character',
            'location': 'location',
            'faction': 'faction'
        }

        entity_type = table_to_type.get(table_name.lower())
        if entity_type:
            cache_key = (entity_type, entity_id)
            if cache_key in self._entity_details_cache:
                del self._entity_details_cache[cache_key]

    def clear_entity_cache(self):
        """Clear all cached entity details."""
        self._entity_details_cache.clear()

    def _on_storyweaver_entity_hover(self, entity_id: str, entity_type: str, storyline_id: int, setting_id: int):
        """
        Handle entity hover request from Storyweaver widget.

        Args:
            entity_id: Entity ID in format "type_id" (e.g., "actor_13")
            entity_type: Entity type (character, location, faction)
            storyline_id: Current storyline ID
            setting_id: Current setting ID
        """
        try:
            # Extract numeric ID from entity_id
            numeric_id = int(entity_id.split('_')[1]) if '_' in entity_id else None
            if not numeric_id:
                return

            # Check cache first
            cache_key = (entity_type, numeric_id)
            if cache_key in self._entity_details_cache:
                entity_name, details = self._entity_details_cache[cache_key]
                if entity_name:
                    self.storyweaver_widget.show_entity_details(entity_name, entity_type, details, entity_id)
                return

            # Cache miss - query database
            with Session(self.model.engine) as session:
                entity_name = ""
                details = ""

                if entity_type == "character":
                    # Fetch Actor details
                    actor = session.query(Actor).filter(Actor.id == numeric_id).first()
                    if actor:
                        # Construct full name
                        name_parts = []
                        if actor.first_name:
                            name_parts.append(actor.first_name)
                        if actor.middle_name:
                            name_parts.append(actor.middle_name)
                        if actor.last_name:
                            name_parts.append(actor.last_name)
                        entity_name = " ".join(name_parts) if name_parts else f"Actor {actor.id}"

                        # Build details string
                        detail_parts = []
                        if actor.title:
                            detail_parts.append(f"Title: {actor.title}")
                        if actor.actor_role:
                            detail_parts.append(f"Role: {actor.actor_role}")
                        if actor.actor_age:
                            detail_parts.append(f"Age: {actor.actor_age}")
                        if actor.job:
                            detail_parts.append(f"Occupation: {actor.job}")
                        if actor.appearance:
                            detail_parts.append(f"\n{actor.appearance[:150]}..." if len(actor.appearance) > 150 else f"\n{actor.appearance}")

                        details = "\n".join(detail_parts) if detail_parts else "No additional details available."

                elif entity_type == "location":
                    # Fetch Location details
                    from storymaster.model.database.schema.base import Location
                    location = session.query(Location).filter(Location.id == numeric_id).first()
                    if location:
                        entity_name = location.name or f"Location {location.id}"

                        # Build details string
                        detail_parts = []
                        if location.location_type:
                            detail_parts.append(f"Type: {location.location_type}")
                        if location.description:
                            detail_parts.append(f"\n{location.description[:150]}..." if len(location.description) > 150 else f"\n{location.description}")

                        details = "\n".join(detail_parts) if detail_parts else "No additional details available."

                elif entity_type == "faction":
                    # Fetch Faction details
                    faction = session.query(Faction).filter(Faction.id == numeric_id).first()
                    if faction:
                        entity_name = faction.name or f"Faction {faction.id}"

                        # Build details string
                        detail_parts = []
                        if faction.description:
                            detail_parts.append(f"{faction.description[:150]}..." if len(faction.description) > 150 else faction.description)
                        if faction.goals:
                            detail_parts.append(f"Goals: {faction.goals[:100]}..." if len(faction.goals) > 100 else f"Goals: {faction.goals}")

                        details = "\n".join(detail_parts) if detail_parts else "No additional details available."

                # Cache the results
                if entity_name:
                    self._entity_details_cache[cache_key] = (entity_name, details)

                # Show the info card
                if entity_name:
                    self.storyweaver_widget.show_entity_details(entity_name, entity_type, details, entity_id)

        except Exception as e:
            print(f"[Storyweaver] Error fetching entity details: {e}")
            import traceback
            traceback.print_exc()

    def load_database_structure(self):
        """Fetches table names from the model and populates the tree view."""
        # DEPRECATED: This method is no longer used with the new Lorekeeper interface
        # Keeping as no-op to avoid breaking existing code that calls it
        pass

    def on_db_tree_item_clicked(self, index):
        """Fetches and displays the content of the selected table when clicked."""
        # DEPRECATED: This method is no longer used with the new Lorekeeper interface
        # Keeping as no-op to avoid breaking existing code that calls it
        pass

    def _refresh_current_table_view(self):
        """Helper method to reload the data in the main table view."""
        # DEPRECATED: This method is no longer used with the new Lorekeeper interface
        # Keeping as no-op to avoid breaking existing code that calls it
        pass

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def get_visible_tables(self) -> set[str] | None:
        """Get the current set of visible tables. None means show all available tables."""
        return self.visible_tables

    def set_visible_tables(self, visible_tables: set[str]):
        """Set which tables should be visible in the Lorekeeper tree view."""
        # DEPRECATED: This method is no longer used with the new Lorekeeper interface
        # Still save preferences for backward compatibility
        self.visible_tables = visible_tables
        self.save_table_visibility_preferences()

    def _clear_form_widgets(self):
        """Clear the form widgets in both edit and add tabs."""
        # DEPRECATED: This method is no longer used with the new Lorekeeper interface
        # Keeping as no-op to avoid breaking existing code that calls it
        pass

    def save_table_visibility_preferences(self):
        """Save table visibility preferences to a file."""
        try:
            import json
            from pathlib import Path

            # Use the same directory as the database
            config_dir = Path.home() / ".local" / "share" / "storymaster"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "table_visibility.json"

            # Prepare data to save
            data = {"visible_tables": (list(self.visible_tables) if self.visible_tables else None)}

            with open(config_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            pass  # Could not save table visibility preferences

    def load_table_visibility_preferences(self):
        """Load table visibility preferences from file."""
        try:
            import json
            from pathlib import Path

            config_file = Path.home() / ".local" / "share" / "storymaster" / "table_visibility.json"

            if config_file.exists():
                with open(config_file, "r") as f:
                    data = json.load(f)

                visible_tables = data.get("visible_tables")
                if visible_tables:
                    self.visible_tables = set(visible_tables)

        except Exception as e:
            # Continue with default behavior (show all tables)
            pass

    def on_about_clicked(self):
        """Handle showing the About dialog."""
        from storymaster.view.common.about_dialog import AboutDialog

        dialog = AboutDialog(self.view)
        dialog.exec()

    def cleanup(self):
        """Clean up resources before shutdown."""
        if hasattr(self, "backup_manager") and self.backup_manager:
            self.backup_manager.stop_automatic_backups()

        if hasattr(self, "storyweaver_widget") and self.storyweaver_widget:
            self.storyweaver_widget.cleanup()
