# app/feature/cycle_manager/cycle_manager_controller.py

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack

from app.services.interfaces import ICycleService
from ..cycle_editor.components.cycle_command_factory import CycleCommandFactory
from .cycle_manager_view import CycleManagerView

log = logging.getLogger(__name__)


class CycleManagerController(QObject):
    creation_requested = Signal()
    edit_requested_with_id = Signal(int)

    def __init__(self, view: CycleManagerView, undo_stack: QUndoStack,
                 cycle_service: ICycleService):
        super().__init__(view)
        self._view = view
        self.undo_stack = undo_stack
        self.cycle_service = cycle_service

        # The command factory is now created on-demand where needed,
        # or would be injected if it had more complex dependencies.
        # For now, we remove it as a long-lived instance variable.

        self._view.create_new_requested.connect(self.creation_requested.emit)
        self._view.delete_requested.connect(self.delete_cycle)
        self._view.set_active_requested.connect(self.set_cycle_active)
        self._view.edit_requested.connect(self.edit_requested_with_id.emit)

    def load_data(self):
        """Fetches data and populates the view. Called after initialization."""
        log.debug("CycleManagerController loading its data.")
        active_cycle = self.cycle_service.get_active()
        # A more robust app would manage the current exam context explicitly.
        # For now, we get it from the active cycle or a default.
        exam_id = active_cycle.exam_id if active_cycle else 1  # Placeholder exam_id
        cycles = self.cycle_service.get_all_for_exam(exam_id)
        self._view.populate_table(cycles)

    def delete_cycle(self, cycle_id: int):
        log.info(f"Queueing DeleteCycleCommand for cycle_id: {cycle_id}")
        # Command instantiation is simple, no need for a factory here.
        from ..cycle_editor.components.cycle_commands import DeleteCycleCommand
        command = DeleteCycleCommand(cycle_id, self.cycle_service)
        self.undo_stack.push(command)

    def set_cycle_active(self, cycle_id: int):
        log.info(f"Queueing SetActiveCycleCommand for cycle_id: {cycle_id}")
        from ..cycle_editor.components.cycle_commands import SetActiveCycleCommand
        active_cycle = self.cycle_service.get_active()
        previously_active_id = active_cycle.id if active_cycle else None

        if previously_active_id != cycle_id:
            command = SetActiveCycleCommand(cycle_id, previously_active_id, self.cycle_service)
            self.undo_stack.push(command)