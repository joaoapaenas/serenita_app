# app/features/main_window/toolbar_manager.py
import logging

from PySide6.QtWidgets import QToolBar, QPushButton, QWidget, QSizePolicy

from app.core.icon_manager import get_icon
from app.features.main_window.components.dual_plan_view import DualPlanView
from app.features.main_window.components.human_factor_widget import HumanFactorWidget
from app.features.onboarding.onboarding_view import OnboardingView
from app.features.study_session.study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class ToolbarManager:
    """
    Manages the creation, state, and visibility of widgets in the main toolbar.
    """

    def __init__(self, main_controller):
        self._main_ctl = main_controller
        self._toolbar: QToolBar | None = None

        self.human_factor_widget: HumanFactorWidget | None = None
        self.view_toggle_button: QPushButton | None = None
        self.return_to_session_button: QPushButton | None = None
        self.return_to_onboarding_button: QPushButton | None = None

    def setup_widgets(self, toolbar: QToolBar):
        """Creates and adds all contextual widgets to the toolbar."""
        self._toolbar = toolbar
        self._toolbar.addSeparator()

        self.human_factor_widget = HumanFactorWidget({})
        # DELEGATION: Connect the widget's signal directly to the PlanManager's slot.
        # The MainWindowController is no longer involved in this interaction.
        self.human_factor_widget.human_factor_saved.connect(self._main_ctl.plan_manager.update_human_factor_and_replan)
        self._toolbar.addWidget(self.human_factor_widget)

        self.view_toggle_button = QPushButton(" View Tactical List")
        self.view_toggle_button.setIcon(get_icon("HISTORY"))
        self.view_toggle_button.setCheckable(True)
        self.view_toggle_button.toggled.connect(self._on_plan_view_toggled)
        self._toolbar.addWidget(self.view_toggle_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._toolbar.addWidget(spacer)

        self.return_to_onboarding_button = QPushButton(" Resume Cycle Setup")
        self.return_to_onboarding_button.setIcon(get_icon("EDIT"))
        self.return_to_onboarding_button.clicked.connect(self._main_ctl.navigator.show_onboarding)
        self.return_to_onboarding_button.setVisible(False)
        self._toolbar.addWidget(self.return_to_onboarding_button)

        self.return_to_session_button = QPushButton(" Return to Session")
        self.return_to_session_button.setIcon(get_icon("START_SESSION"))
        self.return_to_session_button.clicked.connect(self._main_ctl.navigator.show_active_session)
        self.return_to_session_button.setVisible(False)
        self._toolbar.addWidget(self.return_to_session_button)

    def update_visibility_and_state(self):
        """
        Updates the visibility and state of all contextual toolbar widgets
        based on the application's current state.
        """
        is_cycle_active = self._main_ctl.active_cycle is not None
        current_widget = self._main_ctl.current_main_widget
        is_plan_view_active = is_cycle_active and isinstance(current_widget, DualPlanView)

        is_session_active = self._main_ctl.session_manager.is_session_active()
        is_showing_session_widget = isinstance(current_widget, StudySessionWidget)

        is_onboarding_active = self._main_ctl._active_onboarding_controller is not None
        is_showing_onboarding_widget = isinstance(current_widget, OnboardingView)

        log.debug(
            f"Updating toolbar. Cycle: {is_cycle_active}, PlanView: {is_plan_view_active}, "
            f"Session: {is_session_active}, ShowingSession: {is_showing_session_widget}, "
            f"Onboarding: {is_onboarding_active}, ShowingOnboarding: {is_showing_onboarding_widget}"
        )

        self.return_to_onboarding_button.setVisible(is_onboarding_active and not is_showing_onboarding_widget)

        can_show_main_buttons = not is_session_active and not is_onboarding_active

        self.human_factor_widget.setVisible(is_cycle_active and can_show_main_buttons)

        self.view_toggle_button.setVisible(is_cycle_active and can_show_main_buttons)
        self.view_toggle_button.setEnabled(is_plan_view_active)
        if not is_plan_view_active:
            self.view_toggle_button.setChecked(False)

        self.return_to_session_button.setVisible(is_session_active and not is_showing_session_widget)
        if is_session_active and self._main_ctl.session_manager.session_controller:
            minutes, seconds = divmod(self._main_ctl.session_manager.session_controller.time_elapsed_sec, 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.return_to_session_button.setText(f" Session in Progress ({time_str})")

    def _on_plan_view_toggled(self, checked: bool):
        """Handles toggling between Strategic and Tactical plan views."""
        if checked:
            self.view_toggle_button.setText(" View Strategic Plan")
            self.view_toggle_button.setIcon(get_icon("REBALANCE"))
        else:
            self.view_toggle_button.setText(" View Tactical List")
            self.view_toggle_button.setIcon(get_icon("HISTORY"))

        if isinstance(self._main_ctl.current_main_widget, DualPlanView):
            self._main_ctl.current_main_widget.set_tactical_view_active(checked)