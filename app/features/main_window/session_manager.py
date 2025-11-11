# app/features/main_window/session_manager.py
import logging
from datetime import datetime, timezone

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from app.features.study_session.study_session_controller import StudySessionController
from app.features.study_session.study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class SessionManager(QObject):
    """
    Manages the lifecycle of a study session.
    This extracts the session management responsibility from MainWindowController.
    """
    rebalance_prompt_requested = Signal()

    REBALANCE_PROMPT_THRESHOLD = 10
    REBALANCE_PROMPT_INTERVAL = 5

    def __init__(self, main_controller):
        super().__init__(main_controller)
        self._main_ctl = main_controller
        self.session_controller = None
        self.session_view: StudySessionWidget | None = None

    def start_study_session(self, session_data: dict):
        """
        Shows the session mode choice view (Manual vs. Stopwatch)
        instead of directly starting the timer.
        """
        log.info(f"Session initiation requested for subject: '{session_data.get('subject_name')}'. Showing mode choice.")
        self._main_ctl.navigator.show_session_mode_choice(session_data)


    def handle_manual_session_log(self, log_data: dict):
        """Handles the request to log a session manually without a timer."""
        log.info(f"Handling manual session log for subject_id: {log_data['subject_id']}")
        try:
            # 1. Log the session to the database as before
            self._main_ctl.app_context.session_service.log_manual_session(
                user_id=self._main_ctl.current_user.id,
                cycle_id=self._main_ctl.active_cycle.id,
                subject_id=log_data['subject_id'],
                topic_id=log_data['topic_id'],
                start_datetime_iso=log_data['start_datetime'],
                duration_minutes=log_data['duration_minutes'],
                description="Manually logged session."
            )
            QMessageBox.information(self._main_ctl.view, "Success", "Manual session has been logged.")

            # 2. Find the correct cycle_subject_id to remove from the plan
            # The plan uses cycle_subject IDs, but the log form gives us master subject IDs.
            # We need to find the matching cycle subject from the plan's context.
            cached_plan = self._main_ctl.plan_manager.get_cached_plan()
            target_cycle_subject_id = None
            if cached_plan and 'subjects' in cached_plan:
                full_subject_models = cached_plan['subjects']
                matching_subject = next((cs for cs in full_subject_models if cs.subject_id == log_data['subject_id']), None)
                if matching_subject:
                    target_cycle_subject_id = matching_subject.id

            # 3. Use the new lightweight method to update the plan view
            if target_cycle_subject_id:
                self._main_ctl.plan_manager.mark_session_as_completed(target_cycle_subject_id)
            else:
                # Fallback to a full replan if we can't find the specific subject
                log.warning("Could not find matching cycle subject for manual log. Falling back to full replan.")
                self._main_ctl.refresh_data_and_views(force_replan=True)

        except Exception as e:
            log.error("Failed to log manual session.", exc_info=True)
            QMessageBox.critical(self._main_ctl.view, "Error", f"Could not log the session: {e}")


    def handle_stopwatch_session_start(self, session_data: dict):
        """
        The second step of starting a session. Creates the live stopwatch
        view and controller after user confirmation.
        """
        subject_id = session_data.get('subject_id')
        topic_id = session_data.get('topic_id')
        topic_name = session_data.get('topic_name')
        log.info(f"Starting stopwatch session for subject: '{session_data.get('subject_name')}'.")

        full_cycle_subject = self._main_ctl.app_context.cycle_subject_service.get_cycle_subject(subject_id)

        if not full_cycle_subject:
            log.error(f"Could not find CycleSubject with id {subject_id} to start session.")
            QMessageBox.warning(self._main_ctl.view, "Error", "Could not find the subject data to start the session.")
            return

        new_session_id = self._main_ctl.app_context.session_service.start_session(
            user_id=self._main_ctl.current_user.id,
            subject_id=full_cycle_subject.subject_id,
            cycle_id=self._main_ctl.active_cycle.id,
            topic_id=topic_id
        )

        topics_for_subject = self._main_ctl.app_context.master_subject_service.get_topics_for_subject(full_cycle_subject.subject_id)

        self.session_view = StudySessionWidget(
            subject_name=full_cycle_subject.name,
            topic_name=topic_name,
            topics=topics_for_subject,
            parent=self._main_ctl.view
        )
        self.session_controller = StudySessionController(
            view=self.session_view,
            cycle_subject=full_cycle_subject,
            session_id=new_session_id,
            session_service=self._main_ctl.app_context.session_service
        )
        self.session_controller.block_completed.connect(self._on_block_completed)
        self.session_controller.timer.timeout.connect(self._main_ctl.toolbar_manager.update_visibility_and_state)

        self._main_ctl.navigator.show_active_session()
        self._main_ctl.action_factory.new_cycle_action.setEnabled(False)
        self._main_ctl.update_action_states()

    def _on_block_completed(self, cycle_subject, performance_data):
        """Handles the completion of a study block."""
        if not self._main_ctl.active_cycle: return
        log.info(f"Block complete for subject '{cycle_subject.name}'. Advancing application state.")

        # --- Session cleanup ---
        if self.session_controller:
            self.session_controller.timer.stop()
            self.session_controller = None
        self.session_view = None

        # --- Rebalance prompt logic (unchanged) ---
        session_count = self._main_ctl.app_context.session_service.get_completed_session_count(self._main_ctl.active_cycle.id)
        log.debug(f"Cycle has {session_count} completed sessions.")
        should_prompt = (
            session_count >= self.REBALANCE_PROMPT_THRESHOLD and
            session_count % self.REBALANCE_PROMPT_INTERVAL == 0
        )
        if should_prompt:
            self.rebalance_prompt_requested.emit()

        # --- MODIFIED: Use the new lightweight update instead of a full replan ---
        self._main_ctl.plan_manager.mark_session_as_completed(cycle_subject.id)
        self._main_ctl.action_factory.new_cycle_action.setEnabled(True)

    def is_session_active(self) -> bool:
        """Checks if a session controller currently exists."""
        return self.session_controller is not None