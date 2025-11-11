# app/feature/main_window/components/work_unit_card_widget.py

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR

log = logging.getLogger(__name__)


class WorkUnitCardWidget(QFrame):
    """A card that displays a single Work Unit from the tactical plan."""
    completion_requested = Signal(str)  # Emits the work_unit_id

    def __init__(self, task_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("blockWidget")
        self.task_data = task_data

        main_layout = QHBoxLayout(self)

        # Left side: Information
        info_layout = QVBoxLayout()
        title_label = QLabel(task_data.get('work_unit_title', 'Unnamed Task'))
        title_label.setObjectName("blockTitle")

        context_text = f"{task_data.get('subject_name', 'N/A')} ({task_data.get('allocated_minutes', 0)} min)"
        context_label = QLabel(context_text)
        context_label.setObjectName("lightText")

        info_layout.addWidget(title_label)
        info_layout.addWidget(context_label)
        info_layout.addStretch()

        # Right side: Action Button
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.complete_button = QPushButton(" Mark as Done")  # Made instance attribute
        self.complete_button.setIcon(get_icon("ACCEPT", color=THEME_ACCENT_TEXT_COLOR))
        self.complete_button.setObjectName("primaryButton")
        self.complete_button.clicked.connect(self._on_complete)

        action_layout.addWidget(self.complete_button)

        main_layout.addLayout(info_layout, stretch=1)
        main_layout.addLayout(action_layout)

        # --- Set initial completed state directly from task_data ---
        if task_data.get('is_completed', False):
            self.set_completed_state()

    def _on_complete(self):
        """Emits the ID and updates the UI state immediately."""
        log.debug(f"Completion requested for work unit: {self.task_data.get('work_unit_title')}")
        self.set_completed_state()
        self.completion_requested.emit(self.task_data.get('work_unit_id'))

    def set_completed_state(self):
        """Visually updates the card to a 'completed' state."""
        self.complete_button.setText("Done!")
        self.complete_button.setEnabled(False)
        # Add a property to the stylesheet to visually distinguish completed cards
        self.setProperty("completed", True)
        self.style().polish(self)  # Re-apply stylesheet

        # Add a visual indicator that this task is completed
        completed_label = QLabel("✓ COMPLETED")
        completed_label.setObjectName("completedIndicator")
        completed_label.setStyleSheet("""
            color: #4CAF50;
            font-weight: bold;
            font-size: 10pt;
        """)

        # Add the completed label to the top right corner
        layout = self.layout()
        if layout:
            # Find the header layout (first item in the main layout)
            if layout.count() > 0:
                header_item = layout.itemAt(0)
                if header_item and header_item.layout():
                    header_layout = header_item.layout()
                    header_layout.addWidget(completed_label, 0, Qt.AlignmentFlag.AlignRight)