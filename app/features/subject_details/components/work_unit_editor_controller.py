# app/features/subject_details/components/work_unit_editor_controller.py

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from app.models.subject import WorkUnit
from app.services.interfaces import IWorkUnitService
from .work_unit_editor_view import WorkUnitEditorView

log = logging.getLogger(__name__)


class WorkUnitEditorController(QObject):
    """Controller for the Work Unit editor dialog."""
    work_unit_saved = Signal()

    def __init__(self, view: WorkUnitEditorView, subject_id: int, work_unit_service: IWorkUnitService,
                 work_unit_to_edit: WorkUnit | None = None):
        super().__init__(view)
        self.subject_id = subject_id
        self.work_unit_service = work_unit_service
        self.work_unit_to_edit = work_unit_to_edit

        self._view = view
        self._view.save_requested.connect(self._on_save_requested)

        if self.work_unit_to_edit:
            self._view.set_data(self.work_unit_to_edit)

    def show(self):
        """Shows the dialog to the user."""
        self._view.exec()

    def _on_save_requested(self, data: dict):
        """Validates data and calls the appropriate service method."""
        if not data['title']:
            QMessageBox.warning(self._view, "Input Error", "The Work Unit title cannot be empty.")
            return

        if self.work_unit_to_edit:
            # --- Edit Mode ---
            success = self.work_unit_service.update_work_unit(self.work_unit_to_edit.id, data)
        else:
            # --- Create Mode ---
            new_unit = self.work_unit_service.add_work_unit(self.subject_id, data)
            success = new_unit is not None

        if success:
            self.work_unit_saved.emit()
            self._view.accept()
        else:
            QMessageBox.critical(self._view, "Database Error", "Could not save the Work Unit. Please check the logs.")