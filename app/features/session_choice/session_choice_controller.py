# app/features/session_mode_choice/session_mode_choice_controller.py
import logging
from datetime import datetime

from PySide6.QtCore import QObject, Signal, QDateTime

from app.models.subject import Subject
from app.services.interfaces import IMasterSubjectService
from .session_mode_choice_view import SessionModeChoiceView

log = logging.getLogger(__name__)


class SessionModeChoiceController(QObject):
    """Controller for the session mode selection view."""
    manual_log_requested = Signal(dict)
    stopwatch_start_requested = Signal(dict)

    def __init__(self, view: SessionModeChoiceView, master_subject_service: IMasterSubjectService,
                 all_subjects: list[Subject], initial_session_data: dict):
        super().__init__(view)
        self._view = view
        self.master_subject_service = master_subject_service
        self.all_subjects = all_subjects
        self.initial_session_data = initial_session_data

        # Connect signals from the view
        self._view.manual_log_submitted.connect(self.manual_log_requested.emit)
        self._view.stopwatch_start_submitted.connect(self._on_stopwatch_start)
        self._view.subject_changed.connect(self._on_subject_changed)

        self._populate_initial_data()

    def _populate_initial_data(self):
        """Populates the view with subjects and sets the initial selection."""
        # Find the full master subject model from the initial data
        initial_subject_name = self.initial_session_data.get('subject_name')
        initial_subject_model = next((s for s in self.all_subjects if s.name == initial_subject_name), None)

        self._view.populate_subjects(self.all_subjects, initial_subject_model)
        if initial_subject_model:
            self._on_subject_changed(initial_subject_model.id)

    def _on_subject_changed(self, subject_id: int):
        """Fetches topics for the selected subject and updates the view."""
        if subject_id:
            topics = self.master_subject_service.get_topics_for_subject(subject_id)
            self._view.populate_topics(topics)
        else:
            self._view.populate_topics([])

    def _on_stopwatch_start(self, data: dict):
        """
        Enriches the stopwatch data with the full cycle subject ID before emitting.
        The initial data only has the master subject ID.
        """
        # The session manager needs the cycle_subject_id from the plan, not the master subject_id
        # We can pass through the original session data which contains the correct ID.
        full_data = self.initial_session_data.copy()
        full_data.update(data)
        self.stopwatch_start_requested.emit(full_data)