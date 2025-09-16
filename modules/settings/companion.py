# Basic
from dataclasses import dataclass

# Custom modules
from .config_loader import load_config
from modules.core import PathManager



@dataclass
class CompanionSettings:
    model_scale: float = 1.4
    horizontal_anchor: float = 0.50
    vertical_anchor: float = 0.80



companion_settings = load_config(
    CompanionSettings,
    PathManager.get_companions_config_path()
)