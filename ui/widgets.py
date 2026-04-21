from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal


class ClickableLabel(QLabel):
    """可点击的 QLabel，用于检测画面显示区域。"""
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
