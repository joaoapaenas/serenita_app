# app/feature/main_window/action_factory.py
import logging

from PySide6.QtGui import QAction, QKeySequence, QUndoStack
from PySide6.QtWidgets import QMainWindow

from app.core.icon_manager import get_icon

log = logging.getLogger(__name__)


class ActionFactory:
    """Creates and holds all global QAction instances for the application."""

    def __init__(self, parent_view: QMainWindow, undo_stack: QUndoStack):
        log.debug("Initializing ActionFactory")
        self.parent = parent_view
        self.undo_stack = undo_stack

        self.new_cycle_action = QAction(get_icon("NEW_CYCLE"), "&New Cycle...", self.parent)
        self.new_cycle_action.setShortcut(QKeySequence.StandardKey.New)

        self.quit_action = QAction("&Quit Serenita", self.parent)
        self.quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.quit_action.triggered.connect(self.parent.close)

        self.start_session_action = QAction(get_icon("START_SESSION"), "Start Next &Session", self.parent)
        self.start_session_action.setShortcut(QKeySequence("Ctrl+R"))

        self.rebalance_action = QAction(get_icon("REBALANCE"), "&Rebalance Cycle...", self.parent)
        self.rebalance_action.setToolTip("Analyze performance and suggest optimizations for the current cycle.")

        self.undo_action = self.undo_stack.createUndoAction(self.parent, "&Undo")
        self.undo_action.setIcon(get_icon('UNDO'))
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)

        self.redo_action = self.undo_stack.createRedoAction(self.parent, "&Redo")
        self.redo_action.setIcon(get_icon('REDO'))
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)

        self.help_action = QAction(get_icon("HELP"), "&Help Contents...", self.parent)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)

    def populate_menu_bar(self, menu_bar):
        """Populates a QMenuBar with the created actions."""
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_cycle_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        session_menu = menu_bar.addMenu("&Session")
        session_menu.addAction(self.start_session_action)
        session_menu.addAction(self.rebalance_action)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.help_action)

    def populate_tool_bar(self, toolbar):
        """Populates a QToolBar with the created actions."""
        toolbar.addAction(self.new_cycle_action)
        toolbar.addSeparator()
        toolbar.addAction(self.start_session_action)
        toolbar.addAction(self.rebalance_action)