# app/features/session_mode_choice/session_mode_choice_view.py
import logging
from datetime import datetime

from PySide6.QtCore import Signal, Qt, QDate, QTime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                               QComboBox, QDateEdit, QTimeEdit, QSpinBox, QFormLayout)

from app.common.widgets.card_widget import ActionCardWidget
from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from app.models.subject import Subject, Topic

log = logging.getLogger(__name__)


class SessionModeChoiceView(QWidget):
    """
    A view that allows the user to choose between logging a session manually
    or starting a live stopwatch timer.
    """
    manual_log_submitted = Signal(dict)
    stopwatch_start_submitted = Signal(dict)
    subject_changed = Signal(int)
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)

        title = QLabel("How would you like to record this session?")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack = QStackedWidget()
        self._create_choice_page()
        self._create_manual_log_page()
        self._create_stopwatch_page()

        main_layout.addWidget(self.stack)

    def _create_choice_page(self):
        """Creates the initial page with two ActionCardWidgets."""
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setSpacing(SPACING_LARGE)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        manual_card = ActionCardWidget(
            "Manual Log", "Log a study session that you've already completed.", "EDIT"
        )
        manual_card.clicked.connect(lambda: self.stack.setCurrentWidget(self.manual_page))

        stopwatch_card = ActionCardWidget(
            "Live Stopwatch", "Start a new study session with a real-time timer.", "START_SESSION"
        )
        stopwatch_card.clicked.connect(lambda: self.stack.setCurrentWidget(self.stopwatch_page))

        layout.addWidget(manual_card)
        layout.addWidget(stopwatch_card)
        self.stack.addWidget(page)

    def _create_manual_log_page(self):
        """Creates the form for manually logging a session."""
        self.manual_page = QWidget()
        layout = QVBoxLayout(self.manual_page)
        form_layout = QFormLayout()

        self.manual_subject_combo = QComboBox()
        self.manual_topic_combo = QComboBox()
        self.manual_date_edit = QDateEdit(QDate.currentDate())
        self.manual_date_edit.setCalendarPopup(True)
        self.manual_time_edit = QTimeEdit(QTime.currentTime())
        self.manual_duration_spinbox = QSpinBox()
        self.manual_duration_spinbox.setRange(1, 480)
        self.manual_duration_spinbox.setValue(60)
        self.manual_duration_spinbox.setSuffix(" minutes")

        form_layout.addRow("Subject:", self.manual_subject_combo)
        form_layout.addRow("Topic:", self.manual_topic_combo)
        form_layout.addRow("Start Date:", self.manual_date_edit)
        form_layout.addRow("Start Time:", self.manual_time_edit)
        form_layout.addRow("Duration:", self.manual_duration_spinbox)

        save_button = QPushButton(" Save Manual Log")
        save_button.setIcon(get_icon("SAVE", color=THEME_ACCENT_TEXT_COLOR))
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self._on_manual_save)

        layout.addWidget(QLabel("Manual Session Log"), 0, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addLayout(self._create_nav_buttons(save_button))

        self.manual_subject_combo.currentIndexChanged.connect(
            lambda: self.subject_changed.emit(self.manual_subject_combo.currentData())
        )
        self.stack.addWidget(self.manual_page)

    def _create_stopwatch_page(self):
        """Creates the form for confirming the subject before starting the stopwatch."""
        self.stopwatch_page = QWidget()
        layout = QVBoxLayout(self.stopwatch_page)
        form_layout = QFormLayout()

        self.stopwatch_subject_combo = QComboBox()
        self.stopwatch_topic_combo = QComboBox()

        form_layout.addRow("Subject:", self.stopwatch_subject_combo)
        form_layout.addRow("Topic:", self.stopwatch_topic_combo)

        start_button = QPushButton(" Start Activity")
        start_button.setIcon(get_icon("START_SESSION", color=THEME_ACCENT_TEXT_COLOR))
        start_button.setObjectName("primaryButton")
        start_button.clicked.connect(self._on_stopwatch_start)

        layout.addWidget(QLabel("Confirm Session Details"), 0, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addLayout(self._create_nav_buttons(start_button))

        self.stopwatch_subject_combo.currentIndexChanged.connect(
            lambda: self.subject_changed.emit(self.stopwatch_subject_combo.currentData())
        )
        self.stack.addWidget(self.stopwatch_page)

    def _create_nav_buttons(self, primary_button: QPushButton) -> QHBoxLayout:
        """Helper to create the back/cancel/primary button layout."""
        layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_requested.emit)

        layout.addWidget(cancel_btn)
        layout.addWidget(back_button)
        layout.addStretch()
        layout.addWidget(primary_button)
        return layout

    def populate_subjects(self, subjects: list[Subject], initial_subject: Subject | None):
        """Populates both subject combo boxes."""
        for combo in [self.manual_subject_combo, self.stopwatch_subject_combo]:
            combo.blockSignals(True)
            combo.clear()
            for subject in subjects:
                combo.addItem(subject.name, subject.id)
            if initial_subject:
                combo.setCurrentText(initial_subject.name)
            combo.blockSignals(False)

    def populate_topics(self, topics: list[Topic]):
        """Populates both topic combo boxes."""
        for combo in [self.manual_topic_combo, self.stopwatch_topic_combo]:
            combo.clear()
            combo.addItem("General Study (No Topic)", None)
            for topic in topics:
                combo.addItem(topic.name, topic.id)

    def _on_manual_save(self):
        date = self.manual_date_edit.date().toString("yyyy-MM-dd")
        time = self.manual_time_edit.time().toString("HH:mm:ss")
        start_datetime = f"{date}T{time}"

        data = {
            "subject_id": self.manual_subject_combo.currentData(),
            "topic_id": self.manual_topic_combo.currentData(),
            "start_datetime": start_datetime,
            "duration_minutes": self.manual_duration_spinbox.value()
        }
        self.manual_log_submitted.emit(data)

    def _on_stopwatch_start(self):
        data = {
            "subject_id": self.stopwatch_subject_combo.currentData(),
            "topic_id": self.stopwatch_topic_combo.currentData(),
            "topic_name": self.stopwatch_topic_combo.currentText()
        }
        self.stopwatch_start_submitted.emit(data)