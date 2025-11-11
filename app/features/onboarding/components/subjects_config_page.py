# app/features/onboarding/components/subjects_config_page.py

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from app.features.cycle_editor.components.subject_selector_presenter import SubjectSelectorPresenter
from app.features.cycle_editor.components.subject_selector_widget import SubjectSelectorWidget


class SubjectsConfigPage(QWidget):
    """
    A wizard page for configuring subjects using the SubjectSelectorWidget.
    """

    master_subject_add_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        title = QLabel("Configure Your Subjects")
        title.setObjectName("viewTitle")
        info = QLabel(
            "Set the initial weights for your subjects and put any to sleep that you don't want in your first cycle.")
        info.setWordWrap(True)

        # This page creates and owns its subject selector and presenter
        self.selector_widget = SubjectSelectorWidget(self)
        self.presenter = SubjectSelectorPresenter(self.selector_widget, self)

        # This line will now work correctly
        self.selector_widget.master_subject_add_requested.connect(self.master_subject_add_requested.emit)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        layout.addWidget(self.selector_widget, 1)

    def get_data(self) -> list:
        """Returns the configured subjects from the presenter."""
        return self.presenter.get_configured_subjects()