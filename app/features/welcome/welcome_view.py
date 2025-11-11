# app/features/welcome/welcome_view.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QWidget, QApplication

from app.core.constants import SPACING_LARGE
from app.core.icon_manager import get_icon


class WelcomeView(QDialog):
    """
    A modal dialog for the first-run user setup. It collects the user's
    name and study experience level.
    """
    start_requested = Signal(str, str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Serenita!")
        self.setModal(True)
        self.setMinimumWidth(400)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING_LARGE)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Let's Get You Set Up")
        title.setObjectName("viewTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QLabel("Please tell us a bit about yourself to personalize your experience.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")

        self.experience_combo = QComboBox()
        self.experience_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        self.experience_combo.setToolTip(
            "Beginner: New to structured study.\n"
            "Intermediate: Familiar with study plans.\n"
            "Advanced: Experienced with complex study schedules."
        )

        self.start_button = QPushButton(" Get Started")
        self.start_button.setIcon(get_icon("ARROW_RIGHT"))
        self.start_button.setObjectName("primaryButton")
        self.start_button.setEnabled(False)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Your Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Your Study Experience Level:"))
        layout.addWidget(self.experience_combo)
        layout.addStretch()
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Connections ---
        self.name_input.textChanged.connect(lambda text: self.start_button.setEnabled(bool(text.strip())))
        self.start_button.clicked.connect(self._on_start)

    def _on_start(self):
        """Emits the collected user data when the start button is clicked."""
        name = self.name_input.text().strip()
        experience = self.experience_combo.currentText()
        self.start_requested.emit(name, experience)