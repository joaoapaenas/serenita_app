# app/feature/main_window/components/today_dashboard_widget.py

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar

from app.core.constants import PAGE_MARGINS
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from app.models.cycle import Cycle
from app.models.subject import CycleSubject

log = logging.getLogger(__name__)


class TodayDashboardWidget(QWidget):
    """
    A widget that displays the user's generated study plan for the current day.
    """
    start_session_requested = Signal(CycleSubject)  # Emits the specific subject to start

    # --- MODIFIED: Accept minutes instead of counts ---
    def __init__(self, cycle: Cycle, todays_plan: list, completed_minutes: int, goal_minutes: int, parent=None):
        super().__init__(parent)
        log.debug(f"Initializing TodayDashboardWidget for cycle '{cycle.name}'. Plan has {len(todays_plan)} blocks.")
        self.setObjectName("TodayDashboardWidget")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Header with progress ---
        header_layout = QHBoxLayout()

        title = QLabel(f"Active Cycle: {cycle.name}")
        title.setObjectName("viewTitle")
        header_layout.addWidget(title)

        # Add progress indicator
        self._add_progress_indicator(header_layout, completed_minutes, goal_minutes)

        main_layout.addLayout(header_layout)

        # --- Progress display ---
        progress_text = f"Today's Goal: {completed_minutes} of {goal_minutes} Minutes Completed"
        progress_label = QLabel(progress_text)
        progress_label.setObjectName("sectionHeader")

        main_layout.addWidget(progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        # --- MODIFIED: The condition for completion is now based on time ---
        if not todays_plan or completed_minutes >= goal_minutes:
            log.info("Today's time-based goal is complete.")
            all_done_label = QLabel("🎉 Daily goal complete! Great work! 🎉")
            all_done_label.setObjectName("largeDisplay")
            main_layout.addWidget(all_done_label, alignment=Qt.AlignmentFlag.AlignCenter, stretch=1)
        else:
            log.debug("Building dashboard with today's plan.")

            # Add a clear indicator for the next subject
            if todays_plan:
                next_subject_label = QLabel(f"Next Subject: {todays_plan[0].name}")
                next_subject_label.setObjectName("nextSubjectIndicator")
                main_layout.addWidget(next_subject_label, alignment=Qt.AlignmentFlag.AlignCenter)

            plan_label = QLabel("TODAY'S PLAN")
            plan_label.setObjectName("sectionHeader")
            main_layout.addWidget(plan_label)

            next_subject = todays_plan[0]
            self._create_block_widget(main_layout, next_subject, is_next=True, duration=cycle.block_duration_min)

            if len(todays_plan) > 1:
                upcoming_label = QLabel("UPCOMING")
                upcoming_label.setObjectName("sectionHeader")
                main_layout.addWidget(upcoming_label)
                for subject in todays_plan[1:]:
                    self._create_block_widget(main_layout, subject, is_next=False, duration=cycle.block_duration_min)

        main_layout.addStretch()

    def _add_progress_indicator(self, layout, completed_minutes, goal_minutes):
        """Add a visual progress indicator."""
        progress_percent = (completed_minutes / goal_minutes * 100) if goal_minutes > 0 else 0

        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(int(progress_percent))
        self.progress_bar.setFixedWidth(150)
        progress_layout.addWidget(self.progress_bar)

        progress_layout.addWidget(QLabel(f"{int(progress_percent)}%"))

        layout.addWidget(progress_widget)
        layout.addStretch()

    def _create_block_widget(self, layout: QVBoxLayout, subject: CycleSubject, is_next: bool, duration: int):
        """Helper to create a row for a study block."""
        block_widget = QWidget()
        block_widget.setObjectName("blockWidget")

        # Apply special styling for the next subject
        if is_next:
            block_widget.setObjectName("nextSubjectBlock")
            block_widget.setStyleSheet("""
                #nextSubjectBlock {
                    background-color: #FFF8E1; /* Light yellow background */
                    border: 2px solid #FFCC00; /* Yellow border */
                    border-radius: 8px;
                    padding: 10px;
                }
            """)

        block_layout = QHBoxLayout(block_widget)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon("SUBJECTS").pixmap(24, 24))

        name_label = QLabel(subject.name)
        name_label.setObjectName("blockTitle")

        duration_label = QLabel(f"{duration} min")
        duration_label.setObjectName("lightText")

        block_layout.addWidget(icon_label)
        block_layout.addWidget(name_label, stretch=1)
        block_layout.addWidget(duration_label)

        if is_next:
            log.debug(f"Created 'Next Up' block widget for subject '{subject.name}'.")
            start_button = QPushButton("Start Session")
            start_button.setIcon(get_icon("START_SESSION", color=THEME_ACCENT_TEXT_COLOR))
            start_button.setObjectName("primaryButton")
            start_button.clicked.connect(lambda: self.start_session_requested.emit(subject))
            block_layout.addWidget(start_button)
        else:
            log.debug(f"Created 'Upcoming' block widget for subject '{subject.name}'.")

        layout.addWidget(block_widget)