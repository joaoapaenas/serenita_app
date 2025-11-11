# app/features/subject_details/components/glossary_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                               QScrollArea, QWidget, QFrame, QApplication)

from app.features.help.glossary_widget import GlossaryWidget

class GlossaryDialog(QDialog):
    """A dialog that explains the core concepts of the cognitive tutor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tutor Concepts Glossary")
        self.setMinimumSize(500, 400)
        # Apply the application's current stylesheet to this dialog
        self.setStyleSheet(QApplication.instance().styleSheet())

        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("transparentScrollArea")

        # --- FIX: Use the new reusable widget for the content ---
        content_widget = GlossaryWidget()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

    def _create_entry(self, term, definition):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        term_label = QLabel(f"<b>{term}</b>")
        def_label = QLabel(definition)
        def_label.setWordWrap(True)
        def_label.setObjectName("lightText")
        layout.addWidget(term_label)
        layout.addWidget(def_label)
        return widget

    def _create_sub_entry(self, term, definition):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 0, 0, 0)
        term_label = QLabel(f"• <b>{term}:</b>")
        def_label = QLabel(definition)
        def_label.setWordWrap(True)
        def_label.setObjectName("lightText")
        layout.addWidget(term_label)
        layout.addWidget(def_label, 1)
        return widget

    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        return separator