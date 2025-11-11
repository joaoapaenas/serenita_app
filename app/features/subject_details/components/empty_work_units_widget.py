# app/features/subject_details/components/empty_work_units_widget.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from app.core.icon_manager import get_icon

class EmptyWorkUnitsWidget(QWidget):
    """A widget shown when a subject has no work units defined."""
    add_unit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("blockWidget")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon("SUBJECTS").pixmap(48, 48))

        title_label = QLabel("Plan Your Work")
        title_label.setObjectName("blockTitle")

        info_label = QLabel(
            "Break this subject down into smaller tasks like 'Read Chapter 1' or "
            "'Complete problem set' for a more detailed daily plan. This will enable the Tactical View."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setObjectName("lightText")

        add_button = QPushButton(" Add First Work Unit")
        add_button.setIcon(get_icon("ADD"))
        add_button.clicked.connect(self.add_unit_requested.emit)

        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter)