# app/features/subject_details/components/work_unit_editor_view.py

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QSpinBox, QPushButton, QHBoxLayout, QApplication)

from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from app.models.subject import WorkUnit

log = logging.getLogger(__name__)


class WorkUnitEditorView(QDialog):
    """A modal dialog for creating or editing a single Work Unit."""
    save_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Work Unit Editor")
        self.setModal(True)
        self.setMinimumWidth(400)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Read Chapter 1: Limits")

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Reading", "Problem Set", "Video Lecture", "Review", "Practice Exam"])

        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(5, 480)
        self.time_spinbox.setValue(60)
        self.time_spinbox.setSuffix(" minutes")

        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., limits (for performance tracking)")

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Type:", self.type_combo)
        form_layout.addRow("Estimated Time:", self.time_spinbox)
        form_layout.addRow("Performance Topic:", self.topic_input)

        main_layout.addLayout(form_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton(" Save Work Unit")
        self.save_button.setIcon(get_icon("SAVE", color=THEME_ACCENT_TEXT_COLOR))
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

    def _on_save(self):
        """Gathers data from the form and emits it."""
        data = {
            "title": self.title_input.text().strip(),
            "type": self.type_combo.currentText(),
            "estimated_time": self.time_spinbox.value(),
            "topic": self.topic_input.text().strip()
        }
        self.save_requested.emit(data)

    def set_data(self, work_unit: WorkUnit):
        """Populates the form with data from an existing WorkUnit for editing."""
        self.setWindowTitle("Edit Work Unit")
        self.title_input.setText(work_unit.title)
        self.type_combo.setCurrentText(work_unit.type)
        self.time_spinbox.setValue(work_unit.estimated_time_minutes)
        self.topic_input.setText(work_unit.related_questions_topic)