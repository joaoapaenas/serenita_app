# app/features/performance_graphs/performance_graph_controller.py

from PySide6.QtCore import QObject

from app.services.interfaces import IPerformanceService, IMasterSubjectService
from .performance_graph_view import PerformanceGraphView


class PerformanceGraphController(QObject):
    """Controller for the performance graphs view."""

    def __init__(self, view: PerformanceGraphView, user_id: int,
                 performance_service: IPerformanceService, master_subject_service: IMasterSubjectService):
        super().__init__(view)
        self._view = view
        self.user_id = user_id
        self.performance_service = performance_service
        self.master_subject_service = master_subject_service

        self._view.subject_changed.connect(self._on_subject_selected)

        self._populate_initial_data()

    def _populate_initial_data(self):
        # --- FIX: Fetch only subjects that have performance data ---
        subjects_with_data = self.performance_service.get_subjects_with_performance_data(
            self.user_id
        )
        self._view.populate_subject_combo(subjects_with_data)

        # Load overall performance by default
        self._on_subject_selected(-1)

    def _on_subject_selected(self, subject_id: int):
        # -1 is the sentinel for "Overall Performance"
        filter_subject_id = subject_id if subject_id != -1 else None

        performance_data = self.performance_service.get_performance_over_time(
            user_id=self.user_id,
            subject_id=filter_subject_id
        )
        self._view.update_chart(performance_data)