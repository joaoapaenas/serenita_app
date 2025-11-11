# app/features/cycle_editor/components/cycle_commands.py

import logging

from PySide6.QtGui import QUndoCommand

from app.core.builders import CycleBuilder
from app.core.signals import app_signals
from app.services.interfaces import ICycleService

log = logging.getLogger(__name__)


class CreateCycleCommand(QUndoCommand):
    """An undoable command for creating a new study cycle. Uses CycleBuilder."""

    def __init__(self, exam_id: int, cycle_data: dict, subjects_data: list,
                 builder: CycleBuilder, parent: QUndoCommand | None = None):
        super().__init__(parent)
        self.exam_id = exam_id
        self.cycle_data = cycle_data
        self.subjects_data = subjects_data
        self.builder = builder
        self._new_cycle_id = None
        self.setText(f"Create Cycle '{self.cycle_data['name']}'")

    def redo(self):
        log.info(f"Executing CreateCycleCommand via Builder for cycle '{self.cycle_data['name']}'")
        self.builder._cycle_service.set_all_inactive()
        self._new_cycle_id = (self.builder.for_exam(self.exam_id)
                              .with_properties(self.cycle_data)
                              .with_subjects(self.subjects_data)
                              .build())
        app_signals.data_changed.emit()

    def undo(self):
        if self._new_cycle_id is None: return
        log.info(f"Undoing CreateCycleCommand for cycle_id: {self._new_cycle_id}")
        self.builder._cycle_service.soft_delete(self._new_cycle_id)
        app_signals.data_changed.emit()


class EditCycleCommand(QUndoCommand):
    """An undoable command for editing an existing study cycle. Uses CycleBuilder."""

    def __init__(self, cycle_id: int, old_data: dict, new_data: dict,
                 builder: CycleBuilder, parent: QUndoCommand | None = None):
        super().__init__(parent)
        self.cycle_id = cycle_id
        self.old_data = old_data
        self.new_data = new_data
        self.builder = builder
        self.setText(f"Edit Cycle '{old_data['cycle_data']['name']}'")

    def redo(self):
        log.info(f"Executing EditCycleCommand via Builder for cycle_id: {self.cycle_id}")
        self._apply_data(self.new_data)
        app_signals.data_changed.emit()

    def undo(self):
        log.info(f"Undoing EditCycleCommand for cycle_id: {self.cycle_id}")
        self._apply_data(self.old_data)
        app_signals.data_changed.emit()

    def _apply_data(self, data_to_apply: dict):
        if data_to_apply['cycle_data'].get('is_active', False):
            self.builder._cycle_service.set_all_inactive()
        (self.builder.from_existing(self.cycle_id)
         .with_properties(data_to_apply['cycle_data'])
         .with_subjects(data_to_apply['subjects_data'])
         .build())


class DeleteCycleCommand(QUndoCommand):
    """An undoable command for deleting a study cycle."""

    def __init__(self, cycle_id: int,
                 cycle_service: ICycleService,
                 parent: QUndoCommand | None = None):
        super().__init__(parent)
        self.cycle_id = cycle_id
        self._cycle_name_for_text = ""
        self.setText("Delete Cycle")
        self.cycle_service = cycle_service

    def redo(self):
        """Performs the soft-deletion."""
        log.info(f"Executing DeleteCycleCommand for cycle_id: {self.cycle_id}")
        cycle = self.cycle_service.get_by_id(self.cycle_id)
        if not cycle:
            log.error(f"Cannot delete cycle {self.cycle_id}: it does not exist.")
            self.setObsolete(True)
            return
        self._cycle_name_for_text = cycle.name
        self.setText(f"Delete Cycle '{self._cycle_name_for_text}'")
        self.cycle_service.soft_delete(self.cycle_id)
        app_signals.data_changed.emit()

    def undo(self):
        """Restores the soft-deleted cycle."""
        if self.cycle_id is None: return
        log.info(f"Undoing DeleteCycleCommand for cycle_id '{self.cycle_id}'")
        self.cycle_service.restore_soft_deleted(self.cycle_id)
        app_signals.data_changed.emit()


class SetActiveCycleCommand(QUndoCommand):
    """An undoable command for changing the active cycle."""

    def __init__(self, cycle_id_to_activate: int, previously_active_id: int | None,
                 cycle_service: ICycleService, parent: QUndoCommand | None = None):
        super().__init__(parent)
        self.cycle_id_to_activate = cycle_id_to_activate
        self.previously_active_id = previously_active_id
        self.setText("Set Active Cycle")
        self.cycle_service = cycle_service

    def redo(self):
        log.info(f"Executing SetActiveCycleCommand for cycle_id: {self.cycle_id_to_activate}")
        self.cycle_service.set_active(self.cycle_id_to_activate)
        app_signals.data_changed.emit()

    def undo(self):
        log.info(f"Undoing SetActiveCycleCommand. Restoring active status to cycle_id: {self.previously_active_id}")
        if self.previously_active_id:
            self.cycle_service.set_active(self.previously_active_id)
        else:
            self.cycle_service.set_all_inactive()
        app_signals.data_changed.emit()