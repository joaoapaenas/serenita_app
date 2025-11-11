# app/features/training_screen/widgets.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar, QCheckBox, QSpinBox, QComboBox

class RestTimerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("RestTimerWidget")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Rest Timer Controls and Display"))
        layout.addWidget(QPushButton("Start Rest"))
        layout.addWidget(QPushButton("Skip Rest"))

class ExerciseStatsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ExerciseStatsWidget")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Exercise Statistics (Accuracy, Time, etc.)"))
        layout.addWidget(QLabel("Accuracy: 85%"))
        layout.addWidget(QLabel("Time Spent: 1m 30s"))

class ExerciseNotesWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ExerciseNotesWidget")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Notes related to the current exercise or topic"))
        # In a real implementation, this would be a QTextEdit or similar
        layout.addWidget(QLabel("User's notes will appear here."))

class ExerciseContentWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ExerciseContentWidget")
        layout = QVBoxLayout(self)

        # Questions Done
        layout.addWidget(QLabel("Questions Done:"))
        self.questions_done_spinbox = QSpinBox(self)
        self.questions_done_spinbox.setRange(0, 9999) # Arbitrary large range
        layout.addWidget(self.questions_done_spinbox)

        # Questions Correct
        layout.addWidget(QLabel("Questions Correct:"))
        self.questions_correct_spinbox = QSpinBox(self)
        self.questions_correct_spinbox.setRange(0, 9999) # Arbitrary large range
        layout.addWidget(self.questions_correct_spinbox)

        # Subject Selection
        layout.addWidget(QLabel("Subject:"))
        self.subject_combobox = QComboBox(self)
        # Placeholder items, will be populated by controller
        self.subject_combobox.addItem("Select Subject")
        layout.addWidget(self.subject_combobox)

        # Topic Selection (Optional)
        layout.addWidget(QLabel("Topic (Optional):"))
        self.topic_combobox = QComboBox(self)
        self.topic_combobox.addItem("Select Topic (Optional)")
        layout.addWidget(self.topic_combobox)

        # Log Session Button
        self.log_session_button = QPushButton("Log Session")
        layout.addWidget(self.log_session_button)

class SessionOverviewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SessionOverviewWidget")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Session Progress:"))
        progress_bar = QProgressBar(self)
        progress_bar.setValue(50) # Placeholder value
        layout.addWidget(progress_bar)
        layout.addWidget(QLabel("Time Spent: 00:15:30"))
        layout.addWidget(QLabel("Exercises Completed: 10/20"))
        layout.addWidget(QLabel("Accuracy: 75%"))

class SettingsToolsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SettingsToolsWidget")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Session Settings:"))
        layout.addWidget(QCheckBox("Enable Adaptive Difficulty"))
        layout.addWidget(QCheckBox("Show Explanations After Answer"))
        layout.addWidget(QPushButton("End Session"))
