# app/feature/main_window/components/sidebar/sidebar_view.py

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QPushButton
)

from app.core.constants import SPACING_LARGE
from app.core.icon_manager import get_icon
from app.core.signals import app_signals

log = logging.getLogger(__name__)


class SidebarView(QWidget):
    """
    The left-hand sidebar navigation widget. It is a self-contained component.
    """
    navigation_selected = Signal(dict)
    # A custom role to store the icon's string name on the item
    ICON_NAME_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        log.debug("Initializing SidebarView.")
        self.setObjectName("Sidebar")
        self.setAutoFillBackground(True)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.setMinimumWidth(250)

        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setIndentation(SPACING_LARGE)
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        self.tree_view.setStyleSheet("""
            QTreeView {
                border: none;
                background-color: transparent; /* Make tree background transparent to show sidebar color */
            }
            QTreeView::item {
                padding: 5px;
            }
            QTreeView::item:selected {
                /* The foreground color (text) is now handled by the stylesheet for simplicity */
                background-color: #FFCC00;
                color: #111111;
                border-radius: 4px;
            }
            QTreeView::item:focus {
                outline: none;
            }
            QTreeView::branch {
                background: transparent;
            }
        """)

        self.add_tree_item("Overview", {"type": "overview"}, icon_name="OVERVIEW")
        self.add_tree_item("Dashboard", {"type": "performance_dashboard"}, icon_name="VIEW_PERFORMANCE",
                           tooltip="Your daily performance summary.")
        self.add_tree_item("Performance", {"type": "performance_graphs"}, icon_name="VIEW_PERFORMANCE",
                           tooltip="Historical evolution graphs.")
        self.add_tree_item("History", {"type": "history"}, icon_name="HISTORY")
        self.add_tree_item("Analytics", {"type": "analytics"}, icon_name="REBALANCE",
                           tooltip="In-depth analysis of strengths and weaknesses.")
        self.add_tree_item("Training", {"type": "training_screen"}, icon_name="REBALANCE")
        self.subjects_parent_item = self.add_tree_item("Subjects", {"type": "subjects_category"}, icon_name="SUBJECTS")
        self.add_tree_item("Help", {"type": "help"}, icon_name="HELP")

        self.tree_view.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)

        self.config_button = QPushButton(" Configurations")
        self.config_button.setIcon(get_icon("CONFIGURATIONS"))
        self.config_button.setFlat(True)
        self.config_button.clicked.connect(lambda: self.navigation_selected.emit({"type": "configurations"}))

        self.layout.addWidget(self.tree_view, 1)
        self.layout.addWidget(self.config_button)

        app_signals.theme_changed.connect(self._update_theme)
        self._update_theme() # Set initial state

    def _update_theme(self):
        """Updates all icons and buttons to match the current theme."""
        log.debug("Sidebar updating theme.")
        text_color = self.palette().color(QPalette.ColorRole.Text)
        self.config_button.setIcon(get_icon("CONFIGURATIONS", color=text_color))
        self._update_tree_icon_colors()

    def _update_tree_icon_colors(self):
        """Iterates through the tree model and updates every icon color."""
        root = self.model.invisibleRootItem()
        for row in range(root.rowCount()):
            item = root.child(row)
            self._update_item_icon(item)
            if item.hasChildren():
                for child_row in range(item.rowCount()):
                    child_item = item.child(child_row)
                    self._update_item_icon(child_item)

    def _update_item_icon(self, item: QStandardItem):
        """Helper to update a single item's icon based on theme color."""
        icon_name = item.data(self.ICON_NAME_ROLE)
        if icon_name:
            # Icons now always use the standard text color. Selection is handled by the stylesheet.
            color = self.palette().color(QPalette.ColorRole.Text)
            item.setIcon(get_icon(icon_name, color=color))

    def add_tree_item(self, text: str, user_data: dict, parent_item: QStandardItem | None = None,
                      icon_name: str | None = None, tooltip: str | None = None):
        """Helper to add a styled item to the tree view."""
        icon = get_icon(icon_name) if icon_name else None
        item = QStandardItem(icon, text) if icon else QStandardItem(text)
        item.setEditable(False)
        item.setData(user_data, Qt.ItemDataRole.UserRole)
        if icon_name:
            item.setData(icon_name, self.ICON_NAME_ROLE)
        if tooltip:
            item.setToolTip(tooltip)

        (parent_item if parent_item else self.model).appendRow(item)
        return item

    def _on_tree_selection_changed(self, selected, deselected):
        """
        Handler for when a user clicks an item in the tree.
        This no longer manually changes colors, delegating all styling to QSS.
        """
        indexes = selected.indexes()
        if indexes:
            item = self.model.itemFromIndex(indexes[0])
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if item_data:
                log.debug(f"Sidebar navigation selected: {item_data}")
                self.navigation_selected.emit(item_data)

    def update_subjects(self, subjects_list: list):
        """
        Public method to dynamically update the list of subjects.
        """
        log.debug(f"Updating sidebar with {len(subjects_list)} subjects.")
        self.subjects_parent_item.removeRows(0, self.subjects_parent_item.rowCount())

        for subject_data in subjects_list:
            user_data = {
                "type": "subject_details",
                "name": subject_data.get('subject_name'),
                "cycle_subject_id": subject_data.get('subject_id')
            }
            self.add_tree_item(subject_data.get('subject_name', 'Unknown Subject'), user_data,
                               parent_item=self.subjects_parent_item, icon_name="SUBJECT")

        self._update_tree_icon_colors() # Ensure new subject icons have correct color
        if self.subjects_parent_item.hasChildren():
            self.tree_view.expand(self.subjects_parent_item.index())