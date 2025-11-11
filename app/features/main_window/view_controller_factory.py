# app/features/main_window/view_controller_factory.py

import logging

from PySide6.QtCore import QObject
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout

from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.core.context import AppContext
from app.core.signals import app_signals
from app.features.analitics.analytics_controller import AnalyticsController
from app.features.analitics.analytics_view import AnalyticsView
from app.features.configurations.app_settings_view import AppSettingsView
from app.features.configurations.configuration_controller import ConfigurationController
from app.features.configurations.configurations_landing_controller import ConfigurationsLandingController
from app.features.configurations.configurations_landing_view import ConfigurationsLandingView
from app.features.cycle_editor.cycle_editor_controller import CycleEditorController
from app.features.cycle_editor.cycle_editor_view import CycleEditorView
from app.features.cycle_manager.cycle_manager_controller import CycleManagerController
from app.features.cycle_manager.cycle_manager_view import CycleManagerView
from app.features.exam_editor.exam_editor_controller import ExamEditorController
from app.features.exam_manager.exam_manager_controller import ExamManagerController
from app.features.exam_manager.exam_manager_view import ExamManagerView
from app.features.master_subject_manager.master_subject_manager_controller import MasterSubjectManagerController
from app.features.master_subject_manager.master_subject_manager_view import MasterSubjectManagerView
from app.features.help.help_view import HelpView
from app.features.history.history_controller import HistoryController
from app.features.history.history_view import HistoryView
from app.features.onboarding.onboarding_controller import OnboardingController
from app.features.onboarding.onboarding_view import OnboardingView
from app.features.performance_dashboard.performance_dashboard_controller import PerformanceDashboardController
from app.features.performance_dashboard.performance_dashboard_view import PerformanceDashboardView
from app.features.performance_graphs.performance_graph_controller import PerformanceGraphController
from app.features.performance_graphs.performance_graph_view import PerformanceGraphView
from app.features.session_choice.session_choice_view import SessionChoiceView
from app.features.session_mode_choice.session_mode_choice_controller import SessionModeChoiceController
from app.features.session_mode_choice.session_mode_choice_view import SessionModeChoiceView
from app.features.subject_details.subject_details_controller import SubjectDetailsController
from app.features.subject_details.subject_details_view import SubjectDetailsView
from app.features.subject_summary.subject_summary_controller import SubjectSummaryController
from app.features.subject_summary.subject_summary_view import SubjectSummaryView
from app.features.training_screen.training_screen_view import TrainingScreenView
from app.features.training_screen.training_screen_controller import TrainingScreenController

log = logging.getLogger(__name__)


class ViewControllerFactory:
    """A factory responsible for creating and wiring up all sub-controllers and their views."""

    def __init__(self, app_context: AppContext, navigator, is_dev_mode: bool = False):
        self.app_context = app_context
        self.navigator = navigator
        self.is_dev_mode = is_dev_mode
        self._active_onboarding_controller = None

    def is_onboarding_active(self) -> bool:
        return self._active_onboarding_controller is not None

    def create_session_choice(self, recommended: dict, alternatives: list) -> QWidget:
        view = SessionChoiceView(parent=self.navigator.view)
        view.populate_data(recommended, alternatives)
        view.start_session_requested.connect(self.navigator._main_ctl.session_manager.start_study_session)
        view.cancel_requested.connect(self.navigator.show_overview)
        return view

    def create_session_mode_choice(self, initial_session_data: dict) -> QWidget:
        view = SessionModeChoiceView(parent=self.navigator.view)
        all_master_subjects = self.app_context.master_subject_service.get_all_master_subjects()
        controller = SessionModeChoiceController(
            view=view,
            master_subject_service=self.app_context.master_subject_service,
            all_subjects=all_master_subjects,
            initial_session_data=initial_session_data
        )
        controller.manual_log_requested.connect(self.navigator._main_ctl.session_manager.handle_manual_session_log)
        controller.stopwatch_start_requested.connect(
            self.navigator._main_ctl.session_manager.handle_stopwatch_session_start)
        view.cancel_requested.connect(self.navigator.show_overview)
        view.setProperty("controller", controller)
        return view

    def create_configurations_landing(self) -> QWidget:
        view = ConfigurationsLandingView(parent=self.navigator.view)
        view.set_developer_mode(self.is_dev_mode)
        controller = ConfigurationsLandingController(
            view=view,
            navigator=self.navigator,
            conn_factory=self.app_context.conn_factory
        )
        view.setProperty("controller", controller)
        return view

    def create_history(self) -> QWidget:
        active_cycle = self.navigator.active_cycle
        if not active_cycle:
            return QLabel("No active cycle to show history for.")
        view = HistoryView(parent=self.navigator.view)
        view.start_session_requested.connect(self.navigator._main_ctl._on_start_next_session)
        controller = HistoryController(
            view=view, cycle_id=active_cycle.id,
            session_service=self.app_context.session_service
        )
        view.setProperty("controller", controller)
        return view

    def create_app_settings(self) -> QWidget:
        view = AppSettingsView(parent=self.navigator.view)
        controller = ConfigurationController(
            view=view.profile_form,
            user=self.navigator._main_ctl.current_user,
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

    def create_cycle_manager(self) -> QWidget:
        view = CycleManagerView(parent=self.navigator.view)
        controller = CycleManagerController(
            view=view,
            undo_stack=self.navigator._main_ctl.undo_stack,
            cycle_service=self.app_context.cycle_service
        )
        controller.load_data()
        controller.creation_requested.connect(self.navigator._main_ctl.launch_cycle_creator)
        active_cycle = self.navigator.active_cycle
        controller.edit_requested_with_id.connect(
            lambda cycle_id: self.navigator.show_cycle_editor(active_cycle.exam_id,
                                                              cycle_id) if active_cycle else None
        )
        app_signals.data_changed.connect(controller.load_data)
        return view

    def create_cycle_editor(self, exam_id: int, cycle_id: int | None) -> QWidget:
        view = CycleEditorView(parent=self.navigator.view)
        controller = CycleEditorController(
            view=view, exam_id=exam_id, cycle_id=cycle_id,
            undo_stack=self.navigator._main_ctl.undo_stack,
            cycle_service=self.app_context.cycle_service,
            master_subject_service=self.app_context.master_subject_service,
            cycle_subject_service=self.app_context.cycle_subject_service,
            study_queue_service=self.app_context.study_queue_service
        )
        controller.load_data_into_view()
        controller.save_completed.connect(self.navigator.show_configurations_landing)
        controller.editing_cancelled.connect(self.navigator.show_configurations_landing)
        return view

    def create_onboarding(self) -> tuple[QWidget, QObject]:
        view = OnboardingView(parent=self.navigator.view)
        controller = OnboardingController(
            view=view,
            user_id=self.navigator._main_ctl.current_user.id,
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
            self.navigator._main_ctl.on_onboarding_finished()

        def on_cancelled():
            self._active_onboarding_controller = None
            self.navigator._main_ctl.on_onboarding_cancelled()

        controller.onboarding_complete.connect(on_finished)
        controller.onboarding_cancelled.connect(on_cancelled)
        return view, controller

    def get_active_onboarding_controller(self) -> OnboardingController | None:
        return self._active_onboarding_controller

    def create_subject_summary(self) -> QWidget:
        view = SubjectSummaryView(parent=self.navigator.view)
        controller = SubjectSummaryController(
            view=view,
            v20_plan_data=self.navigator._main_ctl.plan_manager.get_cached_plan(),
            performance_service=self.app_context.performance_service,
            master_subject_service=self.app_context.master_subject_service,
            user_id=self.navigator._main_ctl.current_user.id,
            parent=view
        )
        return view

    def create_subject_details(self, cycle_subject_id: int) -> QWidget:
        cached_plan = self.navigator._main_ctl.plan_manager.get_cached_plan()
        subject_diag = next((s for s in cached_plan.get('processed_subjects', []) if
                             s['subject_id'] == cycle_subject_id), {}) if cached_plan else {}
        cycle_subject = self.app_context.cycle_subject_service.get_cycle_subject(cycle_subject_id)
        if not cycle_subject:
            return QLabel(f"Error: Could not find subject with ID {cycle_subject_id}.")
        view = SubjectDetailsView(parent=self.navigator.view)
        controller = SubjectDetailsController(
            view=view, cycle_subject=cycle_subject,
            v20_diagnostics=subject_diag.get('diagnostics', {}),
            work_unit_service=self.app_context.work_unit_service,
            cycle_subject_service=self.app_context.cycle_subject_service,
            performance_service=self.app_context.performance_service
        )
        controller.load_data()
        return view

    def create_exam_manager(self) -> QWidget:
        view = ExamManagerView(parent=self.navigator.view)
        controller = ExamManagerController(
            view=view, user_id=self.navigator._main_ctl.current_user.id,
            exam_service=self.app_context.exam_service, navigator=self.navigator
        )
        controller.load_data()
        app_signals.data_changed.connect(controller.load_data)
        view.setProperty("controller", controller)
        return view

    def create_master_subject_manager(self) -> QWidget:
        view = MasterSubjectManagerView(parent=self.navigator.view)
        controller = MasterSubjectManagerController(
            view=view,
            master_subject_service=self.app_context.master_subject_service,
            navigator=self.navigator
        )
        view.setProperty("controller", controller)
        return view

    def create_exam_editor(self, exam_id: int | None) -> QWidget:
        controller = ExamEditorController(
            user_id=self.navigator._main_ctl.current_user.id,
            exam_service=self.app_context.exam_service,
            template_subject_service=self.app_context.template_subject_service,
            master_subject_service=self.app_context.master_subject_service,
            cycle_subject_service=self.app_context.cycle_subject_service,
            study_queue_service=self.app_context.study_queue_service,
            cycle_service=self.app_context.cycle_service,
            parent_view=self.navigator.view, exam_id_to_edit=exam_id
        )
        view = controller.get_view()
        controller.save_completed.connect(self.navigator.show_exam_manager)
        view.cancel_requested.connect(self.navigator.show_exam_manager)
        return view

    def create_performance_graphs(self) -> QWidget:
        view = PerformanceGraphView(parent=self.navigator.view)
        controller = PerformanceGraphController(
            view=view, user_id=self.navigator._main_ctl.current_user.id,
            performance_service=self.app_context.performance_service,
            master_subject_service=self.app_context.master_subject_service
        )
        view.setProperty("controller", controller)
        return view

    def create_help(self) -> QWidget:
        return HelpView(parent=self.navigator.view)

    def create_analytics(self) -> QWidget:
        active_cycle = self.navigator.active_cycle
        if not active_cycle:
            return EmptyStateWidget(icon_name="REBALANCE", title="Analytics Unavailable",
                                    message="You need an active study cycle to view analytics.")
        view = AnalyticsView(parent=self.navigator.view)
        controller = AnalyticsController(
            view=view, user_id=self.navigator._main_ctl.current_user.id, cycle_id=active_cycle.id,
            performance_service=self.app_context.performance_service,
            cycle_subject_service=self.app_context.cycle_subject_service
        )
        view.setProperty("controller", controller)
        return view

    def create_performance_dashboard(self) -> QWidget:
        active_cycle = self.navigator.active_cycle
        if not active_cycle:
            return QLabel("No active cycle to show dashboard for.", alignment=Qt.AlignmentFlag.AlignCenter)
        view = PerformanceDashboardView(parent=self.navigator.view)
        controller = PerformanceDashboardController(
            view=view, cycle_id=active_cycle.id, daily_goal=active_cycle.daily_goal_blocks,
            analytics_service=self.app_context.analytics_service
        )
        view.setProperty("controller", controller)
        return view

    def create_training_screen(self) -> QWidget:
        active_cycle = self.navigator.active_cycle
        if not active_cycle:
            return EmptyStateWidget(icon_name="TRAINING", title="Training Unavailable",
                                    message="You need an active study cycle to use the training screen.")
        
        view = TrainingScreenView(parent=self.navigator.view)
        controller = TrainingScreenController(
            view=view,
            session_service=self.app_context.session_service,
            master_subject_service=self.app_context.master_subject_service,
            cycle_subject_service=self.app_context.cycle_subject_service
        )
        controller.set_user_and_cycle(self.navigator._main_ctl.current_user.id, active_cycle.id)
        view.setProperty("controller", controller)
        return view