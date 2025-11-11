# app/features/subject_details/components/performance_snapshot_widget.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
                               QListWidget, QListWidgetItem, QGroupBox)

from app.features.performance_graphs.performance_graph_view import PerformanceGraphView


class PerformanceSnapshotWidget(QWidget):
    """
    A widget for the Subject Hub that displays diagnostics, a performance trend chart,
    and weakest topics for a subject with sufficient history.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main two-column layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        # Left Column: Diagnostics and Topics
        left_column_layout = QVBoxLayout()
        left_column_layout.setContentsMargins(0,0,0,0)

        diag_box = QGroupBox("Tutor Diagnostics")
        self.diag_grid = QGridLayout(diag_box)
        self.diag_grid.setColumnStretch(1, 1)

        topics_box = QGroupBox("Weakest Topics (Last 90 Days)")
        topics_layout = QVBoxLayout(topics_box)
        self.topics_list = QListWidget()
        self.topics_list.setObjectName("transparentList")
        topics_layout.addWidget(self.topics_list)

        left_column_layout.addWidget(diag_box)
        left_column_layout.addWidget(topics_box)

        # Right Column: Chart
        chart_box = QGroupBox("Performance Trend (Last 30 Days)")
        chart_layout = QVBoxLayout(chart_box)
        self.chart_view = PerformanceGraphView()
        self.chart_view.subject_combo.setVisible(False)
        self.chart_view.findChild(QLabel, "viewTitle").setVisible(False)
        chart_layout.addWidget(self.chart_view)

        main_layout.addLayout(left_column_layout, 1)
        main_layout.addWidget(chart_box, 1)

    def populate_data(self, diagnostics: dict, performance_trend: list, topic_performance: list):
        """Fills the widget with all necessary performance data."""
        self._populate_diagnostics(diagnostics)
        self._populate_topics(topic_performance)
        self.chart_view.update_chart(performance_trend)

    def _populate_diagnostics(self, diagnostics: dict):
        # Clear existing widgets from the grid
        while (item := self.diag_grid.takeAt(0)) is not None:
            if (widget := item.widget()) is not None:
                widget.deleteLater()

        # Create and add new widgets
        self.diag_grid.addWidget(self._create_diag_label("Strategic Mode:"), 0, 0)
        self.diag_grid.addWidget(self._create_diag_value(diagnostics.get('strategic_mode', 'N/A').replace('_', ' ').title()), 0, 1)
        self.diag_grid.addWidget(self._create_diag_label("Durable Mastery:"), 1, 0)
        self.diag_grid.addWidget(self._create_diag_value(f"{diagnostics.get('durable_mastery_score', 0):.1%}"), 1, 1)
        self.diag_grid.addWidget(self._create_diag_label("Mastery Confidence:"), 2, 0)
        self.diag_grid.addWidget(self._create_diag_value(f"{diagnostics.get('mastery_confidence_score', 0):.1%}"), 2, 1)
        self.diag_grid.addWidget(self._create_diag_label("Total Questions:"), 3, 0)
        self.diag_grid.addWidget(self._create_diag_value(str(diagnostics.get('total_questions', 0))), 3, 1)

    def _populate_topics(self, topic_performance: list):
        self.topics_list.clear()
        # Take the top 5 weakest topics
        weakest_topics = sorted(topic_performance, key=lambda x: x['accuracy'])[:5]
        if not weakest_topics:
            self.topics_list.addItem("No specific topic data found.")
            return

        for topic in weakest_topics:
            item = QListWidgetItem(f"{topic['accuracy']:.1f}% - {topic['topic_name']}")
            self.topics_list.addItem(item)

    @staticmethod
    def _create_diag_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("lightText")
        return label

    @staticmethod
    def _create_diag_value(text: str) -> QLabel:
        value = QLabel(text)
        font = value.font()
        font.setBold(True)
        value.setFont(font)
        value.setAlignment(Qt.AlignmentFlag.AlignRight)
        return value