# app/feature/main_window/components/human_factor_widget.py

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton

from app.core.constants import SPACING_MEDIUM
from app.core.icon_manager import get_icon

log = logging.getLogger(__name__)


class HumanFactorWidget(QWidget):
    """A widget for the user to input their daily energy and stress levels."""
    human_factor_saved = Signal(dict)

    def __init__(self, current_factors: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("humanFactorWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        # Removed AlignCenter to allow it to sit nicely on the left of the toolbar
        layout.setSpacing(SPACING_MEDIUM)

        layout.addWidget(QLabel("Daily Check-in:"))

        self.energy_combo = QComboBox()
        self.energy_combo.addItems(["High", "Normal", "Low"])

        self.stress_combo = QComboBox()
        self.stress_combo.addItems(["High", "Normal", "Low"])

        layout.addWidget(QLabel("Energy:"))
        layout.addWidget(self.energy_combo)
        layout.addWidget(QLabel("Stress:"))
        layout.addWidget(self.stress_combo)

        self.save_button = QPushButton("Update Plan")
        self.save_button.setIcon(get_icon("REBALANCE"))
        self.save_button.setToolTip("Save today's check-in and regenerate the plan.")
        self.save_button.clicked.connect(self._on_save)
        layout.addWidget(self.save_button)

        self.update_factors(current_factors)

    def update_factors(self, current_factors: dict):
        """Public method to update the combo boxes with new data."""
        self.energy_combo.setCurrentText(current_factors.get('energy_level', 'Normal'))
        self.stress_combo.setCurrentText(current_factors.get('stress_level', 'Normal'))

    def _on_save(self):
        """Emits the selected data and triggers a replan."""
        data = {
            'energy_level': self.energy_combo.currentText(),
            'stress_level': self.stress_combo.currentText()
        }
        log.info(f"Human factor input saved by user: {data}")
        self.human_factor_saved.emit(data)