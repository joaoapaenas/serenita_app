# app/feature/study_session/states/timer_state.py
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from app.core.icon_manager import get_icon

if TYPE_CHECKING:
    from ..study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class TimerState:
    """The state for when the session timer is active."""

    def __init__(self, context: 'StudySessionWidget'):
        self._context = context

    def enter(self):
        log.debug("Entering TimerState: building timer UI.")
        self._context.clear_layout()

        subject_label = QLabel(self._context.subject_name)
        subject_label.setObjectName("viewTitle")
        topic_text = self._context.topic_name or "General Study"
        topic_label = QLabel(topic_text)
        topic_label.setObjectName("sectionHeader")
        self._context.timer_label.setObjectName("timerDisplay")

        self._context.pause_resume_button.setText("Pause")
        self._context.pause_resume_button.setIcon(get_icon("PAUSE"))
        self._context.pause_resume_button.setChecked(False)

        finish_button = QPushButton("Finish & Log")
        finish_button.setIcon(get_icon("FINISH_FLAG"))
        finish_button.clicked.connect(self._context.logging_requested.emit)

        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        controls_layout.addWidget(self._context.pause_resume_button)
        controls_layout.addWidget(finish_button)
        controls_layout.addStretch()

        self._context.layout.addStretch(1)
        self._context.layout.addWidget(subject_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._context.layout.addWidget(topic_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._context.layout.addWidget(self._context.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._context.layout.addLayout(controls_layout)
        self._context.layout.addStretch(2)