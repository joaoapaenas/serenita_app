# app/feature/main_window/main_window_view.py
import logging
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QHBoxLayout, QToolBar
)

# Import the newly separated Sidebar component
from .components.sidebar.sidebar_view import SidebarView

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """The main application window, configured for native vibrancy on macOS."""
    navigation_requested = Signal(dict)

    def __init__(self):
        super().__init__()
        log.debug("Initializing MainWindow (View).")
        self.setWindowTitle("Serenita")  # A simple, static title is fine for the main window
        self.resize(1100, 700) # Increased default size for better initial view

        if sys.platform == "darwin":
            self.setAttribute(Qt.WA_MacAlwaysShowToolBar)
            self.setUnifiedTitleAndToolBarOnMac(True)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)


        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)


        self.splitter = QSplitter(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self.sidebar = SidebarView(self)
        self.sidebar.setMaximumWidth(240)
        self.main_pane = QWidget()
        self.main_pane.setObjectName("mainPane")

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_pane)
        self.splitter.setSizes([240, 860])

        # --- Ensure the main pane stretches while the sidebar does not ---
        # The first parameter (0) applies to the sidebar (no stretch).
        # The second parameter (1) applies to the main pane (give it all extra space).
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.sidebar.navigation_selected.connect(self.navigation_requested.emit)

    def get_toolbar(self) -> QToolBar:
        """Provides access to the toolbar for the controller."""
        return self.toolbar

    def set_main_pane_widget(self, widget: QWidget):
        """Replaces the current widget in the main pane without deleting it."""
        log.debug(f"Setting main pane widget to: {widget.__class__.__name__}")

        if self.main_pane:
            self.main_pane.setParent(None)

        self.main_pane = widget
        self.main_pane.setObjectName("mainPane")

        if sys.platform == "darwin":
            self.main_pane.setStyleSheet("#mainPane { padding-top: 24px; }")

        self.splitter.insertWidget(1, self.main_pane)