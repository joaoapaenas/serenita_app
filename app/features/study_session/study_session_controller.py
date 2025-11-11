# app/feature/study_session/study_session_controller.py
import logging

from PySide6.QtCore import QObject, Signal, QTimer

from app.models.subject import CycleSubject
from app.services.interfaces import ISessionService
from .study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class StudySessionController(QObject):
    """Controller for an active study session. Manages the timer and session data."""
    block_completed = Signal(CycleSubject, dict)

    def __init__(self, view: StudySessionWidget, cycle_subject: CycleSubject, session_id: int,
                 session_service: ISessionService):
        super().__init__(view)
        self._view = view
        self.cycle_subject = cycle_subject
        self.session_id = session_id
        self.session_service = session_service

        self.time_elapsed_sec = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 second

        # Connect signals
        self.timer.timeout.connect(self._update_timer)
        self._view.logging_requested.connect(self._on_logging_requested)
        self._view.session_paused.connect(self.pause_timer)
        self._view.session_resumed.connect(self.resume_timer)
        self._view.session_finished.connect(self.finish_session)

        self.start_timer()

    def start_timer(self):
        log.info(f"Starting timer for session_id: {self.session_id}")
        self.timer.start()

    def pause_timer(self):
        log.info(f"Pausing timer for session_id: {self.session_id}")
        self.timer.stop()
        self.session_service.add_pause_start(self.session_id)

    def resume_timer(self):
        log.info(f"Resuming timer for session_id: {self.session_id}")
        self.timer.start()
        self.session_service.add_pause_end(self.session_id)

    def _update_timer(self):
        self.time_elapsed_sec += 1
        minutes, seconds = divmod(self.time_elapsed_sec, 60)
        self._view.update_timer_display(f"{minutes:02d}:{seconds:02d}")

    def _on_logging_requested(self):
        """Stops the timer and transitions the view to the logging state."""
        log.debug("Logging requested. Stopping timer and showing logging view.")
        self.timer.stop()
        self._view.show_logging_view()

    def finish_session(self, performance_data: dict):
        """
        Logs the final session details and emits the block_completed signal.
        """
        log.info(f"Finishing session {self.session_id} for subject '{self.cycle_subject.name}'")
        self.session_service.finish_session(
            session_id=self.session_id,
            description=performance_data.get('description'),
            questions=performance_data.get('questions_list'),
            topic_id=performance_data.get('topic_id')
        )
        self.block_completed.emit(self.cycle_subject, performance_data)