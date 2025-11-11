# app/commom/subject_editor/subject_editor_controller.py

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from app.common.subject_editor.subject_editor_view import SubjectEditorView

log = logging.getLogger(__name__)


class SubjectEditorController(QObject):
    subject_saved = Signal(dict)

    def __init__(self, parent_view=None):
        super().__init__()
        log.debug("Initializing SubjectEditorController.")
        self._view = SubjectEditorView(parent=parent_view)
        # Connect to the view's raw save signal
        self._view.subject_saved.connect(self._validate_and_relay_save)
        self._view.rejected.connect(self.close)  # Handle user closing the dialog

    def show(self):
        log.debug("Showing subject editor dialog.")
        self._view.exec()

    def _validate_and_relay_save(self, data: dict):
        """
        Receives raw data from the view, validates it, and then either
        relays the 'subject_saved' signal or handles the error.
        """
        log.debug(f"Validating subject data: {data}")
        if not data['name']:
            QMessageBox.warning(self._view, "Validation Error", "Subject name cannot be empty.")
            # Don't close the dialog, let the user fix it.
            return

        # Validation passed, emit the approved data.
        log.info(f"Subject '{data['name']}' validation passed. Relaying signal.")
        self.subject_saved.emit(data)
        # Now we can close the dialog.
        self._view.accept()

    def close(self):
        log.debug("Closing subject editor dialog.")
        self._view.close()
