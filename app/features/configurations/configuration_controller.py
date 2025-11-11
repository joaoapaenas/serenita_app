# app/features/configurations/configuration_controller.py

import logging
import os

from PySide6.QtWidgets import QMessageBox, QInputDialog, QApplication

from app.core.database import get_db_file_path
from app.core.signals import app_signals
from app.core.theme_manager import apply_theme
from app.models.user import User
from app.services.interfaces import IUserService
# The view is now just the form, not the whole page
from .configuration_view import ConfigurationView

log = logging.getLogger(__name__)


class ConfigurationController:
    """Controller for the global configurations view."""

    def __init__(self, view: ConfigurationView, user: User, user_service: IUserService, navigator):
        self._view = view
        self._user = user
        self.user_service = user_service
        self.navigator = navigator

        # Connections are now made in the factory

    def load_data(self):
        """Loads the initial data into the view."""
        self._view.set_data(self._user)

    def on_save(self):
        """Handles saving the user profile and theme."""
        data = self._view.get_data()

        if not data["name"].strip():
            QMessageBox.warning(self._view, "Input Error", "Your name cannot be empty.")
            return

        updated_user = self.user_service.update_user(
            self._user.id, data["name"], data["study_level"], data["theme"]
        )

        if updated_user:
            self._user = updated_user
            apply_theme(QApplication.instance(), self._user.theme)
            app_signals.theme_changed.emit() # Notify all components of the theme change
            QMessageBox.information(
                self._view, "Success",
                "Your settings have been updated."
            )
            self.navigator.show_overview()
        else:
            QMessageBox.critical(self._view, "Error", "Could not update your profile. Please check the logs.")

    def on_reset(self):
        """Handles the multi-step confirmation for resetting the database."""
        """Handles the multi-step confirmation for resetting the database."""
        # ... (confirmation dialogs remain the same) ...
        if not ok or text.strip().upper() != "RESET":
            QMessageBox.information(self._view, "Cancelled", "Reset operation has been cancelled.")
            return

        # --- REVISED LOGIC ---
        log.warning("USER INITIATED DATABASE RESET. Staging reset for next startup.")
        try:
            # Get the base path of the project
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

            # Create a simple flag file in the root directory
            reset_flag_path = os.path.join(base_path, ".reset_on_next_boot")
            with open(reset_flag_path, "w") as f:
                f.write("reset")  # The content doesn't matter, just its existence

            log.info(f"Reset flag created at: {reset_flag_path}")

            # Inform user and quit the application
            QMessageBox.information(self._view, "Resetting Application",
                                    "The application data will be reset on the next startup. The application will now close.")
            QApplication.instance().quit()

        except Exception as e:
            log.error("Failed to create the reset flag file.", exc_info=True)
            QMessageBox.critical(self._view, "Error", f"Could not stage the application reset: {e}")

    def on_cancel(self):
        """Handles the cancel action."""
        self.navigator.show_overview()