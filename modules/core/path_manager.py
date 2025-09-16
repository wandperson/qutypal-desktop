# Basic
import sys
from pathlib import Path



class PathManager:
    # This parameter used to get the path of the entry
    # point of the application, instead of module path
    MAIN_DIR = Path(sys.argv[0]).resolve().parent

    @staticmethod
    def get_icon_path():
        return PathManager.MAIN_DIR / 'assets' / 'icon.ico'
    
    @staticmethod
    def get_companions_dir():
        return PathManager.MAIN_DIR / 'companions'

    @staticmethod
    def get_companions_config_path():
        return PathManager.MAIN_DIR / 'resources' / 'configs' / 'companion.toml'
    
    @staticmethod
    def get_app_settings_path():
        return PathManager.MAIN_DIR / 'resources' / 'configs' / 'application.toml'

    @staticmethod
    def get_locales_dir():
        return PathManager.MAIN_DIR / 'resources' / 'locales'