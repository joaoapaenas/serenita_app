# app/features/exam_editor/exam_editor_view.py

from PySide6.QtCore import Signal, QDate, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                               QPushButton, QDateEdit, QComboBox, QHBoxLayout)

from app.core.constants import PAGE_MARGINS, SPACING_XLARGE
from app.models.exam import Exam


class ExamEditorView(QWidget):
    """
    A widget for creating a new Exam Goal. This view is shown in the main
    pane when a user needs to create an exam before creating a study cycle.
    """
    save_requested = Signal(dict)
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(*PAGE_MARGINS)
        main_layout.setSpacing(SPACING_XLARGE)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel("Create a New Exam Goal")
        self.title.setObjectName("viewTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)

        info = QLabel("Define the properties of your exam goal.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.institution_input = QLineEdit()
        self.role_input = QLineEdit()
        self.exam_board_input = QLineEdit()

        self.area_combo = QComboBox()
        self.area_combo.addItems([
            "Fiscal (e.g., Receita Federal)",
            "Controle (e.g., TCU, TCE)",
            "Policial (e.g., PF, PRF)",
            "Tribunais (e.g., TRT, TRF)",
            "Bancária (e.g., Banco do Brasil)",
            "Legislativa (e.g., Senado, Câmara)",
            "Administrativa / Geral (e.g., Nível Médio)"
        ])

        self.predicted_date_input = QDateEdit()
        self.predicted_date_input.setCalendarPopup(True)
        self.predicted_date_input.setDate(QDate.currentDate().addMonths(6))
        self.predicted_date_input.setDisplayFormat("yyyy-MM-dd")

        self.template_combo = QComboBox()
        self.template_combo.setToolTip("Select a template to pre-populate your subject list.")
        self.template_label = QLabel("Start with a Template:")

        form_layout.addRow("Exam Name*:", self.name_input)
        form_layout.addRow("Institution:", self.institution_input)
        form_layout.addRow("Role/Position:", self.role_input)
        form_layout.addRow("Area:", self.area_combo)
        form_layout.addRow("Exam Board:", self.exam_board_input)
        form_layout.addRow("Predicted Exam Date:", self.predicted_date_input)
        form_layout.addRow(self.template_label, self.template_combo)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        action_buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_requested.emit)

        self.save_button = QPushButton("Save Exam")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setEnabled(False)

        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(cancel_button)
        action_buttons_layout.addWidget(self.save_button)
        main_layout.addLayout(action_buttons_layout)

        self.name_input.textChanged.connect(lambda text: self.save_button.setEnabled(bool(text.strip())))
        self.save_button.clicked.connect(self._on_save)

    def set_edit_mode(self, is_editing: bool):
        """Configures the view for either create or edit mode."""
        if is_editing:
            self.title.setText("Edit Exam Goal")
            self.save_button.setText("Save Changes")
            self.template_label.setVisible(False)
            self.template_combo.setVisible(False)
        else:
            self.title.setText("Create New Exam Goal")
            self.save_button.setText("Save and Create Cycle")
            self.template_label.setVisible(True)
            self.template_combo.setVisible(True)

    def populate_templates(self, templates: list[Exam]):
        """Populates the template combo box for create mode."""
        self.template_combo.clear()
        self.template_combo.addItem("None (Start from scratch)", None)
        for template in templates:
            self.template_combo.addItem(template.name, template.id)

    def set_data(self, exam: Exam):
        """Populates the form fields with data from an existing exam."""
        self.name_input.setText(exam.name)
        self.institution_input.setText(exam.institution)
        self.role_input.setText(exam.role)
        self.exam_board_input.setText(exam.exam_board)
        # Find the full text in the combo box that starts with the clean area name
        area_items = [self.area_combo.itemText(i) for i in range(self.area_combo.count())]
        matching_area = next((item for item in area_items if item.startswith(exam.area)), exam.area)
        self.area_combo.setCurrentText(matching_area)
        if exam.predicted_exam_date:
            self.predicted_date_input.setDate(QDate.fromString(exam.predicted_exam_date, "yyyy-MM-dd"))

    def _on_save(self):
        """Emits the collected exam data."""
        raw_area_text = self.area_combo.currentText()
        clean_area = raw_area_text.split('(')[0].strip()
        data = {
            "name": self.name_input.text().strip(),
            "institution": self.institution_input.text().strip(),
            "role": self.role_input.text().strip(),
            "exam_board": self.exam_board_input.text().strip(),
            "area": clean_area,
            "predicted_exam_date": self.predicted_date_input.date().toString("yyyy-MM-dd"),
            "exam_date": self.predicted_date_input.date().toString("yyyy-MM-dd"),
            "template_id": self.template_combo.currentData() if self.template_combo.isVisible() else None
        }
        self.save_requested.emit(data)