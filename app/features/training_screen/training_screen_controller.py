import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Dict, Optional, Any

from PySide6.QtWidgets import QMessageBox

from app.services.interfaces import ISessionService, IMasterSubjectService, ICycleSubjectService
from app.models.subject import Subject, Topic, CycleSubject # Import Subject and Topic models
from app.models.user import User # Assuming User model is needed for user_id

if TYPE_CHECKING:
    from .training_screen_view import TrainingScreenView

log = logging.getLogger(__name__)

class TrainingScreenController:
    def __init__(self, view: 'TrainingScreenView',
                 session_service: ISessionService,
                 master_subject_service: IMasterSubjectService,
                 cycle_subject_service: ICycleSubjectService):
        self.view = view
        self.session_service = session_service
        self.master_subject_service = master_subject_service
        self.cycle_subject_service = cycle_subject_service

        self._current_user_id: Optional[int] = None # Will be set by main controller
        self._current_cycle_id: Optional[int] = None # Will be set by main controller
        self._subjects: List[Subject] = []
        self._cycle_subjects: List[CycleSubject] = []
        self._subject_map: Dict[int, Subject] = {} # id -> Subject
        self._topics_by_subject: Dict[int, List[Topic]] = {} # subject_id -> List[Topic]

        self._connect_signals()
        # _load_initial_data is not strictly needed here as set_user_and_cycle will trigger subject loading

    def set_user_and_cycle(self, user_id: int, cycle_id: int):
        self._current_user_id = user_id
        self._current_cycle_id = cycle_id
        self._load_subjects_for_cycle()

    def _connect_signals(self):
        self.view.exercise_content_widget.log_session_button.clicked.connect(self._log_session)
        self.view.exercise_content_widget.subject_combobox.currentIndexChanged.connect(self._on_subject_selected)

    def _load_subjects_for_cycle(self):
        if self._current_cycle_id is None:
            log.warning("Cannot load subjects: current_cycle_id is not set.")
            return

        # Get cycle subjects first
        self._cycle_subjects = self.cycle_subject_service.get_subjects_for_cycle(self._current_cycle_id)
        
        # Then get master subjects and their topics
        self._subjects = []
        self._subject_map = {}
        self._topics_by_subject = {}

        for cs in self._cycle_subjects:
            master_subject = self.master_subject_service.get_subject_by_id(cs.subject_id)
            if master_subject:
                self._subjects.append(master_subject)
                self._subject_map[master_subject.id] = master_subject
                
                topics = self.master_subject_service.get_topics_for_subject(master_subject.id)
                self._topics_by_subject[master_subject.id] = topics

        self.view.exercise_content_widget.subject_combobox.clear()
        self.view.exercise_content_widget.subject_combobox.addItem("Select Subject", userData=None) # Use None for placeholder
        for subject in self._subjects:
            self.view.exercise_content_widget.subject_combobox.addItem(subject.name, userData=subject.id)

        # Clear topic combobox initially
        self.view.exercise_content_widget.topic_combobox.clear()
        self.view.exercise_content_widget.topic_combobox.addItem("Select Topic (Optional)", userData=None)

    def _on_subject_selected(self, index: int):
        self.view.exercise_content_widget.topic_combobox.clear()
        self.view.exercise_content_widget.topic_combobox.addItem("Select Topic (Optional)", userData=None)

        if index == 0: # "Select Subject" item
            return

        subject_id = self.view.exercise_content_widget.subject_combobox.currentData()
        if subject_id:
            topics = self._topics_by_subject.get(subject_id, [])
            for topic in topics:
                self.view.exercise_content_widget.topic_combobox.addItem(topic.name, userData=topic.id)

    def _log_session(self):
        if self._current_user_id is None or self._current_cycle_id is None:
            QMessageBox.warning(self.view, "Error", "User or Cycle not set. Cannot log session.")
            return

        questions_done = self.view.exercise_content_widget.questions_done_spinbox.value()
        questions_correct = self.view.exercise_content_widget.questions_correct_spinbox.value()
        
        selected_subject_id = self.view.exercise_content_widget.subject_combobox.currentData()
        if selected_subject_id is None:
            QMessageBox.warning(self.view, "Error", "Please select a subject.")
            return
        
        selected_topic_id = self.view.exercise_content_widget.topic_combobox.currentData()
        # If "Select Topic (Optional)" is selected, currentData() might be None
        # It's already set to None for the placeholder, so no extra check needed.

        # Get current UTC time for logging
        log_time_iso = datetime.now(timezone.utc).isoformat()

        try:
            self.session_service.log_manual_session(
                user_id=self._current_user_id,
                cycle_id=self._current_cycle_id,
                subject_id=selected_subject_id,
                topic_id=selected_topic_id,
                start_datetime_iso=log_time_iso,
                total_questions_done=questions_done,
                total_questions_correct=questions_correct,
                duration_minutes=0, # Manual logging doesn't explicitly track duration from UI
                description="Manual session log from Training Screen"
            )
            QMessageBox.information(self.view, "Success", "Session logged successfully!")
            # Optionally clear inputs or update UI
            self.view.exercise_content_widget.questions_done_spinbox.setValue(0)
            self.view.exercise_content_widget.questions_correct_spinbox.setValue(0)
            self.view.exercise_content_widget.subject_combobox.setCurrentIndex(0) # Reset subject
        except Exception as e:
            log.error(f"Failed to log session: {e}", exc_info=True)
            QMessageBox.critical(self.view, "Error", f"Failed to log session: {e}")
