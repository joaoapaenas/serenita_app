# app/feature/cycle_editor/components/subject_selector_widget.py

import logging
from typing import List

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter

from app.models.subject import Subject

from .available_subjects_widget import AvailableSubjectsWidget
from .configured_subjects_widget import ConfiguredSubjectsWidget

log = logging.getLogger(__name__)


class SubjectSelectorWidget(QWidget):
    """
    A 'dumb' view component for selecting and configuring subjects.
    It holds no state and emits signals for all user interactions, which are
    handled by its Presenter. This class has been refactored to be a container
    for AvailableSubjectsWidget and ConfiguredSubjectsWidget.
    """
    # --- Signals for the presenter ---
    master_subject_add_requested = Signal(str)
    subject_toggled = Signal(int, bool)  # subject_id, is_checked
    subject_config_changed = Signal(int, dict)  # subject_id, {key: value}

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.available_pane = AvailableSubjectsWidget(self)
        self.selected_pane = ConfiguredSubjectsWidget(self)

        splitter.addWidget(self.available_pane)
        splitter.addWidget(self.selected_pane)
        splitter.setSizes([280, 500])

        self.available_pane.master_subject_add_requested.connect(self.master_subject_add_requested.emit)
        self.available_pane.subject_toggled.connect(self.subject_toggled.emit)
        self.selected_pane.subject_config_changed.connect(self.subject_config_changed.emit)

    def blockSignals(self, block: bool):
        """Blocks signals for all relevant widgets during bulk updates."""
        self.available_pane.blockSignals(block)
        self.selected_pane.blockSignals(block)

    def load_available_subjects(self, master_subjects: List[Subject]):
        """Clears and populates the available subjects list."""
        self.available_pane.load_available_subjects(master_subjects)

    def add_new_master_subject(self, subject: Subject, check_item: bool = False):
        """Adds a newly created master subject to the available list."""
        self.available_pane.add_new_master_subject(subject, check_item)

    def set_subject_checked(self, subject_id: int, is_checked: bool):
        """Finds a subject in the available list and sets its checked state."""
        self.available_pane.set_subject_checked(subject_id, is_checked)

    def add_or_update_selected_row(self, subject_id: int, data: dict):
        """Adds a new row to the selected table or updates it if it exists."""
        self.selected_pane.add_or_update_row(subject_id, data)

    def remove_selected_row(self, subject_id: int):
        """Removes a subject's row from the selected table."""
        self.selected_pane.remove_row(subject_id)
