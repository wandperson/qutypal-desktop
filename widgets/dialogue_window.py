# Application
from PyQt6.QtWidgets import QDialog, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

# Custom modules
from modules.core import lang_


class DialogWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.setStyleSheet("background: transparent;")

        # TRANSLATORS: Hello phrase of companion Sebastian
        self.label = QLabel(parent=self, text=lang_("companion_say_hello"))
        self.label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                color: black;
                font-size: 16px;
                border: 1px solid #ccc;
            }
        """)
        self.label.adjustSize()

        # === Create a mask dynimically from a rendered QLabel ===
        pixmap = QPixmap(self.label.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        self.render(pixmap)
        self.setMask(pixmap.createMaskFromColor(Qt.GlobalColor.transparent))

        self.messageTimer = QTimer(self)
        self.messageTimer.setSingleShot(True)
        self.messageTimer.timeout.connect(self.hide)

    def showDialog(self):
        parent_rect = self.parentWidget().geometry()
        x = parent_rect.center().x() - self.width() // 2
        y = parent_rect.top() - 60
        self.move(x, y)
        self.show()
        offset = max(2000, len(self.label.text()) * 125)
        self.messageTimer.start(offset)