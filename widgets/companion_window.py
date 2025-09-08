# Basic
import random as r
import math
from dataclasses import dataclass

# Application
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

# Custom modules
from modules.core import lang_, platman
from modules.settings import companion_settings
from .dialogue_window import DialogWindow
from .sprite_label import SpriteLabel



from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modules.companion_base import Companion



@dataclass
class Screen:
    width: int
    height: int
    work_area_height: int



class CompanionWindow(QWidget):
    def __init__(self, companion: "Companion"):
        super().__init__()
        
        self._companion = companion

        # Holds state for platform attributes
        self.user_screen = Screen(*platman.get_resolution())

        self._start_pos = None
        self._drag_pos = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            # Prevents the window from being managed by the window manager
            # Added for Linux Cinnamon specifically to avoid
            # the window snapping/sticking to screen edges
            Qt.WindowType.BypassWindowManagerHint |
            # Added for Windows specifically to
            # hide window from the taskbar
            Qt.WindowType.Tool
        )
        # Make the window transparent when mask applied
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set the cursor to the "open hand" shape, which
        # indicates that the companion is grabbable.
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self.setWindowTitle(self._companion.name)

        # Create context menu
        self.context_menu = self._buildContextMenu()

        # Widget to "render" the companion sprites
        self.label = SpriteLabel(parent=self, companion_name=self._companion.name)

        # Widget for companion dialogue window
        self.dialog = DialogWindow(self)

        # Prevent the window from being resized
        self.setFixedSize(self.label.size())
        
        # Use to define distance from the top of
        # the window to the companion feet level
        self.anchor = [
            int(self.size().width() * companion_settings.horizontal_anchor),
            int(self.size().height() * companion_settings.vertical_anchor)
        ]
        
        self.setStartingPosition("random_offscreen")

        self.show()

    def setStartingPosition(self, spawn_type: str = "center") -> None:
        x = 0
        if spawn_type == "center":
            x = self.user_screen.width / 2
        elif spawn_type == "random_offscreen":
            x = r.choice([
                0 - self.size().width() * 1.2,
                self.user_screen.width + self.size().width() * 1.2
            ])
        
        y = self.user_screen.work_area_height - self.anchor[1] - 1
        
        self.move(int(x), y)

    def _buildContextMenu(self):
        menu = QMenu(self)

        # listenAction = QAction("Слухай!", self)
        # listenAction.triggered.connect(
        #     lambda: self.companion_state.interactions.append("Assist")
        # )
        # menu.addAction(listenAction)

        # TRANSLATORS: This is a context menu item for the companion window
        # When clicked, the companion repeat the last phrase spoken
        repeatAction = QAction(lang_("companion_command_repeat"), self)
        repeatAction.triggered.connect(
            lambda: self.dialog.showDialog()
        )
        menu.addAction(repeatAction)

        menu.addSeparator()
        
        # TRANSLATORS: This is a context menu item for the companion window
        # This is a name of submenu with some companion attr control features
        tweakMenu = QMenu(lang_("companion_tweaker"), self)

        # TRANSLATORS: This is a context submenu item for the companion window
        # When clicked, the companion will restore its energy to max
        recoverAction = QAction(lang_("companion_command_recover"), self)
        recoverAction.triggered.connect(
            lambda: self._companion.refill_energy()
        )
        tweakMenu.addAction(recoverAction)

        # TRANSLATORS: This is a context submenu item for the companion window
        # When clicked, the companion will reset its energy to zero
        exhaustAction = QAction(lang_("companion_command_exhaust"), self)
        exhaustAction.triggered.connect(
            lambda: self._companion.deplete_energy()
        )
        tweakMenu.addAction(exhaustAction)

        menu.addMenu(tweakMenu)

        menu.addSeparator()

        # TRANSLATORS: This is a context menu item for the companion window
        # When clicked, the companion window will disappear
        releaseAction = QAction(lang_("companion_close"), self)
        releaseAction.triggered.connect(
            lambda: self._companion.close_window())
        menu.addAction(releaseAction)

        # TRANSLATORS: This is a context menu item for the companion window
        # When clicked, the app will quit
        exitAction = QAction(lang_("exit"), self)
        exitAction.triggered.connect(
            lambda: self._companion.quit_app())
        menu.addAction(exitAction)

        return menu

    def contextMenuEvent(self, event):
        # Launching the context menu
        self.context_menu.popup(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._companion.add_interaction("Hold")
            self._start_pos = event.globalPosition()
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self._companion.add_interaction("Disturb")

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    @staticmethod
    def apply_sqrt(dx, dy) -> tuple[float, float]:
        """
        Map a drag vector (dx, dy) to velocity (vx, vy) using a sqrt transfer function.

        Returns:
        vx, vy : floats
        """
        L = math.hypot(dx, dy)
        if L == 0:
            return 0, 0

        L0 = 800
        terminal_velocity = 64.0

        # Normalized factor
        t = min(L / L0, 1.0)
        mag = terminal_velocity * math.sqrt(t**1.2)

        ux = dx / L
        uy = dy / L
        vx = ux * mag
        vy = uy * mag
        
        return (vx, vy)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            vector = event.globalPosition() - self._start_pos
            self._companion.set_velocities(*self.apply_sqrt(vector.x(), vector.y()))

        self._companion.remove_interaction("Hold")

        self._start_pos = None
        self._drag_pos = None
        event.accept()

    # DoubleClick event also triger click and drag events.
    # And that's a problem, so it's middle click for now
    # def mouseDoubleClickEvent(self, event):
    #     print("Double Click Event")
    #     self.companion_state.interactions.append("Disturb")

    def moveEvent(self, event):
        super().moveEvent(event)
        # Bind dialog window to companion movement
        if self.dialog and self.dialog.isVisible():
            parent_rect = self.geometry()
            x = parent_rect.center().x() - self.dialog.width() // 2
            y = parent_rect.top() - 60
            self.dialog.move(x, y)

    def closeWindow(self):
        self.close()
        self.deleteLater()