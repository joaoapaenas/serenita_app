# app/features/onboarding/components/import_topics_help_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                               QScrollArea, QWidget, QApplication)

class ImportTopicsHelpDialog(QDialog):
    """A dialog that explains how to use the Import Topics feature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Topics Help")
        self.setMinimumSize(500, 400)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("transparentScrollArea")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Title
        title = QLabel("<b>Import & Refine Topics</b>")
        title.setObjectName("viewTitle")

        # Description
        description = QLabel(
            "This page allows you to import and organize topics for your subjects. "
            "Topics help the tutor engine create more targeted study sessions."
        )
        description.setWordWrap(True)

        # Steps
        steps_title = QLabel("<b>How to Use:</b>")
        steps_title.setObjectName("sectionHeader")

        step1 = QLabel(
            "1. <b>Select a subject</b> from the dropdown menu."
        )
        step1.setWordWrap(True)

        step2 = QLabel(
            "2. <b>Paste topics</b> from your syllabus or study material into the text area. "
            "The system will automatically parse and organize them."
        )
        step2.setWordWrap(True)

        step3 = QLabel(
            "3. <b>Process topics</b> by clicking the 'Process and Add Topics' button. "
            "The system will analyze your input and create a structured topic list."
        )
        step3.setWordWrap(True)

        step4 = QLabel(
            "4. <b>Refine topics</b> in the preview area. You can add new topics, create sub-topics, "
            "or remove unnecessary items using the buttons below the preview."
        )
        step4.setWordWrap(True)

        # Benefits
        benefits_title = QLabel("<b>Benefits:</b>")
        benefits_title.setObjectName("sectionHeader")

        benefit1 = QLabel(
            "• <b>Targeted Sessions:</b> Topics help the tutor create more specific study sessions "
            "focused on particular areas of a subject."
        )
        benefit1.setWordWrap(True)

        benefit2 = QLabel(
            "• <b>Better Tracking:</b> Performance is tracked per topic, giving you detailed "
            "insights into your strengths and weaknesses."
        )
        benefit2.setWordWrap(True)

        benefit3 = QLabel(
            "• <b>Personalized Questions:</b> When using the question bank feature, topics "
            "ensure you get questions relevant to what you're studying."
        )
        benefit3.setWordWrap(True)

        # Add all widgets to content layout
        content_layout.addWidget(title)
        content_layout.addWidget(description)
        content_layout.addSpacing(15)
        content_layout.addWidget(steps_title)
        content_layout.addWidget(step1)
        content_layout.addWidget(step2)
        content_layout.addWidget(step3)
        content_layout.addWidget(step4)
        content_layout.addSpacing(15)
        content_layout.addWidget(benefits_title)
        content_layout.addWidget(benefit1)
        content_layout.addWidget(benefit2)
        content_layout.addWidget(benefit3)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)