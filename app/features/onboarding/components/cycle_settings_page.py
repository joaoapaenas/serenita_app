# app/features/onboarding/components/cycle_settings_page.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QSpinBox, QHBoxLayout, QFrame)

from app.common.widgets.drag_widgets import DragWidget


class CycleSettingsPage(QWidget):
    """
    A wizard page for finalizing cycle settings like subject order and daily goal.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel("Finalize Cycle Settings")
        title.setObjectName("viewTitle")

        # Subject Order Box
        order_box = QGroupBox("Subject Priority Order")
        order_layout = QVBoxLayout(order_box)
        order_info = QLabel("Drag and drop subjects to set a preferred study order for the start of your cycle.")
        order_info.setWordWrap(True)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 15, 0)
        header_layout.setSpacing(10)

        handle_spacer = QWidget()
        handle_spacer.setFixedWidth(16 + 10)

        subject_header = QLabel("Subject")
        weight_header = QLabel("Calculated Weight")

        font = subject_header.font()
        font.setBold(True)
        subject_header.setFont(font)
        weight_header.setFont(font)
        subject_header.setObjectName("lightText")
        weight_header.setObjectName("lightText")

        header_layout.addWidget(handle_spacer)
        header_layout.addWidget(subject_header, 1)
        header_layout.addWidget(weight_header)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.order_widget = DragWidget()

        order_layout.addWidget(order_info)
        order_layout.addWidget(header_widget)
        order_layout.addWidget(separator)
        # --- FIX: Add stretch factor of 1 to the DragWidget ---
        # This tells the layout to give all extra vertical space to this widget.
        order_layout.addWidget(self.order_widget, 1)

        # Daily Goal Box
        goal_box = QGroupBox("Daily Study Goal")
        goal_layout = QFormLayout(goal_box)
        self.daily_goal_spinbox = QSpinBox()
        self.daily_goal_spinbox.setRange(1, 12)
        self.daily_goal_spinbox.setValue(3)
        self.daily_goal_spinbox.setSuffix(" blocks/day")
        goal_layout.addRow("How many study blocks per day?", self.daily_goal_spinbox)

        layout.addWidget(title)
        layout.addWidget(order_box, 1)
        layout.addWidget(goal_box)

    def populate_subject_order_list(self, subjects_with_weights: list):
        """Populates the DragWidget with custom DragItem widgets."""
        self.order_widget.clear()
        for subject_data in subjects_with_weights:
            self.order_widget.add_item(
                text=subject_data['name'],
                data=subject_data['name'],
                value=f"{subject_data['weight']:.2f}"
            )

    def get_subject_order(self) -> list[str]:
        return self.order_widget.get_item_data()

    def get_daily_goal(self) -> int:
        return self.daily_goal_spinbox.value()