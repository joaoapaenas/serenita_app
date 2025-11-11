# app/features/onboarding/components/goal_page.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QListWidget, QFormLayout)

from app.models.exam import Exam


class GoalPage(QWidget):
    goal_selected = Signal(object)

    def __init__(self, templates: list[Exam], parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("What are you preparing for?")
        title.setObjectName("viewTitle")

        content_layout = QHBoxLayout()
        selection_layout = QVBoxLayout()

        self.template_combo = QComboBox()
        self.template_combo.addItem("Select an option...", "none")
        for template in templates:
            clean_name = template.name.replace(" (Template)", "")
            self.template_combo.addItem(clean_name, template)
        self.template_combo.insertSeparator(self.template_combo.count())
        self.template_combo.addItem("Create a custom exam plan", "custom")
        self.template_combo.currentIndexChanged.connect(
            lambda: self.goal_selected.emit(self.template_combo.currentData())
        )
        selection_layout.addWidget(self.template_combo)
        self.template_combo.setMaximumWidth(350)
        selection_layout.addStretch()

        self.details_container = QFrame()
        self.details_container.setObjectName("blockWidget")
        self.details_container.setMinimumWidth(350)
        details_layout = QVBoxLayout(self.details_container)
        details_header = QLabel("Template Details")
        details_header.setObjectName("sectionHeader")
        details_form = QFormLayout()
        self.institution_label = QLabel()
        self.area_label = QLabel()
        details_form.addRow("Institution:", self.institution_label)
        details_form.addRow("Area:", self.area_label)
        subjects_label = QLabel("Subjects Included:")
        subjects_label.setObjectName("lightText")
        self.subjects_list = QListWidget()
        self.subjects_list.setObjectName("transparentList")
        details_layout.addWidget(details_header)
        details_layout.addLayout(details_form)
        details_layout.addWidget(subjects_label)
        details_layout.addWidget(self.subjects_list, 1)

        content_layout.addLayout(selection_layout, 1)
        content_layout.addWidget(self.details_container, 1)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(content_layout, 1)

        self.details_container.setVisible(False)

    def update_details(self, exam: Exam | None, subjects: list | None):
        if not exam:
            self.details_container.setVisible(False)
            return
        self.institution_label.setText(exam.institution or "N/A")
        self.area_label.setText(exam.area or "N/A")
        self.subjects_list.clear()
        if subjects:
            for subject in subjects:
                self.subjects_list.addItem(subject['name'])
        self.details_container.setVisible(True)

    def get_selection(self) -> Exam | str:
        return self.template_combo.currentData()
