# app/features/configurations/developer_tools_controller.py

import logging
import os

from PySide6.QtWidgets import QMessageBox

from app.common.error_handler import show_error_message
from app.core.database import IDatabaseConnectionFactory
from .developer_tools_dialog import DeveloperToolsDialog

log = logging.getLogger(__name__)


class DeveloperToolsController:
    """
    Controller for the Developer Tools dialog.
    """

    def __init__(self, conn_factory: IDatabaseConnectionFactory, parent_view=None):
        self._conn_factory = conn_factory
        self._parent_view = parent_view
        self._dialog = DeveloperToolsDialog(parent=parent_view)
        self._dialog.seed_long_term_user_requested.connect(self._on_seed_long_term_user)

    def show(self):
        """Shows the developer tools dialog."""
        self._dialog.exec()

    def _on_seed_long_term_user(self):
        """
        Reads and executes the long_term_user_seed.sql script.
        """
        reply = QMessageBox.question(
            self._dialog,
            "Confirm Data Seeding",
            "This will execute a large SQL script to simulate a long-term user. "
            "It may add a lot of data to your current database. Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Assuming the script is in 'lib/long_term_user_seed.sql' relative to the project root
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            script_path = os.path.join(base_path, "lib", "long_term_user_seed.sql")

            if not os.path.exists(script_path):
                show_error_message(self._dialog, "Error", f"SQL script not found at {script_path}")
                return

            with open(script_path, "r") as f:
                sql_script = f.read()

            conn = self._conn_factory.get_connection()
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()

            log.info("Successfully executed long_term_user_seed.sql")
            QMessageBox.information(self._dialog, "Success", "Long-term user data has been seeded successfully.")

        except Exception as e:
            log.error("Failed to execute seed script", exc_info=True)
            show_error_message(self._dialog, "Error", "Failed to execute the seed script.", str(e))
