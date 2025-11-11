# app/features/performance_graphs/performance_graph_view.py
import logging
from collections import deque
from datetime import datetime

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Signal, Qt, QDateTime
from PySide6.QtGui import QPainter, QPalette, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QApplication, QStackedWidget)

from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.core.constants import PAGE_MARGINS
from app.core.signals import app_signals

log = logging.getLogger(__name__)


class PerformanceGraphView(QWidget):
    """A view for displaying performance graphs over time."""
    subject_changed = Signal(int)  # Emits subject_id, or -1 for "Overall"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)

        header_layout = QHBoxLayout()
        title = QLabel("Performance Evolution")
        title.setObjectName("viewTitle")

        self.subject_combo = QComboBox()
        self.subject_combo.setMinimumWidth(250)
        self.subject_combo.currentIndexChanged.connect(self._on_subject_change)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("View performance for:"))
        header_layout.addWidget(self.subject_combo)
        main_layout.addLayout(header_layout)

        # Use a Stacked Widget to switch between the chart and an empty state
        self.content_stack = QStackedWidget()

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.empty_widget = EmptyStateWidget(
            icon_name="VIEW_PERFORMANCE",
            title="Not Enough Data",
            message="Complete at least two study sessions with questions to see your performance trends here."
        )

        self.content_stack.addWidget(self.chart_view)
        self.content_stack.addWidget(self.empty_widget)
        main_layout.addWidget(self.content_stack)

        self._apply_theme_to_chart()
        app_signals.theme_changed.connect(self._apply_theme_to_chart)

    def _apply_theme_to_chart(self):
        """Applies the current application theme colors to the chart."""
        palette = QApplication.instance().palette()
        text_color = palette.color(QPalette.ColorRole.Text)
        base_color = palette.color(QPalette.ColorRole.Base)
        grid_color = palette.color(QPalette.ColorRole.AlternateBase)

        self.chart.setTitleBrush(text_color)
        self.chart.setBackgroundBrush(base_color)
        self.chart.legend().setLabelColor(text_color)

        for axis in self.chart.axes():
            axis.setLabelsBrush(text_color)
            axis.setTitleBrush(text_color)
            axis.setGridLineColor(grid_color)

    def populate_subject_combo(self, subjects: list[dict]):
        self.subject_combo.blockSignals(True)
        self.subject_combo.clear()
        self.subject_combo.addItem("Overall Performance", -1)
        for subject in subjects:
            self.subject_combo.addItem(subject['name'], subject['id'])
        self.subject_combo.blockSignals(False)

    def _on_subject_change(self):
        subject_id = self.subject_combo.currentData()
        self.subject_changed.emit(subject_id)

    def update_chart(self, performance_data: list[dict]):
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if len(performance_data) < 2:
            self.chart.setTitle("Not enough data to display")
            self.content_stack.setCurrentWidget(self.empty_widget)
            self._apply_theme_to_chart()
            return

        self.content_stack.setCurrentWidget(self.chart_view)
        self.chart.setTitle("Accuracy Over Time")

        accuracy_series = QLineSeries()
        accuracy_series.setName("Daily Accuracy")
        accuracy_series.setColor(QColor("#007bff"))

        moving_avg_series = QLineSeries()
        moving_avg_series.setName("7-Day Moving Average")
        moving_avg_series.setColor(QColor("#FFCC00"))

        dates = []
        accuracies = []
        for item in performance_data:
            date_obj = QDateTime.fromString(item['date'], "yyyy-MM-dd")
            dates.append(date_obj)

            accuracy = (item['total_correct'] / item['total_questions']) * 100 if item['total_questions'] > 0 else 0
            accuracies.append(accuracy)

            accuracy_series.append(date_obj.toMSecsSinceEpoch(), accuracy)

        # Calculate 7-day moving average
        window_size = 7
        for i in range(len(accuracies)):
            window = accuracies[max(0, i - window_size + 1):i + 1]
            avg = sum(window) / len(window)
            moving_avg_series.append(dates[i].toMSecsSinceEpoch(), avg)

        self.chart.addSeries(accuracy_series)
        self.chart.addSeries(moving_avg_series)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setTitleText("Date")
        axis_x.setTickCount(min(10, len(dates)))
        axis_x.setRange(dates[0], dates[-1])
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        accuracy_series.attachAxis(axis_x)
        moving_avg_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%d%%")
        axis_y.setTitleText("Accuracy")
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        accuracy_series.attachAxis(axis_y)
        moving_avg_series.attachAxis(axis_y)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Apply theme after all elements are created
        self._apply_theme_to_chart()