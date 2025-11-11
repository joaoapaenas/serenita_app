# app/features/exam_editor/exam_editor_controller.py
import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from app.common.error_handler import show_error_message
from app.core.builders import CycleBuilder
from app.core.signals import app_signals
from app.services.interfaces import (IExamService, ITemplateSubjectService, IMasterSubjectService,
                                     ICycleSubjectService, IStudyQueueService, ICycleService)
from .exam_editor_view import ExamEditorView

log = logging.getLogger(__name__)


class ExamEditorController(QObject):
    """
    Controller for the Exam Editor widget. Handles both creating a new exam
    and editing an existing one.
    """
    save_completed = Signal()

    def __init__(self, user_id: int, exam_service: IExamService,
                 template_subject_service: ITemplateSubjectService, master_subject_service: IMasterSubjectService,
                 cycle_subject_service: ICycleSubjectService, study_queue_service: IStudyQueueService,
                 cycle_service: ICycleService, parent_view=None, exam_id_to_edit: int | None = None):
        super().__init__(parent_view)
        self._user_id = user_id
        self.exam_service = exam_service
        self.template_subject_service = template_subject_service
        self.master_subject_service = master_subject_service
        self.cycle_subject_service = cycle_subject_service
        self.study_queue_service = study_queue_service
        self.cycle_service = cycle_service
        self.exam_id_to_edit = exam_id_to_edit
        self._view = ExamEditorView(parent=parent_view)
        self._view.save_requested.connect(self.save_exam)

        if self.exam_id_to_edit:
            self._view.set_edit_mode(True)
            exam_model = self.exam_service.get_by_id(self.exam_id_to_edit)
            if exam_model: self._view.set_data(exam_model)
        else:
            self._view.set_edit_mode(False)
            templates = self.exam_service.get_available_templates()
            self._view.populate_templates(templates)

    def get_view(self) -> ExamEditorView:
        return self._view

    def save_exam(self, data: dict):
        if self.exam_id_to_edit:
            self._update_exam(data)
        else:
            self._create_exam(data)

    def _update_exam(self, data: dict):
        log.info(f"Updating exam {self.exam_id_to_edit} with new data.")
        try:
            self.exam_service.update(
                exam_id=self.exam_id_to_edit, name=data["name"], institution=data["institution"],
                role=data["role"], exam_board=data["exam_board"], area=data["area"],
                predicted_exam_date=data["predicted_exam_date"], exam_date=data["exam_date"],
                status="PREVISTO", has_edital=0
            )
            app_signals.data_changed.emit()
            self.save_completed.emit()
        except Exception as e:
            show_error_message(self._view, "Error", "Could not update the exam.", details=str(e))

    def _create_exam(self, data: dict):
        log.info(f"Creating new exam '{data['name']}' for user {self._user_id}.")
        new_id = self.exam_service.create(
            user_id=self._user_id, name=data["name"], institution=data["institution"],
            role=data["role"], exam_board=data["exam_board"], area=data["area"],
            predicted_exam_date=data["predicted_exam_date"], exam_date=data["exam_date"]
        )
        if not new_id:
            show_error_message(self._view, "Error", "Could not create the exam.")
            return
        if template_id := data.get("template_id"):
            self._create_cycle_from_template(new_id, data['name'], template_id)
        app_signals.data_changed.emit()
        self.save_completed.emit()

    def _create_cycle_from_template(self, new_exam_id: int, exam_name: str, template_id: int):
        log.info(f"Exam created from template_id {template_id}. Creating initial study cycle.")
        try:
            template_subjects = self.template_subject_service.get_subjects_for_template(template_id)
            subjects_data = [
                {"name": s['name'], "relevance": s.get('relevance_weight', 3),
                 "volume": s.get('volume_weight', 3), "difficulty": 3, "is_active": True}
                for s in template_subjects
            ]
            cycle_data = {'name': f"Initial Plan for {exam_name}", 'duration': 60,
                          'is_continuous': True, 'daily_goal': 3, 'timing_strategy': 'Adaptive'}
            (CycleBuilder(self.cycle_service, self.cycle_subject_service, self.master_subject_service,
                          self.study_queue_service)
             .for_exam(new_exam_id).with_properties(cycle_data).with_subjects(subjects_data).build())
        except Exception as e:
            log.error(f"Failed to create initial cycle from template for exam {new_exam_id}", exc_info=True)
            QMessageBox.warning(self._view, "Cycle Creation Failed",
                                f"The exam was created, but the initial study cycle could not be "
                                f"generated. You can create one manually.")