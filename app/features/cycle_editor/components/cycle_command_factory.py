# app/features/cycle_editor/components/cycle_command_factory.py
import logging

from PySide6.QtGui import QUndoCommand

from app.core.builders import CycleBuilder
from app.services.interfaces import (ICycleService, ICycleSubjectService, IMasterSubjectService,
                                     IStudyQueueService)
from .cycle_commands import CreateCycleCommand, EditCycleCommand, DeleteCycleCommand, SetActiveCycleCommand

log = logging.getLogger(__name__)


class CycleCommandFactory:
    """A factory for creating QUndoCommand instances for cycle operations."""

    def __init__(self, cycle_service: ICycleService, cycle_subject_service: ICycleSubjectService,
                 master_subject_service: IMasterSubjectService, study_queue_service: IStudyQueueService):
        self.cycle_service = cycle_service
        self.cycle_subject_service = cycle_subject_service
        self.master_subject_service = master_subject_service
        self.study_queue_service = study_queue_service

    def _create_builder(self) -> CycleBuilder:
        """Helper to instantiate the builder with all necessary services."""
        return CycleBuilder(
            self.cycle_service,
            self.cycle_subject_service,
            self.master_subject_service,
            self.study_queue_service
        )

    def create_new_cycle_command(self, exam_id: int, cycle_data: dict, subjects_data: list,
                                 parent: QUndoCommand | None = None) -> CreateCycleCommand:
        """Creates a command to build a new cycle."""
        log.debug(f"Factory creating CreateCycleCommand for exam_id {exam_id}")
        return CreateCycleCommand(
            exam_id=exam_id,
            cycle_data=cycle_data,
            subjects_data=subjects_data,
            builder=self._create_builder(),
            parent=parent
        )

    def create_edit_cycle_command(self, cycle_id: int, old_data: dict, new_data: dict,
                                  parent: QUndoCommand | None = None) -> EditCycleCommand:
        """Creates a command to edit an existing cycle."""
        log.debug(f"Factory creating EditCycleCommand for cycle_id {cycle_id}")
        return EditCycleCommand(
            cycle_id=cycle_id,
            old_data=old_data,
            new_data=new_data,
            builder=self._create_builder(),
            parent=parent
        )

    def create_delete_cycle_command(self, cycle_id: int, parent: QUndoCommand | None = None) -> DeleteCycleCommand:
        """Creates a command to delete a cycle."""
        log.debug(f"Factory creating DeleteCycleCommand for cycle_id {cycle_id}")
        return DeleteCycleCommand(
            cycle_id=cycle_id,
            cycle_service=self.cycle_service,
            parent=parent
        )

    def create_set_active_cycle_command(self, cycle_id_to_activate: int,
                                        parent: QUndoCommand | None = None) -> SetActiveCycleCommand:
        """Creates a command to set the active cycle."""
        log.debug(f"Factory creating SetActiveCycleCommand for cycle_id {cycle_id_to_activate}")
        active_cycle = self.cycle_service.get_active()
        previously_active_id = active_cycle.id if active_cycle else None

        if previously_active_id == cycle_id_to_activate:
            return None  # No command needed if it's already active

        return SetActiveCycleCommand(
            cycle_id_to_activate=cycle_id_to_activate,
            previously_active_id=previously_active_id,
            cycle_service=self.cycle_service,
            parent=parent
        )