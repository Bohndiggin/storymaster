"""Arc Type Manager Dialog"""

from PySide6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from .arc_type_dialog import ArcTypeDialog
from .arc_type_manager_dialog_ui import Ui_ArcTypeManagerDialog
from storymaster.view.common.theme import get_button_style, get_dialog_style, COLORS


class ArcTypeManagerDialog(QDialog):
    """Dialog for managing arc types"""

    def __init__(self, model, setting_id, parent=None):
        super().__init__(parent)
        self.model = model
        self.setting_id = setting_id
        self.current_arc_type = None

        # Setup UI
        self.ui = Ui_ArcTypeManagerDialog()
        self.ui.setupUi(self)

        # Apply theming
        self.setStyleSheet(get_dialog_style())

        self.setup_ui()
        self.connect_signals()
        self.refresh_arc_types()

    def setup_ui(self):
        """Initialize UI components"""
        # Configure table
        self.ui.arcTypesTable.setSelectionBehavior(
            self.ui.arcTypesTable.SelectionBehavior.SelectRows
        )
        self.ui.arcTypesTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.ui.arcTypesTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        # Apply component theming
        self.ui.addArcTypeButton.setStyleSheet(get_button_style("primary"))
        self.ui.editArcTypeButton.setStyleSheet(get_button_style())
        self.ui.deleteArcTypeButton.setStyleSheet(get_button_style("danger"))

        # Apply dark theme to table
        table_style = f"""
            QTableWidget {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_main']};
                gridline-color: {COLORS['border_main']};
                selection-background-color: {COLORS['primary']};
                alternate-background-color: {COLORS['bg_secondary']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border_main']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                padding: 8px;
                border: 1px solid {COLORS['border_main']};
                font-weight: bold;
            }}
        """
        self.ui.arcTypesTable.setStyleSheet(table_style)

    def connect_signals(self):
        """Connect widget signals"""
        self.ui.addArcTypeButton.clicked.connect(self.on_add_arc_type)
        self.ui.editArcTypeButton.clicked.connect(self.on_edit_arc_type)
        self.ui.deleteArcTypeButton.clicked.connect(self.on_delete_arc_type)
        self.ui.arcTypesTable.itemSelectionChanged.connect(self.on_selection_changed)
        self.ui.arcTypesTable.itemDoubleClicked.connect(self.on_edit_arc_type)

    def refresh_arc_types(self):
        """Refresh the arc types table"""
        self.ui.arcTypesTable.setRowCount(0)

        try:
            arc_types = self.model.get_arc_types(self.setting_id)

            self.ui.arcTypesTable.setRowCount(len(arc_types))

            for row, arc_type in enumerate(arc_types):
                # Name
                name_item = QTableWidgetItem(arc_type.name)
                name_item.setData(Qt.ItemDataRole.UserRole, arc_type.id)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.ui.arcTypesTable.setItem(row, 0, name_item)

                # Description
                description = arc_type.description or ""
                desc_item = QTableWidgetItem(description)
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.ui.arcTypesTable.setItem(row, 1, desc_item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load arc types: {e}")

    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.ui.arcTypesTable.selectedItems()

        if selected_items:
            row = selected_items[0].row()
            arc_type_id = self.ui.arcTypesTable.item(row, 0).data(
                Qt.ItemDataRole.UserRole
            )

            try:
                self.current_arc_type = self.model.get_arc_type(arc_type_id)
                self.ui.editArcTypeButton.setEnabled(True)
                self.ui.deleteArcTypeButton.setEnabled(True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load arc type: {e}")
                self.current_arc_type = None
                self.ui.editArcTypeButton.setEnabled(False)
                self.ui.deleteArcTypeButton.setEnabled(False)
        else:
            self.current_arc_type = None
            self.ui.editArcTypeButton.setEnabled(False)
            self.ui.deleteArcTypeButton.setEnabled(False)

    def on_add_arc_type(self):
        """Handle add arc type button"""
        dialog = ArcTypeDialog(self.model, self.setting_id, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.operation_successful:
            self.refresh_arc_types()

    def on_edit_arc_type(self):
        """Handle edit arc type button"""
        if not self.current_arc_type:
            return

        dialog = ArcTypeDialog(
            self.model, self.setting_id, self.current_arc_type, parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.operation_successful:
            self.refresh_arc_types()

    def on_delete_arc_type(self):
        """Handle delete arc type button"""
        if not self.current_arc_type:
            return

        reply = QMessageBox.question(
            self,
            "Delete Arc Type",
            f"Are you sure you want to delete the arc type '{self.current_arc_type.name}'?\n\n"
            "This will also delete all character arcs using this type.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.model.delete_arc_type(self.current_arc_type.id)
                self.refresh_arc_types()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete arc type: {e}")
