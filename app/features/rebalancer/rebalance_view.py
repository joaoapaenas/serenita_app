# app/feature/rebalancer/rebalance_view.py

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QApplication
)

from app.common.widgets.empty_state_widget import EmptyStateWidget
from app.core.icon_manager import get_icon

log = logging.getLogger(__name__)


class RebalanceView(QDialog):
    """
    The View for displaying rebalance suggestions. It shows a table of
    proposed changes and allows the user to accept or cancel.
    """
    # Signal that emits the list of suggestions when the user accepts.
    rebalance_accepted = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        log.debug("Initializing RebalanceView dialog.")
        self.setWindowTitle("Rebalance Suggestions")
        self.setMinimumSize(650, 400)
        self.setModal(True)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        self.suggestions = []
        self.layout = QVBoxLayout(self)

        info_label = QLabel(
            "Based on your performance, we suggest adjusting the 'Difficulty' weight for these subjects.\n"
            "This will change how often they appear in your study queue."
        )
        info_label.setWordWrap(True)

        self.table = QTableWidget()
        self._setup_table()

        self.accept_button = QPushButton(" Accept & Rebuild Cycle")
        self.accept_button.setIcon(get_icon("ACCEPT"))
        self.cancel_button = QPushButton("Cancel")

        self.accept_button.clicked.connect(self.on_accept)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.accept_button)
        buttons_layout.addWidget(self.cancel_button)

        self.layout.addWidget(info_label)
        self.layout.addWidget(self.table)
        self.layout.addLayout(buttons_layout)

    def _setup_table(self):
        """Initializes the table structure and headers."""
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Subject", "Reason for Change", "Old Difficulty", "New Difficulty"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only

    def populate_suggestions(self, suggestions: list):
        """
        Public method called by the controller to fill the table with suggestions.
        """
        log.debug(f"Populating rebalance view with {len(suggestions)} suggestions.")
        self.suggestions = suggestions
        if not self.suggestions:
            self.table.hide()
            self.accept_button.hide()
            empty_widget = EmptyStateWidget(
                icon_name="REBALANCE",
                title="No Rebalancing Suggestions",
                message="Your performance is on track with your difficulty ratings. Keep up the great work!"
            )
            self.layout.insertWidget(1, empty_widget)  # Insert msg where table was
            log.info("No rebalance suggestions to display.")
            return

        self.table.setRowCount(len(suggestions))
        for row, sugg in enumerate(suggestions):
            self.table.setItem(row, 0, QTableWidgetItem(sugg['subject_name']))
            self.table.setItem(row, 1, QTableWidgetItem(sugg['reason']))
            self.table.setItem(row, 2, QTableWidgetItem(str(sugg['old_difficulty'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(sugg['new_difficulty'])))

    def on_accept(self):
        """Emits the accepted suggestions and closes the dialog."""
        log.info(f"Rebalance accepted by user. Emitting {len(self.suggestions)} suggestions.")
        self.rebalance_accepted.emit(self.suggestions)
        self.accept()