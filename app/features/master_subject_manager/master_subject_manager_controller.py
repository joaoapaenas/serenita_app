# app/features/master_subject_manager/master_subject_manager_controller.py

import logging

from PySide6.QtWidgets import QMessageBox

from app.common.error_handler import show_error_message
from app.core.signals import app_signals
from app.services.interfaces import IMasterSubjectService
from app.models.subject import Subject
from .master_subject_editor_dialog import MasterSubjectEditorDialog
from .master_subject_manager_view import MasterSubjectManagerView

log = logging.getLogger(__name__)


class MasterSubjectManagerController:
    """
    Controller for the MasterSubjectManagerView.
    """

    def __init__(self, view: MasterSubjectManagerView,
                 master_subject_service: IMasterSubjectService,
                 navigator):
        self._view = view
        self._service = master_subject_service
        self._navigator = navigator
        self._connect_signals()
        self.load_data()

    def _connect_signals(self):
        self._view.add_requested.connect(self._on_add)
        self._view.edit_requested.connect(self._on_edit)
        self._view.delete_requested.connect(self._on_delete)
        self._view.back_requested.connect(self._navigator.show_configurations_landing)
        app_signals.data_changed.connect(self.load_data)

    def load_data(self):
        """Loads all master subjects from the service and populates the view."""
        try:
            subjects = self._service.get_all_master_subjects()
            self._view.populate_subjects(subjects)
        except Exception as e:
            show_error_message(self._view, "Error", "Could not load subjects.", str(e))

    def _on_add(self):
        """Handles the request to add a new subject."""
        dialog = MasterSubjectEditorDialog(parent=self._view)
        if dialog.exec():
            new_name = dialog.get_subject_name()
            if new_name:
                try:
                    self._service.create(new_name)
                    log.info(f"New master subject '{new_name}' created.")
                    app_signals.data_changed.emit() # Reload data in all relevant views
                except Exception as e:
                    show_error_message(self._view, "Error", f"Could not create subject '{new_name}'.", str(e))

    def _on_edit(self, subject: Subject):
        """Handles the request to edit an existing subject."""
        dialog = MasterSubjectEditorDialog(subject_name=subject.name, parent=self._view)
        if dialog.exec():
            new_name = dialog.get_subject_name()
            if new_name and new_name != subject.name:
                try:
                    self._service.update(subject.id, new_name)
                    log.info(f"Master subject {subject.id} renamed to '{new_name}'.")
                    app_signals.data_changed.emit()
                except Exception as e:
                    show_error_message(self._view, "Error", f"Could not update subject '{subject.name}'.", str(e))

    def _on_delete(self, subject: Subject):
        """Handles the request to delete a subject."""
        reply = QMessageBox.warning(
            self._view,
            "Confirm Deletion",
            f"Are you sure you want to delete '{subject.name}'?\n\n" 
            "This will remove the subject from the master list. It will NOT remove it from "
            "existing cycles, but it will no longer be available to add to new cycles.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._service.delete(subject.id)
                log.info(f"Master subject '{subject.name}' (ID: {subject.id}) deleted.")
                app_signals.data_changed.emit()
            except Exception as e:
                show_error_message(self._view, "Error", f"Could not delete subject '{subject.name}'.", str(e))