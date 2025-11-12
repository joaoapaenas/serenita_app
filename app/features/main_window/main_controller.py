# app/features/main_window/main_controller.py

import logging
from typing import Optional, Dict, Any

from PySide6.QtCore import QObject, QThreadPool, Qt
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QWidget, QMessageBox, QLabel, QPushButton

from app.core import business_logic
from app.core.context import AppContext
from app.core.signals import app_signals
from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.features.rebalancer.rebalance_controller import RebalanceController
from app.navigation_service import NavigationService
from app.features.configurations.configurations_landing_view import ConfigurationsLandingView
from app.features.configurations.configurations_landing_controller import ConfigurationsLandingController
from app.features.configurations.app_settings_view import AppSettingsView
from app.features.configurations.configuration_controller import ConfigurationController
from app.features.cycle_manager.cycle_manager_view import CycleManagerView
from app.features.cycle_manager.cycle_manager_controller import CycleManagerController
from app.features.exam_manager.exam_manager_view import ExamManagerView
from app.features.exam_manager.exam_manager_controller import ExamManagerController
from app.features.master_subject_manager.master_subject_manager_view import MasterSubjectManagerView
from app.features.master_subject_manager.master_subject_manager_controller import MasterSubjectManagerController
from app.features.exam_editor.exam_editor_controller import ExamEditorController
from app.features.cycle_editor.cycle_editor_view import CycleEditorView
from app.features.cycle_editor.cycle_editor_controller import CycleEditorController
from app.features.onboarding.onboarding_view import OnboardingView
from app.features.onboarding.onboarding_controller import OnboardingController
from app.features.subject_summary.subject_summary_view import SubjectSummaryView
from app.features.subject_summary.subject_summary_controller import SubjectSummaryController
from app.features.history.history_view import HistoryView
from app.features.history.history_controller import HistoryController
from app.features.subject_details.subject_details_view import SubjectDetailsView
from app.features.subject_details.subject_details_controller import SubjectDetailsController
from app.features.help.help_view import HelpView
from app.features.analitics.analytics_view import AnalyticsView
from app.features.analitics.analytics_controller import AnalyticsController
from app.features.performance_dashboard.performance_dashboard_view import PerformanceDashboardView
from app.features.performance_dashboard.performance_dashboard_controller import PerformanceDashboardController
from app.features.training_screen.training_screen_view import TrainingScreenView
from app.features.training_screen.training_screen_controller import TrainingScreenController
from app.features.performance_graphs.performance_graph_view import PerformanceGraphView
from app.features.performance_graphs.performance_graph_controller import PerformanceGraphController
from app.features.session_choice.session_choice_view import SessionChoiceView
from app.features.session_mode_choice.session_mode_choice_view import SessionModeChoiceView
from app.features.session_mode_choice.session_mode_choice_controller import SessionModeChoiceController
from app.models.user import User
from .action_factory import ActionFactory
from .navigator import Navigator
from .plan_manager import PlanManager
from .session_manager import SessionManager
from .toolbar_manager import ToolbarManager

log = logging.getLogger(__name__)


class MainWindowController(QObject):
    def __init__(self, view, current_user: User, app_context: AppContext, is_dev_mode: bool = False):
        super().__init__()
        self.view = view
        self.current_user = current_user
        self.app_context = app_context
        self.is_dev_mode = is_dev_mode

        self.undo_stack = QUndoStack(self.view)
        self.threadpool = QThreadPool.globalInstance()
        self.action_factory = ActionFactory(self.view, self.undo_stack)

        self.active_cycle = None
        self._next_session_data = None
        self.current_main_widget: QWidget | None = None
        self.onboarding_page_cache: int = 0
        self._active_onboarding_controller: OnboardingController | None = None

        self.navigation_service = NavigationService()
        self.navigator = Navigator(self, self.navigation_service)

        self.toolbar_manager = ToolbarManager(self)
        self.session_manager = SessionManager(self)
        self.plan_manager = PlanManager(self)

        self._register_features()
        self._connect_signals_and_actions()
        self._populate_ui()
        self.refresh_data_and_views(force_replan=True)

    def _register_features(self):
        """Registers all view providers with the NavigationService."""
        # Provider for Configurations Landing
        def create_configurations_landing() -> QWidget:
            view = ConfigurationsLandingView(parent=self.view)
            view.set_developer_mode(self.is_dev_mode)
            controller = ConfigurationsLandingController(
                view=view,
                navigator=self.navigator,
                conn_factory=self.app_context.conn_factory
            )
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("configurations_landing", create_configurations_landing)

        # Provider for App Settings
        def create_app_settings() -> QWidget:
            view = AppSettingsView(parent=self.view)
            controller = ConfigurationController(
                view=view.profile_form,
                user=self.current_user,
                user_service=self.app_context.user_service,
                navigator=self.navigator
            )
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(controller.on_cancel)
            save_button = QPushButton("Save Changes")
            save_button.setObjectName("primaryButton")
            save_button.clicked.connect(controller.on_save)
            view.reset_button.clicked.connect(controller.on_reset)
            view.add_action_button(cancel_button)
            view.add_action_button(save_button)
            controller.load_data()
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("app_settings", create_app_settings)

        # Provider for Cycle Manager
        def create_cycle_manager() -> QWidget:
            view = CycleManagerView(parent=self.view)
            controller = CycleManagerController(
                view=view,
                undo_stack=self.undo_stack,
                cycle_service=self.app_context.cycle_service
            )
            controller.load_data()
            controller.creation_requested.connect(self.launch_cycle_creator)
            active_cycle = self.active_cycle
            controller.edit_requested_with_id.connect(
                lambda cycle_id: self.navigator.show_cycle_editor(active_cycle.exam_id,
                                                                  cycle_id) if active_cycle else None
            )
            app_signals.data_changed.connect(controller.load_data)
            return view

        self.navigation_service.register("cycle_manager", create_cycle_manager)

        # Provider for Exam Manager
        def create_exam_manager() -> QWidget:
            view = ExamManagerView(parent=self.view)
            controller = ExamManagerController(
                view=view, user_id=self.current_user.id,
                exam_service=self.app_context.exam_service, navigator=self.navigator
            )
            controller.load_data()
            app_signals.data_changed.connect(controller.load_data)
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("exam_manager", create_exam_manager)

        # Provider for Master Subject Manager
        def create_master_subject_manager() -> QWidget:
            view = MasterSubjectManagerView(parent=self.view)
            controller = MasterSubjectManagerController(
                view=view,
                master_subject_service=self.app_context.master_subject_service,
                navigator=self.navigator
            )
            view.setProperty("controller", controller)
            return view
        
        self.navigation_service.register("master_subject_manager", create_master_subject_manager)

        # Provider for Exam Editor
        def create_exam_editor(exam_id: int | None) -> QWidget:
            controller = ExamEditorController(
                user_id=self.current_user.id,
                exam_service=self.app_context.exam_service,
                template_subject_service=self.app_context.template_subject_service,
                master_subject_service=self.app_context.master_subject_service,
                cycle_subject_service=self.app_context.cycle_subject_service,
                study_queue_service=self.app_context.study_queue_service,
                cycle_service=self.app_context.cycle_service,
                parent_view=self.view, exam_id_to_edit=exam_id
            )
            view = controller.get_view()
            controller.save_completed.connect(self.navigator.show_exam_manager)
            view.cancel_requested.connect(self.navigator.show_exam_manager)
            return view

        self.navigation_service.register("exam_editor", create_exam_editor)

        # Provider for Cycle Editor
        def create_cycle_editor(exam_id: int, cycle_id: int | None) -> QWidget:
            view = CycleEditorView(parent=self.view)
            controller = CycleEditorController(
                view=view, exam_id=exam_id, cycle_id=cycle_id,
                undo_stack=self.undo_stack,
                cycle_service=self.app_context.cycle_service,
                master_subject_service=self.app_context.master_subject_service,
                cycle_subject_service=self.app_context.cycle_subject_service,
                study_queue_service=self.app_context.study_queue_service
            )
            controller.load_data_into_view()
            controller.save_completed.connect(self.navigator.show_configurations_landing)
            controller.editing_cancelled.connect(self.navigator.show_configurations_landing)
            return view

        self.navigation_service.register("cycle_editor", create_cycle_editor)

        # Provider for Onboarding
        def create_onboarding() -> tuple[QWidget, OnboardingController]:
            view = OnboardingView(parent=self.view)
            controller = OnboardingController(
                view=view,
                user_id=self.current_user.id,
                exam_service=self.app_context.exam_service,
                master_subject_service=self.app_context.master_subject_service,
                template_subject_service=self.app_context.template_subject_service,
                cycle_service=self.app_context.cycle_service,
                cycle_subject_service=self.app_context.cycle_subject_service,
                study_queue_service=self.app_context.study_queue_service,
                work_unit_service=self.app_context.work_unit_service
            )
            self._active_onboarding_controller = controller
            controller.start()

            def on_finished():
                self._active_onboarding_controller = None
                self.on_onboarding_finished()

            def on_cancelled():
                self._active_onboarding_controller = None
                self.on_onboarding_cancelled()

            controller.onboarding_complete.connect(on_finished)
            controller.onboarding_cancelled.connect(on_cancelled)
            return view, controller

        self.navigation_service.register("onboarding", create_onboarding)

        # Provider for Subject Summary
        def create_subject_summary() -> QWidget:
            view = SubjectSummaryView(parent=self.view)
            controller = SubjectSummaryController(
                view=view,
                v20_plan_data=self.plan_manager.get_cached_plan(),
                performance_service=self.app_context.performance_service,
                master_subject_service=self.app_context.master_subject_service,
                user_id=self.current_user.id,
                parent=view
            )
            return view

        self.navigation_service.register("subject_summary", create_subject_summary)

        # Provider for History
        def create_history() -> QWidget:
            active_cycle = self.navigator.active_cycle
            if not active_cycle:
                return QLabel("No active cycle to show history for.")
            view = HistoryView(parent=self.view)
            view.start_session_requested.connect(self._on_start_next_session)
            controller = HistoryController(
                view=view, cycle_id=active_cycle.id,
                session_service=self.app_context.session_service
            )
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("history", create_history)

        # Provider for Subject Details
        def create_subject_details(cycle_subject_id: int) -> QWidget:
            cached_plan = self.plan_manager.get_cached_plan()
            subject_diag = next((s for s in cached_plan.get('processed_subjects', []) if
                                 s['subject_id'] == cycle_subject_id), {}) if cached_plan else {}
            cycle_subject = self.app_context.cycle_subject_service.get_cycle_subject(cycle_subject_id)
            if not cycle_subject:
                return QLabel(f"Error: Could not find subject with ID {cycle_subject_id}.")
            view = SubjectDetailsView(parent=self.view)
            controller = SubjectDetailsController(
                view=view, cycle_subject=cycle_subject,
                v20_diagnostics=subject_diag.get('diagnostics', {}),
                work_unit_service=self.app_context.work_unit_service,
                cycle_subject_service=self.app_context.cycle_subject_service,
                performance_service=self.app_context.performance_service
            )
            controller.load_data()
            return view

        self.navigation_service.register("subject_details", create_subject_details)

        # Provider for Help
        def create_help() -> QWidget:
            return HelpView(parent=self.view)

        self.navigation_service.register("help", create_help)

        # Provider for Analytics
        def create_analytics() -> QWidget:
            active_cycle = self.navigator.active_cycle
            if not active_cycle:
                return EmptyStateWidget(icon_name="REBALANCE", title="Analytics Unavailable",
                                        message="You need an active study cycle to view analytics.")
            view = AnalyticsView(parent=self.view)
            controller = AnalyticsController(
                view=view, user_id=self.current_user.id, cycle_id=active_cycle.id,
                performance_service=self.app_context.performance_service,
                cycle_subject_service=self.app_context.cycle_subject_service
            )
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("analytics", create_analytics)

        # Provider for Performance Dashboard
        def create_performance_dashboard() -> QWidget:
            active_cycle = self.navigator.active_cycle
            if not active_cycle:
                return QLabel("No active cycle to show dashboard for.", alignment=Qt.AlignmentFlag.AlignCenter)
            view = PerformanceDashboardView(parent=self.view)
            controller = PerformanceDashboardController(
                view=view, cycle_id=active_cycle.id, daily_goal=active_cycle.daily_goal_blocks,
                analytics_service=self.app_context.analytics_service
            )
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("performance_dashboard", create_performance_dashboard)

        # Provider for Training Screen
        def create_training_screen() -> QWidget:
            active_cycle = self.navigator.active_cycle
            if not active_cycle:
                return EmptyStateWidget(icon_name="TRAINING", title="Training Unavailable",
                                        message="You need an active study cycle to use the training screen.")
            
            view = TrainingScreenView(parent=self.view)
            controller = TrainingScreenController(
                view=view,
                session_service=self.app_context.session_service,
                master_subject_service=self.app_context.master_subject_service,
                cycle_subject_service=self.app_context.cycle_subject_service
            )
            controller.set_user_and_cycle(self.current_user.id, active_cycle.id)
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("training_screen", create_training_screen)

        # Provider for Performance Graphs
        def create_performance_graphs() -> QWidget:
            view = PerformanceGraphView(parent=self.view)
            controller = PerformanceGraphController(
                view=view, user_id=self.current_user.id,
                performance_service=self.app_context.performance_service,
                master_subject_service=self.app_context.master_subject_service
            )
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("performance_graphs", create_performance_graphs)

        # Provider for Session Choice
        def create_session_choice(recommended: dict, alternatives: list) -> QWidget:
            view = SessionChoiceView(parent=self.view)
            view.populate_data(recommended, alternatives)
            view.start_session_requested.connect(self.navigator._main_ctl.session_manager.start_study_session)
            view.cancel_requested.connect(self.navigator.show_overview)
            return view

        self.navigation_service.register("session_choice", create_session_choice)

        # Provider for Session Mode Choice
        def create_session_mode_choice(initial_session_data: dict) -> QWidget:
            view = SessionModeChoiceView(parent=self.view)
            all_master_subjects = self.app_context.master_subject_service.get_all_master_subjects()
            controller = SessionModeChoiceController(
                view=view,
                master_subject_service=self.app_context.master_subject_service,
                all_subjects=all_master_subjects,
                initial_session_data=initial_session_data
            )
            controller.manual_log_requested.connect(self.session_manager.handle_manual_session_log)
            controller.stopwatch_start_requested.connect(self.session_manager.handle_stopwatch_session_start)
            view.cancel_requested.connect(self.navigator.show_overview)
            view.setProperty("controller", controller)
            return view

        self.navigation_service.register("session_mode_choice", create_session_mode_choice)

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

        if self._active_onboarding_controller: # Check if onboarding is active
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