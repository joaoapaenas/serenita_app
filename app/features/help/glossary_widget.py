# app/features/help/glossary_widget.py

from PySide6.QtWidgets import (QVBoxLayout, QLabel, QWidget, QFrame)

from app.core.constants import SPACING_LARGE


class GlossaryWidget(QWidget):
    """A reusable widget that displays the glossary of tutor concepts."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING_LARGE)

        layout.addWidget(self._create_entry(
            "Strategic Mode",
            "This is the tutor's high-level strategy for a subject, determining the primary goal for the upcoming cycle."
        ))
        layout.addWidget(self._create_sub_entry("DISCOVERY",
                                                "For new subjects. The goal is to establish an initial performance baseline and build momentum."))
        layout.addWidget(self._create_sub_entry("DEEP WORK",
                                                "The primary learning phase. The goal is to consistently build foundational knowledge and improve mastery."))
        layout.addWidget(self._create_sub_entry("CONQUER",
                                                "You are close to mastering this subject. The goal is a final push to reach the finish line."))
        layout.addWidget(self._create_sub_entry("CEMENT",
                                                "Overall mastery is good, but some weak points remain. The goal is to reinforce this knowledge to make it last."))
        layout.addWidget(self._create_sub_entry("MAINTAIN",
                                                "You have mastered this subject. Short, infrequent review sessions are scheduled to prevent you from forgetting it."))

        layout.addWidget(self._create_separator())

        layout.addWidget(self._create_entry(
            "Durable Mastery Score",
            "This score represents your long-term knowledge retention. It is an accuracy score where recent performance is weighted more heavily than older performance. A high score means you consistently answer correctly over time."
        ))

        layout.addWidget(self._create_entry(
            "Mastery Confidence Score",
            "This score represents how confident the tutor is in your Mastery Score. Confidence increases with more questions answered and more recent study sessions. A low score means the tutor needs more data to make accurate recommendations."
        ))

        layout.addStretch()

    def _create_entry(self, term, definition):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        term_label = QLabel(f"<b>{term}</b>")
        def_label = QLabel(definition)
        def_label.setWordWrap(True)
        def_label.setObjectName("lightText")
        layout.addWidget(term_label)
        layout.addWidget(def_label)
        return widget

    def _create_sub_entry(self, term, definition):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 0, 0, 0)
        term_label = QLabel(f"• <b>{term}:</b> {definition}")
        term_label.setWordWrap(True)
        term_label.setObjectName("lightText")
        layout.addWidget(term_label)
        return widget

    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        return separator