# app/feature/cycle_editor/cycle_editor_controller.py

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QMessageBox

from app.core.builders import CycleBuilder
from app.models.subject import Subject
from app.services.interfaces import (ICycleService, IMasterSubjectService, ICycleSubjectService, IStudyQueueService)
from .components.cycle_commands import EditCycleCommand, CreateCycleCommand
from .cycle_editor_view import CycleEditorView

log = logging.getLogger(__name__)


class CycleEditorController(QObject):
    save_completed = Signal()
    editing_cancelled = Signal()

    def __init__(self, view: CycleEditorView, exam_id: int, cycle_id: int | None, undo_stack: QUndoStack,
                 cycle_service: ICycleService, master_subject_service: IMasterSubjectService,
                 cycle_subject_service: ICycleSubjectService, study_queue_service: IStudyQueueService):
        super().__init__(view)
        self._view = view
        self.exam_id = exam_id
        self._cycle_id = cycle_id
        self.undo_stack = undo_stack
        self._cycle_service = cycle_service
        self._master_subject_service = master_subject_service
        self._cycle_subject_service = cycle_subject_service
        self._study_queue_service = study_queue_service
        self.old_data_for_undo = None

        self._view.save_requested.connect(self.save_cycle)
        self._view.cancel_requested.connect(self.editing_cancelled.emit)
        self._view.master_subject_add_requested.connect(self._on_add_master_subject)

    def load_data_into_view(self):
        """Fetches data and populates the injected view after initialization."""
        master_subjects = self._master_subject_service.get_all_master_subjects()
        cycle_to_edit_data = None
        subjects_in_cycle = None

        if self._cycle_id:
            cycle_model = self._cycle_service.get_by_id(self._cycle_id)
            if cycle_model:
                cycle_to_edit_data = {
                    'id': cycle_model.id, 'cycle_name': cycle_model.name,
                    'block_duration_min': cycle_model.block_duration_min,
                    'is_continuous': cycle_model.is_continuous,
                    'daily_goal_blocks': cycle_model.daily_goal_blocks,
                    'timing_strategy': cycle_model.timing_strategy
                }
                subjects_in_cycle = self._cycle_subject_service.get_subjects_for_cycle(self._cycle_id)
                self.old_data_for_undo = {
                    "cycle_data": {
                        'name': cycle_model.name, 'duration': cycle_model.block_duration_min,
                        'is_continuous': cycle_model.is_continuous, 'daily_goal': cycle_model.daily_goal_blocks,
                        'is_active': cycle_model.is_active,
                        'timing_strategy': cycle_model.timing_strategy
                    },
                    "subjects_data": [
                        {"name": s.name, "relevance": s.relevance_weight, "volume": s.volume_weight,
                         "difficulty": s.difficulty_weight, "is_active": s.is_active} for s in subjects_in_cycle
                    ]
                }
        self._view.populate_data(cycle_to_edit_data, subjects_in_cycle, master_subjects)

    def _on_add_master_subject(self, name: str):
        log.info(f"Attempting to add new master subject: '{name}'")
        new_id = self._master_subject_service.add_master_subject(name)
        if new_id:
            log.info(f"Successfully added master subject '{name}' with new ID: {new_id}")
            new_subject_model = Subject(id=new_id, name=name, color=None, created_at="", updated_at="",
                                        soft_delete=False, deleted_at=None)
            self._view.get_subject_selector().add_new_master_subject(new_subject_model, check_item=True)
        else:
            log.warning(f"Failed to add master subject '{name}'. It likely already exists.")
            QMessageBox.warning(self._view, "Duplicate Subject", f"The subject '{name}' already exists.")

    def save_cycle(self, cycle_data: dict, subjects_data: list):
        log.info(f"Queueing save command for cycle: '{cycle_data['name']}'")
        builder = CycleBuilder(self._cycle_service, self._cycle_subject_service, self._master_subject_service,
                               self._study_queue_service)

        if self._cycle_id:
            new_data = {"cycle_data": cycle_data, "subjects_data": subjects_data}
            command = EditCycleCommand(self._cycle_id, self.old_data_for_undo, new_data, builder)
        else:
            command = CreateCycleCommand(self.exam_id, cycle_data, subjects_data, builder)

        self.undo_stack.push(command)
        self.save_completed.emit()