# app/feature/main_window/components/dual_plan_view.py

import logging

from PySide6.QtCore import Signal, Qt, Slot
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget, QLabel, QFrame, QPushButton, QHBoxLayout, QProgressBar, QGridLayout)

from app.core.constants import SPACING_LARGE, PAGE_MARGINS
from .strategic_view_widget import StrategicViewWidget
from .tactical_view_widget import TacticalViewWidget

log = logging.getLogger(__name__)


class DualPlanView(QWidget):
    start_session_requested = Signal(dict)
    work_unit_completed = Signal(str)

    def __init__(self, v20_plan: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.v20_plan = v20_plan
        self.setObjectName("DualPlanView")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)

        # --- Simplified Header ---
        # Top line for Title and Progress
        top_header_layout = QHBoxLayout()
        title_label = QLabel("Today's Plan")
        title_label.setObjectName("viewTitle")
        top_header_layout.addWidget(title_label)
        top_header_layout.addStretch()
        self._add_progress_indicator(top_header_layout)
        main_layout.addLayout(top_header_layout)

        # Centered focus summary as a subtitle
        focus_label = QLabel(v20_plan.get('cycle_focus', 'No focus determined.'))
        focus_label.setObjectName("focusSummaryText") # New name for styling
        focus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        focus_label.setWordWrap(True)
        main_layout.addWidget(focus_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)
        # --- End of Simplified Header ---


        self.stacked_widget = QStackedWidget()
        self.strategic_view = StrategicViewWidget(v20_plan)
        self.tactical_view = TacticalViewWidget(v20_plan)

        self.stacked_widget.addWidget(self.strategic_view)
        self.stacked_widget.addWidget(self.tactical_view)

        main_layout.addWidget(self.stacked_widget, stretch=1)

        self.strategic_view.start_session_requested.connect(self.start_session_requested.emit)
        self.tactical_view.work_unit_completed.connect(self.work_unit_completed.emit)

    def _add_progress_indicator(self, layout):
        """Add a progress indicator showing plan completion status."""
        sequenced_plan = self.v20_plan.get('sequenced_plan', [])
        total_tasks = len(sequenced_plan)
        completed_tasks = sum(1 for task in sequenced_plan if task.get('is_completed', False))

        progress_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)

        progress_label = QLabel(f"{completed_tasks}/{total_tasks} tasks")
        progress_layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(int(progress_percent))
        self.progress_bar.setFixedWidth(150)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_widget)


    @Slot(bool)
    def set_tactical_view_active(self, is_tactical: bool):
        """
        Public slot allowing the owner (MainWindowController) to toggle
        which view is currently visible.
        """
        if is_tactical:
            self.stacked_widget.setCurrentWidget(self.tactical_view)
        else:
            self.stacked_widget.setCurrentWidget(self.strategic_view)