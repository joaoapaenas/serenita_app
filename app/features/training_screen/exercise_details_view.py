# app/features/training_screen/exercise_details_view.py

import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtCore import Qt

from .widgets import RestTimerWidget, ExerciseStatsWidget, ExerciseNotesWidget

log = logging.getLogger(__name__)


class ExerciseDetailsView(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        log.debug("Initializing ExerciseDetailsView.")
        self.setObjectName("ExerciseDetailsView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("ExerciseDetailsTabWidget")
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South) # Set tabs to the bottom

        # Add placeholder tabs for exercise details
        self.rest_timer_tab = RestTimerWidget()
        self.tab_widget.addTab(self.rest_timer_tab, "Rest Timer")

        self.exercise_stats_tab = ExerciseStatsWidget()
        self.tab_widget.addTab(self.exercise_stats_tab, "Exercise Stats")

        self.exercise_notes_tab = ExerciseNotesWidget()
        self.tab_widget.addTab(self.exercise_notes_tab, "Exercise Notes")

        main_layout.addWidget(self.tab_widget)