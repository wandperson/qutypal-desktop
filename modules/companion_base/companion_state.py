# Basic
import random as r
from typing import Optional
from dataclasses import dataclass, field

# Custom modules
from modules.core import platman



@dataclass
class CompanionState:
    # Characteristics
    max_energy: float = 100_000
    energy: float =  max_energy
    move_speed: int = 6

    # Intentions
    desire_spot_x: Optional[float] = None

    # Positioning
    # direction: int = r.choice((-1, 1))
    vector: list[float] = field(default_factory=list)
    horizontal_velocity: float = 0.0
    vertical_velocity: float = 0.0
    land_velocity: float = 0.0

    # Holds state for animations
    interactions: list[str] = field(default_factory=list)