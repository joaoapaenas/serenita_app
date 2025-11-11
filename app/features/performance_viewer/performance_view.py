# app/feature/performance_viewer/performance_view.py
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QApplication
)

log = logging.getLogger(__name__)


class PerformanceView(QDialog):
    """
    The View for displaying aggregated performance data for a study cycle.
    It's a "dumb" component that simply displays the data it's given.
    """

    def __init__(self, cycle_name: str, parent=None):
        super().__init__(parent)
        log.debug(f"Initializing PerformanceView for cycle: '{cycle_name}'")
        self.setWindowTitle(f"Performance for '{cycle_name}'")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self._setup_table()
        self.layout.addWidget(self.table)

    def _setup_table(self):
        """Initializes the table structure and headers."""
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Subject", "Total Questions", "Total Correct", "Accuracy"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Make columns fill width
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only

    def populate_data(self, summary_data: list):
        """
        Public method called by the controller to fill the table with data.
        Handles the case where there is no data to display.
        """
        log.debug(f"Populating performance view with data for {len(summary_data)} subjects.")
        if not summary_data:
            self.table.hide()  # Hide the empty table
            no_data_label = QLabel("No performance data has been logged for this cycle yet.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(no_data_label)
            log.info("No performance data available to display in PerformanceView.")
            return

        self.table.setRowCount(len(summary_data))
        for row_index, perf in enumerate(summary_data):
            # The 'perf' object is a SubjectPerformance dataclass instance
            self.table.setItem(row_index, 0, QTableWidgetItem(perf.subject_name))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(perf.total_questions)))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(perf.total_correct)))
            self.table.setItem(row_index, 3, QTableWidgetItem(f"{perf.accuracy:.2f}%"))