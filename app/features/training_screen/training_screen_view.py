# app/features/training_screen/training_screen_view.py

import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PySide6.QtCore import Qt

from .exercise_details_view import ExerciseDetailsView
from .widgets import ExerciseContentWidget, SessionOverviewWidget, SettingsToolsWidget # Import the new widgets

log = logging.getLogger(__name__)


class TrainingScreenView(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        log.debug("Initializing TrainingScreenView.")
        self.setObjectName("TrainingScreenView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins for full tab widget usage

        # Bottom Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("TrainingTabWidget")
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South) # Set tabs to the bottom

        # Add "Study" tab (main content area for exercises)
        self.study_tab = QWidget()
        self.study_tab_layout = QVBoxLayout(self.study_tab)
        
        # Add the ExerciseContentWidget to the study tab
        self.exercise_content_widget = ExerciseContentWidget()
        self.study_tab_layout.addWidget(self.exercise_content_widget)
        
        # Integrate ExerciseDetailsView directly into the Study tab's layout
        self.exercise_details_view = ExerciseDetailsView()
        self.study_tab_layout.addWidget(self.exercise_details_view)
        
        self.tab_widget.addTab(self.study_tab, "Log Exercises")

        # Add "Session Overview/Progress" tab
        self.session_overview_tab = QWidget()
        self.session_overview_tab_layout = QVBoxLayout(self.session_overview_tab)
        
        # Add the SessionOverviewWidget to the session overview tab
        self.session_overview_widget = SessionOverviewWidget()
        self.session_overview_tab_layout.addWidget(self.session_overview_widget)
        
        self.tab_widget.addTab(self.session_overview_tab, "Session Overview/Progress")

        # Add "Settings/Tools" tab
        self.settings_tools_tab = QWidget()
        self.settings_tools_tab_layout = QVBoxLayout(self.settings_tools_tab)
        
        # Add the SettingsToolsWidget to the settings/tools tab
        self.settings_tools_widget = SettingsToolsWidget()
        self.settings_tools_tab_layout.addWidget(self.settings_tools_widget)
        
        self.tab_widget.addTab(self.settings_tools_tab, "Settings/Tools")

        # Add the tab widget to the main layout
        main_layout.addWidget(self.tab_widget)
