# app/features/main_window/components/strategic_view_widget.py

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox, QHBoxLayout, QFrame, QButtonGroup, QGridLayout

from app.common.widgets.card_widget import ActionCardWidget
from app.common.widgets.flow_layout import FlowLayout
from app.core.constants import SPACING_MEDIUM

log = logging.getLogger(__name__)


class StrategicViewWidget(QWidget):
    """Renders the Strategic View (`plan_scaffold`) of the v20 plan."""
    start_session_requested = Signal(dict)

    def __init__(self, v20_plan: dict, parent: QWidget | None = None):
        super().__init__(parent)

        self.v20_plan = v20_plan
        self.plan_data = v20_plan.get('plan_scaffold', {})
        self.all_plans = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 10, 0, 0)

        # Plan selector with button group for better interaction
        self.plan_selector_layout = QHBoxLayout()
        self.plan_selector_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plan_buttons_group = QButtonGroup(self)
        self.plan_buttons_group.setExclusive(True)

        main_layout.addLayout(self.plan_selector_layout)

        self.cards_container = QWidget()
        self.content_layout = QVBoxLayout(self.cards_container)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("transparentScrollArea")
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area)

        tactical_tip_label = QLabel("Tip: Click the 'View Tactical List' button in the toolbar for a daily checklist.")
        tactical_tip_label.setObjectName("lightText")
        font = tactical_tip_label.font()
        font.setItalic(True)
        tactical_tip_label.setFont(font)
        tactical_tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(tactical_tip_label)
        if not v20_plan.get('sequenced_plan'):
            tactical_tip_label.setVisible(False)

        recommended = self.plan_data.get('recommended_plan')
        if recommended:
            self.all_plans[recommended['focus_mode']] = recommended['sessions']
            btn = QPushButton(recommended['focus_mode'])
            btn.setCheckable(True)
            btn.setObjectName("planSelectorButton")
            self.plan_buttons_group.addButton(btn)
            btn.clicked.connect(lambda checked, mode=recommended['focus_mode']: self._render_plan(mode))
            self.plan_selector_layout.addWidget(btn)

        for alt_plan in self.plan_data.get('alternative_plans', []):
            self.all_plans[alt_plan['focus_mode']] = alt_plan['sessions']
            btn = QPushButton(alt_plan['focus_mode'])
            btn.setCheckable(True)
            btn.setObjectName("planSelectorButton")
            self.plan_buttons_group.addButton(btn)
            btn.clicked.connect(lambda checked, mode=alt_plan['focus_mode']: self._render_plan(mode))
            self.plan_selector_layout.addWidget(btn)

        if len(self.all_plans) > 0:
            first_button = self.plan_buttons_group.buttons()[0]
            first_button.setChecked(True)
            self._render_plan(first_button.text())

    def _render_plan(self, mode: str):
        """Clears and rebuilds the UI with cards for the selected plan mode."""
        while (item := self.content_layout.takeAt(0)) is not None:
            if (widget := item.widget()) is not None:
                widget.deleteLater()

        sessions = self.all_plans.get(mode, [])
        if not sessions:
            no_data_label = QLabel("No study sessions were allocated for this plan.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_data_label)
        else:
            processed_subjects_map = {s['subject_id']: s for s in self.v20_plan.get('processed_subjects', [])}
            # Use a FlowLayout for the cards to make the UI responsive
            cards_flow_layout = FlowLayout(spacing=SPACING_MEDIUM)

            for i, session_stub in enumerate(sessions):
                full_session_data = processed_subjects_map.get(session_stub['subject_id'], {}).copy()
                full_session_data.update(session_stub)
                card = self._create_session_card(full_session_data, is_first=(i == 0))
                cards_flow_layout.addWidget(card)
            self.content_layout.addLayout(cards_flow_layout)

    def _create_session_card(self, session_data: dict, is_first: bool = False) -> ActionCardWidget:
        """Creates a single ActionCardWidget for a study session."""
        title = f"{session_data['subject_name']} ({session_data.get('allocated_minutes', 0)} min)"
        description = session_data.get('reasoning', 'No reasoning provided.')

        # Use the strategic mode to select a more descriptive icon
        mode = session_data.get('diagnostics', {}).get('strategic_mode', 'DEEP_WORK')
        icon_map = {
            'DEEP_WORK': 'SUBJECTS',
            'CONQUER': 'FINISH_FLAG',
            'CEMENT': 'REBALANCE',
            'MAINTAIN': 'HISTORY',
            'DISCOVERY': 'HELP'
        }
        icon_name = icon_map.get(mode, 'SUBJECT')

        card = ActionCardWidget(
            title_text=title,
            desc_text=description,
            icon_name=icon_name
        )

        if is_first:
            card.setObjectName("nextSubjectCard")
            # Improved style for better clarity and contrast
            card.setStyleSheet("""
                #nextSubjectCard {
                    background-color: #383830; /* A subtle, warm dark gray for good text contrast */
                    border: 2px solid #FFCC00; /* A clear accent border */
                }
                #nextSubjectCard:hover {
                    background-color: #454538; /* Slightly lighter on hover */
                }
            """)

        card.clicked.connect(lambda: self.start_session_requested.emit(session_data))
        return card