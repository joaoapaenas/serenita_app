# app/common/widgets/empty_state_widget.py
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from app.core.constants import SPACING_LARGE
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR


class EmptyStateWidget(QWidget):
    """A reusable, centered widget for displaying empty states with an optional call to action."""
    action_requested = Signal()

    def __init__(self, icon_name: str, title: str, message: str,
                 button_text: str | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("blockWidget")

        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING_LARGE)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(48, 48))

        title_label = QLabel(title)
        title_label.setObjectName("blockTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setObjectName("lightText")

        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        if button_text:
            self.action_button = QPushButton(f" {button_text}")
            self.action_button.setIcon(get_icon("ARROW_RIGHT", color=THEME_ACCENT_TEXT_COLOR))
            self.action_button.setObjectName("primaryButton")
            self.action_button.clicked.connect(self.action_requested.emit)
            layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)