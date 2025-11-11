# app/common/widgets/card_widget.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QLabel

from app.core.icon_manager import get_icon


class ActionCardWidget(QPushButton):
    """
    A reusable, clickable card widget that displays an icon, title, and description.
    It inherits from QPushButton, making it easy to connect to its `clicked` signal.
    """

    def __init__(self, title_text: str, desc_text: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("blockWidget")
        self.setMinimumHeight(150)
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon_name).pixmap(32, 32))

        title_label = QLabel(title_text)
        title_label.setObjectName("blockTitle")

        desc_label = QLabel(desc_text)
        desc_label.setObjectName("lightText")
        desc_label.setWordWrap(True)

        header_layout = QHBoxLayout()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)

        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addStretch()