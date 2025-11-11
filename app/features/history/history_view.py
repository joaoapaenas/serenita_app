# app/features/history/history_view.py

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QStackedWidget, QTabWidget, QTreeView
)

from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.core.constants import PAGE_MARGINS

log = logging.getLogger(__name__)


class HistoryView(QWidget):
    """A view that displays a table of past study sessions."""
    start_session_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)

        title = QLabel("Study Session History")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- First Tab: Session History ---
        self.session_history_tab = QWidget()
        session_layout = QVBoxLayout(self.session_history_tab)
        session_layout.setContentsMargins(0, 0, 0, 0)

        # Use a QStackedWidget to switch between the table and the empty state
        self.content_stack = QStackedWidget()
        session_layout.addWidget(self.content_stack)

        self.history_table = QTableWidget()
        self._setup_table()

        self.empty_widget = EmptyStateWidget(
            icon_name="HISTORY",
            title="No History Yet",
            message="Your completed study sessions will appear here. Let's get the ball rolling!",
            button_text="Start First Session"
        )
        self.empty_widget.action_requested.connect(self.start_session_requested.emit)

        self.content_stack.addWidget(self.history_table)
        self.content_stack.addWidget(self.empty_widget)
        
        # --- Second Tab: Daily Breakdown ---
        self.daily_breakdown_tab = QWidget()
        explorer_layout = QVBoxLayout(self.daily_breakdown_tab)
        explorer_layout.setContentsMargins(0, 0, 0, 0)

        self.daily_breakdown_tree = QTreeView()
        self.daily_breakdown_tree.setHeaderHidden(True)
        self.daily_breakdown_tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.daily_breakdown_model = QStandardItemModel()
        self.daily_breakdown_tree.setModel(self.daily_breakdown_model)
        explorer_layout.addWidget(self.daily_breakdown_tree)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.session_history_tab, "Session History")
        self.tab_widget.addTab(self.daily_breakdown_tab, "Daily Breakdown")

    def _setup_table(self):
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Subject", "Date", "Duration", "Questions", "Correct", "Accuracy"
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSortingEnabled(True)

    def clear_history(self):
        """Clears the table for refreshing."""
        self.history_table.setRowCount(0)

    def populate_history(self, history_data: list):
        if not history_data:
            self.content_stack.setCurrentWidget(self.empty_widget)
            return

        self.content_stack.setCurrentWidget(self.history_table)

        self.history_table.setSortingEnabled(False)  # Disable sorting during population for performance
        self.history_table.setRowCount(len(history_data))
        for row, session_data in enumerate(history_data):
            # Create items that can be sorted by their actual value, not just text
            duration_item = QTableWidgetItem(session_data['duration_str'])
            duration_item.setData(Qt.ItemDataRole.UserRole, session_data['duration_sec'])

            questions_item = QTableWidgetItem(str(session_data['questions_done']))
            questions_item.setData(Qt.ItemDataRole.UserRole, session_data['questions_done'])

            correct_item = QTableWidgetItem(str(session_data['questions_correct']))
            correct_item.setData(Qt.ItemDataRole.UserRole, session_data['questions_correct'])

            accuracy_item = QTableWidgetItem(f"{session_data['accuracy']:.1f}%")
            accuracy_item.setData(Qt.ItemDataRole.UserRole, session_data['accuracy'])

            self.history_table.setItem(row, 0, QTableWidgetItem(session_data['subject_name']))
            self.history_table.setItem(row, 1, QTableWidgetItem(session_data['date']))
            self.history_table.setItem(row, 2, duration_item)
            self.history_table.setItem(row, 3, questions_item)
            self.history_table.setItem(row, 4, correct_item)
            self.history_table.setItem(row, 5, accuracy_item)

        self.history_table.setSortingEnabled(True)
        # Sort by date descending by default
        self.history_table.sortByColumn(1, Qt.SortOrder.DescendingOrder)

    def populate_daily_breakdown(self, daily_data: dict):
        self.daily_breakdown_model.clear()
        for date, subjects in sorted(daily_data.items(), reverse=True):
            date_item = QStandardItem(date)
            date_item.setEditable(False)  # Disable editing for date items
            self.daily_breakdown_model.appendRow(date_item)
            for subject_name in subjects:
                subject_item = QStandardItem(subject_name)
                subject_item.setEditable(False)  # Disable editing for subject items
                date_item.appendRow(subject_item)
            self.daily_breakdown_tree.expand(date_item.index()) # Automatically expand date items