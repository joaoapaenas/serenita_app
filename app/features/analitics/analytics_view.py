# app/features/analytics/analytics_view.py
import logging
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QBrush, QPalette
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QHeaderView,
                               QTableWidgetItem, QProgressBar, QFrame, QApplication, QStackedWidget, QPushButton)

from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.core.constants import PAGE_MARGINS
from app.core.icon_manager import get_icon
from app.core.signals import app_signals

log = logging.getLogger(__name__)


class AnalyticsView(QWidget):
    subject_changed = Signal(int)
    period_changed = Signal(object)  # Can emit int or None
    prioritize_topic_requested = Signal(str) # Emits topic_name

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)

        self._cached_topic_data = [] # Cache topic data for theme updates

        header_layout = QHBoxLayout()
        title = QLabel("Analytics Dashboard")
        title.setObjectName("viewTitle")

        self.period_combo = QComboBox()
        self.period_combo.addItem("Last 7 Days", 7)
        self.period_combo.addItem("Last 30 Days", 30)
        self.period_combo.addItem("Last 90 Days", 90)
        self.period_combo.addItem("All Time", None)
        self.period_combo.setCurrentText("Last 30 Days")
        self.period_combo.currentIndexChanged.connect(self._on_period_change)

        self.subject_combo = QComboBox()
        self.subject_combo.setMinimumWidth(250)
        self.subject_combo.currentIndexChanged.connect(self._on_subject_change)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Period:"))
        header_layout.addWidget(self.period_combo)
        header_layout.addWidget(QLabel("Subject:"))
        header_layout.addWidget(self.subject_combo)
        main_layout.addLayout(header_layout)

        # Work Unit Progress Section (Remains All-Time)
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("blockWidget")
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_header = QLabel("Work Unit Progress (All Time)")
        progress_header.setObjectName("sectionHeader")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("0/0 Units Completed")
        progress_layout.addWidget(progress_header)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.progress_frame)

        # Content Stack for summary table, topic table, and empty states
        self.content_stack = QStackedWidget()
        self.subject_summary_table = self._create_subject_summary_table()
        self.topics_table = self._create_topics_table()
        self.empty_data_widget = EmptyStateWidget(
            icon_name="SUBJECTS",
            title="No Study Data",
            message="No study sessions with question data were found for the selected period."
        )
        self.empty_topic_widget = EmptyStateWidget(
            icon_name="HELP",
            title="No Topic Data",
            message="No topic-specific question data was found for this subject in the selected period."
        )

        self.content_stack.addWidget(self.subject_summary_table)
        self.content_stack.addWidget(self.topics_table)
        self.content_stack.addWidget(self.empty_data_widget)
        self.content_stack.addWidget(self.empty_topic_widget)
        main_layout.addWidget(self.content_stack)

        app_signals.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Re-applies the heatmap colors when the theme changes."""
        self.update_topic_performance_table(self._cached_topic_data)

    def _create_subject_summary_table(self) -> QTableWidget:
        """Creates the new table for overall subject performance."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Subject", "Study Time", "Sessions", "Questions", "Accuracy"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _create_topics_table(self) -> QTableWidget:
        """Creates the original table for topic-specific performance."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Topic", "Accuracy", "Correct", "Total Questions", "Actions"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def populate_subject_combo(self, subjects: list[dict]):
        self.subject_combo.blockSignals(True)
        self.subject_combo.clear()
        self.subject_combo.addItem("All Subjects", -1)
        for subject in subjects:
            self.subject_combo.addItem(subject['name'], subject['id'])
        self.subject_combo.blockSignals(False)

    def _on_subject_change(self):
        subject_id = self.subject_combo.currentData()
        self.subject_changed.emit(subject_id)

    def _on_period_change(self):
        period_days = self.period_combo.currentData()
        self.period_changed.emit(period_days)

    def update_work_unit_summary(self, summary: dict):
        total = summary.get('total_units', 0)
        completed = summary.get('completed_units', 0)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(completed)
        self.progress_label.setText(f"{completed} / {total} Work Units Completed")

    def update_subject_summary_table(self, summary_data: list[dict]):
        """Populates the new overall subject summary table."""
        if not summary_data:
            self.content_stack.setCurrentWidget(self.empty_data_widget)
            return

        self.content_stack.setCurrentWidget(self.subject_summary_table)
        self.subject_summary_table.setRowCount(len(summary_data))
        for row, data in enumerate(summary_data):
            total_minutes = data.get('total_study_minutes', 0)
            hours, minutes = divmod(total_minutes, 60)
            time_str = f"{int(hours)}h {int(minutes)}m"

            self.subject_summary_table.setItem(row, 0, QTableWidgetItem(data['subject_name']))
            self.subject_summary_table.setItem(row, 1, QTableWidgetItem(time_str))
            self.subject_summary_table.setItem(row, 2, QTableWidgetItem(str(data['session_count'])))
            self.subject_summary_table.setItem(row, 3, QTableWidgetItem(str(data['total_questions'])))
            self.subject_summary_table.setItem(row, 4, QTableWidgetItem(f"{data['accuracy']:.1f}%"))

    def update_topic_performance_table(self, topics_data: list[dict]):
        """Populates the topic-specific performance table."""
        self._cached_topic_data = topics_data
        if not topics_data:
            self.content_stack.setCurrentWidget(self.empty_topic_widget)
            return

        self.content_stack.setCurrentWidget(self.topics_table)
        self.topics_table.setRowCount(len(topics_data))

        palette = QApplication.instance().palette()
        is_light_theme = palette.color(QPalette.ColorRole.Base).lightness() > 127

        for row, data in enumerate(topics_data):
            accuracy = data.get('accuracy', 0)
            self.topics_table.setItem(row, 0, QTableWidgetItem(data['topic_name']))
            self.topics_table.setItem(row, 1, QTableWidgetItem(f"{accuracy:.1f}%"))
            self.topics_table.setItem(row, 2, QTableWidgetItem(str(data['total_correct'])))
            self.topics_table.setItem(row, 3, QTableWidgetItem(str(data['total_questions'])))

            # --- START: Add Action Button ---
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            prioritize_button = QPushButton()
            prioritize_button.setIcon(get_icon("MAGIC_WAND"))
            prioritize_button.setToolTip(f"Prioritize '{data['topic_name']}' by increasing its subject's study frequency.")
            prioritize_button.clicked.connect(lambda checked=False, name=data['topic_name']: self.prioritize_topic_requested.emit(name))

            actions_layout.addWidget(prioritize_button)
            self.topics_table.setCellWidget(row, 4, actions_widget)
            # --- END: Add Action Button ---

            # "Heat Map" coloring
            if accuracy < 60:
                color = QColor("#E57373")  # Red
            elif accuracy < 80:
                color = QColor("#FFD54F")  # Amber
            else:
                color = QColor("#81C784")  # Green

            brush_color = color.lighter(160) if not is_light_theme else color.darker(105)

            for col in range(self.topics_table.columnCount()):
                self.topics_table.item(row, col).setBackground(QBrush(brush_color))