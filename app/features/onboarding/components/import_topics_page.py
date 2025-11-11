# app/features/onboarding/components/import_topics_page.py

from collections import defaultdict

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
                               QComboBox, QTextEdit, QAbstractItemView, QTreeView)

from app.core.icon_manager import get_icon
from .import_topics_help_dialog import ImportTopicsHelpDialog


class ImportTopicsPage(QWidget):
    """
    A wizard page for importing, parsing, and editing topics for subjects.
    """
    process_topics_requested = Signal(str, str)
    topics_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        title = QLabel("Import & Refine Topics (Optional)")
        title.setObjectName("viewTitle")
        info = QLabel("Paste topics from your syllabus, then add, edit, or remove them as needed.")
        info.setWordWrap(True)

        self.subject_combo = QComboBox()
        self.paste_area = QTextEdit()
        self.paste_area.setPlaceholderText("Paste topics for the selected subject here...")

        process_button = QPushButton(" Process and Add Topics")
        process_button.setIcon(get_icon("MAGIC_WAND"))
        process_button.clicked.connect(self._on_process_topics)

        self.tree_view = QTreeView()
        self.tree_view.setObjectName("transparentScrollArea")
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)
        self.model.itemChanged.connect(self._on_topic_edited)

        importer_layout = QHBoxLayout()
        importer_layout.addWidget(self.subject_combo)
        importer_layout.addWidget(process_button)

        controls_layout = QHBoxLayout()
        add_topic_button = QPushButton("Add Topic")
        add_topic_button.setIcon(get_icon("PLUS"))
        add_subtopic_button = QPushButton("Add Sub-topic")
        add_subtopic_button.setIcon(get_icon("PLUS_CIRCLE"))
        remove_button = QPushButton("Remove")
        remove_button.setIcon(get_icon("DELETE"))

        controls_layout.addWidget(add_topic_button)
        controls_layout.addWidget(add_subtopic_button)
        controls_layout.addStretch()
        controls_layout.addWidget(remove_button)

        add_topic_button.clicked.connect(self._on_add_topic)
        add_subtopic_button.clicked.connect(self._on_add_subtopic)
        remove_button.clicked.connect(self._on_remove_topic)

        # Create a layout for the title and the new help button
        title_layout = QHBoxLayout()
        title_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)
        title_layout.addStretch()
        help_button = QPushButton()
        help_button.setIcon(get_icon("HELP"))
        help_button.setFlat(True)
        help_button.setToolTip("What is this for?")
        help_button.clicked.connect(self._show_help_dialog)
        title_layout.addWidget(help_button, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(title_layout)
        layout.addWidget(info)
        layout.addLayout(importer_layout)
        layout.addWidget(self.paste_area, 1)
        layout.addWidget(QLabel("Imported Topics Preview:"))
        layout.addLayout(controls_layout)
        layout.addWidget(self.tree_view, 2)

    def populate_subjects_combo(self, subject_names: list[str]):
        self.subject_combo.clear()
        self.subject_combo.addItems(subject_names)

    def update_imported_topics_preview(self, all_imported_topics: dict):
        self.model.blockSignals(True)
        self.model.clear()
        for subject_name, topics in all_imported_topics.items():
            if not topics:
                continue

            parent_item = QStandardItem(subject_name)
            font = parent_item.font()
            font.setBold(True)
            parent_item.setFont(font)
            parent_item.setEditable(False)
            parent_item.setData(subject_name, Qt.ItemDataRole.UserRole)

            for topic in topics:
                child_item = QStandardItem(topic)
                child_item.setEditable(True)
                parent_item.appendRow(child_item)

            self.model.appendRow(parent_item)
            self.tree_view.expand(parent_item.index())
        self.model.blockSignals(False)

    def clear_paste_area(self):
        self.paste_area.clear()

    def _on_add_topic(self):
        subject_name = self.subject_combo.currentText()
        if not subject_name: return
        self._add_item_to_tree(subject_name, "New Topic", is_subtopic=False)
        self._emit_topics_changed()

    def _on_add_subtopic(self):
        selection = self.tree_view.selectedIndexes()
        if not selection: return

        selected_item = self.model.itemFromIndex(selection[0])
        # If a sub-item is selected, add to its parent (the subject).
        # If a subject is selected, add to it directly.
        parent = selected_item.parent() or selected_item
        subject_name = parent.data(Qt.ItemDataRole.UserRole)

        if not subject_name: # Handle case where a sub-item's parent might not have the data
             subject_name = parent.text()

        self._add_item_to_tree(subject_name, "New Sub-topic", is_subtopic=True)
        # --- FIX: Ensure the controller is notified of the change ---
        self._emit_topics_changed()

    def _add_item_to_tree(self, subject_name: str, text: str, is_subtopic: bool):
        parent_item = next(
            (self.model.item(r) for r in range(self.model.rowCount()) if self.model.item(r).text() == subject_name),
            None)

        if not parent_item:
            parent_item = QStandardItem(subject_name)
            font = parent_item.font()
            font.setBold(True)
            parent_item.setFont(font)
            parent_item.setEditable(False)
            parent_item.setData(subject_name, Qt.ItemDataRole.UserRole)
            self.model.appendRow(parent_item)

        new_item = QStandardItem(text)
        new_item.setEditable(True)

        target_parent = parent_item
        if is_subtopic and self.tree_view.selectedIndexes():
            selected_item = self.model.itemFromIndex(self.tree_view.selectedIndexes()[0])
            # If the selected item has a parent, it's a topic. Add the new item there.
            # Otherwise, the selected item is the subject itself. Add to it.
            target_parent = selected_item if selected_item.parent() else parent_item

        target_parent.appendRow(new_item)
        self.tree_view.expand(parent_item.index())
        self.tree_view.setCurrentIndex(new_item.index())
        self.tree_view.edit(new_item.index())

    def _on_remove_topic(self):
        selection = self.tree_view.selectedIndexes()
        if not selection: return

        item_to_remove = self.model.itemFromIndex(selection[0])
        (item_to_remove.parent() or self.model).removeRow(item_to_remove.row())
        self._emit_topics_changed()

    def _on_topic_edited(self, item: QStandardItem):
        if not item.text().strip():
            (item.parent() or self.model).removeRow(item.row())
        self._emit_topics_changed()

    def _emit_topics_changed(self):
        all_topics = defaultdict(list)
        for row in range(self.model.rowCount()):
            subject_item = self.model.item(row)
            subject_name = subject_item.text()
            for child_row in range(subject_item.rowCount()):
                topic_item = subject_item.child(child_row)
                all_topics[subject_name].append(topic_item.text())
        self.topics_changed.emit(dict(all_topics))

    def _on_process_topics(self):
        subject_name = self.subject_combo.currentText()
        pasted_text = self.paste_area.toPlainText()
        if subject_name and pasted_text:
            self.process_topics_requested.emit(subject_name, pasted_text)

    def _show_help_dialog(self):
        """Show the help dialog for importing topics."""
        dialog = ImportTopicsHelpDialog(self)
        dialog.exec()
        dialog.exec()
