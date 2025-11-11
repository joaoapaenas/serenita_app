# app/feature/study_session/session_states.py

from __future__ import annotations

import logging
import random
from typing import Protocol, TYPE_CHECKING, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFormLayout

from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from app.models.session import QuestionPerformance

# Use a forward reference to avoid a circular import error.
if TYPE_CHECKING:
    from .study_session_widget import StudySessionWidget

log = logging.getLogger(__name__)


class ISessionState(Protocol):
    """
    Defines the interface for all session states. Each state is responsible
    for building its own UI and handling its specific events.
    """

    def __init__(self, context: StudySessionWidget):
        """Initializes the state with a reference to the context widget."""
        ...

    def enter(self):
        """
        Called when this state is entered. This method is responsible for
        clearing the old UI and building the new one for this state.
        """
        ...


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


class LoggingState:
    """The state for when the user is logging performance data."""

    def __init__(self, context: 'StudySessionWidget'):
        self._context = context

    def enter(self):
        log.debug("Entering LoggingState: building logging form UI.")
        self._context.clear_layout()

        log_label = QLabel(f"Log Performance for '{self._context.subject_name}'")
        log_label.setObjectName("viewTitle")

        form_layout = QFormLayout()

        # Populate and add the topic combo box
        self._context.topic_combo.clear()
        self._context.topic_combo.addItem("General Study (No Specific Topic)", None)
        for topic in self._context.topics:
            self._context.topic_combo.addItem(topic.name, topic.id)
        form_layout.addRow("Topic Studied:", self._context.topic_combo)

        # Reset input values
        self._reset_spinbox_values()
        self._context.questions_done_input.setRange(0, 1000)
        self._context.questions_correct_input.setRange(0, 1000)
        self._context.questions_done_input.valueChanged.connect(self._context.questions_correct_input.setMaximum)
        self._context.description_input.clear()
        self._context.description_input.setPlaceholderText("Any notes about this session?")
        self._context.description_input.setMaximumHeight(80)

        form_layout.addRow("Questions Done:", self._context.questions_done_input)
        form_layout.addRow("Questions Correct:", self._context.questions_correct_input)
        form_layout.addRow("Notes:", self._context.description_input)

        save_button = QPushButton("Save Log")
        save_button.setIcon(get_icon("SAVE", color=THEME_ACCENT_TEXT_COLOR))
        save_button.setObjectName("primaryButton")
        # Tell the context to save the log when clicked
        save_button.clicked.connect(self._on_save_clicked)

        self._context.layout.addStretch(1)
        self._context.layout.addWidget(log_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._context.layout.addLayout(form_layout)
        self._context.layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self._context.layout.addStretch(2)

    def _on_save_clicked(self):
        """Gathers aggregate data and generates simulated granular data."""
        topic_id = self._context.topic_combo.currentData()
        questions_done = self._context.questions_done_input.value()
        questions_correct = self._context.questions_correct_input.value()
        description = self._context.description_input.toPlainText().strip()

        generated_questions = self._generate_dummy_questions(questions_done, questions_correct)

        log_data = {
            'topic_id': topic_id,
            'questions_done': questions_done,
            'questions_correct': questions_correct,
            'description': description,
            'questions_list': generated_questions
        }
        self._context.save_log(log_data)

    @staticmethod
    def _generate_dummy_questions(total: int, correct: int) -> List[QuestionPerformance]:
        """Creates a list of QuestionPerformance objects matching the aggregates."""
        if total == 0:
            return []

        incorrect = total - correct
        results = ([True] * correct) + ([False] * incorrect)
        random.shuffle(results)

        dummy_questions = []
        for is_correct in results:
            # We don't have real topic/difficulty, so we use placeholders.
            # The engine is robust enough to handle this.
            dummy_questions.append(
                QuestionPerformance(
                    id=None,  # DB will assign
                    session_id=None,  # Service will assign
                    topic_name="general",
                    difficulty_level=random.randint(1, 5),
                    is_correct=is_correct
                )
            )
        return dummy_questions

    def _reset_spinbox_values(self):
        """Helper to ensure form is clear when entering state."""
        self._context.questions_done_input.blockSignals(True)
        self._context.questions_correct_input.blockSignals(True)

        self._context.questions_done_input.setValue(0)
        self._context.questions_correct_input.setValue(0)

        self._context.questions_done_input.blockSignals(False)
        self._context.questions_correct_input.blockSignals(False)
