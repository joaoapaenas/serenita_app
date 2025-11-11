# app/feature/cycle_editor/components/cycle_settings_widget.py

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox

log = logging.getLogger(__name__)


class CycleSettingsWidget(QWidget):
    """Component for editing a cycle's main properties, including scheduling rules."""
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        log.debug("Initializing CycleSettingsWidget.")
        layout = QFormLayout(self)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.cycle_name_input = QLineEdit()
        self.cycle_name_input.setPlaceholderText("e.g., Spring Semester Exam Prep")

        self.block_duration_input = QSpinBox()
        self.block_duration_input.setRange(30, 180)
        self.block_duration_input.setValue(60)
        self.block_duration_input.setSuffix(" min")

        self.timing_strategy_combo = QComboBox()
        self.timing_strategy_combo.addItems(["Adaptive", "Basic", "Fixed"])
        self.timing_strategy_combo.setToolTip(
            "<b>Adaptive:</b> The tutor engine allocates time based on subject priority (40-110 min).\n"
            "<b>Basic:</b> Subjects are grouped into 3 time tiers (45, 60, 90 min).\n"
            "<b>Fixed:</b> All subjects are allocated the same 'Block Duration' time."
        )

        # --- NEW WIDGETS ---
        self.is_continuous_checkbox = QCheckBox("Schedule this cycle continuously")
        self.daily_goal_spinbox = QSpinBox()
        self.daily_goal_spinbox.setRange(1, 10)
        self.daily_goal_spinbox.setValue(2)
        self.daily_goal_spinbox.setSuffix(" blocks/day")
        self.daily_goal_spinbox.setEnabled(False)  # Disabled by default
        self.is_continuous_checkbox.toggled.connect(self.daily_goal_spinbox.setEnabled)
        # --- END NEW WIDGETS ---

        layout.addRow("Cycle Name:", self.cycle_name_input)
        layout.addRow("Block Duration:", self.block_duration_input)
        layout.addRow("Timing Strategy:", self.timing_strategy_combo)
        layout.addRow("", self.is_continuous_checkbox)
        layout.addRow("Daily Goal:", self.daily_goal_spinbox)

        self.cycle_name_input.textChanged.connect(lambda: self.settings_changed.emit())
        self.block_duration_input.valueChanged.connect(lambda: self.settings_changed.emit())
        self.timing_strategy_combo.currentTextChanged.connect(lambda: self.settings_changed.emit())
        self.is_continuous_checkbox.toggled.connect(lambda: self.settings_changed.emit())
        self.daily_goal_spinbox.valueChanged.connect(lambda: self.settings_changed.emit())

    def get_data(self) -> dict:
        """Returns the current data from the form fields."""
        return {
            'name': self.cycle_name_input.text().strip(),
            'duration': self.block_duration_input.value(),
            'is_continuous': self.is_continuous_checkbox.isChecked(),
            'daily_goal': self.daily_goal_spinbox.value(),
            'timing_strategy': self.timing_strategy_combo.currentText()
        }

    def set_data(self, name: str, duration: int, is_continuous: bool, daily_goal: int, timing_strategy: str):
        """Populates the form fields with existing data."""
        self.cycle_name_input.setText(name)
        self.block_duration_input.setValue(duration)
        self.timing_strategy_combo.setCurrentText(timing_strategy)
        self.is_continuous_checkbox.setChecked(is_continuous)
        self.daily_goal_spinbox.setValue(daily_goal)
