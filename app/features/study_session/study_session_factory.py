# app/features/study_session/study_session_factory.py
import logging

from PySide6.QtWidgets import QMessageBox

from app.models.subject import CycleSubject
from app.services.interfaces import ISessionService, ISubjectService
from .study_session_controller import StudySessionController
from .study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class StudySessionFactory:
    """
    Encapsulates the logic for creating and wiring up all components
    needed for a study session.
    """

    def __init__(self, session_service: ISessionService, subject_service: ISubjectService,
                 parent_view=None):
        self.session_service = session_service
        self.subject_service = subject_service
        self.parent_view = parent_view

    def create_session(self, cycle_id: int, session_data: dict) -> tuple[
        StudySessionWidget | None, StudySessionController | None]:
        """
        Creates a new study session, including DB record, view, and controller.
        Returns a tuple of the view and controller, or (None, None) on failure.
        """
        subject_name = session_data.get('subject_name')
        subject_id = session_data.get('subject_id')
        full_cycle_subject = self.subject_service.get_cycle_subject(subject_id)

        if not full_cycle_subject:
            log.error(f"Could not find CycleSubject with id {subject_id} to start session.")
            QMessageBox.warning(self.parent_view, "Error",
                                "Could not find the subject data to start the session.")
            return None, None

        log.info(f"Factory creating session for subject: '{subject_name}'.")

        # 1. Create the persistent session record in the database.
        new_session_id = self.session_service.start_session(
            subject_id=full_cycle_subject.subject_id,
            cycle_id=cycle_id
        )

        # 2. Fetch dependencies for the view (e.g., topics).
        topics_for_subject = self.subject_service.get_topics_for_subject(full_cycle_subject.subject_id)

        # 3. Create the View instance.
        view = StudySessionWidget(
            subject_name=full_cycle_subject.name,
            topic_name=None,
            topics=topics_for_subject,
            parent=self.parent_view
        )

        # 4. Create the Controller instance, injecting the view and other dependencies.
        controller = StudySessionController(
            view=view,
            cycle_subject=full_cycle_subject,
            session_id=new_session_id,
            session_service=self.session_service
        )

        return view, controller