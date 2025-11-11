# app/features/configurations/developer_tools_dialog.py

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel


class DeveloperToolsDialog(QDialog):
    """
    A dialog for developer-specific actions.
    """
    seed_long_term_user_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Tools")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        info_label = QLabel("These tools are for development and testing purposes.")
        layout.addWidget(info_label)

        seed_button = QPushButton("Seed Long-term User Data")
        seed_button.setToolTip("Executes 'long_term_user_seed.sql' to simulate a long-term user.")
        seed_button.clicked.connect(self.seed_long_term_user_requested.emit)
        layout.addWidget(seed_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
