"""Arc Point Add/Edit Dialog"""

from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt
from .arc_point_dialog_ui import Ui_ArcPointDialog
from storymaster.view.common.theme import (
    get_button_style,
    get_input_style,
    get_dialog_style,
    COLORS,
)
from storymaster.view.common.tooltips import (
    apply_character_arc_tooltips,
    apply_general_tooltips,
)
from storymaster.view.common.custom_widgets import enable_smart_tab_navigation


class ArcPointDialog(QDialog):
    """Dialog for adding or editing arc points"""

    def __init__(self, model, arc_id, storyline_id, arc_point=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.arc_id = arc_id
        self.storyline_id = storyline_id
        self.arc_point = arc_point  # None for add, ArcPoint object for edit

        # Setup UI
        self.ui = Ui_ArcPointDialog()
        self.ui.setupUi(self)

        # Apply theming
        self.setStyleSheet(get_dialog_style())

        self.setup_ui()
        self.load_nodes()

    def setup_ui(self):
        """Initialize UI components"""
        if self.arc_point:
            # Edit mode
            self.ui.titleLabel.setText("Edit Arc Point")
            self.ui.orderSpinBox.setValue(self.arc_point.order_index)
            self.ui.titleEdit.setText(self.arc_point.title)
            self.ui.descriptionEdit.setPlainText(self.arc_point.description or "")
            self.ui.emotionalStateEdit.setPlainText(
                self.arc_point.emotional_state or ""
            )
            self.ui.relationshipsEdit.setPlainText(
                self.arc_point.character_relationships or ""
            )
            self.ui.goalsEdit.setPlainText(self.arc_point.goals or "")
            self.ui.conflictEdit.setPlainText(self.arc_point.internal_conflict or "")

            # Set node selection
            if self.arc_point.node_id:
                for i in range(self.ui.nodeComboBox.count()):
                    if self.ui.nodeComboBox.itemData(i) == self.arc_point.node_id:
                        self.ui.nodeComboBox.setCurrentIndex(i)
                        break
        else:
            # Add mode
            self.ui.titleLabel.setText("Add Arc Point")
            # Set next order index
            try:
                existing_points = self.model.get_arc_points(self.arc_id)
                next_order = (
                    max([p.order_index for p in existing_points], default=0) + 1
                )
                self.ui.orderSpinBox.setValue(next_order)
            except Exception:
                self.ui.orderSpinBox.setValue(1)

        # Apply component theming and tooltips
        self.ui.titleLabel.setStyleSheet(f"color: {COLORS['text_accent']};")

        self.ui.titleEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.titleEdit, "arc_point_title")

        self.ui.orderSpinBox.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.orderSpinBox, "arc_point_order")

        self.ui.descriptionEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.descriptionEdit, "arc_point_description")

        self.ui.emotionalStateEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(
            self.ui.emotionalStateEdit, "arc_point_emotional_state"
        )

        self.ui.relationshipsEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(
            self.ui.relationshipsEdit, "arc_point_relationships"
        )

        self.ui.goalsEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.goalsEdit, "arc_point_goals")

        self.ui.conflictEdit.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.conflictEdit, "arc_point_conflict")

        self.ui.nodeComboBox.setStyleSheet(get_input_style())
        apply_character_arc_tooltips(self.ui.nodeComboBox, "arc_point_node")

        # Style button box
        ok_button = self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Ok)
        cancel_button = self.ui.buttonBox.button(
            self.ui.buttonBox.StandardButton.Cancel
        )
        if ok_button:
            ok_button.setStyleSheet(get_button_style("primary"))
        if cancel_button:
            cancel_button.setStyleSheet(get_button_style())

        # Note: Button signals are already connected in the UI file
        # self.ui.buttonBox.accepted.connect(self.accept) - already connected
        # self.ui.buttonBox.rejected.connect(self.reject) - already connected

        # Set up enhanced tab navigation
        enable_smart_tab_navigation(self)

    def load_nodes(self):
        """Load available story nodes into the combo box"""
        try:
            # Clear existing items except "No Node"
            self.ui.nodeComboBox.clear()
            self.ui.nodeComboBox.addItem("No Node", None)

            # Get nodes for the current storyline
            nodes = self.model.get_nodes_for_storyline(self.storyline_id)

            for node in nodes:
                # Use the new format: "name (node_type)"
                display_text = f"{node.name} ({node.node_type.value})"
                self.ui.nodeComboBox.addItem(display_text, node.id)

        except Exception as e:
            print(f"Warning: Could not load nodes: {e}")

    def accept(self):
        """Handle OK button click"""
        title = self.ui.titleEdit.text().strip()
        order_index = self.ui.orderSpinBox.value()
        description = self.ui.descriptionEdit.toPlainText().strip()
        emotional_state = self.ui.emotionalStateEdit.toPlainText().strip()
        relationships = self.ui.relationshipsEdit.toPlainText().strip()
        goals = self.ui.goalsEdit.toPlainText().strip()
        conflict = self.ui.conflictEdit.toPlainText().strip()
        node_id = self.ui.nodeComboBox.currentData()

        if not title:
            QMessageBox.warning(
                self, "Validation Error", "Arc point title is required."
            )
            return

        try:
            if self.arc_point:
                # Edit existing arc point
                self.model.update_arc_point(
                    self.arc_point.id,
                    title=title,
                    order_index=order_index,
                    description=description if description else None,
                    emotional_state=emotional_state if emotional_state else None,
                    character_relationships=relationships if relationships else None,
                    goals=goals if goals else None,
                    internal_conflict=conflict if conflict else None,
                    node_id=node_id,
                )
            else:
                # Create new arc point
                self.model.create_arc_point(
                    arc_id=self.arc_id,
                    title=title,
                    order_index=order_index,
                    description=description if description else None,
                    emotional_state=emotional_state if emotional_state else None,
                    character_relationships=relationships if relationships else None,
                    goals=goals if goals else None,
                    internal_conflict=conflict if conflict else None,
                    node_id=node_id,
                )

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save arc point: {e}")

    def get_result(self):
        """Get the dialog result data"""
        return {
            "title": self.ui.titleEdit.text().strip(),
            "order_index": self.ui.orderSpinBox.value(),
            "description": self.ui.descriptionEdit.toPlainText().strip(),
            "emotional_state": self.ui.emotionalStateEdit.toPlainText().strip(),
            "character_relationships": self.ui.relationshipsEdit.toPlainText().strip(),
            "goals": self.ui.goalsEdit.toPlainText().strip(),
            "internal_conflict": self.ui.conflictEdit.toPlainText().strip(),
            "node_id": self.ui.nodeComboBox.currentData(),
        }
