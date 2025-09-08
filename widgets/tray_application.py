# Base
import sys
import traceback

# PyQt
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction

# Custom modules
from modules.core import PathManager, lang_
from modules.settings import app_settings
from modules.companion_base import Companion
from .settings_window import SettingsWindow



class TrayApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Prevent QApplication from quitting when no window is visible
        self.setQuitOnLastWindowClosed(False)
        
        # Initialize tray
        self.tray = QSystemTrayIcon()

        self.tray.setIcon(QIcon(str(PathManager.get_icon_path())))
        self.tray.setVisible(True)

        self.tray.setContextMenu(self._buildTrayContextMenu())

        # Initialize settings window
        self.settings_window = SettingsWindow()

        # Initialize companion window
        self.companion = None
        if app_settings.companion_run_on_launch:
            self.recallCompanion()

    def _buildTrayContextMenu(self):
        tray_menu = QMenu()

        # TRANSLATORS: Text in tray menu to return companion to screen
        recallAction = QAction(lang_("return_companion"), self.tray)
        recallAction.triggered.connect(self.recallCompanion)
        tray_menu.addAction(recallAction)

        tray_menu.addSeparator()

        # TRANSLATORS: Text in tray menu to open settings
        settingsAction = QAction(lang_("preferences"), self.tray)
        settingsAction.triggered.connect(self.showSettings)
        tray_menu.addAction(settingsAction)

        tray_menu.addSeparator()

        # TRANSLATORS: Text in tray menu to quit from app
        exitAction = QAction(lang_("quit"), self.tray)
        exitAction.triggered.connect(self.quitApp)
        tray_menu.addAction(exitAction)

        return tray_menu

    def showSettings(self):
        self.settings_window.show()             # Makes window visible
        self.settings_window.raise_()           # Brings window to top
        self.settings_window.activateWindow()   # Requests focus for window

    def recallCompanion(self):
        # Temporary stupid error handling, just to have something working
        # TODO: Rewrite error handling
        try:
            if self.companion:
                ...
            else:
                self.companion = Companion(companion_name="Sebastian")
                self.companion.signalDestroyRequested.connect(self.releaseCompanion)
                self.companion.signalQuitAppRequested.connect(self.quitApp)
                self.companion.start_activity()
        except Exception:
            # Console output
            self.show_companion_error(
                "Companion Error",
                "".join(traceback.format_exception(*sys.exc_info())),
            )

    @staticmethod
    def show_companion_error(title: str, text: str):
        # For console output
        print(text)
        # For user feedback
        QMessageBox.critical(
            None,
            title,
            text,
            QMessageBox.StandardButton.Ok
        )

    def releaseCompanion(self):
        print("Releasing companion")
        self.companion.stop_activity()
        self.companion._window.closeWindow()
        self.companion.signalDestroyRequested.disconnect(self.releaseCompanion)
        self.companion.signalQuitAppRequested.disconnect(self.quitApp)
        self.companion = None

    def quitApp(self):        
        # Close explicitly in case of cleanup logic
        if self.companion:
            self.releaseCompanion()
        self.settings_window.close()
        
        print("Quitting")
        
        # Qt will auto-close all top-level windows
        self.quit()