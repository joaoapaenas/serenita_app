# app/features/configurations/configuration_view.py

from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QComboBox, QGroupBox)

from app.models.user import User


class ConfigurationView(QGroupBox):
    """
    A view for managing user profile settings.
    This is now just the form content, not the entire page.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__("User Profile", parent)

        # The view is now a QGroupBox containing a form.
        profile_layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.experience_combo = QComboBox()
        self.experience_combo.addItems(["Beginner", "Intermediate", "Advanced"])

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])

        profile_layout.addRow("Your Name:", self.name_input)
        profile_layout.addRow("Study Experience Level:", self.experience_combo)
        profile_layout.addRow("Application Theme:", self.theme_combo)

    def set_data(self, user: User):
        """Populates the form with the current user's data."""
        self.name_input.setText(user.name)
        self.experience_combo.setCurrentText(user.study_level)
        self.theme_combo.setCurrentText(user.theme)

    def get_data(self) -> dict:
        """Gathers data from the form inputs."""
        return {
            "name": self.name_input.text().strip(),
            "study_level": self.experience_combo.currentText(),
            "theme": self.theme_combo.currentText()
        }