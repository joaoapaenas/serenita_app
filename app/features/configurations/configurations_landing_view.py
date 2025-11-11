# app/features/configurations/configurations_landing_view.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel)

from app.common.widgets.card_widget import ActionCardWidget
# --- FIX: Import the new FlowLayout ---
from app.common.widgets.flow_layout import FlowLayout
from app.core.constants import PAGE_MARGINS


class ConfigurationsLandingView(QWidget):
    """A landing page that provides access to different configuration screens."""

    manage_cycles_requested = Signal()
    manage_exams_requested = Signal()
    manage_subjects_requested = Signal()
    app_settings_requested = Signal()
    developer_tools_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Configurations")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- FIX: Use FlowLayout instead of QHBoxLayout for responsiveness ---
        cards_layout = FlowLayout()
        main_layout.addLayout(cards_layout)

        # Card for managing exams
        exam_card = ActionCardWidget(
            title_text="Manage Exams",
            desc_text="Create, edit, and delete your high-level exam goals.",
            icon_name="FINISH_FLAG"
        )
        exam_card.clicked.connect(self.manage_exams_requested.emit)
        cards_layout.addWidget(exam_card)

        # Card for managing cycles
        cycle_card = ActionCardWidget(
            title_text="Manage Cycles",
            desc_text="Create, edit, delete, and set your active study cycles for an exam.",
            icon_name="NEW_CYCLE"
        )
        cycle_card.clicked.connect(self.manage_cycles_requested.emit)
        cards_layout.addWidget(cycle_card)

        # Card for managing master subjects
        subject_card = ActionCardWidget(
            title_text="Manage Subjects",
            desc_text="Add, edit, and remove master subjects from the system.",
            icon_name="SUBJECTS"
        )
        subject_card.clicked.connect(self.manage_subjects_requested.emit)
        cards_layout.addWidget(subject_card)

        # Card for managing app settings
        settings_card = ActionCardWidget(
            title_text="App Settings",
            desc_text="Manage your user profile and application-wide settings.",
            icon_name="CONFIGURATIONS"
        )
        settings_card.clicked.connect(self.app_settings_requested.emit)
        cards_layout.addWidget(settings_card)

        # Card for developer tools
        self.dev_tools_card = ActionCardWidget(
            title_text="Developer Tools",
            desc_text="Tools for testing and development.",
            icon_name="DEV_TOOLS"
        )
        self.dev_tools_card.clicked.connect(self.developer_tools_requested.emit)
        cards_layout.addWidget(self.dev_tools_card)
        self.dev_tools_card.setVisible(False) # Hidden by default

        main_layout.addStretch()

    def set_developer_mode(self, is_dev: bool):
        """Shows or hides the developer tools card."""
        self.dev_tools_card.setVisible(is_dev)
    