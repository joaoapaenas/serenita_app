# app/feature/cycle_editor/components/configured_subjects_widget.py
import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QHeaderView, QAbstractItemView, QTableWidgetItem, QSpinBox, QCheckBox
)

log = logging.getLogger(__name__)


class ConfiguredSubjectsWidget(QWidget):
    """A widget for displaying and editing the configuration of subjects selected for a cycle."""
    subject_config_changed = Signal(int, dict)  # subject_id, {key: value}

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._row_map = {}  # Maps subject_id to table row index

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 0, 0)
        header = QLabel("SUBJECTS IN THIS CYCLE")
        header.setObjectName("sectionHeader")

        self.selected_table = QTableWidget()
        self._setup_table()

        layout.addWidget(header)
        # --- FIX: Add a stretch factor of 1 to the table widget ---
        # This makes the table expand to fill all available vertical space.
        layout.addWidget(self.selected_table, 1)

    def _setup_table(self):
        """Initializes the table structure, headers, and tooltips."""
        self.selected_table.setColumnCount(5)
        self.selected_table.setHorizontalHeaderLabels(["Active", "Subject", "Relevance", "Volume", "Difficulty"])

        header = self.selected_table.horizontalHeader()
        header.model().setHeaderData(2, Qt.Orientation.Horizontal,
                                     "How important is this subject for your exam score? (1=Low, 5=High)",
                                     Qt.ItemDataRole.ToolTipRole)
        header.model().setHeaderData(3, Qt.Orientation.Horizontal,
                                     "How much material is there to cover for this subject? (1=Low, 5=High)",
                                     Qt.ItemDataRole.ToolTipRole)
        header.model().setHeaderData(4, Qt.Orientation.Horizontal,
                                     "How difficult do you personally find this subject? (1=Easy, 5=Hard)",
                                     Qt.ItemDataRole.ToolTipRole)

        self.selected_table.verticalHeader().setVisible(False)
        self.selected_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.selected_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.selected_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.selected_table.verticalHeader().setDefaultSectionSize(36)

    def add_or_update_row(self, subject_id: int, data: dict):
        """Adds a new row to the selected table or updates it if it exists."""
        if subject_id in self._row_map:
            row = self._row_map[subject_id]
        else:
            row = self.selected_table.rowCount()
            self.selected_table.insertRow(row)
            self._row_map[subject_id] = row

        self.blockSignals(True)

        # Active Checkbox
        active_checkbox = QCheckBox()
        active_checkbox.setChecked(data['is_active'])
        active_checkbox.toggled.connect(
            lambda checked, sid=subject_id: self.subject_config_changed.emit(sid, {"is_active": checked}))
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(active_checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.selected_table.setCellWidget(row, 0, cell_widget)

        # Name
        name_item = QTableWidgetItem(data['name'])
        name_item.setData(Qt.ItemDataRole.UserRole, subject_id)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.selected_table.setItem(row, 1, name_item)

        # SpinBoxes
        for i, key in enumerate(['relevance', 'volume', 'difficulty'], start=2):
            spin_box = QSpinBox()
            spin_box.setRange(1, 5)
            spin_box.setValue(data[key])
            spin_box.valueChanged.connect(
                lambda value, k=key, sid=subject_id: self.subject_config_changed.emit(sid, {k: value}))
            self.selected_table.setCellWidget(row, i, spin_box)

        self.blockSignals(False)

    def remove_row(self, subject_id: int):
        """Removes a subject's row from the selected table."""
        if subject_id in self._row_map:
            row_to_remove = self._row_map[subject_id]
            self.selected_table.removeRow(row_to_remove)
            del self._row_map[subject_id]
            # Update the row map for all subsequent rows
            for sid, r in self._row_map.items():
                if r > row_to_remove:
                    self._row_map[sid] = r - 1

    def blockSignals(self, should_block: bool):
        self.selected_table.blockSignals(should_block)