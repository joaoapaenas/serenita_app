# app/features/configurations/configurations_landing_controller.py

from .configurations_landing_view import ConfigurationsLandingView


class ConfigurationsLandingController:
    """Controller for the configurations landing page."""

    def __init__(self, view: ConfigurationsLandingView, navigator):
        self._view = view
        self.navigator = navigator

        # Wire up the view's signals to the navigator's methods
        self._view.manage_cycles_requested.connect(self.navigator.show_cycle_manager)
        self._view.manage_exams_requested.connect(self.navigator.show_exam_manager)
        self._view.manage_subjects_requested.connect(self.navigator.show_master_subject_manager)
        self._view.app_settings_requested.connect(self.navigator.show_app_settings)
