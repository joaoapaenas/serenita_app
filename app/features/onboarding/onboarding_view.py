# app/features/onboarding/onboarding_view.py

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from app.models.exam import Exam
from .components.cycle_settings_page import CycleSettingsPage
from .components.define_exam_page import DefineExamPage
# Import the new page components
from .components.goal_page import GoalPage
from .components.import_topics_page import ImportTopicsPage
from .components.subjects_config_page import SubjectsConfigPage

log = logging.getLogger(__name__)


class OnboardingView(QWidget):
    """
    A container view for the onboarding wizard. It creates and manages the
    individual page widgets.
    """
    goal_selected = Signal(object)
    process_topics_requested = Signal(str, str)
    topics_changed = Signal(dict)
    next_step_requested = Signal()
    back_step_requested = Signal()
    finish_requested = Signal()
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.pages: list[QWidget] = []  # A list to hold the page instances

        main_layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        self.back_button = QPushButton(" Back")
        self.back_button.setIcon(get_icon("ARROW_LEFT"))
        self.next_button = QPushButton(" Next")
        self.next_button.setIcon(get_icon("ARROW_RIGHT"))
        self.finish_button = QPushButton(" Create My Study Plan")
        self.finish_button.setIcon(get_icon("MAGIC_WAND", color=THEME_ACCENT_TEXT_COLOR))
        self.cancel_button = QPushButton("Cancel")
        self.finish_button.setObjectName("primaryButton")

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.cancel_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.finish_button)
        main_layout.addLayout(nav_layout)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)

        self.next_button.clicked.connect(self.next_step_requested.emit)
        self.back_button.clicked.connect(self.back_step_requested.emit)
        self.finish_button.clicked.connect(self.finish_requested.emit)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

    def add_page(self, widget: QWidget):
        self.pages.append(widget)
        self.stacked_widget.addWidget(widget)

    def remove_page(self, page_index: int):
        if 0 <= page_index < len(self.pages):
            widget = self.pages.pop(page_index)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

    def go_to_page(self, page_widget: QWidget):
        """
        Navigates the stacked widget to the specified page widget.
        """
        # FIX: The logic is now much simpler. It is always given the exact
        # widget to show, removing any ambiguity with indexes.
        self.stacked_widget.setCurrentWidget(page_widget)

    def update_navigation(self, current_index: int, total_pages: int, can_proceed: bool):
        self.back_button.setVisible(current_index > 0)
        self.next_button.setVisible(current_index < total_pages - 1)
        self.finish_button.setVisible(current_index == total_pages - 1)
        self.next_button.setEnabled(can_proceed)
        self.finish_button.setEnabled(can_proceed)

    # --- Page Factory Methods ---
    def create_page_goal(self, templates: list[Exam]) -> GoalPage:
        page = GoalPage(templates, self)
        return page

    def create_page_define_exam(self) -> DefineExamPage:
        return DefineExamPage(self)

    def create_page_subjects_config(self) -> SubjectsConfigPage:
        return SubjectsConfigPage(self)

    def create_page_import_topics(self) -> ImportTopicsPage:
        page = ImportTopicsPage(self)
        return page

    def create_page_cycle_settings(self) -> CycleSettingsPage:
        return CycleSettingsPage(self)

    # --- Data Getter Methods ---
    def get_goal_selection(self) -> Exam | str:
        goal_page = next((p for p in self.pages if isinstance(p, GoalPage)), None)
        return goal_page.get_selection() if goal_page else "none"

    def get_custom_exam_data(self) -> dict:
        exam_page = next((p for p in self.pages if isinstance(p, DefineExamPage)), None)
        return exam_page.get_data() if exam_page else {}

    def get_custom_subjects_config(self) -> list:
        subjects_page = next((p for p in self.pages if isinstance(p, SubjectsConfigPage)), None)
        return subjects_page.get_data() if subjects_page else []

    def get_subject_order(self) -> list:
        settings_page = next((p for p in self.pages if isinstance(p, CycleSettingsPage)), None)
        return settings_page.get_subject_order() if settings_page else []

    def get_daily_goal(self) -> int:
        settings_page = next((p for p in self.pages if isinstance(p, CycleSettingsPage)), None)
        return settings_page.get_daily_goal() if settings_page else 3