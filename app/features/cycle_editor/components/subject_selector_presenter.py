# app/feature/cycle_editor/components/subject_selector_presenter.py

import logging
from typing import List, Dict, Any

from PySide6.QtCore import QObject, Signal

from app.models.subject import Subject, CycleSubject
from .subject_selector_widget import SubjectSelectorWidget

log = logging.getLogger(__name__)


class SubjectSelectorPresenter(QObject):
    """
    Presenter for the SubjectSelectorWidget. Manages the state and logic
    for selecting and configuring subjects in a cycle. This adheres to MVP
    by separating logic from the view.
    """
    selection_changed = Signal()

    def __init__(self, view: SubjectSelectorWidget, parent: QObject | None = None):
        super().__init__(parent)
        self._view = view
        self._master_subjects_map: Dict[int, Subject] = {}

        # This dictionary holds the configuration state for selected subjects.
        # Key: subject_id, Value: dict of weights and is_active status.
        self._configured_subjects: Dict[int, Dict[str, Any]] = {}

        self._connect_signals()

    def _connect_signals(self):
        """Connect to the view's signals to respond to user actions."""
        self._view.subject_toggled.connect(self._on_subject_toggled)
        self._view.subject_config_changed.connect(self._on_subject_config_changed)

    def load_master_subjects(self, master_subjects: List[Subject]):
        """Loads the list of all available subjects into the presenter and tells the view to display them."""
        self._master_subjects_map = {s.id: s for s in master_subjects}
        self._view.load_available_subjects(master_subjects)

    def add_new_master_subject(self, subject: Subject, check_item: bool):
        """
        Updates the internal map with a new master subject and commands the
        view to display it.
        """
        if subject.id not in self._master_subjects_map:
            self._master_subjects_map[subject.id] = subject
        self._view.add_new_master_subject(subject, check_item)

    def populate_for_editing(self, subjects_in_cycle: List[CycleSubject]):
        """Pre-populates the view and presenter state when editing an existing cycle."""
        self._view.blockSignals(True)  # Prevent signals during bulk population

        for cs in subjects_in_cycle:
            # 1. Update the presenter's internal state
            self._configured_subjects[cs.subject_id] = {
                "name": cs.name,
                "is_active": cs.is_active,
                "relevance": cs.relevance_weight,
                "volume": cs.volume_weight,
                "difficulty": cs.difficulty_weight
            }
            # 2. Command the view to update its UI
            self._view.set_subject_checked(cs.subject_id, True)
            self._view.add_or_update_selected_row(cs.subject_id, self._configured_subjects[cs.subject_id])

        self._view.blockSignals(False)

    def _on_subject_toggled(self, subject_id: int, is_checked: bool):
        """Handles the logic when a subject is checked or unchecked in the available list."""
        if is_checked:
            if subject_id not in self._configured_subjects:
                # Add with default values if it's new to the selection
                master_subject = self._master_subjects_map[subject_id]
                self._configured_subjects[subject_id] = {
                    "name": master_subject.name, "is_active": True,
                    "relevance": 3, "volume": 3, "difficulty": 3
                }
            # Command the view to show this subject in the selected table
            self._view.add_or_update_selected_row(subject_id, self._configured_subjects[subject_id])
        else:
            # Remove from our state and command the view to remove the row
            if subject_id in self._configured_subjects:
                del self._configured_subjects[subject_id]
            self._view.remove_selected_row(subject_id)

        self.selection_changed.emit()

    def _on_subject_config_changed(self, subject_id: int, config_data: Dict[str, Any]):
        """Handles a change in a spinbox or checkbox in the selected table."""
        if subject_id in self._configured_subjects:
            self._configured_subjects[subject_id].update(config_data)
        self.selection_changed.emit()

    def get_configured_subjects(self) -> List[Dict[str, Any]]:
        """
        Returns the final list of configured subjects.
        This logic is now cleanly separated from the UI.
        """
        # The keys of our state dict are the subject_ids. We just need the values.
        return list(self._configured_subjects.values())
