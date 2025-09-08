# Base
import math

# Application
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

# Custom modules
from widgets.companion_window import CompanionWindow
from modules.settings import companion_settings
from .companion_state import CompanionState
from .companion_behavior import load_behavior_tree



# from decimal import Decimal, ROUND_HALF_UP
# print(int(Decimal(2.5).quantize(0, rounding=ROUND_HALF_UP)))




# === State Attributes ===
class StateMixin:
    _state: CompanionState


    def get_interactions(self) -> list[str]:
        return self._state.interactions

    def add_interaction(self, name: str) -> None:
        self._state.interactions.append(name)

    def remove_interaction(self, name: str) -> None:
        self._state.interactions = \
            [v for v in self._state.interactions if v != name]

    def resolve_interactions(self) -> None:
        if len(self._state.interactions) > 1:
            self._state.interactions = self._state.interactions[-1:]
        else:
            self._state.interactions = []
    
    def get_energy(self) -> float:
        return self._state.energy
    
    def get_energy_level(self) -> float:
        current_level = self._state.energy / self._state.max_energy
        return round(current_level, 2)

    def change_energy(self, amount: int) -> None:
        # Ensuring it stays within the valid range of 0 to max_energy
        self._state.energy = \
            max( 0,
                min(
                    self._state.max_energy,
                    self._state.energy + amount)
            )
    
    def refill_energy(self) -> None:
        self._state.energy = self._state.max_energy
        self._behavior.stop(self._behavior.status.INVALID)

    def deplete_energy(self) -> None:
        self._state.energy = 0
        self._behavior.stop(self._behavior.status.INVALID)

    def set_velocities(self, vx: float, vy: float) -> None:
        self._state.horizontal_velocity = vx
        self._state.vertical_velocity = vy

    def get_velocities(self) -> tuple[float, float]:
        vx = self._state.horizontal_velocity
        vy = self._state.vertical_velocity
        return (vx, vy)
    
    def get_land_velocity(self) -> float:
        return self._state.land_velocity



# === Position ===
class PositionMixin:
    _state: CompanionState
    _window: CompanionWindow

    def get_position(self) -> tuple:
        return self._window.pos()
    
    def get_ground_level(self) -> int:
        return self._window.user_screen.work_area_height
    
    def get_feet_pos(self) -> tuple[int, int]:
        x = self._window.pos().x() + self._window.anchor[0]
        y = self._window.pos().y() + self._window.anchor[1]
        return (x, y)
    
    def get_centers(self) -> tuple[int, int]:
        x = self._window.geometry().center().x()
        y = self._window.geometry().center().y()
        return (x, y)

    def get_walking_area_x(self) -> tuple[int, int]:
        low = self._window.anchor[0]
        high = self._window.user_screen.width - (self._window.size().width() - self._window.anchor[0])
        return (low, high)



# === Animations ===
class AnimationMixin:
    _window: CompanionWindow

    def start_animation(self, name: str, repeat: int = -1, force_reset: bool = False) -> None:
        if self._window.label.animation == name \
        and not force_reset:
            return
        
        self._window.label.animation = name
        self._window.label.repeats = repeat
        self._window.label.frame_id = 0
        self._window.label.animator.start(0)
    
    def stop_animation(self) -> None:
        self._window.label.animator.stop()
    
    def is_animating(self) -> bool:
        return self._window.label.animator.isActive()

    def resolve_gaze(self, look_at_x: int) -> None:
        if look_at_x > self._window.pos().x():
            self._window.label.direction = 1
        elif look_at_x < self._window.pos().x():
            self._window.label.direction = -1



# === Movement ===
class MovementMixin:
    _state: CompanionState
    _window: CompanionWindow

    def move_to_goal(self, x: int, y: int = None, speed_multiplier: float = 1.0) -> bool:
        """
        Move the window to the target position (x, y) with a specified speed.

        Args:
            x (int): The target x-coordinate.
            y (int): The target y-coordinate
                Defaults to the current window's y-coordinate
            speed_multiplier (float, optional): The speed multiplier.
                Defaults to 1.0

        Returns:
            bool: False if the window is reaching the target position, True if reached.
        """
        current_x, current_y = self._window.pos().x(), self._window.pos().y()

        if speed_multiplier == 0:
            self._window.move(x, current_y)
            return False

        distance_remain_x = x - current_x - self._window.anchor[0]
        move_distance_x = self._state.move_speed * speed_multiplier

        if abs(move_distance_x) >= abs(distance_remain_x):
            self._window.move(x - self._window.anchor[0], current_y)
            return False

        new_x = current_x + math.copysign(move_distance_x, distance_remain_x)

        self._window.move(int(new_x), current_y)
        return True
    
    def fall_to_ground(self, gravity: int = 64, delay: int = 32) -> bool:
        """
        Simulate falling to the ground by moving window.

        Args:
            gravity (int, optional): The speed of moving window in px/sec.
                Defaults to 64
            delay (int, optional): The delay in behavior tree ticks.
                Defaults to 32

        Returns:
            bool: False if the window is reaching the ground, True if reached.
        """
        if self._state.horizontal_velocity > 0:
            self._window.label.direction = 1
        elif self._state.horizontal_velocity < 0:
            self._window.label.direction = -1

        delta_time = delay / 1_000

        # Simulate air resistance
        self._state.horizontal_velocity *= 1 - ( 0.1 * delta_time)
        # Simulate gravity acceleration
        self._state.vertical_velocity += gravity * delta_time

        x = self._window.pos().x() + int(self._state.horizontal_velocity)
        y = self._window.pos().y() + int(self._state.vertical_velocity)

        if y + self._window.anchor[1] >= self._window.user_screen.work_area_height \
        and self._state.vertical_velocity >= 0:
            self._state.land_velocity = self._state.vertical_velocity
            self._state.vertical_velocity = 0
            self._state.horizontal_velocity = 0
            feet_level = self._window.user_screen.work_area_height - self._window.anchor[1] - 1
            self._window.move(x, feet_level)
            return False
        
        self._window.move(x, y)
        return True



class Companion(QObject,
                StateMixin, PositionMixin, AnimationMixin, MovementMixin):
    # Signals
    signalDestroyRequested = pyqtSignal()
    signalQuitAppRequested = pyqtSignal()

    def __init__(self, companion_name: str):
        super().__init__()
        
        self.name = companion_name

        self._state = CompanionState()
        self._window = CompanionWindow(self)

        behavior_module = load_behavior_tree(self.name)
        self._behavior = behavior_module.create_tree(self)

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick_tree)

    def close_window(self):
        self.signalDestroyRequested.emit()

    def quit_app(self):
        self.signalQuitAppRequested.emit()

    def _tick_tree(self):
        self._behavior.tick_once()
    
    def start_activity(self, interval_ms: int = 32):
        self._timer.start(interval_ms)

    def stop_activity(self):
        self._timer.stop()