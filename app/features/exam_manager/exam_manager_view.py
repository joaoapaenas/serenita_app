# app/features/exam_manager/exam_manager_view.py
import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel
)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon

log = logging.getLogger(__name__)

class ExamManagerView(QWidget):
    """
    A widget for managing all exam goals. It displays a table of exams
    and buttons for interaction.
    """
    create_new_requested = Signal()
    delete_requested = Signal(int)
    edit_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        log.debug("Initializing ExamManagerView.")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(*PAGE_MARGINS)
        self.layout.setSpacing(SPACING_LARGE)

        title_label = QLabel("Exam Goal Management")
        title_label.setObjectName("viewTitle")

        self.table = QTableWidget()
        self._setup_table()

        self.create_button = QPushButton(" Create New Exam")
        self.create_button.setIcon(get_icon("ADD"))

        self.edit_button = QPushButton(" Edit Selected")
        self.edit_button.setIcon(get_icon("EDIT"))

        self.delete_button = QPushButton(" Delete Selected")
        self.delete_button.setIcon(get_icon("DELETE", color="#E57373"))

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)

        self.layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self._update_button_states)
        self.create_button.clicked.connect(self.create_new_requested.emit)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

        self._update_button_states()

    def _setup_table(self):
        """Initializes the table structure and headers."""
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Exam Name", "Institution", "Area", "Predicted Date"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.hideColumn(0)

    def populate_table(self, exams_data):
        """Public method called by the controller to fill the table."""
        log.debug(f"Populating exam manager table with {len(exams_data)} exams.")
        self.table.setRowCount(len(exams_data))
        for row, exam in enumerate(exams_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(exam.id)))
            self.table.setItem(row, 1, QTableWidgetItem(exam.name))
            self.table.setItem(row, 2, QTableWidgetItem(exam.institution))
            self.table.setItem(row, 3, QTableWidgetItem(exam.area))
            self.table.setItem(row, 4, QTableWidgetItem(exam.predicted_exam_date))
        self._update_button_states()

    def _get_selected_exam_id(self) -> int | None:
        """Helper to safely get the ID from the selected row."""
        selected_items = self.table.selectedItems()
        if selected_items:
            return int(self.table.item(selected_items[0].row(), 0).text())
        return None

    def _update_button_states(self):
        """Enables or disables buttons based on table selection."""
        is_selection_valid = self._get_selected_exam_id() is not None
        self.delete_button.setEnabled(is_selection_valid)
        self.edit_button.setEnabled(is_selection_valid)

    def _on_edit_clicked(self):
        if exam_id := self._get_selected_exam_id():
            self.edit_requested.emit(exam_id)

    def _on_delete_clicked(self):
        if exam_id := self._get_selected_exam_id():
            self.delete_requested.emit(exam_id)