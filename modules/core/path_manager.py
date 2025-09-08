# Basic
import sys
from pathlib import Path



class PathManager:
    # This parameter used to get the path of the entry
    # point of the application, instead of module path
    MAIN_DIR = Path(sys.argv[0]).resolve().parent

    @staticmethod
    def get_icon_path():
        return PathManager.MAIN_DIR / 'assets' / 'app.ico'
    
    @staticmethod
    def get_companions_dir():
        return PathManager.MAIN_DIR / 'companions'