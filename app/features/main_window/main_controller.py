# app/features/main_window/main_controller.py

import logging
from typing import Optional, Dict, Any

from PySide6.QtCore import QObject, QThreadPool
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QWidget, QMessageBox

from app.core import business_logic
from app.core.context import AppContext
from app.core.signals import app_signals
from app.features.rebalancer.rebalance_controller import RebalanceController
from app.models.user import User
from .action_factory import ActionFactory
from .navigator import Navigator
from .plan_manager import PlanManager
from .session_manager import SessionManager
from .toolbar_manager import ToolbarManager
from .view_controller_factory import ViewControllerFactory

log = logging.getLogger(__name__)


class MainWindowController(QObject):
    def __init__(self, view, current_user: User, app_context: AppContext):
        super().__init__()
        self.view = view
        self.current_user = current_user
        self.app_context = app_context

        self.undo_stack = QUndoStack(self.view)
        self.threadpool = QThreadPool.globalInstance()
        self.action_factory = ActionFactory(self.view, self.undo_stack)

        self.active_cycle = None
        self._next_session_data = None
        self.current_main_widget: QWidget | None = None
        self.onboarding_page_cache: int = 0

        self.navigator = Navigator(self)
        self.view_controller_factory = ViewControllerFactory(app_context, self.navigator)
        self.navigator.set_factory(self.view_controller_factory)

        self.toolbar_manager = ToolbarManager(self)
        self.session_manager = SessionManager(self)
        self.plan_manager = PlanManager(self)

        self._connect_signals_and_actions()
        self._populate_ui()
        self.refresh_data_and_views(force_replan=True)

    def _connect_signals_and_actions(self):
        # Top-level actions owned by the main window
        self.action_factory.new_cycle_action.triggered.connect(self.launch_cycle_creator)
        self.action_factory.start_session_action.triggered.connect(self._on_start_next_session)
        self.action_factory.rebalance_action.triggered.connect(self.launch_rebalancer)
        self.action_factory.help_action.triggered.connect(self.navigator.show_help)

        # Connections to global and manager signals
        self.view.navigation_requested.connect(self.navigator.handle_navigation)
        app_signals.data_changed.connect(lambda: self.refresh_data_and_views(force_replan=True))
        self.session_manager.rebalance_prompt_requested.connect(self.prompt_for_rebalance)

    def _populate_ui(self):
        self.action_factory.populate_menu_bar(self.view.menuBar())
        self.action_factory.populate_tool_bar(self.view.get_toolbar())
        self.toolbar_manager.setup_widgets(self.view.get_toolbar())

    def refresh_data_and_views(self, force_replan: bool = False):
        log.debug(f"Refreshing views. Force replan: {force_replan}")
        if self.session_manager.is_session_active():
            log.warning("Refresh called while session is active. Aborting and showing session view.")
            self.navigator.show_active_session()
            return

        self.active_cycle = self.app_context.cycle_service.get_active()
        self.navigator.set_active_cycle(self.active_cycle)

        # --- MODIFICATION START ---
        # On a normal refresh, try to load a valid plan from today's cache first.
        if not force_replan:
            self.plan_manager.load_and_validate_cached_plan()
        else:
            self.plan_manager.clear_cache() # If forcing, clear the cache first.
        # --- MODIFICATION END ---

        self.toolbar_manager.update_visibility_and_state()

        if self.active_cycle:
            # The condition is now simpler: if there's no cached plan, regenerate it.
            if not self.plan_manager.get_cached_plan():
                self.plan_manager.regenerate_plan()
            else:
                log.info("Displaying cached plan without regeneration.")
                cached_plan = self.plan_manager.get_cached_plan()
                if cached_plan:
                    self.view.sidebar.update_subjects(cached_plan.get('processed_subjects', []))
                    # Refresh the view with the loaded plan
                    self.navigator.show_dual_plan_view(cached_plan)

                # Ensure action states are updated even when using cached plan
                self.update_action_states()
        else:
            self.plan_manager.clear_cache()
            self.navigator.show_overview()
            self.update_action_states()

    def update_action_states(self):
        self._next_session_data = None
        cached_plan = self.plan_manager.get_cached_plan()
        if cached_plan:
            recommended_plan = cached_plan.get('plan_scaffold', {}).get('recommended_plan', {})
            todays_sessions = recommended_plan.get('sessions', [])
            if todays_sessions:
                self._next_session_data = todays_sessions[0]
        can_start_session = self._next_session_data is not None and not self.session_manager.is_session_active()
        self.action_factory.start_session_action.setEnabled(can_start_session)
        # Also update the toolbar manager to ensure UI consistency
        self.toolbar_manager.update_visibility_and_state()

    def _on_start_next_session(self, session_data_override: Optional[Dict[str, Any]] = None):
        if session_data_override:
            self.session_manager.start_study_session(session_data_override)
            return

        cached_plan = self.plan_manager.get_cached_plan()
        if not cached_plan:
            log.warning("Start session requested, but no plan is cached.")
            return

        recommended_plan = cached_plan.get('plan_scaffold', {}).get('recommended_plan', {})
        todays_sessions = recommended_plan.get('sessions', [])
        if not todays_sessions:
            QMessageBox.information(self.view, "Plan Complete", "No more sessions are scheduled in this plan.")
            return

        self.navigator.show_session_choice(todays_sessions[0], todays_sessions[1:])

    def launch_cycle_creator(self):
        log.info("Launch cycle creator action triggered.")
        if not self.current_user: return

        if self.view_controller_factory.is_onboarding_active():
            self.navigator.show_onboarding()
            return

        if not self.active_cycle:
            self.navigator.show_onboarding()
        else:
            self.navigator.show_cycle_editor(exam_id=self.active_cycle.exam_id, cycle_id=None)

    def launch_rebalancer(self):
        if not self.active_cycle: return
        log.info("Rebalance action triggered. Launching rebalancer dialog.")
        rebalance_controller = RebalanceController(
            cycle_id=self.active_cycle.id,
            cycle_subject_service=self.app_context.cycle_subject_service,
            performance_service=self.app_context.performance_service,
            study_queue_service=self.app_context.study_queue_service,
            parent_view=self.view
        )
        rebalance_controller.show()

    def prompt_for_rebalance(self):
        if not self.active_cycle: return
        subjects = self.app_context.cycle_subject_service.get_subjects_for_cycle(self.active_cycle.id)
        performance = self.app_context.performance_service.get_summary(self.active_cycle.id)
        suggestions = business_logic.suggest_rebalance(subjects, performance)

        if not suggestions:
            log.info("Rebalance prompt triggered, but no suggestions were generated.")
            return

        reply = QMessageBox.question(
            self.view, "Optimize Your Plan?",
            "We've analyzed your recent performance and have some suggestions to optimize your study plan.\n\n"
            "Would you like to review them now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.launch_rebalancer()

    def on_onboarding_finished(self):
        """Called when the onboarding process is completed successfully."""
        log.info("Onboarding finished. Refreshing data and views.")
        self.refresh_data_and_views(force_replan=True)
        self.navigator.show_overview()

    def on_onboarding_cancelled(self):
        """Called when the onboarding process is cancelled."""
        log.info("Onboarding cancelled.")
        self.navigator.show_overview()