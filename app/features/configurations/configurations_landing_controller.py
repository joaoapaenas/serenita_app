# app/features/configurations/configurations_landing_controller.py

from app.core.database import IDatabaseConnectionFactory
from .configurations_landing_view import ConfigurationsLandingView
from .developer_tools_controller import DeveloperToolsController


class ConfigurationsLandingController:
    """Controller for the configurations landing page."""

    def __init__(self, view: ConfigurationsLandingView, navigator, conn_factory: IDatabaseConnectionFactory):
        self._view = view
        self.navigator = navigator
        self._conn_factory = conn_factory

        # Wire up the view's signals to the navigator's methods
        self._view.manage_cycles_requested.connect(self.navigator.show_cycle_manager)
        self._view.manage_exams_requested.connect(self.navigator.show_exam_manager)
        self._view.manage_subjects_requested.connect(self.navigator.show_master_subject_manager)
        self._view.app_settings_requested.connect(self.navigator.show_app_settings)
        self._view.developer_tools_requested.connect(self._on_developer_tools)

    def _on_developer_tools(self):
        """Shows the developer tools dialog."""
        dev_tools_controller = DeveloperToolsController(
            conn_factory=self._conn_factory,
            parent_view=self._view
        )
        dev_tools_controller.show()
