# app/features/history/history_controller.py

import logging
from collections import defaultdict
from datetime import datetime

from PySide6.QtCore import QObject

from app.core.signals import app_signals
from app.services.interfaces import ISessionService

from .history_view import HistoryView

log = logging.getLogger(__name__)


class HistoryController(QObject):
    """Controller for the study session history view."""

    def __init__(self, view: HistoryView, cycle_id: int, session_service: ISessionService):
        super().__init__(view)
        self._view = view
        self.cycle_id = cycle_id
        self.session_service = session_service

        # Connect to the global signal to refresh data when needed
        app_signals.data_changed.connect(self.load_data)

        # Perform the initial data load
        self.load_data()

    def load_data(self):
        """Fetches, processes, and displays the latest session history and daily breakdown data."""
        log.debug(f"HistoryController loading data for cycle_id: {self.cycle_id}")

        # --- Load Session History ---
        self._view.clear_history()
        sessions = self.session_service.get_history_for_cycle(self.cycle_id)
        history_entries = []
        daily_breakdown_data = defaultdict(list)

        for session in sessions:
            if not session.end_time:
                continue

            # Data for Session History tab
            questions_done = len(session.questions)
            questions_correct = sum(1 for q in session.questions if q.is_correct)
            accuracy = (questions_correct / questions_done * 100) if questions_done > 0 else 0.0
            minutes, seconds = divmod(session.liquid_duration_sec, 60)
            duration_str = f"{int(minutes)}m {int(seconds)}s"
            history_entries.append({
                'subject_name': session.subject_name,
                'date': datetime.fromisoformat(session.start_time).strftime('%Y-%m-%d %H:%M'),
                'duration_str': duration_str,
                'duration_sec': session.liquid_duration_sec,
                'questions_done': questions_done,
                'questions_correct': questions_correct,
                'accuracy': accuracy,
            })

            # Data for Daily Breakdown tab
            session_date = datetime.fromisoformat(session.start_time).strftime('%Y-%m-%d')
            daily_breakdown_data[session_date].append(session.subject_name)

        self._view.populate_history(history_entries)
        self._view.populate_daily_breakdown(daily_breakdown_data)