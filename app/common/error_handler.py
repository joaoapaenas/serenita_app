# app/common/error_handler.py

import logging
import traceback

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.logger import LOG_DIR

log = logging.getLogger(__name__)


def show_error_message(parent, title: str, message: str, details: str = ""):
    """
    A centralized function to show a standardized error message box.
    Includes a "Report Bug" feature to help users provide useful feedback.
    """
    log.error(
        f"Displaying error dialog. Title: '{title}', Message: '{message}', Details: '{details}'"
    )

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(f"<b>{message}</b>")

    # If no specific details are provided, use the last exception info
    if not details:
        details = traceback.format_exc()

    msg_box.setInformativeText(
        "An unexpected error occurred. Please see details below. "
        "You can help us fix this by reporting the bug."
    )
    msg_box.setDetailedText(details)

    # Add custom buttons
    msg_box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
    report_button = msg_box.addButton("Report Bug", QMessageBox.ButtonRole.ActionRole)

    def on_report_clicked():
        """Handles the 'Report Bug' button action."""
        # 1. Copy the error details to the clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(f"Error: {message}\n\nDetails:\n{details}")

        # 2. Open the directory containing the log files
        QDesktopServices.openUrl(QUrl.fromLocalFile(LOG_DIR))

        # 3. Inform the user
        info_box = QMessageBox(parent)
        info_box.setIcon(QMessageBox.Icon.Information)
        info_box.setText(
            "Error details have been copied to your clipboard, and the log file folder has been opened."
        )
        info_box.setInformativeText(
            "Please include this information in your bug report."
        )
        info_box.exec()

    report_button.clicked.connect(on_report_clicked)
    msg_box.exec()
