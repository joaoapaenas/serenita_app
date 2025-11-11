# app/features/performance_dashboard/performance_dashboard_controller.py
import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QObject

from app.core import analytics_logic
from app.services.interfaces import IAnalyticsService, WeeklyPerformance
from .performance_dashboard_view import PerformanceDashboardView

log = logging.getLogger(__name__)


class PerformanceDashboardController(QObject):
    """Controller for the performance dashboard view."""

    def __init__(self, view: PerformanceDashboardView, cycle_id: int, daily_goal: int,
                 analytics_service: IAnalyticsService):
        super().__init__(view)
        self._view = view
        self.cycle_id = cycle_id
        self.daily_goal = daily_goal
        self.analytics_service = analytics_service

        # State for the current filter
        self.current_period_days: Optional[int] = 30  # Default to 30 days

        self._view.period_changed.connect(self._on_period_changed)
        self._load_dashboard_data()

    def _on_period_changed(self, days_ago: Optional[int]):
        """Handles the user selecting a new date range."""
        log.debug(f"Dashboard period changed to: {days_ago} days")
        self.current_period_days = days_ago
        self._load_dashboard_data()

    def _load_dashboard_data(self):
        """Fetches, calculates, and populates all dashboard data based on the current filter."""
        # 1. Fetch the core daily data using the current filter
        daily_data = self.analytics_service.get_daily_performance(self.cycle_id, days_ago=self.current_period_days)
        # Fetch weekly summary directly from the service
        weekly_data = self.analytics_service.get_weekly_summary(self.cycle_id, days_ago=self.current_period_days)

        # 2. Perform business logic calculations on the filtered daily data
        summary_data = self._calculate_overall_summary(daily_data)
        streak_data = analytics_logic.calculate_streak_stats(daily_data, self.daily_goal)
        question_counts = [d.questions_done for d in daily_data]
        trend_line_data = analytics_logic.calculate_moving_average(question_counts, window_size=7)
        average_questions = (summary_data['total_questions'] / len(daily_data)) if daily_data else 0

        # 3. Populate the view with the newly processed data
        self._view.populate_summary_stats(summary_data)
        self._view.populate_streak_stats(streak_data)
        self._view.populate_weekly_table(weekly_data)
        self._view.populate_chart(daily_data, trend_line_data, average_questions)

    @staticmethod
    def _calculate_overall_summary(daily_data: list) -> dict:
        """Calculates summary stats from a list of DailyPerformance objects."""
        if not daily_data:
            return {'start_date': None, 'end_date': None, 'days_in_period': 0, 'total_questions': 0,
                    'total_correct': 0}

        start_date = daily_data[0].date
        end_date = daily_data[-1].date
        days_in_period = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1
        total_questions = sum(d.questions_done for d in daily_data)
        total_correct = sum(d.questions_correct for d in daily_data)

        return {'start_date': start_date, 'end_date': end_date, 'days_in_period': days_in_period,
                'total_questions': total_questions, 'total_correct': total_correct}