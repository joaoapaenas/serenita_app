# app/features/session_choice/session_choice_view.py

import logging
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame
)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon, THEME_ACCENT_TEXT_COLOR

log = logging.getLogger(__name__)


class SessionChoiceView(QWidget):
    """
    A view that allows the user to either confirm the recommended study
    session or choose an alternative from the day's plan. This is displayed
    in the main application pane.
    """
    start_session_requested = Signal(dict)
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Next Study Session")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Choose Your Next Session")
        title.setObjectName("viewTitle")
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Recommended Session Section ---
        self.recommended_frame = QFrame()
        self.recommended_frame.setObjectName("blockWidget")
        rec_layout = QVBoxLayout(self.recommended_frame)

        rec_header = QLabel("Recommended Next Session")
        rec_header.setObjectName("sectionHeader")

        self.rec_title = QLabel("Subject Name (XX min)")
        self.rec_title.setObjectName("blockTitle")

        self.rec_reason = QLabel("Reasoning for this recommendation...")
        self.rec_reason.setObjectName("lightText")
        self.rec_reason.setWordWrap(True)

        self.start_recommended_button = QPushButton(" Start Recommended Session")
        self.start_recommended_button.setIcon(get_icon("START_SESSION", color=THEME_ACCENT_TEXT_COLOR))
        self.start_recommended_button.setObjectName("primaryButton")

        rec_layout.addWidget(rec_header)
        rec_layout.addWidget(self.rec_title)
        rec_layout.addWidget(self.rec_reason)
        rec_layout.addWidget(self.start_recommended_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.recommended_frame)

        # --- Alternative Sessions Section ---
        self.alternatives_frame = QFrame()
        alt_layout = QVBoxLayout(self.alternatives_frame)
        alt_header = QLabel("Or, choose another session for today:")
        alt_header.setObjectName("sectionHeader")

        self.alternatives_list = QListWidget()
        self.start_selected_button = QPushButton(" Start Selected Session")
        self.start_selected_button.setIcon(get_icon("START_SESSION"))
        self.start_selected_button.setEnabled(False)

        alt_layout.addWidget(alt_header)
        alt_layout.addWidget(self.alternatives_list, 1)
        alt_layout.addWidget(self.start_selected_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.alternatives_frame, 1)  # Add stretch factor

        main_layout.addStretch()

        # --- Cancel Button ---
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_requested.emit)
        main_layout.addWidget(cancel_button, alignment=Qt.AlignmentFlag.AlignRight)

        # --- Connections ---
        self.alternatives_list.itemSelectionChanged.connect(
            lambda: self.start_selected_button.setEnabled(True)
        )

    def populate_data(self, recommended: dict, alternatives: list):
        """Fills the view with session data."""
        self.rec_title.setText(f"{recommended['subject_name']} ({recommended.get('allocated_minutes', 0)} min)")
        self.rec_reason.setText(recommended.get('reasoning', 'No reasoning available.'))

        # Store data in the button for easy retrieval
        self.start_recommended_button.setProperty("session_data", recommended)
        self.start_recommended_button.clicked.connect(self._on_start_clicked)

        if not alternatives:
            self.alternatives_frame.setVisible(False)
            return

        for alt_session in alternatives:
            item_text = f"{alt_session['subject_name']} ({alt_session.get('allocated_minutes', 0)} min)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, alt_session)
            self.alternatives_list.addItem(item)

        self.start_selected_button.clicked.connect(self._on_start_selected)

    def _on_start_clicked(self):
        """Handles starting the recommended session."""
        session_data = self.sender().property("session_data")
        self.start_session_requested.emit(session_data)

    def _on_start_selected(self):
        """Handles starting the user-selected alternative session."""
        selected_item = self.alternatives_list.currentItem()
        if selected_item:
            session_data = selected_item.data(Qt.ItemDataRole.UserRole)
            self.start_session_requested.emit(session_data)