# Basic
from dataclasses import dataclass

# Custom modules
from .config_loader import load_config
from modules.core import PathManager



@dataclass
class AppSettings:
    companion_run_on_launch: bool = True
    language: str = "en"



app_settings = load_config(
    AppSettings,
    PathManager.get_app_settings_path()
)