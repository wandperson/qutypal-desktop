# Basic
import sys

# Custom modules
from widgets import TrayApplication



if __name__ == '__main__':
    app = TrayApplication(sys.argv)
    sys.exit(app.exec())