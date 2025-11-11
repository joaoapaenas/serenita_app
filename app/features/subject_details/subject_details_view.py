# app/features/subject_details/subject_details_view.py

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QTableWidget, QHeaderView, QTableWidgetItem, QFrame, QStackedWidget)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon
from app.models.subject import CycleSubject, WorkUnit
from .components.empty_work_units_widget import EmptyWorkUnitsWidget

from .components.getting_started_widget import GettingStartedWidget
from .components.performance_snapshot_widget import PerformanceSnapshotWidget

log = logging.getLogger(__name__)


class SubjectDetailsView(QWidget):
    add_work_unit_requested = Signal()
    edit_work_unit_requested = Signal(WorkUnit)
    delete_work_unit_requested = Signal(WorkUnit)
    prioritize_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)

        # --- Header ---
        title_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("viewTitle")
        self.prioritize_button = QPushButton(" Prioritize this Subject")
        self.prioritize_button.setIcon(get_icon("ACTIVE_STATUS"))
        self.prioritize_button.setToolTip("Increase this subject's frequency in your study plan.")
        self.prioritize_button.clicked.connect(self.prioritize_requested.emit)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.prioritize_button)
        main_layout.addLayout(title_layout)

        # --- Adaptive Content Area using QStackedWidget ---
        self.adaptive_content_stack = QStackedWidget()
        self.getting_started_widget = GettingStartedWidget()
        self.performance_hub_widget = PerformanceSnapshotWidget()
        self.adaptive_content_stack.addWidget(self.getting_started_widget)
        self.adaptive_content_stack.addWidget(self.performance_hub_widget)
        main_layout.addWidget(self.adaptive_content_stack)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        # --- Work Units Section (always visible) ---
        wu_header_layout = QHBoxLayout()
        wu_label = QLabel("Tactical Work Units")
        wu_label.setObjectName("sectionHeader")
        self.add_button = QPushButton(" Add Unit")
        self.add_button.setIcon(get_icon("ADD"))
        self.add_button.clicked.connect(self.add_work_unit_requested.emit)
        wu_header_layout.addWidget(wu_label)
        wu_header_layout.addStretch()
        wu_header_layout.addWidget(self.add_button)
        main_layout.addLayout(wu_header_layout)

        self.work_units_stack = QStackedWidget()
        self.work_units_table = QTableWidget()
        self.empty_work_units_widget = EmptyWorkUnitsWidget()
        self.empty_work_units_widget.add_unit_requested.connect(self.add_work_unit_requested.emit)

        self.work_units_stack.addWidget(self.work_units_table)
        self.work_units_stack.addWidget(self.empty_work_units_widget)
        self._setup_table()
        main_layout.addWidget(self.work_units_stack, 1) # Add stretch factor

    def set_view_mode(self, mode: str, **kwargs):
        """Switches the adaptive content view and populates it with data."""
        if mode == 'getting_started':
            self.adaptive_content_stack.setCurrentWidget(self.getting_started_widget)
        elif mode == 'performance_hub':
            self.performance_hub_widget.populate_data(
                diagnostics=kwargs.get('diagnostics', {}),
                performance_trend=kwargs.get('performance_trend', []),
                topic_performance=kwargs.get('topic_performance', [])
            )
            self.adaptive_content_stack.setCurrentWidget(self.performance_hub_widget)

    def populate_static_data(self, cycle_subject: CycleSubject):
        """Populates the non-adaptive parts of the view."""
        self.title_label.setText(cycle_subject.name)
        self.getting_started_widget.set_subject_name(cycle_subject.name)

    def _setup_table(self):
        self.work_units_table.setColumnCount(5)
        self.work_units_table.setHorizontalHeaderLabels(["Title", "Type", "Est. Time (min)", "Status", "Actions"])
        header = self.work_units_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.work_units_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def populate_work_units(self, work_units: list[WorkUnit]):
        if not work_units:
            self.work_units_stack.setCurrentWidget(self.empty_work_units_widget)
            self.add_button.setVisible(False)
            return

        self.work_units_stack.setCurrentWidget(self.work_units_table)
        self.add_button.setVisible(True)

        self.work_units_table.setRowCount(len(work_units))
        for row, unit in enumerate(work_units):
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            edit_button = QPushButton()
            edit_button.setIcon(get_icon("EDIT"))
            edit_button.clicked.connect(lambda checked=False, u=unit: self.edit_work_unit_requested.emit(u))
            delete_button = QPushButton()
            delete_button.setIcon(get_icon("DELETE"))
            delete_button.clicked.connect(lambda checked=False, u=unit: self.delete_work_unit_requested.emit(u))
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            self.work_units_table.setItem(row, 0, QTableWidgetItem(unit.title))
            self.work_units_table.setItem(row, 1, QTableWidgetItem(unit.type))
            self.work_units_table.setItem(row, 2, QTableWidgetItem(str(unit.estimated_time_minutes)))
            self.work_units_table.setItem(row, 3, QTableWidgetItem("Completed" if unit.is_completed else "Pending"))
            self.work_units_table.setCellWidget(row, 4, actions_widget)