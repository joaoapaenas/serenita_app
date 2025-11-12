# app/features/welcome/welcome_controller.py
import logging

from app.services.interfaces import IUserService
from .welcome_view import WelcomeView

log = logging.getLogger(__name__)


class WelcomeController:
    """
    Controller for the first-run welcome and user setup screen.
    Receives its view via constructor injection for testability.
    """

    def __init__(self, view: WelcomeView, user_service: IUserService):
        self._view = view
        self.user_service = user_service
        self._view.start_requested.connect(self._on_start_requested) # Connect to new handler

    def run(self):
        """
        Checks for an existing user and populates the view if found.
        Returns the existing user if found, otherwise None.
        """
        log.info("Running first-time user setup.")
        existing_user = self.user_service.get_first_user()
        if existing_user:
            log.info(f"Existing user '{existing_user.name}' found. Populating welcome screen.")
            self._view.set_user_data(existing_user.name, existing_user.study_level)
            return existing_user
        return None

    def _on_start_requested(self, name: str, study_level: str):
        """
        Handles the start_requested signal, either creating a new user or
        accepting the dialog for an existing user.
        """
        existing_user = self.user_service.get_first_user()
        if existing_user:
            log.info(f"Existing user '{existing_user.name}' confirmed. Accepting welcome screen.")
            self._view.accept()
        else:
            self.create_user(name, study_level)

    def create_user(self, name: str, study_level: str):
        """
        Calls the user service to create the new user.
        """
        log.info(f"Welcome screen submitted. Creating user '{name}'.")
        new_user = self.user_service.create_user(name, study_level)
        if new_user:
            self._view.accept()
        else:
            # In a real app, you'd show an error message here
            log.error("Failed to create user from welcome screen.")
            self._view.reject()
