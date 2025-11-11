# app/feature/study_session/study_session_widget.py
import logging
from typing import Protocol

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QTextEdit, QComboBox

from app.core.icon_manager import get_icon
from app.models.subject import Topic

from .states.logging_state import LoggingState
from .states.timer_state import TimerState

log = logging.getLogger(__name__)



class ISessionState(Protocol):
    """
    Defines the interface for all session states. Each state is responsible
    for building its own UI and handling its specific events.
    """

    def __init__(self, context: "StudySessionWidget"):
        """Initializes the state with a reference to the context widget."""
        ...

    def enter(self):
        """
        Called when this state is entered. This method is responsible for
        clearing the old UI and building the new one for this state.
        """
        ...


class StudySessionWidget(QWidget):
    """
    A non-modal widget for an in-progress study session. This class acts as the
    'Context' in a State design pattern. It holds a reference to a state
    object and delegates UI building and state-specific logic to it.
    """
    logging_requested = Signal()
    session_finished = Signal(dict)
    session_paused = Signal()
    session_resumed = Signal()

    def __init__(self, subject_name: str, topic_name: str | None, topics: list[Topic], parent=None):
        super().__init__(parent)
        log.debug(f"Initializing StudySessionWidget for subject: '{subject_name}'")
        self.setObjectName("StudySessionWidget")

        # --- Shared UI Elements (owned by the Context) ---
        self.timer_label = QLabel("00:00")
        self.pause_resume_button = QPushButton()  # Text/icon set by state
        self.questions_done_input = QSpinBox()
        self.questions_correct_input = QSpinBox()
        self.description_input = QTextEdit()
        self.topic_combo = QComboBox()

        # --- Context Data ---
        self.subject_name = subject_name
        self.topic_name = topic_name
        self.topics = topics

        # --- State Management ---
        self._state: ISessionState = None
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pause_resume_button.setCheckable(True)
        self.pause_resume_button.toggled.connect(self._on_pause_toggled)

        self.set_state(TimerState(self))

    def set_state(self, new_state: ISessionState):
        """Transitions the widget to a new state and tells it to build its UI."""
        log.info(f"Transitioning session widget to state: {new_state.__class__.__name__}")
        self._state = new_state
        self._state.enter()

    def show_logging_view(self):
        """
        Public method for the CONTROLLER to call to force a transition
        to the logging state.
        """
        if not isinstance(self._state, LoggingState):
            self.set_state(LoggingState(self))

    def save_log(self, log_data: dict):
        """
        Public method for states to call to finalize the log.
        This now receives the full data package from the state.
        """
        log.info("Save log action triggered. Emitting session_finished signal.")
        self.session_finished.emit(log_data)

    def update_timer_display(self, time_str: str):
        self.timer_label.setText(time_str)

    def _on_pause_toggled(self, checked: bool):
        if checked:
            self.pause_resume_button.setText("Resume")
            self.pause_resume_button.setIcon(get_icon("START_SESSION"))
            log.debug("Session paused. Emitting session_paused signal.")
            self.session_paused.emit()
        else:
            self.pause_resume_button.setText("Pause")
            self.pause_resume_button.setIcon(get_icon("PAUSE"))
            log.debug("Session resumed. Emitting session_resumed signal.")
            self.session_resumed.emit()

    def clear_layout(self):
        """Helper method provided to states for clearing the UI before drawing."""
        while item := self.layout.takeAt(0):
            if widget := item.widget():
                widget.deleteLater()
            elif layout := item.layout():
                while layout_item := layout.takeAt(0):
                    if sub_widget := layout_item.widget():
                        sub_widget.deleteLater()