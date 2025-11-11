# app/feature/main_window/components/empty_dashboard_widget.py

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from app.common.widgets.card_widget import ActionCardWidget
from app.core.constants import SPACING_XLARGE, SPACING_LARGE

log = logging.getLogger(__name__)


class EmptyDashboardWidget(QWidget):
    """
    A self-contained component for the main dashboard's 'empty' state.
    This is displayed when no study cycle is currently active.
    """
    create_cycle_requested = Signal()
    manage_cycles_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        log.debug("Initializing EmptyDashboardWidget (no active cycle).")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Welcome Message ---
        welcome_label = QLabel("Welcome to Serenita!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = welcome_label.font()
        font.setPointSize(18)
        font.setBold(True)
        welcome_label.setFont(font)

        info_label = QLabel("No study cycle found. Create one to get started.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_font = info_label.font()
        info_font.setPointSize(12)
        info_label.setFont(info_font)

        # --- Action Cards ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(SPACING_XLARGE)

        # Create a card for creating a new cycle
        create_cycle_card = ActionCardWidget(
            title_text="Create New Cycle",
            desc_text="Define your subjects and schedule to begin a new study plan.",
            icon_name="NEW_CYCLE"
        )
        # Connect the card's click to the view's signal
        create_cycle_card.clicked.connect(self.create_cycle_requested.emit)

        # Create a card for navigating to the configurations/management screen
        manage_configs_card = ActionCardWidget(
            title_text="Go to Configurations",
            desc_text="Manage your cycles, user profile, and application-wide settings.",
            icon_name="CONFIGURATIONS"
        )
        # Connect the card's click to the view's signal
        manage_configs_card.clicked.connect(self.manage_cycles_requested.emit)

        cards_layout.addWidget(create_cycle_card)
        cards_layout.addWidget(manage_configs_card)

        # --- Assemble Layout ---
        layout.addStretch(1)
        layout.addWidget(welcome_label)
        layout.addSpacing(SPACING_LARGE)
        layout.addWidget(info_label)
        layout.addSpacing(30)
        layout.addLayout(cards_layout)
        layout.addStretch(2)

    def _on_create_cycle_requested(self):
        log.info("Create cycle button clicked on empty dashboard.")
        self.create_cycle_requested.emit()

    def _on_manage_cycles_requested(self):
        log.info("Manage cycles button clicked on empty dashboard.")
        self.manage_cycles_requested.emit()