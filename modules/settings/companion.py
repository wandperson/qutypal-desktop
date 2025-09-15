# Basic
import json
from typing import Optional
from dataclasses import dataclass, field



@dataclass
class CompanionSettings:
    model_scale: float = 1.4
    horizontal_anchor: float = 0.50
    vertical_anchor: float = 0.80

    def save(self, filename="settings.json"):
        with open(filename, "w") as f:
            json.dump(dict(self), f, indent=4)
    
    @classmethod
    def load(cls, filename="settings.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            return cls()

companion_settings = CompanionSettings()