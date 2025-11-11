# app/feature/rebalancer/rebalance_controller.py

import logging

from PySide6.QtWidgets import QMessageBox

from app.common.error_handler import show_error_message
from app.core import business_logic
from app.core.signals import app_signals
from app.services.interfaces import ICycleSubjectService, IPerformanceService, IStudyQueueService
from .rebalance_view import RebalanceView

log = logging.getLogger(__name__)


class RebalanceController:
    def __init__(self, cycle_id: int, cycle_subject_service: ICycleSubjectService,
                 performance_service: IPerformanceService, study_queue_service: IStudyQueueService,
                 parent_view=None):
        self.cycle_id = cycle_id
        self.parent_view = parent_view
        self.cycle_subject_service = cycle_subject_service
        self.performance_service = performance_service
        self.study_queue_service = study_queue_service
        log.debug(f"Initializing RebalanceController for cycle_id: {cycle_id}")

        subjects_in_cycle = self.cycle_subject_service.get_subjects_for_cycle(self.cycle_id)
        performance_summary = self.performance_service.get_summary(self.cycle_id)

        self.suggestions = business_logic.suggest_rebalance(subjects_in_cycle, performance_summary)
        log.info(f"Generated {len(self.suggestions)} rebalance suggestions.")

        self._view = RebalanceView(parent=self.parent_view)
        self._view.populate_suggestions(self.suggestions)
        self._view.rebalance_accepted.connect(self.apply_rebalance)

    def show(self):
        log.debug("Showing rebalance dialog.")
        self._view.exec()

    def apply_rebalance(self, accepted_suggestions: list):
        log.info(f"Applying {len(accepted_suggestions)} rebalance suggestions for cycle_id: {self.cycle_id}")
        if not accepted_suggestions:
            log.warning("apply_rebalance called with no suggestions. Aborting.")
            return
        try:
            for sugg in accepted_suggestions:
                self.cycle_subject_service.update_cycle_subject_difficulty(sugg['cycle_subject_id'], sugg['new_difficulty'])

            all_subjects_in_cycle = self.cycle_subject_service.get_subjects_for_cycle(self.cycle_id)

            for cycle_subject in all_subjects_in_cycle:
                new_final_weight = business_logic.calculate_final_weight(
                    cycle_subject.relevance_weight, cycle_subject.volume_weight, cycle_subject.difficulty_weight
                )
                new_num_blocks = business_logic.calculate_num_blocks(new_final_weight)
                self.cycle_subject_service.update_cycle_subject_calculated_fields(cycle_subject.id, new_final_weight,
                                                                            new_num_blocks)

            updated_subjects = self.cycle_subject_service.get_subjects_for_cycle(self.cycle_id)
            active_subjects = [cs for cs in updated_subjects if cs.is_active]
            new_queue = business_logic.generate_study_queue(active_subjects)
            self.study_queue_service.save_queue(self.cycle_id, new_queue)

            QMessageBox.information(self.parent_view, "Success", "Your study cycle has been rebalanced!")
            app_signals.data_changed.emit()
        except Exception as e:
            log.error("Failed to apply rebalance changes.", exc_info=True)
            show_error_message(self.parent_view, "Error", f"Could not apply changes.", details=str(e))