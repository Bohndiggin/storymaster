"""Holds the controller for the main page"""

from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainterPath,
    QPen,
    QPolygonF,
    QStandardItem,
    QStandardItemModel,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
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
    NodeType,
    Object_,
    PlotSectionType,
    Race,
    Skills,
    SubRace,
    WorldData,
)
from storymaster.view.common.common_view import MainView
from storymaster.view.common.database_manager_dialog import DatabaseManagerDialog
from storymaster.view.common.new_setting_dialog import NewSettingDialog
from storymaster.view.common.new_storyline_dialog import NewStorylineDialog
from storymaster.view.common.open_storyline_dialog import OpenStorylineDialog
from storymaster.view.common.plot_manager_dialog import PlotManagerDialog
from storymaster.view.common.setting_switcher_dialog import SettingSwitcherDialog
from storymaster.view.common.storyline_switcher_dialog import StorylineSwitcherDialog

# Import the dialogs
from storymaster.view.litographer.add_node_dialog import AddNodeDialog
from storymaster.view.litographer.node_notes_dialog import NodeNotesDialog


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


class RectangleNodeItem(QGraphicsRectItem):
    """Rectangle node for EXPOSITION"""

    def __init__(self, x, y, width, height, node_data, controller):
        super().__init__(x, y, width, height)
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class CircleNodeItem(QGraphicsEllipseItem):
    """Circle node for REACTION"""

    def __init__(self, x, y, width, height, node_data, controller):
        super().__init__(x, y, width, height)
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class DiamondNodeItem(QGraphicsPolygonItem):
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
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class StarNodeItem(QGraphicsPolygonItem):
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
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class HexagonNodeItem(QGraphicsPolygonItem):
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
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.on_node_context_menu(self.node_data, event.screenPos())
        else:
            super().mousePressEvent(event)
            self.controller.on_node_clicked(self.node_data)


class TriangleNodeItem(QGraphicsPolygonItem):
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
        self.node_data = node_data
        self.controller = controller
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)

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
                section = (
                    session.query(LitographyPlotSection)
                    .filter_by(id=self.section_id)
                    .first()
                )
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
                section = (
                    session.query(LitographyPlotSection)
                    .filter_by(id=self.section_id)
                    .first()
                )
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
        self.controller.on_add_node_button_clicked(
            self.position_type, self.reference_node_id
        )

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
        self.current_storyline_id = 1  # Default to storyline 1
        self.current_setting_id = 1  # Default to setting 1
        self.current_table_name = None
        self.current_row_data = None
        self.current_foreign_keys = {}
        self.edit_form_widgets = {}
        self.add_form_widgets = {}

        # --- Set up Lorekeeper models ---
        self.db_tree_model = QStandardItemModel()
        self.view.ui.databaseTreeView.setModel(self.db_tree_model)
        self.db_table_model = QStandardItemModel()
        self.view.ui.databaseTableView.setModel(self.db_table_model)

        # --- Set up Litographer scene ---
        self.node_scene = QGraphicsScene()
        self.view.ui.nodeGraphView.setScene(self.node_scene)

        # Enable context menu on graphics view
        self.view.ui.nodeGraphView.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
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

        database_path = os.getenv(
            "DATABASE_CONNECTION", "sqlite:///storymaster.db"
        ).replace("sqlite:///", "")
        self.backup_manager = BackupManager(database_path)

        # Connect backup signals
        self.backup_manager.backup_created.connect(self.on_backup_created)
        self.backup_manager.backup_failed.connect(self.on_backup_failed)

        # Start automatic backups
        self.backup_manager.start_automatic_backups()

        self.connect_signals()
        self.on_litographer_selected()  # Start on the litographer page
        self.update_status_indicators()  # Initialize status indicators

    def validate_ui_database_sync(self):
        """Check if UI and database are in sync and force refresh if not"""
        try:
            # Get current database state
            db_nodes = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )
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
                "background-color: #1e1e1e; border-left: 1px solid #424242;"
            )

            panel_layout = QVBoxLayout(self.node_panel)

            # Node info section
            node_info_group = QGroupBox("Node Information")
            node_info_layout = QFormLayout(node_info_group)

            self.node_id_label = QLabel("None")
            self.node_type_combo = QComboBox()
            self.node_height_spin = QDoubleSpinBox()
            self.node_height_spin.setRange(0.0, 1.0)
            self.node_height_spin.setSingleStep(0.1)
            self.node_height_spin.setDecimals(2)

            node_info_layout.addRow("Node ID:", self.node_id_label)
            node_info_layout.addRow("Node Type:", self.node_type_combo)
            node_info_layout.addRow("Height (Tension):", self.node_height_spin)

            # Connections section
            connections_group = QGroupBox("Connections")
            connections_layout = QFormLayout(connections_group)

            self.previous_node_combo = QComboBox()
            self.next_node_combo = QComboBox()
            self.section_combo = QComboBox()

            connections_layout.addRow("Previous Node:", self.previous_node_combo)
            connections_layout.addRow("Next Node:", self.next_node_combo)
            connections_layout.addRow("Plot Section:", self.section_combo)

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

            # Buttons
            button_layout = QHBoxLayout()
            self.save_node_btn = QPushButton("Save Changes")
            self.delete_node_btn = QPushButton("Delete Node")
            self.delete_node_btn.setStyleSheet(
                "QPushButton { background-color: #8B0000; }"
            )

            button_layout.addWidget(self.save_node_btn)
            button_layout.addWidget(self.delete_node_btn)

            # Add to panel
            panel_layout.addWidget(node_info_group)
            panel_layout.addWidget(connections_group)
            panel_layout.addWidget(notes_group)
            panel_layout.addLayout(button_layout)
            panel_layout.addStretch()

            # Add to splitter
            splitter.addWidget(graph_container)
            splitter.addWidget(self.node_panel)
            splitter.setSizes([800, 300])  # Initial sizes

            # Add the splitter to the existing layout
            current_layout.addWidget(splitter)

            # Connect signals
            self.save_node_btn.clicked.connect(self.on_save_node_changes)
            self.delete_node_btn.clicked.connect(self.on_delete_node)

            # Initially hide the panel
            self.node_panel.hide()

    def setup_plot_section_selector(self, parent_layout):
        """Create the plot section selector UI at the top"""
        # Section selector container
        section_container = QWidget()
        section_container.setFixedHeight(60)
        section_container.setStyleSheet(
            "background-color: #1a1a1a; border-bottom: 1px solid #424242;"
        )

        section_layout = QHBoxLayout(section_container)
        section_layout.setContentsMargins(10, 10, 10, 10)

        # Label
        section_label = QLabel("Plot Sections:")
        section_label.setStyleSheet("color: #dcdcdc; font-weight: bold;")
        section_layout.addWidget(section_label)

        # Tab widget for sections
        self.section_tabs = QTabWidget()
        self.section_tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #424242;
                background-color: #2e2e2e;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #dcdcdc;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5c4a8e;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
        """
        )
        self.section_tabs.currentChanged.connect(self.on_section_changed)

        # Enable context menu on tabs
        self.section_tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.section_tabs.customContextMenuRequested.connect(
            self.on_section_context_menu
        )

        section_layout.addWidget(self.section_tabs)

        # Add section button
        add_section_btn = QPushButton("+ Add Section")
        add_section_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """
        )
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

                self.view.ui.statusbar.showMessage(
                    f"Added new plot section {new_section.id}", 3000
                )
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
            dialog = SectionEditDialog(
                self.view, section_id, self.model, self.current_plot_id
            )
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
                    section = (
                        session.query(LitographyPlotSection)
                        .filter_by(id=section_id)
                        .first()
                    )
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
        # Populate node type combo
        self.node_type_combo.clear()
        for node_type in NodeType:
            self.node_type_combo.addItem(node_type.value, node_type)

        # Set current values
        self.node_id_label.setText(str(node_data.id))
        self.node_type_combo.setCurrentText(node_data.node_type.value)
        self.node_height_spin.setValue(node_data.node_height)

        # Populate connection combos
        self.populate_connection_combos(node_data)

        # Populate section combo
        self.populate_section_combo(node_data)

        # Load notes for this node
        self.load_notes_for_node(node_data.id)

    def populate_connection_combos(self, current_node):
        """Populate the previous/next node combo boxes"""
        # Get all nodes for this project
        all_nodes = self.model.get_litography_nodes(
            storyline_id=self.current_storyline_id
        )

        # Clear combos
        self.previous_node_combo.clear()
        self.next_node_combo.clear()

        # Add "None" option
        self.previous_node_combo.addItem("None", None)
        self.next_node_combo.addItem("None", None)

        # Add all other nodes
        for node in all_nodes:
            if node.id != current_node.id:  # Don't include self
                display_text = f"Node {node.id} ({node.node_type.value})"
                self.previous_node_combo.addItem(display_text, node.id)
                self.next_node_combo.addItem(display_text, node.id)

        # Set current selections
        if current_node.previous_node:
            for i in range(self.previous_node_combo.count()):
                if self.previous_node_combo.itemData(i) == current_node.previous_node:
                    self.previous_node_combo.setCurrentIndex(i)
                    break

        if current_node.next_node:
            for i in range(self.next_node_combo.count()):
                if self.next_node_combo.itemData(i) == current_node.next_node:
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
                    display_text = (
                        f"Section {section.id} ({section.plot_section_type.value})"
                    )
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

    def on_save_node_changes(self):
        """Save changes to the selected node"""
        if not self.selected_node:
            return

        try:
            # Get values from the form
            new_type = self.node_type_combo.currentData()
            new_height = self.node_height_spin.value()
            new_previous = self.previous_node_combo.currentData()
            new_next = self.next_node_combo.currentData()
            # Get section ID from combo index
            section_index = self.section_combo.currentIndex()
            new_section = (
                self.section_combo_sections[section_index].id
                if section_index >= 0
                and hasattr(self, "section_combo_sections")
                and section_index < len(self.section_combo_sections)
                else None
            )

            # Update the node
            update_data = {
                "id": self.selected_node.id,
                "node_type": new_type.value if new_type else None,
                "node_height": new_height,
                "previous_node": new_previous,
                "next_node": new_next,
                "storyline_id": self.current_storyline_id,
            }

            self.model.update_row("litography_node", update_data)

            # Handle section change if needed
            if new_section:
                self.move_node_to_section(self.selected_node.id, new_section)

            self.view.ui.statusbar.showMessage("Node updated successfully", 3000)

            # Refresh the graph
            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error updating node: {e}")
            self.view.ui.statusbar.showMessage(f"Error updating node: {e}", 5000)

    def on_delete_node(self):
        """Delete the selected node"""
        if not self.selected_node:
            return

        try:
            # Delete the node and its notes using SQLAlchemy directly since BaseModel doesn't have delete_row

            with Session(self.model.engine) as session:
                # First delete all notes associated with this node
                notes_to_delete = (
                    session.query(LitographyNotes)
                    .filter_by(
                        linked_node_id=self.selected_node.id,
                        storyline_id=self.current_storyline_id,
                    )
                    .all()
                )

                for note in notes_to_delete:
                    session.delete(note)

                # Then find and delete the node
                node_to_delete = (
                    session.query(LitographyNode)
                    .filter_by(
                        id=self.selected_node.id, storyline_id=self.current_storyline_id
                    )
                    .first()
                )

                if node_to_delete:
                    session.delete(node_to_delete)
                    session.commit()
                    self.view.ui.statusbar.showMessage(
                        "Node and associated notes deleted successfully", 3000
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
        """Handle clicking '+' button to add a connected node"""
        try:
            # First validate UI and database are in sync
            self.validate_ui_database_sync()

            # Import the NodeType enum

            # Create new node data with default values
            new_node_data = {
                "node_type": NodeType.OTHER.value,  # Use the enum value
                "node_height": 0.5,
                "storyline_id": self.current_storyline_id,
                "previous_node": None,
                "next_node": None,
            }

            # Handle starting the first node
            if position_type == "start":
                # Just add a standalone node
                self.model.add_row("litography_node", new_node_data)

                # Get the newly created node and add to current section
                if self.current_plot_section_id:
                    all_nodes_after = self.model.get_litography_nodes(
                        storyline_id=self.current_storyline_id
                    )
                    new_node = max(all_nodes_after, key=lambda n: n.id)
                    self.add_node_to_section(new_node.id, self.current_plot_section_id)

                self.view.ui.statusbar.showMessage("Added first node", 3000)
                self.load_and_draw_nodes()
                return

            if position_type == "before" and reference_node_id:
                # Find the reference node
                all_nodes = self.model.get_litography_nodes(
                    storyline_id=self.current_storyline_id
                )
                reference_node = next(
                    (n for n in all_nodes if n.id == reference_node_id), None
                )

                if not reference_node:
                    self.view.ui.statusbar.showMessage(
                        "Reference node no longer exists", 3000
                    )
                    self.load_and_draw_nodes()
                    return

                if reference_node:
                    # Set connections: new_node -> reference_node
                    new_node_data["next_node"] = reference_node_id
                    if reference_node.previous_node:
                        new_node_data["previous_node"] = reference_node.previous_node
                        # Update the old previous node to point to new node
                        old_previous_data = {
                            "id": reference_node.previous_node,
                            "next_node": None,  # Will be set after we create the new node
                            "storyline_id": self.current_storyline_id,
                        }

            elif position_type == "after" and reference_node_id:
                # Find the reference node
                all_nodes = self.model.get_litography_nodes(
                    storyline_id=self.current_storyline_id
                )
                reference_node = next(
                    (n for n in all_nodes if n.id == reference_node_id), None
                )

                if not reference_node:
                    self.view.ui.statusbar.showMessage(
                        "Reference node no longer exists", 3000
                    )
                    self.load_and_draw_nodes()
                    return

                if reference_node:
                    # Set connections: reference_node -> new_node
                    new_node_data["previous_node"] = reference_node_id
                    if reference_node.next_node:
                        new_node_data["next_node"] = reference_node.next_node

            # Add the new node to database
            self.model.add_row("litography_node", new_node_data)

            # Get the newly created node to get its ID
            all_nodes_after = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )
            new_node = max(
                all_nodes_after, key=lambda n: n.id
            )  # Get the node with highest ID (newest)

            # Add to current section if we have one
            if self.current_plot_section_id:
                self.add_node_to_section(new_node.id, self.current_plot_section_id)

            # Update connections in existing nodes
            if position_type == "before" and reference_node_id:
                # Update reference node to point back to new node
                reference_update = {
                    "id": reference_node_id,
                    "previous_node": new_node.id,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", reference_update)

                # Update old previous node if it exists
                if reference_node and reference_node.previous_node:
                    old_previous_update = {
                        "id": reference_node.previous_node,
                        "next_node": new_node.id,
                        "storyline_id": self.current_storyline_id,
                    }
                    self.model.update_row("litography_node", old_previous_update)

            elif position_type == "after" and reference_node_id:
                # Update reference node to point to new node
                reference_update = {
                    "id": reference_node_id,
                    "next_node": new_node.id,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", reference_update)

                # Update old next node if it exists
                if reference_node and reference_node.next_node:
                    old_next_update = {
                        "id": reference_node.next_node,
                        "previous_node": new_node.id,
                        "storyline_id": self.current_storyline_id,
                    }
                    self.model.update_row("litography_node", old_next_update)

            self.view.ui.statusbar.showMessage(
                f"Added new node {position_type} existing node", 3000
            )
            self.load_and_draw_nodes()

        except Exception as e:
            print(f"Error adding connected node: {e}")
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
        delete_action.triggered.connect(
            lambda: self.on_delete_node_button_clicked(node_data.id)
        )

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
        """Update status bar to show current storyline and setting"""
        try:
            # Get current storyline name
            storylines = self.model.get_all_storylines()
            storyline_name = next(
                (s.name for s in storylines if s.id == self.current_storyline_id),
                "Unknown",
            )

            # Get current setting name
            settings = self.model.get_all_settings()
            setting_name = next(
                (s.name for s in settings if s.id == self.current_setting_id), "Unknown"
            )

            # Update status bar
            status_text = f"Storyline: {storyline_name} | Setting: {setting_name}"
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
                    .filter_by(
                        linked_node_id=node_id, storyline_id=self.current_storyline_id
                    )
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
                    self.view.ui.statusbar.showMessage(
                        "Note updated successfully", 3000
                    )
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
                    self.view.ui.statusbar.showMessage(
                        "Note deleted successfully", 3000
                    )
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
                    .filter_by(
                        linked_node_id=node_id, storyline_id=self.current_storyline_id
                    )
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
                backgrounds = (
                    session.query(Background).filter_by(setting_id=setting_id).all()
                )
                classes = session.query(Class_).filter_by(setting_id=setting_id).all()
                factions = session.query(Faction).filter_by(setting_id=setting_id).all()
                histories = (
                    session.query(History).filter_by(setting_id=setting_id).all()
                )
                locations = (
                    session.query(Location).filter_by(setting_id=setting_id).all()
                )
                objects = session.query(Object_).filter_by(setting_id=setting_id).all()
                races = session.query(Race).filter_by(setting_id=setting_id).all()
                skills = session.query(Skills).filter_by(setting_id=setting_id).all()
                sub_races = (
                    session.query(SubRace).filter_by(setting_id=setting_id).all()
                )
                world_data = (
                    session.query(WorldData).filter_by(setting_id=setting_id).all()
                )

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
                    session.query(LitographyNoteToActor)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["backgrounds"] = (
                    session.query(LitographyNoteToBackground)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["classes"] = (
                    session.query(LitographyNoteToClass)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["factions"] = (
                    session.query(LitographyNoteToFaction)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["histories"] = (
                    session.query(LitographyNoteToHistory)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["locations"] = (
                    session.query(LitographyNoteToLocation)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["objects"] = (
                    session.query(LitographyNoteToObject)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["races"] = (
                    session.query(LitographyNoteToRace).filter_by(note_id=note_id).all()
                )
                associations["skills"] = (
                    session.query(LitographyNoteToSkills)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["sub_races"] = (
                    session.query(LitographyNoteToSubRace)
                    .filter_by(note_id=note_id)
                    .all()
                )
                associations["world_data"] = (
                    session.query(LitographyNoteToWorldData)
                    .filter_by(note_id=note_id)
                    .all()
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
                    association = LitographyNoteToActor(
                        note_id=note_id, actor_id=entity_id
                    )
                elif entity_type == "background":
                    association = LitographyNoteToBackground(
                        note_id=note_id, background_id=entity_id
                    )
                elif entity_type == "class":
                    association = LitographyNoteToClass(
                        note_id=note_id, class_id=entity_id
                    )
                elif entity_type == "faction":
                    association = LitographyNoteToFaction(
                        note_id=note_id, faction_id=entity_id
                    )
                elif entity_type == "history":
                    association = LitographyNoteToHistory(
                        note_id=note_id, history_id=entity_id
                    )
                elif entity_type == "location":
                    association = LitographyNoteToLocation(
                        note_id=note_id, location_id=entity_id
                    )
                elif entity_type == "object":
                    association = LitographyNoteToObject(
                        note_id=note_id, object_id=entity_id
                    )
                elif entity_type == "race":
                    association = LitographyNoteToRace(
                        note_id=note_id, race_id=entity_id
                    )
                elif entity_type == "skill":
                    association = LitographyNoteToSkills(
                        note_id=note_id, skill_id=entity_id
                    )
                elif entity_type == "sub_race":
                    association = LitographyNoteToSubRace(
                        note_id=note_id, sub_race_id=entity_id
                    )
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
            all_db_nodes = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )
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
            all_nodes = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )
            node_to_delete = next((n for n in all_nodes if n.id == node_id), None)

            if not node_to_delete:
                self.view.ui.statusbar.showMessage(
                    "Node not found in current data", 3000
                )
                self.load_and_draw_nodes()
                return

            # Update connections: connect previous and next nodes directly
            # First verify that the connected nodes actually exist
            all_current_nodes = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )
            existing_node_ids = {n.id for n in all_current_nodes}

            # Only update connections if the referenced nodes actually exist
            if (
                node_to_delete.previous_node
                and node_to_delete.previous_node in existing_node_ids
                and node_to_delete.next_node
                and node_to_delete.next_node in existing_node_ids
            ):
                # Connect previous -> next (bypass the deleted node)
                previous_update = {
                    "id": node_to_delete.previous_node,
                    "next_node": node_to_delete.next_node,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", previous_update)

                next_update = {
                    "id": node_to_delete.next_node,
                    "previous_node": node_to_delete.previous_node,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", next_update)

            elif (
                node_to_delete.previous_node
                and node_to_delete.previous_node in existing_node_ids
            ):
                # Only has valid previous node - disconnect it
                previous_update = {
                    "id": node_to_delete.previous_node,
                    "next_node": None,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", previous_update)

            elif (
                node_to_delete.next_node
                and node_to_delete.next_node in existing_node_ids
            ):
                # Only has valid next node - disconnect it
                next_update = {
                    "id": node_to_delete.next_node,
                    "previous_node": None,
                    "storyline_id": self.current_storyline_id,
                }
                self.model.update_row("litography_node", next_update)
            else:
                pass  # No valid connections to update

            # Delete the node and its associated notes from database

            with Session(self.model.engine) as session:
                # First delete all notes associated with this node
                notes_to_delete = (
                    session.query(LitographyNotes)
                    .filter_by(
                        linked_node_id=node_id, storyline_id=self.current_storyline_id
                    )
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
                        "Node and associated notes deleted successfully", 3000
                    )
                else:
                    self.view.ui.statusbar.showMessage(
                        "Node not found in database", 3000
                    )
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
        self.view.ui.lorekeeperNavButton.released.connect(self.on_lorekeeper_selected)

        # --- File Menu ---
        self.view.ui.actionOpen.triggered.connect(self.on_open_storyline_clicked)
        self.view.ui.actionDatabaseManager.triggered.connect(
            self.on_database_manager_clicked
        )
        self.view.ui.actionCreateBackup.triggered.connect(self.on_create_backup_clicked)

        # --- Storyline Menu ---
        self.view.ui.actionNewStoryline.triggered.connect(self.on_new_storyline_clicked)
        self.view.ui.actionSwitchStoryline.triggered.connect(
            self.on_switch_storyline_clicked
        )

        # --- Setting Menu ---
        self.view.ui.actionNewSetting.triggered.connect(self.on_new_setting_clicked)
        self.view.ui.actionSwitchSetting.triggered.connect(
            self.on_switch_setting_clicked
        )

        # --- Plot Actions (context menu only now) ---
        self.view.ui.actionNewPlot.triggered.connect(self.on_new_plot_clicked)
        self.view.ui.actionSwitchPlot.triggered.connect(self.on_switch_plot_clicked)
        self.view.ui.actionDeletePlot.triggered.connect(self.on_delete_plot_clicked)

        # --- Litographer Toolbar ---
        self.view.ui.actionAddNode.triggered.connect(self.on_add_node_clicked)

        # --- Lorekeeper View Signals ---
        self.view.ui.databaseTreeView.clicked.connect(self.on_db_tree_item_clicked)
        self.view.ui.databaseTableView.clicked.connect(self.on_table_row_clicked)

        # --- Lorekeeper Form Buttons ---
        self.view.ui.saveChangesButton.clicked.connect(self.on_save_changes_clicked)
        self.view.ui.addNewRowButton.clicked.connect(self.on_add_new_row_clicked)
        self.view.ui.formTabWidget.currentChanged.connect(self.on_tab_changed)

    # --- Project Handling ---
    def on_open_storyline_clicked(self):
        """Opens a dialog to select a storyline."""
        dialog = OpenStorylineDialog(self.model, self.view)
        storyline_id = dialog.get_selected_storyline_id()
        if storyline_id is not None:
            self.current_storyline_id = storyline_id
            print(f"Switched to Storyline ID: {self.current_storyline_id}")
            self.view.ui.statusbar.showMessage(
                f"Opened Storyline ID: {self.current_storyline_id}", 5000
            )

            # Refresh the current view with the new project's data
            if self.view.ui.pageStack.currentIndex() == 0:
                self.load_and_draw_nodes()
            else:
                self._refresh_current_table_view()

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

    def on_new_storyline_clicked(self):
        """Opens a dialog to create a new storyline."""
        dialog = NewStorylineDialog(self.model, self.view)
        storyline_data = dialog.get_storyline_data()
        if storyline_data is not None:
            try:
                self.model.add_row("storyline", storyline_data)
                self.view.ui.statusbar.showMessage(
                    f"Created new storyline: {storyline_data['name']}", 5000
                )
                print(f"Created new storyline: {storyline_data['name']}")
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
            try:
                self.model.add_row("setting", setting_data)
                self.view.ui.statusbar.showMessage(
                    f"Created new setting: {setting_data['name']}", 5000
                )
                print(f"Created new setting: {setting_data['name']}")
            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Error Creating Setting",
                    f"Failed to create setting: {str(e)}",
                )

    def on_switch_storyline_clicked(self):
        """Opens a dialog to switch between storylines."""
        dialog = StorylineSwitcherDialog(
            self.model, self.current_storyline_id, self.view
        )
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

                    self.view.ui.statusbar.showMessage(
                        f"Switched to storyline: {storyline_name}", 5000
                    )
                    # TODO: Refresh views to show new storyline data
                    self.load_and_draw_nodes()
                    self.update_status_indicators()
                    print(f"Switched to storyline: {storyline_name}")
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Error Switching Storyline",
                        f"Failed to switch storyline: {str(e)}",
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

                    self.view.ui.statusbar.showMessage(
                        f"Switched to setting: {setting_name}", 5000
                    )
                    # TODO: Refresh lorekeeper views to show new setting data
                    if self.db_tree_model.rowCount() > 0:
                        self.load_database_structure()
                    self.update_status_indicators()
                    print(f"Switched to setting: {setting_name}")
                except Exception as e:
                    QMessageBox.critical(
                        self.view,
                        "Error Switching Setting",
                        f"Failed to switch setting: {str(e)}",
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

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(
                    dialog, "action"
                ):
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

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(
                    dialog, "action"
                ):
                    if dialog.action == "switch" and dialog.selected_plot_id:
                        self.current_plot_id = dialog.selected_plot_id

                        plot = session.query(LitographyPlot).get(self.current_plot_id)
                        plot_name = (
                            plot.title if plot else f"Plot {self.current_plot_id}"
                        )

                        self.view.ui.statusbar.showMessage(
                            f"Switched to plot: {plot_name}", 5000
                        )

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

                if dialog.exec() == QDialog.DialogCode.Accepted and hasattr(
                    dialog, "action"
                ):
                    if dialog.action == "delete" and dialog.selected_plot_id:
                        plot_to_delete = session.query(LitographyPlot).get(
                            dialog.selected_plot_id
                        )
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

                        self.view.ui.statusbar.showMessage(
                            f"Deleted plot: {plot_name}", 5000
                        )

        except Exception as e:
            print(f"Error deleting plot: {e}")
            self.view.ui.statusbar.showMessage(f"Error deleting plot: {e}", 5000)

    # --- Litographer Methods ---

    def on_litographer_selected(self):
        """Handle switching to the Litographer page and loading nodes."""
        self.view.ui.pageStack.setCurrentIndex(0)
        self.load_plot_sections()
        self.load_and_draw_nodes()

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
                    section_name = (
                        f"Section {section.id} ({section.plot_section_type.value})"
                    )
                    tab_index = self.section_tabs.addTab(QWidget(), section_name)
                    self.section_tab_ids.append(
                        section.id
                    )  # Store section ID at tab index

                # Select first section by default
                if sections and self.current_plot_section_id is None:
                    self.current_plot_section_id = sections[0].id
                    self.section_tabs.setCurrentIndex(0)
                elif self.current_plot_section_id:
                    # Find and select the current section
                    try:
                        section_index = self.section_tab_ids.index(
                            self.current_plot_section_id
                        )
                        self.section_tabs.setCurrentIndex(section_index)
                    except ValueError:
                        # Section not found, default to first
                        if self.section_tab_ids:
                            self.current_plot_section_id = self.section_tab_ids[0]
                            self.section_tabs.setCurrentIndex(0)

        except Exception as e:
            print(f"Error loading plot sections: {e}")
            self.view.ui.statusbar.showMessage(f"Error loading sections: {e}", 5000)

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
                        LitographyNodeToPlotSection.litography_plot_section_id
                        == section_id,
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
                    print(
                        f"Failed to verify link between node {node_id} and section {section_id}"
                    )
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
                    session.query(LitographyNodeToPlotSection)
                    .filter_by(node_id=node_id)
                    .all()
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

    def on_add_node_clicked(self):
        """Handles the 'Add Node' action by opening a dialog."""
        dialog = AddNodeDialog(self.view)
        new_node_data = dialog.get_data()

        if new_node_data:
            new_node_data["storyline_id"] = self.current_storyline_id

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
        """Fetches node data from the model and draws them on the scene in linked list order."""
        self.node_scene.clear()

        # Get nodes filtered by current plot section
        if self.current_plot_section_id:
            all_nodes = self.get_nodes_in_section(self.current_plot_section_id)
        else:
            all_nodes = self.model.get_litography_nodes(
                storyline_id=self.current_storyline_id
            )

        node_ids = [n.id for n in all_nodes] if all_nodes else []

        if not all_nodes:
            # No nodes exist - add a single "+" button to start the first chain
            start_button = AddNodeButton(100, 100, self, "start", None)
            self.node_scene.addItem(start_button)
            return

        # Order nodes by following the linked list structure
        ordered_nodes = self.order_nodes_by_links(all_nodes)

        # Create a mapping of node ID to position for connection drawing
        node_positions = {}

        # Define colors for different node types
        node_colors = {
            "EXPOSITION": "#FFD700",  # Gold
            "ACTION": "#FF6B6B",  # Red
            "REACTION": "#4ECDC4",  # Teal
            "TWIST": "#FF8C42",  # Orange
            "DEVELOPMENT": "#45B7D1",  # Blue
            "OTHER": "#5c4a8e",  # Purple (default)
        }

        x_pos = 50  # Start with some padding for the first "+" button

        for i, node in enumerate(ordered_nodes):
            y_pos = self.view.ui.nodeGraphView.height() - (node.node_height * 200) - 100

            # Add "+" button before the node (except for the very first node)
            if i == 0:
                # Add "+" button at the very beginning for the first node (centered vertically with node)
                before_button = AddNodeButton(
                    x_pos - 35, y_pos + 27.5, self, "before", node.id
                )  # (80-25)/2 = 27.5
                self.node_scene.addItem(before_button)

            # Add small delete "-" button on the top-right of the node
            delete_button = DeleteNodeButton(
                x_pos + 60, y_pos - 10, self, node.id
            )  # Top-right corner
            self.node_scene.addItem(delete_button)

            # Get color based on node type
            node_color = node_colors.get(node.node_type.name, node_colors["OTHER"])

            # Create the appropriate shape based on node type - make it more square
            node_item = create_node_item(
                x_pos, y_pos, 80, 80, node, self
            )  # Changed to 80x80 for square
            node_item.setBrush(QBrush(QColor(node_color)))
            node_item.setPen(QPen(QColor("#333333"), 2))
            self.node_scene.addItem(node_item)

            # Add note indicator if node has notes
            if self.node_has_notes(node.id):
                note_indicator = QGraphicsTextItem("📝")
                note_indicator.setPos(
                    x_pos + 45, y_pos - 5
                )  # Top-center, avoiding delete button
                note_indicator.setFont(QFont("Arial", 12))
                self.node_scene.addItem(note_indicator)

            # Store position for connection drawing
            center_x = x_pos + 40  # Center of the square (80/2)
            center_y = y_pos + 40
            node_positions[node.id] = (center_x, center_y)

            # Add "+" button after each node (centered vertically with node)
            after_button = AddNodeButton(
                x_pos + 90, y_pos + 27.5, self, "after", node.id
            )  # (80-25)/2 = 27.5
            self.node_scene.addItem(after_button)

            x_pos += 140  # Adjusted spacing for new layout

        # Draw connections between nodes
        for node in ordered_nodes:
            if node.next_node and node.next_node in node_positions:
                # Draw line from current node to next node
                start_pos = node_positions[node.id]
                end_pos = node_positions[node.next_node]

                # Create connection line
                line_item = QGraphicsLineItem(
                    start_pos[0], start_pos[1], end_pos[0], end_pos[1]
                )
                line_item.setPen(QPen(QColor("#FFFFFF"), 3))
                self.node_scene.addItem(line_item)

                # Add an arrowhead to show direction
                arrow_size = 10
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]

                if dx != 0 or dy != 0:
                    # Calculate arrow points
                    import math

                    angle = math.atan2(dy, dx)
                    arrow_x = end_pos[0] - arrow_size * math.cos(angle)
                    arrow_y = end_pos[1] - arrow_size * math.sin(angle)

                    # Create small triangle for arrow
                    arrow_offset = arrow_size * 0.3
                    arrow_p1_x = arrow_x + arrow_offset * math.cos(angle + math.pi / 2)
                    arrow_p1_y = arrow_y + arrow_offset * math.sin(angle + math.pi / 2)
                    arrow_p2_x = arrow_x + arrow_offset * math.cos(angle - math.pi / 2)
                    arrow_p2_y = arrow_y + arrow_offset * math.sin(angle - math.pi / 2)

                    # Draw arrow lines
                    arrow_line1 = QGraphicsLineItem(
                        end_pos[0], end_pos[1], arrow_p1_x, arrow_p1_y
                    )
                    arrow_line2 = QGraphicsLineItem(
                        end_pos[0], end_pos[1], arrow_p2_x, arrow_p2_y
                    )
                    arrow_line1.setPen(QPen(QColor("#FFFFFF"), 2))
                    arrow_line2.setPen(QPen(QColor("#FFFFFF"), 2))
                    self.node_scene.addItem(arrow_line1)
                    self.node_scene.addItem(arrow_line2)

    def order_nodes_by_links(self, nodes):
        """Order nodes by following the linked list structure from head to tail."""
        if not nodes:
            return []

        # Create a lookup dictionary for quick access
        node_dict = {node.id: node for node in nodes}

        # Find all head nodes (nodes with no previous_node)
        head_nodes = [node for node in nodes if node.previous_node is None]

        ordered_nodes = []
        processed_nodes = set()

        # Process each chain starting from head nodes
        for head_node in head_nodes:
            current = head_node
            chain = []

            # Follow the chain from head to tail
            while current and current.id not in processed_nodes:
                chain.append(current)
                processed_nodes.add(current.id)

                # Move to next node
                if current.next_node and current.next_node in node_dict:
                    current = node_dict[current.next_node]
                else:
                    current = None

            ordered_nodes.extend(chain)

        # Add any remaining nodes that aren't in chains (isolated nodes)
        for node in nodes:
            if node.id not in processed_nodes:
                ordered_nodes.append(node)

        return ordered_nodes

    # --- Lorekeeper Methods ---

    def on_tab_changed(self, index: int):
        """Handle tab switching to populate the 'Add New Row' form when selected."""
        if index == 1:
            self.populate_add_form()

    def on_table_row_clicked(self, index):
        """Populates the edit form with the data from the selected row."""
        first_item_in_row = self.db_table_model.item(index.row(), 0)
        if not first_item_in_row:
            return

        self.current_row_data = first_item_in_row.data(Qt.ItemDataRole.UserRole)

        if self.current_row_data:
            self._populate_form(
                self.view.ui.editFormLayout,
                self.edit_form_widgets,
                self.current_row_data,
            )
            self.view.ui.formTabWidget.setCurrentIndex(0)

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
            if is_add_form and key.lower() in ["id", "setting_id", "storyline_id"]:
                continue

            label = QLabel(f"{key.replace('_', ' ').title()}:")

            if key in self.current_foreign_keys:
                field = self._create_dropdown(key, value)
            else:
                field = self._create_text_field(value)

            if key.lower() == "id":
                field.setReadOnly(True)

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
            print(f"Could not populate dropdown for {key}: {e}")
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
            print("No data to save.")
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
        self.view.ui.pageStack.setCurrentIndex(1)
        if self.db_tree_model.rowCount() == 0:
            self.load_database_structure()

    def load_database_structure(self):
        """Fetches table names from the model and populates the tree view."""
        self.db_tree_model.clear()
        self.db_tree_model.setHorizontalHeaderLabels(["Database Tables"])
        try:
            table_names = self.model.get_all_table_names()
            for table_name in table_names:
                item = QStandardItem(table_name)
                item.setEditable(False)
                self.db_tree_model.appendRow(item)
        except Exception as e:
            print(f"Error loading database structure: {e}")

    def on_db_tree_item_clicked(self, index):
        """Fetches and displays the content of the selected table when clicked."""
        self.current_table_name = self.db_tree_model.itemFromIndex(index).text()

        try:
            self.current_foreign_keys = self.model.get_foreign_key_info(
                self.current_table_name
            )
        except Exception as e:
            print(f"Could not get FK info for {self.current_table_name}: {e}")
            self.current_foreign_keys = {}

        self._clear_layout(self.view.ui.editFormLayout)
        self._clear_layout(self.view.ui.addFormLayout)

        if self.view.ui.formTabWidget.currentIndex() == 1:
            self.populate_add_form()

        self._refresh_current_table_view()

    def _refresh_current_table_view(self):
        """Helper method to reload the data in the main table view."""
        if not self.current_table_name:
            return

        self.db_table_model.clear()

        try:
            # Pass the current setting ID to filter the lorekeeper data
            headers, data_rows = self.model.get_table_data(
                self.current_table_name, setting_id=self.current_setting_id
            )
            self.db_table_model.setHorizontalHeaderLabels(headers)

            for row_tuple in data_rows:
                row_dict = dict(zip(headers, row_tuple))
                row_items = [QStandardItem(str(field)) for field in row_tuple]

                row_items[0].setData(row_dict, Qt.ItemDataRole.UserRole)

                for item in row_items:
                    item.setEditable(False)

                self.db_table_model.appendRow(row_items)
        except Exception as e:
            print(f"Error loading table data for '{self.current_table_name}': {e}")

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
