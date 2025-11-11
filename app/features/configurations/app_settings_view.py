# app/features/configurations/app_settings_view.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton

from app.common.widgets.standard_page_view import StandardPageView
from app.core.constants import SPACING_XLARGE
from .configuration_view import ConfigurationView


class AppSettingsView(StandardPageView):
    """
    A dedicated view for the Application Settings screen. It assembles the
    user profile form and the 'Danger Zone' into a standard page layout.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.set_title("Application Configurations")

        # 1. Create the specific content widgets for this page
        self.profile_form = ConfigurationView()  # The QGroupBox form for user profile

        danger_box = QGroupBox("Danger Zone")
        danger_box.setStyleSheet("QGroupBox { border: 1px solid #E57373; }")
        danger_layout = QVBoxLayout(danger_box)
        reset_label = QLabel(
            "This will permanently delete all your data, including users, exams, cycles, "
            "and study history. This action cannot be undone."
        )
        reset_label.setWordWrap(True)
        self.reset_button = QPushButton("Reset All Application Data")
        self.reset_button.setObjectName("dangerButton")
        danger_layout.addWidget(reset_label)
        danger_layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. Assemble the content into a single container widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING_XLARGE)
        content_layout.addWidget(self.profile_form)
        content_layout.addStretch()
        content_layout.addWidget(danger_box)

        # 3. Set the assembled widget as the main content of the page
        self.set_content_widget(content_widget)