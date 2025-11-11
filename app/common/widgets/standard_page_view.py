# app/common/widgets/standard_page_view.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.core.constants import PAGE_MARGINS, SPACING_XLARGE


class StandardPageView(QWidget):
    """
    A reusable container widget that provides a standard page layout.
    It includes a title, a main content area, and an action bar for buttons.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(*PAGE_MARGINS)
        self._main_layout.setSpacing(SPACING_XLARGE)
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Title Area
        self.title_label = QLabel("Default Title")
        self.title_label.setObjectName("viewTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self.title_label)

        # 2. Content Area (a container to hold the feature-specific widget)
        self.content_widget: QWidget | None = None
        self._main_layout.addStretch(1)  # Add some space before content

        # 3. Action Bar Area
        self._action_bar_layout = QHBoxLayout()
        self._action_bar_layout.addStretch()  # Push buttons to the right
        # A container widget for the layout, to be added at the end
        self._action_bar_widget = QWidget()
        self._action_bar_widget.setLayout(self._action_bar_layout)

    def set_title(self, text: str):
        """Sets the main title of the page."""
        self.title_label.setText(text)

    def set_content_widget(self, widget: QWidget):
        """
        Sets the central content widget for the page. Any existing
        content widget will be replaced.
        """
        if self.content_widget:
            self.content_widget.setParent(None)
            self._main_layout.removeWidget(self.content_widget)

        self.content_widget = widget
        # Insert content before the stretch and action bar
        self._main_layout.insertWidget(2, self.content_widget, 5)  # Add with stretch factor
        self._main_layout.addWidget(self._action_bar_widget)  # Ensure action bar is always last

    def add_action_button(self, button: QPushButton):
        """Adds a button to the right-aligned action bar."""
        self._action_bar_layout.addWidget(button)