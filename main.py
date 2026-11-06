# Basic
import os
import sys

# Custom modules
from widgets import TrayApplication



if __name__ == '__main__':
    # Wayland doesn't allow apps to set their window position,
    # so on Linux always use X11 (via XWayland on Wayland sessions)
    if sys.platform.startswith('linux'):
        os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

    app = TrayApplication(sys.argv)
    sys.exit(app.exec())