# app/features/subject_summary/subject_summary_view.py

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLabel, QTabWidget, QTreeView)

from app.core.constants import PAGE_MARGINS

log = logging.getLogger(__name__)


class SubjectSummaryView(QWidget):
    """A view that shows a summary of all subjects in the current cycle."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)

        title = QLabel("Subjects")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- First Tab: Summary ---
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        summary_layout.setContentsMargins(0, 0, 0, 0)

        self.summary_table = QTableWidget()
        self._setup_table()
        summary_layout.addWidget(self.summary_table)

        # --- Second Tab: Subject Explorer ---
        self.subject_explorer_tab = QWidget()
        explorer_layout = QVBoxLayout(self.subject_explorer_tab)
        explorer_layout.setContentsMargins(0, 0, 0, 0)

        self.subject_tree = QTreeView()
        self.subject_tree.setHeaderHidden(True)
        self.subject_tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.subject_tree_model = QStandardItemModel()
        self.subject_tree.setModel(self.subject_tree_model)
        explorer_layout.addWidget(self.subject_tree)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.summary_tab, "Summary")
        self.tab_widget.addTab(self.subject_explorer_tab, "Subject Explorer")

    def _setup_table(self):
        self.summary_table.setColumnCount(8)
        self.summary_table.setHorizontalHeaderLabels([
            "Subject", "Strategic Mode", "Mastery Score", "Confidence",
            "Total Sessions", "Weekly Sessions", "Total Time (min)", "Weekly Time (min)"
        ])
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def populate_summary(self, processed_subjects: list):
        if not processed_subjects:
            self.summary_table.setRowCount(1)
            self.summary_table.setItem(0, 0, QTableWidgetItem("No subject data available."))
            return

        self.summary_table.setRowCount(len(processed_subjects))
        for row, subject_data in enumerate(processed_subjects):
            diagnostics = subject_data.get('diagnostics', {})

            name = subject_data.get('subject_name', 'N/A')
            mode = diagnostics.get('strategic_mode', 'N/A').replace('_', ' ').title()
            mastery = f"{diagnostics.get('durable_mastery_score', 0):.1%}"
            confidence = f"{diagnostics.get('mastery_confidence_score', 0):.1%}"
            total_sessions = str(subject_data.get('total_sessions', 0))
            weekly_sessions = str(subject_data.get('weekly_sessions', 0))
            total_minutes = str(subject_data.get('total_minutes', 0))
            weekly_minutes = str(subject_data.get('weekly_minutes', 0))

            self.summary_table.setItem(row, 0, QTableWidgetItem(name))
            self.summary_table.setItem(row, 1, QTableWidgetItem(mode))
            self.summary_table.setItem(row, 2, QTableWidgetItem(mastery))
            self.summary_table.setItem(row, 3, QTableWidgetItem(confidence))
            self.summary_table.setItem(row, 4, QTableWidgetItem(total_sessions))
            self.summary_table.setItem(row, 5, QTableWidgetItem(weekly_sessions))
            self.summary_table.setItem(row, 6, QTableWidgetItem(total_minutes))
            self.summary_table.setItem(row, 7, QTableWidgetItem(weekly_minutes))

    def populate_subject_explorer(self, subjects_data: list):
        self.subject_tree_model.clear()
        for subject in subjects_data:
            subject_item = QStandardItem(subject['name'])
            subject_item.setEditable(False)  # Disable editing for subject items
            self.subject_tree_model.appendRow(subject_item)
            for topic in subject['topics']:
                topic_item = QStandardItem(topic['name'])
                topic_item.setEditable(False)  # Disable editing for topic items
                subject_item.appendRow(topic_item)
            self.subject_tree.expand(subject_item.index()) # Automatically expand subject items