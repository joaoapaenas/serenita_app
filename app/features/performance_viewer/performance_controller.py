# app/feature/performance_viewer/performance_controller.py
import logging

from app.services.interfaces import IPerformanceService
from .performance_view import PerformanceView

log = logging.getLogger(__name__)


class PerformanceController:
    """
    The Controller for the Performance Viewer feature. Its job is to fetch
    the performance summary and display it in the PerformanceView.
    """

    def __init__(self, cycle_id: int, cycle_name: str, performance_service: IPerformanceService, parent_view=None):
        log.debug(f"Initializing PerformanceController for cycle_id: {cycle_id}")
        # 1. Store injected service and create view
        self.performance_service = performance_service
        self._view = PerformanceView(cycle_name=cycle_name, parent=parent_view)

        # 2. Fetch the necessary data from the service layer.
        summary_data = self.performance_service.get_summary(cycle_id)
        log.info(f"Fetched performance summary for '{cycle_name}' with {len(summary_data)} subjects.")

        # 3. Pass the data to the view for display.
        self._view.populate_data(summary_data)

    def show(self):
        """Shows the performance viewer dialog."""
        log.debug("Showing performance viewer dialog.")
        self._view.exec()
