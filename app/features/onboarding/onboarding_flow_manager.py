# app/features/onboarding/onboarding_flow_manager.py
import logging
from typing import List

from PySide6.QtWidgets import QWidget

log = logging.getLogger(__name__)


class OnboardingFlowManager:
    """
    Manages the state and logic of the onboarding wizard's page flow.
    It determines which pages are shown and in what order.
    """

    def __init__(self, all_pages: dict):
        self._all_pages = all_pages
        self.current_page_index = 0
        # The active_flow determines the order and visibility of pages.
        self.active_flow: List[QWidget] = [self._all_pages["goal"]]

    def set_flow_for_selection(self, selection_key: str | int):
        """Rebuilds the active_flow list based on the user's goal selection."""
        log.debug(f"Setting onboarding flow for selection: {selection_key}")
        if selection_key == "none":
            self.active_flow = [self._all_pages["goal"]]
        elif selection_key == "custom":
            self.active_flow = [
                self._all_pages["goal"],
                self._all_pages["define_exam"],
                self._all_pages["subjects_config"],
                self._all_pages["import_topics"],
                self._all_pages["cycle_settings"]
            ]
        else:  # Template flow
            self.active_flow = [
                self._all_pages["goal"],
                self._all_pages["subjects_config"],
                self._all_pages["import_topics"],
                self._all_pages["cycle_settings"]
            ]
        self.current_page_index = 0

    def can_proceed(self) -> bool:
        """Determines if the user can proceed from the current step."""
        # The only time they can't proceed is on the first page before making a selection.
        return len(self.active_flow) > 1

    def next_page(self) -> QWidget | None:
        """Advances to the next page in the flow and returns it."""
        if self.current_page_index < len(self.active_flow) - 1:
            self.current_page_index += 1
            return self.active_flow[self.current_page_index]
        return None

    def previous_page(self) -> QWidget | None:
        """Moves to the previous page in the flow and returns it."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            return self.active_flow[self.current_page_index]
        return None

    def current_page(self) -> QWidget:
        """Returns the current page widget."""
        return self.active_flow[self.current_page_index]

    def total_pages(self) -> int:
        """Returns the total number of pages in the current active flow."""
        return len(self.active_flow)