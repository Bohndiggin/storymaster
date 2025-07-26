from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QVBoxLayout)


class PlotManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Plots")
        self.setModal(True)
        self.resize(400, 300)
        self.selected_plot_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Plot list
        list_label = QLabel("Available Plots:")
        layout.addWidget(list_label)

        self.plot_list = QListWidget()
        self.plot_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.plot_list)

        # New plot section
        new_plot_layout = QHBoxLayout()
        new_plot_label = QLabel("New Plot Name:")
        self.new_plot_input = QLineEdit()
        self.add_plot_btn = QPushButton("Add Plot")
        self.add_plot_btn.clicked.connect(self.on_add_plot)

        new_plot_layout.addWidget(new_plot_label)
        new_plot_layout.addWidget(self.new_plot_input)
        new_plot_layout.addWidget(self.add_plot_btn)
        layout.addLayout(new_plot_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.switch_btn = QPushButton("Switch to Plot")
        self.switch_btn.setEnabled(False)
        self.switch_btn.clicked.connect(self.on_switch_plot)

        self.delete_btn = QPushButton("Delete Plot")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.on_delete_plot)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.switch_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_plots(self, plots, current_plot_id):
        self.plot_list.clear()
        self.current_plot_id = current_plot_id

        for plot in plots:
            item = QListWidgetItem(plot.title)
            item.setData(Qt.ItemDataRole.UserRole, plot.id)

            if plot.id == current_plot_id:
                item.setText(f"{plot.title} (Current)")
                item.setBackground(Qt.GlobalColor.darkGray)

            self.plot_list.addItem(item)

    def on_selection_changed(self):
        selected_items = self.plot_list.selectedItems()
        has_selection = len(selected_items) > 0

        self.switch_btn.setEnabled(has_selection)

        if has_selection:
            selected_plot_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            is_current = selected_plot_id == self.current_plot_id
            self.switch_btn.setEnabled(not is_current)
            self.delete_btn.setEnabled(True)
        else:
            self.delete_btn.setEnabled(False)

    def on_add_plot(self):
        plot_name = self.new_plot_input.text().strip()
        if not plot_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a plot name.")
            return

        self.accept()
        self.action = "add"
        self.new_plot_name = plot_name

    def on_switch_plot(self):
        selected_items = self.plot_list.selectedItems()
        if selected_items:
            self.selected_plot_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.action = "switch"
            self.accept()

    def on_delete_plot(self):
        selected_items = self.plot_list.selectedItems()
        if not selected_items:
            return

        selected_plot_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        plot_title = selected_items[0].text().replace(" (Current)", "")

        if selected_plot_id == self.current_plot_id:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete the current plot. Switch to another plot first.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the plot '{plot_title}'?\n\n"
            "This will permanently delete all story nodes and sections in this plot.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_plot_id = selected_plot_id
            self.action = "delete"
            self.accept()
