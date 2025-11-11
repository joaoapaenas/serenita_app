# app/features/main_window/plan_manager.py
import logging
from datetime import date
from typing import List, Dict, Any

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from app.core.tutor_engine.input_assembler import V20InputAssembler
from .tutor_runner import TutorRunner

log = logging.getLogger(__name__)


class PlanManager(QObject):
    """
    Manages the state and lifecycle of the V20 study plan. It is responsible
    for caching the plan, triggering regeneration, and handling the results.
    """

    def __init__(self, main_controller):
        super().__init__(main_controller)
        self._main_ctl = main_controller
        self.app_context = main_controller.app_context
        self.cached_v20_plan = None
        self._input_assembler = V20InputAssembler(
            cycle_service=self.app_context.cycle_service,
            cycle_subject_service=self.app_context.cycle_subject_service,
            work_unit_service=self.app_context.work_unit_service,
            session_service=self.app_context.session_service,
            user_service=self.app_context.user_service
        )

    def get_cached_plan(self) -> dict | None:
        return self.cached_v20_plan

    def clear_cache(self):
        self.cached_v20_plan = None
        self._main_ctl.view.sidebar.update_subjects([])

    def mark_session_as_completed(self, completed_cycle_subject_id: int):
        """
        Removes a session from the cached plan, saves the updated plan to the DB, and updates the UI.
        """
        if not self.cached_v20_plan:
            log.warning("Attempted to mark session complete, but no plan is cached.")
            return

        log.info(f"Marking session for cycle_subject_id {completed_cycle_subject_id} as complete in cached plan.")

        recommended_plan = self.cached_v20_plan.get('plan_scaffold', {}).get('recommended_plan', {})
        sessions = recommended_plan.get('sessions', [])
        session_to_remove = next((s for s in sessions if s.get('subject_id') == completed_cycle_subject_id), None)

        if session_to_remove:
            sessions.remove(session_to_remove)
            log.debug(f"Removed session '{session_to_remove.get('subject_name')}' from cached plan.")

            # --- ADD THIS LINE ---
            # Persist the change immediately to the database
            self.app_context.cycle_service.save_plan_cache(self._main_ctl.active_cycle.id, self.cached_v20_plan)
            # --- END ADD ---

        else:
            log.warning(f"Could not find session with cycle_subject_id {completed_cycle_subject_id} in the cached plan to remove it.")

        self._main_ctl.navigator.show_dual_plan_view(self.cached_v20_plan)
        self._main_ctl.update_action_states()

    def regenerate_plan(self):
        """Asynchronously regenerates the study plan using the Tutor engine."""
        if not self._main_ctl.active_cycle:
            log.warning("regenerate_plan called with no active cycle.")
            return

        log.info("Regenerating study plan using v20 Tutor Engine...")
        self._main_ctl.navigator.show_loading_view()

        cycle_config = self._input_assembler.assemble(
            self._main_ctl.active_cycle,
            self._main_ctl.current_user
        )
        runner = TutorRunner(cycle_config, self.app_context.cycle_subject_service)
        runner.signals.finished.connect(self._on_plan_generation_finished)
        runner.signals.error.connect(self._on_plan_generation_error)
        self._main_ctl.threadpool.start(runner)

    def update_human_factor_and_replan(self, factor_data: dict):
        """Saves the user's human factor input and triggers a replan."""
        today_str = date.today().isoformat()
        self.app_context.user_service.save_human_factor(
            self._main_ctl.current_user.id, today_str,
            factor_data['energy_level'],
            factor_data['stress_level']
        )
        self._main_ctl.refresh_data_and_views(force_replan=True)

    def on_work_unit_completed(self, work_unit_id: str):
        """Persists the completion status of a work unit."""
        log.info(f"Persisting completion for work unit '{work_unit_id}'.")
        if not self.cached_v20_plan: return

        all_wus = [wu for subject in self.cached_v20_plan.get('subjects', []) for wu in subject.work_units]
        target_wu = next((wu for wu in all_wus if wu.unit_id == work_unit_id), None)

        if target_wu:
            target_wu.is_completed = True
            self.app_context.work_unit_service.update_work_unit_status(target_wu.id, is_completed=True)
            log.debug("Work unit status persisted in cache and DB.")
        else:
            log.error(f"Could not find work unit with unit_id '{work_unit_id}' to mark as complete.")

    def _on_plan_generation_finished(self, v20_plan: dict):
        """Handles the successful generation of a new plan."""
        log.debug("Plan generation finished. Caching and updating UI.")

        # Re-fetch the full subject models which include work_units, as the plan only has IDs.
        full_subjects = self._input_assembler.assemble(
            self._main_ctl.active_cycle,
            self._main_ctl.current_user
        )['subjects']
        v20_plan['subjects'] = full_subjects

        self._enrich_plan_with_study_times(v20_plan)

        # --- MODIFICATION START ---
        # Add a generation date to the plan before caching
        v20_plan['generation_date'] = date.today().isoformat()
        self.cached_v20_plan = v20_plan

        # Save the ENTIRE plan to the database, not just a small snapshot
        self.app_context.cycle_service.save_plan_cache(self._main_ctl.active_cycle.id, self.cached_v20_plan)
        # --- MODIFICATION END ---

        self._main_ctl.view.sidebar.update_subjects(v20_plan.get('processed_subjects', []))
        self._main_ctl.navigator.show_dual_plan_view(self.cached_v20_plan)
        self._main_ctl.update_action_states()

        # Force update the toolbar to ensure the start session button shows the correct subject
        self._main_ctl.toolbar_manager.update_visibility_and_state()

    def load_and_validate_cached_plan(self):
        """
        Tries to load a plan from the DB cache. If it exists and was generated
        today, it's considered valid and loaded into memory. Otherwise, the cache is cleared.
        """
        if not self._main_ctl.active_cycle:
            self.clear_cache()
            return

        plan_from_db = self.app_context.cycle_service.get_plan_cache(self._main_ctl.active_cycle.id)
        if plan_from_db and plan_from_db.get('generation_date') == date.today().isoformat():
            log.info("Found a valid plan for today in the database cache. Loading it.")
            self.cached_v20_plan = plan_from_db
        else:
            log.info("No valid plan found for today in the cache. A new one will be generated.")
            self.clear_cache()

    def _enrich_plan_with_study_times(self, v20_plan: dict):
        """Adds recent study times to the plan for UI display."""
        user_id = self._main_ctl.current_user.id
        perf_service = self.app_context.performance_service

        time_7d_map = perf_service.get_study_time_summary(user_id, 7)
        time_30d_map = perf_service.get_study_time_summary(user_id, 30)

        for subject_data in v20_plan.get('processed_subjects', []):
            cycle_subject_id = subject_data.get('subject_id')
            original_subject_model = next((s for s in v20_plan['subjects'] if s.id == cycle_subject_id), None)

            if original_subject_model:
                master_subject_id = original_subject_model.subject_id
                subject_data['study_time_7d'] = time_7d_map.get(master_subject_id, 0)
                subject_data['study_time_30d'] = time_30d_map.get(master_subject_id, 0)
            else:
                subject_data['study_time_7d'] = 0
                subject_data['study_time_30d'] = 0

    def _on_plan_generation_error(self, error_message: str):
        log.error(f"Plan generation failed: {error_message}")
        QMessageBox.critical(self._main_ctl.view, "Planning Error",
                             f"Could not generate study plan: {error_message}")
        self._main_ctl.navigator.show_overview()