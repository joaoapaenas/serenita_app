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
        self._view.start_requested.connect(self.create_user)

    def run(self):
        """
        Shows the welcome dialog and blocks execution until the user completes
        the setup or closes the window.
        """
        log.info("Running first-time user setup.")
        self._view.exec()

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
