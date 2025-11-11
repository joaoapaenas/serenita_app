# app/common/widgets/drag_widgets.py

from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag, QPixmap, QPainter
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from app.core.constants import SPACING_SMALL
from app.core.icon_manager import get_icon


class DragItem(QWidget):
    """
    A draggable widget representing a single item in the DragWidget list.
    It now includes a drag handle for better discoverability.
    """

    def __init__(self, text: str, data: any, value: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.data = data

        self.setObjectName("blockWidget")
        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 15, 8)  # Adjust margins for the handle
        layout.setSpacing(10)

        # Using a grip/hamburger menu icon is a common UI pattern for this.
        handle = QLabel()
        handle.setPixmap(get_icon("DRAG_HANDLE").pixmap(16, 16))
        handle.setToolTip("Click and drag to reorder")
        handle.setCursor(Qt.CursorShape.OpenHandCursor)  # Change cursor on hover

        self.text_label = QLabel(text)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("lightText")

        layout.addWidget(handle)  # Add handle to the left
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.value_label)

    def mousePressEvent(self, e):
        """Change cursor to grabbing when mouse is pressed."""
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """Change cursor back when mouse is released."""
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            source_pixmap = self.grab()
            target_pixmap = QPixmap(source_pixmap.size())
            target_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(target_pixmap)
            painter.setOpacity(0.7)
            painter.drawPixmap(0, 0, source_pixmap)
            painter.end()

            drag.setPixmap(target_pixmap)
            drag.setHotSpot(e.position().toPoint())

            drag.exec(Qt.DropAction.MoveAction)


class DragWidget(QWidget):
    """
    A container that allows for reordering of DragItem widgets.
    """
    orderChanged = Signal(list)

    def __init__(self, orientation=Qt.Orientation.Vertical, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.container_layout = QVBoxLayout()
            # --- FIX: Align items to the top of the layout ---
            self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        else:
            self.container_layout = QHBoxLayout()
            self.container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(SPACING_SMALL)
        self.setLayout(self.container_layout)

    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()

        for n in range(self.container_layout.count()):
            w = self.container_layout.itemAt(n).widget()
            if self.orientation == Qt.Orientation.Vertical:
                drop_here = pos.y() < w.y() + w.size().height() // 2
            else:
                drop_here = pos.x() < w.x() + w.size().width() // 2

            if drop_here:
                self.container_layout.insertWidget(n, widget)
                self.orderChanged.emit(self.get_item_data())
                e.acceptProposedAction()
                return

        self.container_layout.addWidget(widget)
        self.orderChanged.emit(self.get_item_data())
        e.acceptProposedAction()

    def add_item(self, text: str, data: any, value: str = ""):
        item = DragItem(text, data, value, self)
        self.container_layout.addWidget(item)

    def get_item_data(self) -> list:
        return [self.container_layout.itemAt(n).widget().data for n in range(self.container_layout.count())]

    def clear(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()