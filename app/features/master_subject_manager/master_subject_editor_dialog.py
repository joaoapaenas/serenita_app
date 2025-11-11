# app/features/master_subject_manager/master_subject_editor_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox,
                               QLabel)


class MasterSubjectEditorDialog(QDialog):
    """
    A dialog for creating or editing a master subject.
    """

    def __init__(self, subject_name: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subject Editor")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        if subject_name:
            self.name_input.setText(subject_name)
            self.setWindowTitle(f"Edit '{subject_name}'")
        else:
            self.setWindowTitle("Create New Subject")

        layout.addWidget(QLabel("Subject Name:"))
        layout.addWidget(self.name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Enable save button only when there is text
        self.name_input.textChanged.connect(lambda text: button_box.button(QDialogButtonBox.StandardButton.Save).setEnabled(bool(text.strip())))
        # Initial state
        button_box.button(QDialogButtonBox.StandardButton.Save).setEnabled(bool(subject_name.strip()))

    def get_subject_name(self) -> str:
        """Returns the entered subject name."""
        return self.name_input.text().strip()
