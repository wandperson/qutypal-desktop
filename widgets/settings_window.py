# Application
from PyQt6.QtWidgets import QMainWindow, QLabel, QSlider
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Custom modules
from modules.core import PathManager, lang_



class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(str(PathManager.get_icon_path())))
        self.setWindowTitle(f"QutyPal - {lang_('preferences')}")
        self.setGeometry(100, 100, 600, 400)
        # Prevent the window from being resized
        self.setFixedSize(self.size())

        self.nothing_label = QLabel(parent=self)
        self.nothing_label.setText("Just a label with nothing in it.")
        # Define label's position and size
        self.nothing_label.setStyleSheet("""
            QLabel {
                border: 4px solid black;                /* 4-pixel black border */
                color: white;                           /* Text color */
                background-color: rgba(0, 0, 0, 0.5);   /* Semi-transparent background */
            }
        """)
        self.nothing_label.setGeometry(10, 10, 200, 60)


        self.slider = QSlider(parent=self, orientation=Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(5)
        self.slider.setPageStep(20)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setTickInterval(10)
        self.slider.setGeometry(10, 80, 200, 20)
        self.slider.setValue(20)

        self.slider_label = QLabel(parent=self)
        self.slider_label.setGeometry(220, 80, 80, 20)
        
        self.slider.valueChanged.connect(self.update_label)
        self.update_label(self.slider.value())

    def update_label(self, value):
        self.slider_label.setText(f"{value}")

    def closeEvent(self, event):
        event.ignore()
        self.hide()