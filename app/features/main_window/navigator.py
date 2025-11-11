# app/features/main_window/navigator.py

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QWidget

from app.features.onboarding.onboarding_view import OnboardingView
from .components.dual_plan_view import DualPlanView
from .components.empty_dashboard_widget import EmptyDashboardWidget

log = logging.getLogger(__name__)


class Navigator:
    """
    Handles navigation. It is the SINGLE SOURCE OF TRUTH for changing the main pane.
    It requests views from the factory, displays them, and updates the main controller's state.
    """

    def __init__(self, main_controller, navigation_service):
        self._main_ctl = main_controller
        self.navigation_service = navigation_service
        self.view = main_controller.view
        self.active_cycle = None

    def _set_current_main_widget(self, widget: QWidget):
        """
        Helper to set the widget in the view, update the controller's reference,
        and cache state if navigating away from a persistent view.
        """
        onboarding_controller = self._main_ctl._active_onboarding_controller
        if isinstance(self._main_ctl.current_main_widget, OnboardingView) and onboarding_controller:
            log.debug(f"Caching onboarding page index: {onboarding_controller.current_page_index}")
            self._main_ctl.onboarding_page_cache = onboarding_controller.current_page_index

        self.view.set_main_pane_widget(widget)
        self._main_ctl.current_main_widget = widget
        self._main_ctl.toolbar_manager.update_visibility_and_state()

    def handle_navigation(self, nav_data: dict):
        nav_type = nav_data.get("type")
        log.debug(f"Navigator handling request: {nav_type}")

        if self._main_ctl._active_onboarding_controller and not isinstance(
                self._main_ctl.current_main_widget, OnboardingView):
            pass

        if nav_type == "overview":
            if self._main_ctl.session_manager.is_session_active():
                self.show_active_session()
            else:
                self.show_overview()
            return

        if nav_type == "configurations":
            self.show_configurations_landing()

        if nav_type == "performance_graphs":
            self.show_performance_graphs()
            return
        elif nav_type == "help":
            self.show_help()
        elif nav_type == "performance_dashboard":
            self.show_performance_dashboard()
        elif nav_type == "analytics":
            self.show_analytics()
        elif nav_type == "history":
            self.show_history()
        elif nav_type == "training_screen":
            self.show_training_screen()
        elif nav_type == "subjects_category":
            self.show_subject_summary()
        elif nav_type == "subject_details":
            self.show_subject_details(nav_data.get("cycle_subject_id"))

    def show_performance_graphs(self):
        log.debug("Navigator creating and showing Performance Graphs view.")
        view = self.navigation_service.get_view("performance_graphs")
        self._set_current_main_widget(view)

    def set_active_cycle(self, cycle):
        self.active_cycle = cycle

    def show_session_choice(self, recommended: dict, alternatives: list):
        """Creates and displays the session choice view in the main pane."""
        log.debug("Navigator showing session choice view.")
        view = self.navigation_service.get_view("session_choice", recommended=recommended, alternatives=alternatives)
        self._set_current_main_widget(view)

    def show_session_mode_choice(self, initial_session_data: dict):
        """Creates and displays the session mode choice (Manual/Stopwatch)."""
        log.debug("Navigator showing session mode choice view.")
        view = self.navigation_service.get_view("session_mode_choice", initial_session_data=initial_session_data)
        self._set_current_main_widget(view)

    def show_active_session(self):
        session_view = self._main_ctl.session_manager.session_view
        if session_view:
            log.debug("Showing active study session view.")
            self._set_current_main_widget(session_view)
        else:
            log.warning("Attempted to show active session, but none was found. Showing overview instead.")
            self.show_overview()

    def show_overview(self):
        if self._main_ctl.session_manager.is_session_active():
            self.show_active_session()
            return

        cached_plan = self._main_ctl.plan_manager.get_cached_plan()
        if self.active_cycle and cached_plan:
            log.debug("Navigator showing overview with cached plan.")
            self.show_dual_plan_view(cached_plan)
        elif self.active_cycle:
            log.debug("Navigator showing overview, but plan needs regeneration.")
            self._main_ctl.plan_manager.regenerate_plan()
        else:
            log.debug("Navigator showing overview with empty dashboard.")
            widget = EmptyDashboardWidget()
            widget.create_cycle_requested.connect(self._main_ctl.launch_cycle_creator)
            widget.manage_cycles_requested.connect(self.show_configurations_landing)
            self._set_current_main_widget(widget)

    def show_dual_plan_view(self, v20_plan: dict):
        human_factor_input = v20_plan.get('meta', {}).get('human_factor_input', {})
        self._main_ctl.toolbar_manager.human_factor_widget.update_factors(human_factor_input)
        widget = DualPlanView(v20_plan)
        widget.start_session_requested.connect(self._main_ctl._on_start_next_session)
        widget.work_unit_completed.connect(self._main_ctl.plan_manager.on_work_unit_completed)
        self._set_current_main_widget(widget)

    def show_loading_view(self):
        loading_widget = QFrame()
        loading_widget.setObjectName("mainPane")
        layout = QVBoxLayout(loading_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner_label = QLabel("Generating your personalized plan...")
        spinner_label.setObjectName("largeDisplay")
        layout.addWidget(spinner_label)
        self._set_current_main_widget(loading_widget)

    def show_configurations_landing(self):
        log.debug("Navigator creating and showing Configurations Landing view.")
        view = self.navigation_service.get_view("configurations_landing")
        self._set_current_main_widget(view)

    def show_app_settings(self):
        log.debug("Navigator creating and showing App Settings view.")
        view = self.navigation_service.get_view("app_settings")
        self._set_current_main_widget(view)

    def show_cycle_manager(self):
        log.debug("Navigator creating and showing Cycle Manager view.")
        view = self.navigation_service.get_view("cycle_manager")
        self._set_current_main_widget(view)

    def show_exam_manager(self):
        log.debug("Navigator creating and showing Exam Manager view.")
        view = self.navigation_service.get_view("exam_manager")
        self._set_current_main_widget(view)

    def show_master_subject_manager(self):
        log.debug("Navigator creating and showing Master Subject Manager view.")
        view = self.navigation_service.get_view("master_subject_manager")
        self._set_current_main_widget(view)

    def show_exam_editor(self, exam_id: int | None):
        log.debug(f"Navigator creating and showing Exam Editor for exam_id: {exam_id}")
        view = self.navigation_service.get_view("exam_editor", exam_id=exam_id)
        self._set_current_main_widget(view)

    def show_cycle_editor(self, exam_id: int, cycle_id: int | None):
        if exam_id is None: return
        log.debug(f"Navigator creating and showing Cycle Editor view.")
        view = self.navigation_service.get_view("cycle_editor", exam_id=exam_id, cycle_id=cycle_id)
        self._set_current_main_widget(view)

    def show_onboarding(self):
        onboarding_controller = self._main_ctl._active_onboarding_controller
        if onboarding_controller:
            log.debug(f"Showing existing onboarding wizard.")
            cached_index = self._main_ctl.onboarding_page_cache
            page_to_show = onboarding_controller.flow_manager.active_flow[cached_index]
            onboarding_controller.view.go_to_page(page_to_show)
            onboarding_controller.current_page_index = cached_index
            self._set_current_main_widget(onboarding_controller.view)
        else:
            log.debug(f"Navigator creating and showing new Onboarding Wizard.")
            view, controller = self.navigation_service.get_view("onboarding")
            self._set_current_main_widget(view)

    def show_subject_summary(self):
        log.debug("Navigator creating and showing Subject Summary view.")
        if not self._main_ctl.plan_manager.get_cached_plan():
            self._set_current_main_widget(QLabel("Please generate a plan first."))
            return
        view = self.navigation_service.get_view("subject_summary")
        self._set_current_main_widget(view)

    def show_history(self):
        log.debug("Navigator creating and showing History view.")
        view = self.navigation_service.get_view("history")
        self._set_current_main_widget(view)

    def show_subject_details(self, cycle_subject_id: int):
        if not cycle_subject_id: return
        log.debug(f"Navigator creating and showing Subject Details view.")
        view = self.navigation_service.get_view("subject_details", cycle_subject_id=cycle_subject_id)
        self._set_current_main_widget(view)

    def show_help(self):
        """Creates and shows the main Help view in the main pane."""
        log.debug("Navigator creating and showing Help view.")
        view = self.navigation_service.get_view("help")
        self._set_current_main_widget(view)

    def show_analytics(self):
        """Creates and shows the Analytics Dashboard view."""
        log.debug("Navigator creating and showing Analytics view.")
        view = self.navigation_service.get_view("analytics")
        self._set_current_main_widget(view)

    def show_performance_dashboard(self):
        log.debug("Navigator creating and showing Performance Dashboard.")
        view = self.navigation_service.get_view("performance_dashboard")
        self._set_current_main_widget(view)

    def show_training_screen(self):
        log.debug("Navigator creating and showing Training Screen.")
        view = self.navigation_service.get_view("training_screen")
        self._set_current_main_widget(view)