# app/feature/cycle_editor/components/available_subjects_widget.py
import logging
from typing import List

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem
)

from app.core.icon_manager import get_icon
from app.models.subject import Subject

log = logging.getLogger(__name__)


class AvailableSubjectsWidget(QWidget):
    """A widget for displaying and interacting with the list of available master subjects."""
    master_subject_add_requested = Signal(str)
    subject_toggled = Signal(int, bool)  # subject_id, is_checked

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 5, 0)
        header = QLabel("AVAILABLE SUBJECTS")
        header.setObjectName("sectionHeader")

        self.available_list = QListWidget()
        self.available_list.itemChanged.connect(self._on_item_changed)

        add_subject_layout = QHBoxLayout()
        self.new_subject_input = QLineEdit()
        self.new_subject_input.setPlaceholderText("Add a new subject...")
        self.add_master_subject_button = QPushButton()
        self.add_master_subject_button.setIcon(get_icon("ADD"))
        self.add_master_subject_button.setObjectName("addButton")
        self.add_master_subject_button.setToolTip("Add to Master List")
        self.add_master_subject_button.setEnabled(False)
        self.new_subject_input.textChanged.connect(
            lambda text: self.add_master_subject_button.setEnabled(bool(text.strip())))
        self.add_master_subject_button.clicked.connect(self._on_add_master_subject)
        add_subject_layout.addWidget(self.new_subject_input)
        add_subject_layout.addWidget(self.add_master_subject_button)

        layout.addWidget(header)
        layout.addWidget(self.available_list)
        layout.addLayout(add_subject_layout)

    def load_available_subjects(self, master_subjects: List[Subject]):
        """Clears and populates the available subjects list."""
        self.blockSignals(True)
        self.available_list.clear()
        for subject in master_subjects:
            self.add_new_master_subject(subject, check_item=False)  # Re-use add logic
        self.blockSignals(False)

    def add_new_master_subject(self, subject: Subject, check_item: bool = False):
        """Adds a newly created master subject to the available list."""
        item = QListWidgetItem(subject.name)
        item.setData(Qt.ItemDataRole.UserRole, subject.id)
        # --- FIX: Add the flag that makes the item checkable ---
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        # --- END FIX ---
        self.available_list.addItem(item)
        if check_item:
            # Set unchecked first to ensure the itemChanged signal fires correctly
            # if it's already considered "checked" from a previous state.
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)
        self.available_list.scrollToItem(item)

    def set_subject_checked(self, subject_id: int, is_checked: bool):
        """Finds a subject in the available list and sets its checked state."""
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == subject_id:
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
                break

    def blockSignals(self, should_block: bool):
        self.available_list.blockSignals(should_block)

    def _on_add_master_subject(self):
        subject_name = self.new_subject_input.text().strip()
        if subject_name:
            self.master_subject_add_requested.emit(subject_name)
            self.new_subject_input.clear()

    def _on_item_changed(self, item: QListWidgetItem):
        subject_id = item.data(Qt.ItemDataRole.UserRole)
        is_checked = item.checkState() == Qt.CheckState.Checked
        self.subject_toggled.emit(subject_id, is_checked)