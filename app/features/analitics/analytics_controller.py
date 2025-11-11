# app/features/analytics/analytics_controller.py
import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from app.common.error_handler import show_error_message
from app.core.signals import app_signals
from app.services.interfaces import IPerformanceService, ICycleSubjectService
from .analytics_view import AnalyticsView

log = logging.getLogger(__name__)


class AnalyticsController(QObject):
    """Controller for the analytics dashboard view."""

    def __init__(self, view: AnalyticsView, user_id: int, cycle_id: int,
                 performance_service: IPerformanceService, cycle_subject_service: ICycleSubjectService):
        super().__init__(view)
        self._view = view
        self.user_id = user_id
        self.cycle_id = cycle_id
        self.performance_service = performance_service
        self.cycle_subject_service = cycle_subject_service

        # State for filters
        self.current_subject_id = -1  # Default to All Subjects
        self.current_period_days = 30  # Default to 30 days

        self._view.subject_changed.connect(self._on_subject_changed)
        self._view.period_changed.connect(self._on_period_changed)
        self._view.prioritize_topic_requested.connect(self._on_prioritize_topic)
        self._populate_initial_data()

    def _populate_initial_data(self):
        """Populates the subject filter with subjects from the current cycle."""
        cycle_subjects = self.cycle_subject_service.get_subjects_for_cycle(self.cycle_id)
        # We need the master subject ID (subject_id) for filtering performance data
        subjects_for_combo = [{'id': s.subject_id, 'name': s.name} for s in cycle_subjects]
        self._view.populate_subject_combo(subjects_for_combo)
        # Trigger initial load for "All Subjects" and default period
        self._load_analytics_data()

    def _on_subject_changed(self, subject_id: int):
        self.current_subject_id = subject_id
        self._load_analytics_data()

    def _on_period_changed(self, days_ago: int | None):
        self.current_period_days = days_ago
        self._load_analytics_data()

    def _load_analytics_data(self):
        """
        Central method to refresh all data based on current filter state.
        It now decides which view (overall summary or topic details) to show.
        """
        work_unit_summary = self.performance_service.get_work_unit_summary(user_id=self.user_id)
        self._view.update_work_unit_summary(work_unit_summary)

        if self.current_subject_id == -1:
            log.debug(f"Loading overall subject summary data for cycle_id: {self.cycle_id}.")
            summary_data = self.performance_service.get_subject_summary_for_analytics(
                user_id=self.user_id,
                cycle_id=self.cycle_id,
                days_ago=self.current_period_days
            )
            self._view.update_subject_summary_table(summary_data)
        else:
            log.debug(f"Loading topic performance data for subject_id: {self.current_subject_id}")
            topic_data = self.performance_service.get_topic_performance(
                user_id=self.user_id,
                subject_id=self.current_subject_id,
                days_ago=self.current_period_days
            )
            self._view.update_topic_performance_table(topic_data)

    def _on_prioritize_topic(self, topic_name: str):
        """Handles the user's request to increase a subject's priority based on a weak topic."""
        if self.current_subject_id == -1:
            log.warning("Prioritize requested from 'All Subjects' view. This should not happen.")
            return

        try:
            all_cycle_subjects = self.cycle_subject_service.get_subjects_for_cycle(self.cycle_id)
            target_subject = next((cs for cs in all_cycle_subjects if cs.subject_id == self.current_subject_id), None)

            if not target_subject:
                show_error_message(self._view, "Error", "Could not find the subject to prioritize.")
                return

            current_difficulty = target_subject.difficulty_weight
            if current_difficulty >= 5:
                QMessageBox.information(self._view, "Max Priority",
                                        f"'{target_subject.name}' is already at the maximum priority (5/5).")
                return

            new_difficulty = current_difficulty + 1
            self.cycle_subject_service.update_cycle_subject_difficulty(target_subject.id, new_difficulty)

            QMessageBox.information(self._view, "Priority Increased",
                                    f"Because you're struggling with '{topic_name}', the priority for the subject "
                                    f"'{target_subject.name}' has been increased.\n\n"
                                    "Your study plan will now be updated.")

            app_signals.data_changed.emit()

        except Exception as e:
            show_error_message(self._view, "Error", "Could not prioritize the subject.", str(e))