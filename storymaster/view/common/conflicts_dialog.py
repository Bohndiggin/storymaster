"""UI for reviewing and resolving sync conflicts."""

from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import sessionmaker

from storymaster.model.database.base_connection import engine as local_engine
from storymaster.model.database.schema.base import SyncConflict
from storymaster.sync_client import conflicts as conflicts_api


# Internal/system fields are not user-meaningful. Hide them from the diff view.
_HIDDEN_FIELDS = {
    "id",
    "sync_uuid",
    "version",
    "created_at",
    "updated_at",
    "deleted_at",
}


def _is_visible(field: str) -> bool:
    if field in _HIDDEN_FIELDS:
        return False
    if field.endswith("_sync_uuid"):
        return False
    return True


class ConflictsDialog(QDialog):
    """List pending sync conflicts and let the user resolve each one."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resolve Sync Conflicts")
        self.resize(900, 700)

        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=local_engine
        )
        # Long-lived session for the dialog's lifetime so SyncConflict rows
        # we read into the UI stay attached.
        self._session = self._SessionLocal()
        self._conflicts: list[SyncConflict] = []
        self._current: Optional[SyncConflict] = None
        # Per-field picks for the currently-selected conflict: field → 'mine' | 'theirs'
        self._picks: dict[str, str] = {}
        self._radio_groups: dict[str, QButtonGroup] = {}

        self._build_ui()
        self.refresh()

    # ---- UI construction ----

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)

        intro = QLabel(
            "Pick a conflict on the left, then resolve by field or with one of "
            "the bulk actions at the bottom.",
            self,
        )
        intro.setWordWrap(True)
        outer.addWidget(intro)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        outer.addWidget(splitter, 1)

        # Left: list of conflicts
        left = QWidget(splitter)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.list_table = QTableWidget(0, 3, left)
        self.list_table.setHorizontalHeaderLabels(["Type", "Source", "Detected"])
        self.list_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.list_table.horizontalHeader().setStretchLastSection(True)
        self.list_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.list_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.list_table.itemSelectionChanged.connect(self._on_select)
        left_layout.addWidget(self.list_table)

        # Right: detail
        right = QWidget(splitter)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.summary_label = QLabel("No conflict selected.", right)
        self.summary_label.setWordWrap(True)
        right_layout.addWidget(self.summary_label)

        self.diff_table = QTableWidget(0, 4, right)
        self.diff_table.setHorizontalHeaderLabels(
            ["Field", "Mine", "Theirs", "Use"]
        )
        self.diff_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.diff_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.diff_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.diff_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.diff_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        right_layout.addWidget(self.diff_table, 1)

        # Per-conflict action buttons
        button_row = QHBoxLayout()
        self.btn_use_mine = QPushButton("Use All Mine")
        self.btn_use_theirs = QPushButton("Use All Theirs")
        self.btn_save_merged = QPushButton("Save Merged Picks")
        self.btn_discard = QPushButton("Discard (No Change)")
        for b in (
            self.btn_use_mine,
            self.btn_use_theirs,
            self.btn_save_merged,
            self.btn_discard,
        ):
            b.setEnabled(False)
            button_row.addWidget(b)
        button_row.addStretch(1)
        right_layout.addLayout(button_row)

        self.btn_use_mine.clicked.connect(self._action_use_mine)
        self.btn_use_theirs.clicked.connect(self._action_use_theirs)
        self.btn_save_merged.clicked.connect(self._action_save_merged)
        self.btn_discard.clicked.connect(self._action_discard)

        # Bulk action buttons
        bulk_row = QHBoxLayout()
        self.btn_discard_all = QPushButton("Discard All Pending")
        self.btn_discard_all.setToolTip(
            "Mark every pending conflict resolved without changing local data. "
            "Useful when conflicts are spurious."
        )
        self.btn_discard_all.clicked.connect(self._action_discard_all)
        bulk_row.addStretch(1)
        bulk_row.addWidget(self.btn_discard_all)
        right_layout.addLayout(bulk_row)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([300, 600])

        # Footer
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        footer.addWidget(self.close_button)
        outer.addLayout(footer)

    # ---- data loading ----

    def refresh(self) -> None:
        # Re-read from DB.
        self._session.expire_all()
        self._conflicts = conflicts_api.list_pending(self._session)
        self.list_table.setRowCount(len(self._conflicts))
        for row, c in enumerate(self._conflicts):
            self.list_table.setItem(row, 0, QTableWidgetItem(c.entity_type))
            self.list_table.setItem(row, 1, QTableWidgetItem(c.source))
            ts = c.detected_at.isoformat(timespec="seconds") if c.detected_at else ""
            self.list_table.setItem(row, 2, QTableWidgetItem(ts))
        if not self._conflicts:
            self._current = None
            self.summary_label.setText("No pending conflicts.")
            self.diff_table.setRowCount(0)
            for b in (
                self.btn_use_mine,
                self.btn_use_theirs,
                self.btn_save_merged,
                self.btn_discard,
            ):
                b.setEnabled(False)
        else:
            self.list_table.selectRow(0)

    def _on_select(self) -> None:
        rows = self.list_table.selectionModel().selectedRows()
        if not rows:
            self._current = None
            return
        self._current = self._conflicts[rows[0].row()]
        self._render_detail()

    # ---- detail rendering ----

    def _render_detail(self) -> None:
        if self._current is None:
            return
        c = self._current
        mine = json.loads(c.mine_data) if c.mine_data else {}
        theirs = json.loads(c.theirs_data) if c.theirs_data else {}

        self.summary_label.setText(
            f"<b>{c.entity_type}</b> &nbsp; "
            f"sync_uuid: <code>{c.target_sync_uuid}</code><br>"
            f"Mine version: {c.mine_version} &nbsp;|&nbsp; "
            f"Theirs version: {c.theirs_version} &nbsp;|&nbsp; "
            f"Source: {c.source}"
        )

        all_fields = sorted(
            f for f in (set(mine) | set(theirs)) if _is_visible(f)
        )
        # Default picks: where values match, doesn't matter; where they differ,
        # default to 'theirs' (server is canonical and most pulls drift toward it).
        self._picks = {}
        self._radio_groups = {}
        for f in all_fields:
            if mine.get(f) != theirs.get(f):
                self._picks[f] = "theirs"

        self.diff_table.setRowCount(len(all_fields))
        for i, field in enumerate(all_fields):
            mv = _format(mine.get(field))
            tv = _format(theirs.get(field))

            self.diff_table.setItem(i, 0, QTableWidgetItem(field))
            mine_item = QTableWidgetItem(mv)
            theirs_item = QTableWidgetItem(tv)
            if mine.get(field) != theirs.get(field):
                yellow = QColor(255, 248, 196)
                mine_item.setBackground(yellow)
                theirs_item.setBackground(yellow)
            self.diff_table.setItem(i, 1, mine_item)
            self.diff_table.setItem(i, 2, theirs_item)

            picker = self._build_picker(field, mine.get(field) != theirs.get(field))
            self.diff_table.setCellWidget(i, 3, picker)

        for b in (
            self.btn_use_mine,
            self.btn_use_theirs,
            self.btn_save_merged,
            self.btn_discard,
        ):
            b.setEnabled(True)

    def _build_picker(self, field: str, differs: bool) -> QWidget:
        """Build a Mine/Theirs radio pair for one row of the diff table."""
        wrapper = QWidget()
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(4, 0, 4, 0)
        rb_mine = QRadioButton("M")
        rb_theirs = QRadioButton("T")
        rb_mine.setToolTip("Use mine for this field")
        rb_theirs.setToolTip("Use theirs for this field")
        if not differs:
            # Equal — gray out, no decision needed.
            rb_mine.setEnabled(False)
            rb_theirs.setEnabled(False)
        else:
            current = self._picks.get(field, "theirs")
            (rb_mine if current == "mine" else rb_theirs).setChecked(True)
        group = QButtonGroup(wrapper)
        group.addButton(rb_mine, 0)
        group.addButton(rb_theirs, 1)

        def on_change(_id, _checked):
            if rb_mine.isChecked():
                self._picks[field] = "mine"
            elif rb_theirs.isChecked():
                self._picks[field] = "theirs"

        group.buttonToggled.connect(on_change)
        self._radio_groups[field] = group
        h.addWidget(rb_mine)
        h.addWidget(rb_theirs)
        h.addStretch(1)
        return wrapper

    # ---- actions ----

    def _action_use_mine(self) -> None:
        if self._current is None:
            return
        try:
            conflicts_api.resolve_use_mine(self._session, self._current.id)
        except Exception as e:
            QMessageBox.critical(self, "Resolution failed", str(e))
            return
        self.refresh()

    def _action_use_theirs(self) -> None:
        if self._current is None:
            return
        try:
            conflicts_api.resolve_use_theirs(self._session, self._current.id)
        except Exception as e:
            QMessageBox.critical(self, "Resolution failed", str(e))
            return
        self.refresh()

    def _action_save_merged(self) -> None:
        if self._current is None:
            return
        c = self._current
        mine = json.loads(c.mine_data) if c.mine_data else {}
        theirs = json.loads(c.theirs_data) if c.theirs_data else {}
        # Build merged dict starting from theirs (so FK sync_uuid keys etc.
        # come along), then overlay each picked field.
        merged = dict(theirs)
        for field, pick in self._picks.items():
            merged[field] = mine.get(field) if pick == "mine" else theirs.get(field)
        try:
            conflicts_api.resolve_with_merged(self._session, c.id, merged)
        except Exception as e:
            QMessageBox.critical(self, "Resolution failed", str(e))
            return
        self.refresh()

    def _action_discard(self) -> None:
        if self._current is None:
            return
        try:
            conflicts_api.discard(self._session, self._current.id)
        except Exception as e:
            QMessageBox.critical(self, "Resolution failed", str(e))
            return
        self.refresh()

    def _action_discard_all(self) -> None:
        n = len(self._conflicts)
        if n == 0:
            return
        confirm = QMessageBox.question(
            self,
            "Discard all conflicts?",
            f"Mark all {n} pending conflicts as resolved without changing any "
            "local data. This is non-destructive — your rows aren't touched. "
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            conflicts_api.discard_all(self._session)
        except Exception as e:
            QMessageBox.critical(self, "Bulk discard failed", str(e))
            return
        self.refresh()

    def closeEvent(self, event):
        self._session.close()
        super().closeEvent(event)


def _format(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)
