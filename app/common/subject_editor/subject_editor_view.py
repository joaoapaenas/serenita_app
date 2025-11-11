# app/commom/subject_editor/subject_editor_view.py
import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QPushButton, QHBoxLayout
)

from app.core.icon_manager import get_icon

log = logging.getLogger(__name__)


class SubjectEditorView(QDialog):
    """
    The View for adding or editing a single Subject. It is a simple
    data entry form that emits the collected data.
    """
    # Signal to emit the new subject data when saved.
    # The signal will carry a dictionary.
    subject_saved = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        log.debug("Initializing SubjectEditorView dialog.")
        self.setWindowTitle("Add New Subject")
        self.setModal(True)
        self.setMinimumWidth(350)

        # Main layout
        self.layout = QVBoxLayout(self)

        # Form layout for inputs
        form_layout = QFormLayout()

        # Input Widgets
        self.subject_name_input = QLineEdit()
        self.relevance_input = self._create_weight_spinbox()
        self.volume_input = self._create_weight_spinbox()
        self.difficulty_input = self._create_weight_spinbox()

        # Add widgets to form layout
        form_layout.addRow("Subject Name:", self.subject_name_input)
        form_layout.addRow("Relevance (in exam):", self.relevance_input)
        form_layout.addRow("Content Volume:", self.volume_input)
        form_layout.addRow("Personal Difficulty:", self.difficulty_input)

        self.layout.addLayout(form_layout)

        # Action Buttons
        self._setup_action_buttons()

    @staticmethod
    def _create_weight_spinbox():
        """Helper function to create a standardized QSpinBox for weights."""
        spinbox = QSpinBox()
        spinbox.setRange(1, 5)
        spinbox.setValue(3)  # Default value
        return spinbox

    def _setup_action_buttons(self):
        """Creates the Save and Cancel buttons."""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()  # Push buttons to the right

        self.save_button = QPushButton(" Save Subject")
        self.save_button.setIcon(get_icon("SAVE"))
        self.save_button.clicked.connect(self.on_save)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # reject() is a standard QDialog slot to close

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(buttons_layout)

    def on_save(self):
        """Collects data and emits the subject_saved signal."""
        # The view no longer validates, it just gathers raw data.
        subject_data = {
            "name": self.subject_name_input.text().strip(),
            "relevance": self.relevance_input.value(),
            "volume": self.volume_input.value(),
            "difficulty": self.difficulty_input.value()
        }
        log.info(f"Save button clicked in SubjectEditorView. Emitting data: {subject_data}")
        # Emit the signal with the raw data dictionary
        self.subject_saved.emit(subject_data)
        # The controller is now responsible for closing the dialog.