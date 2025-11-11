# app/feature/cycle_editor/cycle_editor_view.py
import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.core.constants import PAGE_MARGINS, SPACING_XLARGE
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR
from .components.cycle_settings_widget import CycleSettingsWidget
from .components.subject_selector_presenter import SubjectSelectorPresenter
from .components.subject_selector_widget import SubjectSelectorWidget

log = logging.getLogger(__name__)


class CycleEditorView(QWidget):
    save_requested = Signal(dict, list)
    cancel_requested = Signal()
    master_subject_add_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cycle_to_edit_id = None
        log.debug("Initializing CycleEditorView UI shell.")

        # --- UI Shell Setup (Data-Independent) ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_XLARGE)

        self.title_label = QLabel()  # Text will be set by controller during population
        self.title_label.setObjectName("viewTitle")
        main_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.settings_widget = CycleSettingsWidget(self)
        main_layout.addWidget(self.settings_widget)

        self.subject_selector_widget = SubjectSelectorWidget(self)
        self.subject_selector_presenter = SubjectSelectorPresenter(self.subject_selector_widget, self)
        self.subject_selector_widget.master_subject_add_requested.connect(self.master_subject_add_requested.emit)
        main_layout.addWidget(self.subject_selector_widget, stretch=1)

        action_buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_requested.emit)
        self.save_cycle_button = QPushButton("Save Cycle")
        self.save_cycle_button.setIcon(get_icon("SAVE", color=THEME_ACCENT_TEXT_COLOR))
        self.save_cycle_button.setObjectName("primaryButton")
        self.save_cycle_button.clicked.connect(self._on_save_clicked)
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(cancel_button)
        action_buttons_layout.addWidget(self.save_cycle_button)
        main_layout.addLayout(action_buttons_layout)

    def populate_data(self, cycle_to_edit=None, subjects_in_cycle=None, master_subjects=None):
        """Populates the view's widgets with data provided by the controller."""
        self.cycle_to_edit_id = cycle_to_edit['id'] if cycle_to_edit else None

        title_text = "Edit Study Cycle" if self.cycle_to_edit_id else "Create New Study Cycle"
        self.title_label.setText(title_text)

        self.subject_selector_presenter.load_master_subjects(master_subjects or [])

        if cycle_to_edit:
            self.settings_widget.set_data(
                cycle_to_edit['cycle_name'],
                cycle_to_edit['block_duration_min'],
                cycle_to_edit['is_continuous'],
                cycle_to_edit['daily_goal_blocks'],
                cycle_to_edit['timing_strategy']
            )
            if subjects_in_cycle:
                self.subject_selector_presenter.populate_for_editing(subjects_in_cycle)
        else:
            # If creating new, ensure fields are cleared or set to default
            self.settings_widget.cycle_name_input.setText("")
            self.settings_widget.set_data("", 60, True, 2, "Adaptive")

    def _on_save_clicked(self):
        cycle_data = self.settings_widget.get_data()
        cycle_data['id'] = self.cycle_to_edit_id
        subjects_data = self.subject_selector_presenter.get_configured_subjects()
        log.info(
            f"Save button clicked. Emitting save_requested for cycle '{cycle_data['name']}' with {len(subjects_data)} subjects.")
        self.save_requested.emit(cycle_data, subjects_data)

    def get_subject_selector(self) -> SubjectSelectorWidget:
        """Provides access to the raw widget for specific commands like adding a new master subject."""
        return self.subject_selector_widget