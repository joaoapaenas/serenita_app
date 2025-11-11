# app/features/help/help_view.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel,
                               QScrollArea)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from .glossary_widget import GlossaryWidget


class HelpView(QWidget):
    """A comprehensive help view with tabs for different topics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(*PAGE_MARGINS)

        main_layout = QVBoxLayout(self)

        title = QLabel("Help & Glossary")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title)

        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_about_tab(), "About Serenita")
        tab_widget.addTab(self._create_algorithm_tab(), "The Tutor Engine")
        tab_widget.addTab(self._create_glossary_tab(), "Glossary")

        main_layout.addWidget(tab_widget)

    def _create_scrollable_tab(self, widget_content: QWidget) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("transparentScrollArea")
        scroll_area.setWidget(widget_content)
        return scroll_area

    def _create_about_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(SPACING_LARGE)

        title = QLabel("<b>About Serenita</b>")
        title.setObjectName("viewTitle")

        text = QLabel(
            "Serenita is an intelligent study planner designed to eliminate the guesswork from your exam preparation. "
            "Instead of a static, rigid schedule, Serenita uses a cognitive tutor engine to analyze your performance, "
            "understand your personal challenges, and adapt your study plan in real-time."
            "<br><br>"
            "Its goal is to ensure you are always working on the most impactful subject at the right time, maximizing "
            "your learning efficiency and helping you achieve your exam goals with confidence and less stress."
        )
        text.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch()
        return self._create_scrollable_tab(content)

    def _create_algorithm_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(SPACING_LARGE)

        title = QLabel("<b>The v20 Cognitive Tutor Engine</b>")
        title.setObjectName("viewTitle")

        text = QLabel(
            "The heart of Serenita is its planning algorithm. Each time your plan is generated or updated, "
            "it follows a four-step process:"
        )
        text.setWordWrap(True)

        step1 = QLabel(
            "<b>1. Input Assembly:</b> The engine gathers all available data: your subjects, their importance, your "
            "entire study history, and your self-reported daily 'human factors' (energy and stress levels)."
        )
        step1.setWordWrap(True)

        step2 = QLabel(
            "<b>2. Diagnosis:</b> For each subject, the engine calculates your current 'Durable Mastery Score' and its 'Confidence' in that score. "
            "Based on this, it assigns a 'Strategic Mode' (like DEEP WORK or CEMENT) which defines the main goal for that subject."
        )
        step2.setWordWrap(True)

        step3 = QLabel(
            "<b>3. Prioritization:</b> The engine calculates a numerical priority score for each subject. This starts with a base score from the Strategic Mode "
            "and is then adjusted by modifiers. For example, new subjects get a temporary 'Discovery Boost', while subjects you're stuck on might get a 'Low ROI' penalty."
        )
        step3.setWordWrap(True)

        step4 = QLabel(
            "<b>4. Plan Assembly:</b> Finally, the engine uses the priority scores to allocate your available study time, generating a recommended plan "
            "and a human-readable reason for its top recommendations. This becomes the 'Strategic View' on your dashboard."
        )
        step4.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(step1)
        layout.addWidget(step2)
        layout.addWidget(step3)
        layout.addWidget(step4)
        layout.addStretch()
        return self._create_scrollable_tab(content)

    def _create_glossary_tab(self) -> QWidget:
        return self._create_scrollable_tab(GlossaryWidget())