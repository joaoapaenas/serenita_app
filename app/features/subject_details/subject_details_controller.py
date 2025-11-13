# app/features/subject_details/subject_details_controller.py

import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from app.core.signals import app_signals
from app.models.subject import CycleSubject, WorkUnit
from app.services.interfaces import (
    ICycleSubjectService,
    IPerformanceService,
    IWorkUnitService,
)

from .components.work_unit_editor_view import WorkUnitEditorView
from .subject_details_view import SubjectDetailsView

log = logging.getLogger(__name__)


class SubjectDetailsController(QObject):
    def __init__(
        self,
        view: SubjectDetailsView,
        cycle_subject: CycleSubject,
        v20_diagnostics: dict,
        work_unit_service: IWorkUnitService,
        cycle_subject_service: ICycleSubjectService,
        performance_service: IPerformanceService,
    ):
        super().__init__(view)
        self._view = view
        self.work_unit_service = work_unit_service
        self.cycle_subject_service = cycle_subject_service
        self.performance_service = performance_service
        self.cycle_subject = cycle_subject
        self.v20_diagnostics = v20_diagnostics

        self._view.populate_static_data(self.cycle_subject)

        self._view.add_work_unit_requested.connect(self._on_add_work_unit)
        self._view.edit_work_unit_requested.connect(self._on_edit_work_unit)
        self._view.delete_work_unit_requested.connect(self._on_delete_work_unit)
        self._view.prioritize_requested.connect(self._on_prioritize)

    def load_data(self):
        """
        Loads all dynamic data and determines which view mode to use (Getting Started vs Performance Hub).
        """
        self._load_work_units()

        total_questions = self.v20_diagnostics.get("total_questions", 0)
        if total_questions < 10:
            log.debug(
                f"Subject '{self.cycle_subject.name}' has < 10 questions. Showing 'Getting Started' view."
            )
            self._view.set_view_mode("getting_started")
        else:
            log.debug(
                f"Subject '{self.cycle_subject.name}' has sufficient data. Showing 'Performance Hub' view."
            )
            performance_trend = self.performance_service.get_performance_over_time(
                user_id=1, subject_id=self.cycle_subject.subject_id
            )
            topic_performance = self.performance_service.get_topic_performance(
                user_id=1, subject_id=self.cycle_subject.subject_id, days_ago=90
            )
            self._view.set_view_mode(
                "performance_hub",
                diagnostics=self.v20_diagnostics,
                performance_trend=performance_trend,
                topic_performance=topic_performance,
            )

    def _load_work_units(self):
        log.debug(f"Reloading work units for subject: {self.cycle_subject.name}")
        work_units = self.work_unit_service.get_work_units_for_subject(
            self.cycle_subject.subject_id
        )
        self._view.populate_work_units(work_units)

    def _on_add_work_unit(self):
        """Launches the Work Unit editor in 'create' mode."""
        from .components.work_unit_editor_controller import WorkUnitEditorController

        editor_view = WorkUnitEditorView(self._view)
        editor_controller = WorkUnitEditorController(
            view=editor_view,
            subject_id=self.cycle_subject.subject_id,
            work_unit_service=self.work_unit_service,
        )
        editor_controller.work_unit_saved.connect(self._load_work_units)
        editor_controller.show()

    def _on_edit_work_unit(self, work_unit: WorkUnit):
        """Launches the Work Unit editor in 'edit' mode."""
        from .components.work_unit_editor_controller import WorkUnitEditorController

        editor_view = WorkUnitEditorView(self._view)
        editor_controller = WorkUnitEditorController(
            view=editor_view,
            subject_id=self.cycle_subject.subject_id,
            work_unit_service=self.work_unit_service,
            work_unit_to_edit=work_unit,
        )
        editor_controller.work_unit_saved.connect(self._load_work_units)
        editor_controller.show()

    def _on_delete_work_unit(self, work_unit: WorkUnit):
        """Confirms and deletes a Work Unit."""
        reply = QMessageBox.question(
            self._view,
            "Confirm Delete",
            f"Are you sure you want to delete the work unit:\n\n'{work_unit.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.work_unit_service.delete_work_unit(work_unit.id)
            self._load_work_units()

    def _on_prioritize(self):
        """Handles the user's request to increase a subject's priority."""
        current_difficulty = self.cycle_subject.difficulty_weight
        if current_difficulty >= 5:
            QMessageBox.information(
                self._view,
                "Max Priority",
                "This subject is already at maximum priority (Difficulty 5/5).",
            )
            return

        new_difficulty = current_difficulty + 1
        self.cycle_subject_service.update_cycle_subject_difficulty(
            self.cycle_subject.id, new_difficulty
        )
        self.cycle_subject.difficulty_weight = new_difficulty

        QMessageBox.information(
            self._view,
            "Priority Increased",
            f"'{self.cycle_subject.name}' has been prioritized. Its difficulty rating is now {new_difficulty}.\n\n"
            "Your plan will be updated to reflect this change.",
        )
        app_signals.data_changed.emit()
