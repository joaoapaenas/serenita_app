# app/feature/cycle_manager/cycle_manager_view.py
import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel
)

from app.core.icon_manager import get_icon, THEME_ACCENT_COLOR

log = logging.getLogger(__name__)


class CycleManagerView(QWidget):
    """
    A widget for managing all study cycles. It displays a table of cycles
    and buttons for interaction.
    """
    create_new_requested = Signal()
    delete_requested = Signal(int)
    set_active_requested = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        log.debug("Initializing CycleManagerView.")
        self.setObjectName("CycleManagerView")
        self.layout = QVBoxLayout(self)

        title_label = QLabel("Cycle Management")
        title_label.setObjectName("viewTitle")

        self.table = QTableWidget()
        self._setup_table()

        self.create_button = QPushButton(" Create New Cycle")
        self.create_button.setIcon(get_icon("NEW_CYCLE"))

        self.edit_button = QPushButton(" Edit Selected")
        self.edit_button.setIcon(get_icon("EDIT"))

        self.delete_button = QPushButton(" Delete Selected")
        self.delete_button.setIcon(get_icon("DELETE", color="#E57373"))

        self.set_active_button = QPushButton(" Set as Active")
        self.set_active_button.setIcon(get_icon("ACTIVE_STATUS", color=THEME_ACCENT_COLOR))

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.set_active_button)
        buttons_layout.addWidget(self.delete_button)

        self.layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self._update_button_states)
        self.create_button.clicked.connect(self.create_new_requested.emit)
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.set_active_button.clicked.connect(self.on_set_active_clicked)

        self._update_button_states()

    def _setup_table(self):
        """Initializes the table structure and headers."""
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Cycle Name", "Type", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.hideColumn(0)

    def populate_table(self, cycles_data):
        """Public method called by the controller to fill the table with cycle data."""
        log.debug(f"Populating cycle manager table with {len(cycles_data)} cycles.")
        self.table.setRowCount(len(cycles_data))
        for row, cycle in enumerate(cycles_data):
            status = "Active" if cycle.is_active else "Inactive"
            cycle_type = "Continuous" if cycle.is_continuous else "Fixed-Term"

            self.table.setItem(row, 0, QTableWidgetItem(str(cycle.id)))
            self.table.setItem(row, 1, QTableWidgetItem(cycle.name))
            self.table.setItem(row, 2, QTableWidgetItem(cycle_type))
            self.table.setItem(row, 3, QTableWidgetItem(status))
        self._update_button_states()

    def _get_selected_cycle_id(self) -> int | None:
        """Helper to safely get the ID from the selected row."""
        selected_items = self.table.selectedItems()
        if selected_items:
            return int(self.table.item(selected_items[0].row(), 0).text())
        return None

    def _update_button_states(self):
        """Enables or disables buttons based on table selection."""
        cycle_id = self._get_selected_cycle_id()
        is_selection_valid = cycle_id is not None
        self.delete_button.setEnabled(is_selection_valid)
        self.edit_button.setEnabled(is_selection_valid)

        is_active = False
        if is_selection_valid:
            status_item = self.table.item(self.table.currentRow(), 3)
            is_active = status_item.text() == "Active"
        self.set_active_button.setEnabled(is_selection_valid and not is_active)

    def on_edit_clicked(self):
        if cycle_id := self._get_selected_cycle_id():
            log.info(f"Edit requested for cycle_id: {cycle_id}")
            self.edit_requested.emit(cycle_id)

    def on_delete_clicked(self):
        if cycle_id := self._get_selected_cycle_id():
            log.info(f"Delete requested for cycle_id: {cycle_id}")
            self.delete_requested.emit(cycle_id)

    def on_set_active_clicked(self):
        if cycle_id := self._get_selected_cycle_id():
            log.info(f"Set active requested for cycle_id: {cycle_id}")
            self.set_active_requested.emit(cycle_id)
