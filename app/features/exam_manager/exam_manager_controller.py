# app/features/exam_manager/exam_manager_controller.py

import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from app.core.signals import app_signals
from app.services.interfaces import IExamService
from .exam_manager_view import ExamManagerView

log = logging.getLogger(__name__)

class ExamManagerController(QObject):
    """Controller for the exam management view."""

    def __init__(self, view: ExamManagerView, user_id: int, exam_service: IExamService, navigator):
        super().__init__(view)
        self._view = view
        self.user_id = user_id
        self.exam_service = exam_service
        self.navigator = navigator

        self._view.create_new_requested.connect(
            lambda: self.navigator.show_exam_editor(exam_id=None)
        )
        self._view.edit_requested.connect(
            lambda exam_id: self.navigator.show_exam_editor(exam_id=exam_id)
        )
        self._view.delete_requested.connect(self.delete_exam)

    def load_data(self):
        """Fetches data and populates the view."""
        log.debug(f"ExamManagerController loading exams for user_id: {self.user_id}")
        exams = self.exam_service.get_all_for_user(self.user_id)
        self._view.populate_table(exams)

    def delete_exam(self, exam_id: int):
        log.info(f"Delete requested for exam_id: {exam_id}")

        reply = QMessageBox.question(
            self._view,
            "Confirm Delete",
            "Are you sure you want to delete this exam? This will also delete all associated study cycles and history. This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.exam_service.soft_delete(exam_id)
            log.info(f"Soft deleted exam_id: {exam_id}")
            self.load_data()  # Refresh the view
            app_signals.data_changed.emit()