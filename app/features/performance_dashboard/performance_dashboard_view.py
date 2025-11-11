# app/features/performance_dashboard/performance_dashboard_view.py
import logging
from datetime import datetime

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QSplineSeries, QDateTimeAxis
from PySide6.QtCore import Qt, QDateTime, Signal
from PySide6.QtGui import QPainter, QPalette, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                               QFormLayout, QTableWidget, QHeaderView, QTableWidgetItem, QComboBox, QApplication)

from app.core.constants import SPACING_XLARGE
from app.core.signals import app_signals

log = logging.getLogger(__name__)


class PerformanceDashboardView(QWidget):
    """A view for displaying time-series performance analytics and charts."""
    period_changed = Signal(object)  # Emits int (days) or None (all time)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        title = QLabel("Performance Dashboard")
        title.setObjectName("viewTitle")

        self.period_combo = QComboBox()
        self.period_combo.addItem("Last 7 Days", 7)
        self.period_combo.addItem("Last 30 Days", 30)
        self.period_combo.addItem("Last 90 Days", 90)
        self.period_combo.addItem("All Time", None)
        self.period_combo.setCurrentText("Last 30 Days")
        self.period_combo.currentIndexChanged.connect(self._on_period_change)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Show data for:"))
        header_layout.addWidget(self.period_combo)
        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        left_pane_layout = QVBoxLayout()
        left_pane_layout.setSpacing(SPACING_XLARGE)

        # --- Panes for stats ---
        self.summary_box = QGroupBox("Period Summary")
        self.streak_box = QGroupBox("Streaks & Success Rate")
        self.weekly_table = QTableWidget()

        left_pane_layout.addWidget(self.summary_box)
        left_pane_layout.addWidget(self.streak_box)
        left_pane_layout.addWidget(QLabel("Weekly Breakdown"), 0, Qt.AlignmentFlag.AlignCenter)
        left_pane_layout.addWidget(self.weekly_table)

        # --- Chart ---
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        content_layout.addLayout(left_pane_layout, 1)
        content_layout.addWidget(self.chart_view, 2)
        main_layout.addLayout(content_layout)

        self._setup_ui_elements()
        self._apply_theme_to_chart() # Apply theme on initialization
        app_signals.theme_changed.connect(self._apply_theme_to_chart) # Re-apply on theme change

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

    def _on_period_change(self):
        self.period_changed.emit(self.period_combo.currentData())

    def _setup_ui_elements(self):
        """Initial setup for static UI parts."""
        self.summary_layout = QFormLayout(self.summary_box)
        self.streak_layout = QFormLayout(self.streak_box)

        self.weekly_table.setColumnCount(4)
        self.weekly_table.setHorizontalHeaderLabels(["Week of", "Questions", "Avg/Day", "Accuracy"])
        self.weekly_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.weekly_table.verticalHeader().setVisible(False)

    def populate_summary_stats(self, summary_data: dict):
        """Fills the summary stats boxes."""
        self._clear_layout(self.summary_layout)
        start = summary_data.get('start_date', 'N/A')
        end = summary_data.get('end_date', 'N/A')
        total_q = summary_data.get('total_questions', 0)
        total_c = summary_data.get('total_correct', 0)
        days = summary_data.get('days_in_period', 0)

        accuracy = (total_c / total_q * 100) if total_q > 0 else 0
        q_per_day = (total_q / days) if days > 0 else 0
        q_per_week = q_per_day * 7

        self.summary_layout.addRow("Start Date:", QLabel(start))
        self.summary_layout.addRow("End Date:", QLabel(end))
        self.summary_layout.addRow("Total Questions:", QLabel(f"{total_q}"))
        self.summary_layout.addRow("Total Correct:", QLabel(f"{total_c}"))
        self.summary_layout.addRow("Overall Accuracy:", QLabel(f"{accuracy:.2f}%"))
        self.summary_layout.addRow("Avg. Questions/Day:", QLabel(f"{q_per_day:.2f}"))
        self.summary_layout.addRow("Avg. Questions/Week:", QLabel(f"{q_per_week:.2f}"))

    def populate_streak_stats(self, streak_data: dict):
        self._clear_layout(self.streak_layout)
        success_rate = (streak_data['days_goal_met'] / streak_data['total_days_studied'] * 100) \
            if streak_data['total_days_studied'] > 0 else 100

        self.streak_layout.addRow("Current Streak:", QLabel(f"{streak_data['current_streak']} days"))
        self.streak_layout.addRow("Max Streak:", QLabel(f"{streak_data['max_streak']} days"))
        self.streak_layout.addRow("Goal Success Rate:", QLabel(f"{success_rate:.2f}%"))

    def populate_weekly_table(self, weekly_data: list):
        self.weekly_table.setRowCount(len(weekly_data))
        for row, data in enumerate(weekly_data):
            accuracy = (data.questions_correct / data.questions_done * 100) if data.questions_done > 0 else 0

            self.weekly_table.setItem(row, 0, QTableWidgetItem(data.week_start_date))
            self.weekly_table.setItem(row, 1, QTableWidgetItem(str(data.questions_done)))
            self.weekly_table.setItem(row, 2, QTableWidgetItem(f"{data.avg_per_day:.2f}"))
            self.weekly_table.setItem(row, 3, QTableWidgetItem(f"{accuracy:.2f}%"))

    def populate_chart(self, daily_data: list, trend_data: list, average: float):
        self.chart.removeAllSeries()
        # Use a more robust way to clear axes that works across Qt versions
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if not daily_data:
            self.chart.setTitle("No daily performance data to display")
            self._apply_theme_to_chart() # Ensure empty chart has correct theme
            return

        self.chart.setTitle("Daily Questions Answered")

        daily_series = QLineSeries()
        daily_series.setName("Questions")
        daily_series.setColor(QColor("#007bff")) # A nice blue for daily data

        trend_series = QSplineSeries()
        trend_series.setName("Trendline (7-day avg)")
        trend_series.setColor(QColor("#FFCC00")) # App accent color

        avg_series = QLineSeries()
        avg_series.setName("Average")
        avg_pen = avg_series.pen()
        avg_pen.setStyle(Qt.PenStyle.DashLine)
        avg_pen.setColor(QColor("#888888")) # Muted gray
        avg_series.setPen(avg_pen)


        min_val, max_val = float('inf'), float('-inf')

        for day in daily_data:
            dt = datetime.strptime(day.date, "%Y-%m-%d")
            timestamp = dt.timestamp() * 1000
            daily_series.append(timestamp, day.questions_done)
            min_val = min(min_val, day.questions_done)
            max_val = max(max_val, day.questions_done)

        for i, trend_val in enumerate(trend_data):
            dt = datetime.strptime(daily_data[i].date, "%Y-%m-%d")
            timestamp = dt.timestamp() * 1000
            trend_series.append(timestamp, trend_val)

        if daily_data:
            start_dt = datetime.strptime(daily_data[0].date, "%Y-%m-%d")
            end_dt = datetime.strptime(daily_data[-1].date, "%Y-%m-%d")
            avg_series.append(start_dt.timestamp() * 1000, average)
            avg_series.append(end_dt.timestamp() * 1000, average)

        self.chart.addSeries(daily_series)
        self.chart.addSeries(trend_series)
        self.chart.addSeries(avg_series)

        # --- FIX: Use QDateTimeAxis for a human-readable X-axis ---
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")  # e.g., "Jun 05"
        axis_x.setTitleText("Date")
        axis_x.setTickCount(min(8, len(daily_data) + 1))
        start_qdt = QDateTime.fromString(daily_data[0].date, "yyyy-MM-dd")
        end_qdt = QDateTime.fromString(daily_data[-1].date, "yyyy-MM-dd")
        axis_x.setRange(start_qdt, end_qdt)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        # --- END FIX ---

        axis_y = QValueAxis()
        axis_y.setRange(0, max(10, max_val * 1.1)) # Ensure axis isn't flat if max_val is 0
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        daily_series.attachAxis(axis_x)
        daily_series.attachAxis(axis_y)
        trend_series.attachAxis(axis_x)
        trend_series.attachAxis(axis_y)
        avg_series.attachAxis(axis_x)
        avg_series.attachAxis(axis_y)

        # Apply theme colors to all chart elements, including newly created axes
        self._apply_theme_to_chart()

    def _clear_layout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()