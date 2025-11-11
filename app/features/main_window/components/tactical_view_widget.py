# app/feature/main_window/components/tactical_view_widget.py

from collections import defaultdict

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QScrollArea, QLabel, QHBoxLayout, QFrame, QPushButton

from app.core.constants import SPACING_LARGE
from .work_unit_card_widget import WorkUnitCardWidget


class TacticalViewWidget(QWidget):
    """
    Renders the Tactical View (`sequenced_plan`) of the v20 plan
    using a tabbed interface for each day.
    """
    work_unit_completed = Signal(str)  # Relays the work_unit_id

    def __init__(self, v20_plan: dict, parent: QWidget | None = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 10, 0, 0)
        main_layout.setSpacing(SPACING_LARGE)

        # Add routine guidance
        self._add_routine_guidance(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self._populate_tabs(v20_plan.get('sequenced_plan', []))

    def _add_routine_guidance(self, main_layout):
        """Add guidance for following the tactical routine."""
        guidance_frame = QFrame()
        guidance_frame.setObjectName("routinePathFrame")
        guidance_layout = QVBoxLayout(guidance_frame)

        guidance_title = QLabel("Daily Study Routine")
        guidance_title.setObjectName("sectionHeader")
        guidance_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        guidance_text = QLabel(
            "Complete tasks in order for optimal learning flow:\n"
            "• Start with the highlighted task\n"
            "• Work through tasks sequentially\n"
            "• Mark each task as complete when finished"
        )
        guidance_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        guidance_text.setWordWrap(True)

        guidance_layout.addWidget(guidance_title)
        guidance_layout.addWidget(guidance_text)

        main_layout.addWidget(guidance_frame)

    def _populate_tabs(self, sequenced_plan: list):
        """Groups tasks by day and creates a tab for each."""
        tasks_by_day = defaultdict(list)
        for task in sequenced_plan:
            tasks_by_day[task.get('day_index', 0)].append(task)

        if not tasks_by_day:
            # Handle case where there's no tactical plan
            no_plan_widget = QWidget()
            layout = QVBoxLayout(no_plan_widget)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label = QLabel("No tactical plan generated.\nDefine Work Units for your subjects to enable this view.")
            layout.addWidget(label)
            self.tab_widget.addTab(no_plan_widget, "Plan")
            return

        # Sort tabs by day index
        sorted_days = sorted(tasks_by_day.keys())
        first_day_index = sorted_days[0] if sorted_days else None

        for day_index in sorted_days:
            day_tasks = tasks_by_day[day_index]

            # Create the content widget for the tab's scroll area
            day_content_widget = QWidget()
            day_layout = QVBoxLayout(day_content_widget)
            day_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Highlight the first task if it's the first day
            for i, task in enumerate(day_tasks):
                card = WorkUnitCardWidget(task)
                # If this is the first task of the first day, make it visually distinct
                if day_index == first_day_index and i == 0:
                    card.setObjectName("nextSubjectCard")
                    card.setStyleSheet("""
                        #nextSubjectCard {
                            background-color: #FFF8E1; /* Light yellow background */
                            border: 3px solid #FFCC00; /* Thick yellow border */
                            border-radius: 12px;
                        }
                        #nextSubjectCard:hover {
                            background-color: #FFECB3; /* Slightly darker yellow on hover */
                            border: 3px solid #FFD700; /* Brighter yellow border on hover */
                        }
                    """)
                card.completion_requested.connect(self.work_unit_completed.emit)
                day_layout.addWidget(card)

            # Create a scroll area to hold the content
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setObjectName("transparentScrollArea")
            scroll_area.setWidget(day_content_widget)

            self.tab_widget.addTab(scroll_area, f"Day {day_index + 1}")