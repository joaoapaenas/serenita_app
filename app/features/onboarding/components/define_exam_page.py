# app/features/onboarding/components/define_exam_page.py

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QComboBox, QDateEdit)


class DefineExamPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel("Tell us about your exam")
        title.setObjectName("viewTitle")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.institution_input = QLineEdit()
        self.area_combo = QComboBox()
        self.predicted_date_input = QDateEdit()

        self.area_combo.addItems(
            ["Fiscal", "Controle", "Policial", "Tribunais", "Bancária", "Legislativa", "Administrativa / Geral"])
        self.predicted_date_input.setCalendarPopup(True)
        self.predicted_date_input.setDate(QDate.currentDate().addMonths(6))
        self.predicted_date_input.setDisplayFormat("yyyy-MM-dd")

        form_layout.addRow("Exam Name:", self.name_input)
        form_layout.addRow("Institution (Optional):", self.institution_input)
        form_layout.addRow("Area:", self.area_combo)
        form_layout.addRow("Predicted Date:", self.predicted_date_input)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(form_layout)
        layout.addStretch()

    def get_data(self) -> dict:
        clean_area = self.area_combo.currentText().split('(')[0].strip()
        return {
            "name": self.name_input.text().strip(),
            "institution": self.institution_input.text().strip(),
            "area": clean_area,
            "predicted_exam_date": self.predicted_date_input.date().toString("yyyy-MM-dd")
        }
