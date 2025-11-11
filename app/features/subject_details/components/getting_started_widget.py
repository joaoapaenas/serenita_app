# app/features/subject_details/components/getting_started_widget.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from app.core.icon_manager import get_icon


class GettingStartedWidget(QGroupBox):
    """
    A widget displayed in the Subject Hub for subjects with little to no performance data.
    It guides the user on their next steps.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to this Subject!")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon("MAGIC_WAND").pixmap(32, 32))

        info_label = QLabel(
            "This is a new subject in your plan. The tutor's first goal is to establish a baseline of your performance.\n\n"
            "Complete a few study sessions with questions to unlock performance insights here."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setObjectName("lightText")

        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def set_subject_name(self, name: str):
        self.setTitle(f"Welcome to {name}!")