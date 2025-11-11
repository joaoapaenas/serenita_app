# app/features/master_subject_manager/master_subject_manager_view.py

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QHeaderView, QTableWidgetItem)

from app.core.constants import PAGE_MARGINS, SPACING_LARGE
from app.core.icon_manager import get_icon
from app.models.subject import MasterSubject


class MasterSubjectManagerView(QWidget):
    """
    View for managing master subjects (CRUD).
    """
    add_requested = Signal()
    edit_requested = Signal(MasterSubject)
    delete_requested = Signal(MasterSubject)
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_LARGE)

        # --- Header ---
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Manage Master Subjects")
        self.title_label.setObjectName("viewTitle")
        
        self.add_button = QPushButton(" Add Subject")
        self.add_button.setIcon(get_icon("ADD"))
        self.add_button.clicked.connect(self.add_requested.emit)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        main_layout.addLayout(header_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Subject Name", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # --- Footer ---
        footer_layout = QHBoxLayout()
        back_button = QPushButton("Done")
        back_button.clicked.connect(self.back_requested.emit)
        footer_layout.addStretch()
        footer_layout.addWidget(back_button)
        main_layout.addLayout(footer_layout)

    def populate_subjects(self, subjects: list[MasterSubject]):
        """Populates the table with the list of master subjects."""
        self.table.setRowCount(len(subjects))
        for row, subject in enumerate(subjects):
            self.table.setItem(row, 0, QTableWidgetItem(subject.name))

            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_button = QPushButton()
            edit_button.setIcon(get_icon("EDIT"))
            edit_button.setToolTip("Edit subject name")
            edit_button.clicked.connect(lambda checked=False, s=subject: self.edit_requested.emit(s))

            delete_button = QPushButton()
            delete_button.setIcon(get_icon("DELETE"))
            delete_button.setToolTip("Delete subject")
            delete_button.clicked.connect(lambda checked=False, s=subject: self.delete_requested.emit(s))

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.table.setCellWidget(row, 1, actions_widget)
