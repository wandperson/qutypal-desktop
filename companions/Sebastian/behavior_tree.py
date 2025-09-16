# PyInstaller with console=False sets sys.stdout and sys.stderr to None
#
# Some libraries (namely py_trees.console) expect
# them to always exist and try to access attributes
# like "encoding" which leads to errors
#
# To prevent AttributeError in a "no-console"
# build, we replace "None" with a dummy in-memory
# stream (StringIO). This way, print() and logging
# calls won't break even if there is no real console
import sys, io

if sys.stdout is None:
    sys.stdout = io.StringIO()

if sys.stderr is None:
    sys.stderr = io.StringIO()



# Basic
import random as r
from time import time
from math import sqrt
from typing import TYPE_CHECKING

# IO
from pynput.mouse import Controller

# Behavior
from py_trees.blackboard import Blackboard
from py_trees.common import Status
from py_trees.behaviour import Behaviour
from py_trees.decorators import Inverter
from py_trees.composites import Sequence, Selector

# Custom modules
if TYPE_CHECKING:
    from modules.companion_base import Companion



# Typied Blackboard
class TBoard(Blackboard):
    companion: "Companion"
    mouse: Controller



# ==================================================
#           New Tick
# ==================================================
class Resetter(Behaviour):
    def __init__(self, name="Resetter"):
        super().__init__(name=name)

    def initialise(self):
        energy = TBoard.companion.get_energy()
        energy_percent = int(TBoard.companion.get_energy_level() * 100)
        print(f"Resetter | New tick | ⚡ {energy} ({energy_percent} %)")

        # Stop animation from some of interactions animation
        TBoard.companion.stop_animation()
        # Reduce interaction actions to 1 or 0
        TBoard.companion.resolve_interactions()

    def update(self):
        return Status.SUCCESS


# ==================================================
#           Collisions
# ==================================================
class IsOnGround(Behaviour):
    def __init__(self, name="OnGround?"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.get_feet_pos()[1] + 1 == TBoard.companion.get_ground_level():
            return Status.SUCCESS
        return Status.FAILURE


# ===
# === Falling ===
class IsAboveGround(Behaviour):
    def __init__(self, name="AboveGround?"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.get_feet_pos()[1] + 1 < TBoard.companion.get_ground_level():
            return Status.SUCCESS
        return Status.FAILURE


class Fall(Behaviour):
    def __init__(self, name="Fall"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.fall_to_ground():
            if TBoard.companion.get_velocities()[1] < -4:
                TBoard.companion.start_animation('fly_upward')
            elif TBoard.companion.get_velocities()[1] > 4:
                TBoard.companion.start_animation('fly_downward')
            else:
                TBoard.companion.start_animation('fly_apex')

            if 0 <= TBoard.companion.get_velocities()[1] <= 22:
                self._catch_mouse()
            return Status.RUNNING
        self._catch_mouse()
        return Status.SUCCESS

    def _catch_mouse(self):
        mouse_x, mouse_y = TBoard.mouse.position
        x, y = TBoard.companion.get_feet_pos()
        if x - 28 <= mouse_x <= x + 28 \
        and y - 18 <= mouse_y <= y:
            TBoard.mouse.position = (
                int(mouse_x + TBoard.companion.get_velocities()[0]),
                int(y + TBoard.companion.get_velocities()[1])
            )

class Landing(Behaviour):
    def __init__(self, name="Land"):
        super().__init__(name)

    def initialise(self):
        animation_name = 'land_recover'

        if TBoard.companion.get_land_velocity() > 30:
            animation_name = 'land_flat'
        
        TBoard.companion.start_animation(name=animation_name, repeat=1)

    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-3)
            return Status.RUNNING
        return Status.SUCCESS

# ===
# === Jumping Out ===
class IsUnderGround(Behaviour):
    def __init__(self, name="UnderGround?"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.get_feet_pos()[1] + 1 > TBoard.companion.get_ground_level():
            return Status.SUCCESS
        return Status.FAILURE


class JumpOutSetup(Behaviour):
    def __init__(self, name="JumpOutSetup"):
        super().__init__(name)

    def initialise(self):
        # He-he, another in a hurry obscurantism
        # TODO: Rewrite velocity calculation logic

        x, y = TBoard.companion.get_centers()

        distance_x = 30 * TBoard.companion._window.label.direction
        distance_y = y + 80 - TBoard.companion.get_ground_level()

        gravity = 64
        t = sqrt(2 * abs(distance_y) / gravity)

        # Calculate the required horizontal velocity
        horizontal_velocity = distance_x / (min(1, t)) / 14
        # With vertical motion equation we can find the initial vertical velocity
        vertical_velocity = min(26, (distance_y + 0.5 * gravity * t**2) / t / 4)
        vertical_velocity *= -1

        TBoard.companion.set_velocities(vx=horizontal_velocity, vy=vertical_velocity)
        TBoard.companion.start_animation(name='jump_start', repeat=1)

    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-3)
            return Status.RUNNING
        return Status.SUCCESS


class JumpOut(Behaviour):
    def __init__(self, name="JumpOut"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.fall_to_ground():
            if TBoard.companion.get_velocities()[1] < -4:
                TBoard.companion.start_animation('fly_upward')
            elif TBoard.companion.get_velocities()[1] > 4:
                TBoard.companion.start_animation('fly_downward')
            else:
                TBoard.companion.start_animation('fly_apex')
            return Status.RUNNING
        return Status.SUCCESS


# ==================================================
#           Routines
# ==================================================
class IsUserNotInteracting(Behaviour):
    def __init__(self, name="IsUserNotInteracting"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.get_interactions():
            TBoard.companion.stop_animation()
            return Status.FAILURE
        return Status.SUCCESS


# ===
# === Sleeping ===
class IsEnergyLow(Behaviour):
    def __init__(self, name="EnergyLow?"):
        super().__init__(name)

    def update(self):
        if TBoard.companion.get_energy_level() <= 0.15:
            return Status.SUCCESS
        return Status.FAILURE

class Sleep(Behaviour):
    def __init__(self, name="Sleep"):
        super().__init__(name)

    def initialise(self):
        TBoard.companion.start_animation(name='sleep')
    
    def update(self):
        TBoard.companion.change_energy(40)
        
        if TBoard.companion.get_energy_level() < 0.95:
            return Status.RUNNING
        return Status.SUCCESS


# ===
# === Moving ===
class IsTimeToMove(Behaviour):
    def __init__(self, name="TimeToMove?"):
        super().__init__(name)
        self.init_probability = 0.01
        self.probability = self.init_probability
        self.out_of_field = False

        self.icrease_rate = 0.001
        self.timer = time()

    def initialise(self):
        x = TBoard.companion.get_feet_pos()[0]

        left_x, right_x = TBoard.companion.get_walking_area_x()
        if not left_x <= x <= right_x:
            self.out_of_field = True
            return

        elapsed_time = time() - self.timer
        self.probability = min(1, self.probability + (elapsed_time * self.icrease_rate))

        mouse_x, mouse_y = TBoard.mouse.position

        ground = TBoard.companion.get_ground_level()

        search_sizes = [
            TBoard.companion._window.size().width() * 1.4,
            TBoard.companion._window.anchor[1] * 1.2
        ]
        # Companion want to move to mouse
        # when mouse in the field of sight
        # but not when close to him
        if (ground - 1 - search_sizes[1] <= mouse_y < ground) \
        and not (x - search_sizes[0] <= mouse_x <= x + search_sizes[0]):
            self.probability = min(1, self.probability + 0.35)

    def update(self):
        if self.out_of_field:
            self.out_of_field = False
            return Status.SUCCESS
        
        # Check if the event occurs
        if r.random() <= self.probability:
            self.probability = self.init_probability    # Reset probability
            self.timer = time()                         # Reset time
            return Status.SUCCESS
        return Status.FAILURE


class Move(Behaviour):
    def __init__(self, name="Move"):
        super().__init__(name)
        self.out_of_field = False
        self.desired_position_x = None

    def initialise(self):
        x = TBoard.companion.get_feet_pos()[0]

        left_x, right_x = TBoard.companion.get_walking_area_x()

        if not left_x <= x <= right_x:
            dist_left = abs(x - left_x)
            dist_right = abs(x - right_x)

            ratio = TBoard.companion._window.size().width() / 2
            if dist_left < dist_right:
                self.desired_position_x = r.randint(
                    int(ratio),
                    int(ratio + (5 * TBoard.companion._window.anchor[0]))
                )
            else:
                self.desired_position_x = r.randint(
                    int(right_x - ratio - (5 * TBoard.companion._window.anchor[0])),
                    int(right_x - ratio)
                )
            TBoard.companion.resolve_gaze(self.desired_position_x)
            TBoard.companion.start_animation(name="walk")
            self.out_of_field = True
            return

        mouse_x, mouse_y = TBoard.mouse.position

        ground = TBoard.companion.get_ground_level()

        search_sizes = [
            TBoard.companion._window.size().width() * 1.4,
            TBoard.companion._window.anchor[1] * 1.2
        ]

        if ground - 1 - search_sizes[1] <= mouse_y <= ground:
            self.desired_position_x = mouse_x + r.randint(-120, 120)
        else:
            self.desired_position_x = r.randint(*TBoard.companion.get_walking_area_x())
        
        TBoard.companion.resolve_gaze(self.desired_position_x)
        TBoard.companion.start_animation(name="walk")

    def update(self):
        if TBoard.companion.move_to_goal(x=self.desired_position_x, speed_multiplier=1.6 if self.out_of_field else 1):
            TBoard.companion.change_energy(-5)
            return Status.RUNNING
        self.desired_position_x = None
        self.out_of_field = False
        return Status.SUCCESS


# ===
# === Jumping ===
class IsTimeToJump(Behaviour):
    def __init__(self, name="TimeToJump?"):
        super().__init__(name)
        self.init_probability = 0.01
        self.probability = self.init_probability

        self.icrease_rate = 0.001
        self.timer = time()

    def initialise(self):
        elapsed_time = time() - self.timer
        self.probability = min(1, self.probability + (elapsed_time * self.icrease_rate) / 2)

        x = TBoard.companion.get_feet_pos()[0]
        mouse_x, mouse_y = TBoard.mouse.position

        ground = TBoard.companion.get_ground_level()
        search_sizes = [
            TBoard.companion._window.size().width() * 1.4,
            TBoard.companion._window.anchor[1] * 1.4
        ]

        center_x = TBoard.companion.get_centers()[0]
        
        # Add extra chance when the mouse is nearby
        # So companion totally want to catch it
        if (ground - 1 - search_sizes[1] <= mouse_y <= ground - 1) \
        and (x - search_sizes[0] <= mouse_x <= x + search_sizes[0]):
            self.probability = min(1, self.probability + 0.65)

    def update(self):
        if r.random() <= self.probability:
            self.probability = self.init_probability    # Reset probability
            self.timer = time()                         # Reset time
            return Status.SUCCESS
        return Status.FAILURE


class JumpSetup(Behaviour):
    def __init__(self, name="JumpPreparing"):
        super().__init__(name)

    def initialise(self):
        # He-he, another in a hurry obscurantism
        # TODO: Rewrite velocity calculation logic
        
        mouse_x, mouse_y = TBoard.mouse.position

        distance_x = mouse_x - TBoard.companion.get_centers()[0]
        distance_y = TBoard.companion.get_ground_level() - mouse_y

        gravity = 64
        t = sqrt(2 * abs(distance_y) / gravity)

        # Calculate the required horizontal velocity
        horizontal_velocity = distance_x / (min(1, t)) / 14
        # With vertical motion equation we can find the initial vertical velocity
        vertical_velocity = min(26, (distance_y + 0.5 * gravity * t**2) / t / 4)
        vertical_velocity *= -1

        TBoard.companion.set_velocities(vx=horizontal_velocity, vy=vertical_velocity)
        TBoard.companion.start_animation(name='jump_start', repeat=1)

    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-3)
            return Status.RUNNING
        TBoard.companion.fall_to_ground()
        return Status.SUCCESS


# ===
# === Idling ===
class Idle(Behaviour):
    def __init__(self, name="Idle"):
        super().__init__(name)

    def initialise(self):
        idle = r.choices(
            population=['idle', 'idle_look_back'],
            weights=[0.8, 0.2]
        )[0]

        if idle == 'idle':
            TBoard.companion.start_animation(name=idle, repeat=r.randint(3, 8))
        else:
            TBoard.companion.start_animation(name=idle, repeat=1)
    
    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-3)
            return Status.RUNNING
        return Status.SUCCESS
    

# ==================================================
#           Interactions
# ==================================================
class IsOneInteraction(Behaviour):
    def __init__(self, name="IsOneInteraction"):
        super().__init__(name)

    def update(self):
        if len(TBoard.companion.get_interactions()) == 1:
            return Status.SUCCESS
        return Status.FAILURE


class IsInteraction(Behaviour):
    def __init__(self, name):
        super().__init__(name)

    def update(self):
        if self.name.startswith(TBoard.companion.get_interactions()[0]):
            print(f"Interacting: {self.name[:-1]}")
            return Status.SUCCESS
        return Status.FAILURE


# ===
# === Disturbing ===
class Disturb(Behaviour):
    def __init__(self, name="Disturb"):
        super().__init__(name)

    def initialise(self):
        TBoard.companion.start_animation(name='bristle', repeat=1)
    
    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-3)
            return Status.RUNNING
        return Status.SUCCESS


# ===
# === Holding ===
class Hold(Behaviour):
    def __init__(self, name="Hold"):
        super().__init__(name)

    def initialise(self):
        TBoard.companion.start_animation(name='grabbed')

    def update(self):
        if TBoard.companion.is_animating():
            TBoard.companion.change_energy(-1)
            return Status.RUNNING
        return Status.SUCCESS


# ===
# === Assisting ===
# class Assist(Behaviour):
#     def __init__(self, name="Assist"):
#         super().__init__(name)

#     def initialise(self):
#         self.result_queue = queue.Queue()

#         name = 'idle_2'
#         TBoard.companion.animation_id = TBoard.companion.after(
#             TBoard.companion.animations[name]['duration'],
#                             TBoard.companion.play_animation,
#                             name)
#         TBoard.companion.speaking_id = TBoard.companion.after(0, TBoard.companion.speaking, self.result_queue)
        
#     def update(self):
#         try:
#             result = self.result_queue.get_nowait()  # Non-blocking get from queue
#             TBoard.companion.dialog.show_dialog(result, TBoard.companion.direction)
#             print("Dialog endid")
#             TBoard.companion.user_interacted = ''
#             return Status.SUCCESS
#         except queue.Empty:
#             return Status.RUNNING


# ==================================================
#           Tree
# ==================================================
def create_tree(companion_api: "Companion"):
    TBoard.companion = companion_api
    TBoard.mouse = Controller()

    # Creating a root of the tree
    root = Selector(name="Root", memory=True)

    # ==================================================

    dynamic = Selector(name="Dynamics", memory=True, children=[
        Sequence(name="Falling", memory=True, children=[
            IsAboveGround(), Fall(), Landing()]),
        Sequence(name="JumpingOut", memory=True, children=[
            IsUnderGround(), JumpOutSetup(), JumpOut()]),
        IsOnGround(),
    ])
    
    # сollision  = Sequence(name="Collision", memory=False, children=[
    #     Inverter(name="Inverter", child=
    #         IsOnGround()),
    #     dynamic,
    # ])

    # ==================================================

    activity = Selector(name="Activity", memory=True, children=[
        Sequence(name="Sleeping", memory=True, children=[
            IsEnergyLow(), Sleep()]),
        Sequence(name="Moving", memory=True, children=[
            IsTimeToMove(), Move()]),
        Sequence(name="Jumping", memory=True, children=[
            IsTimeToJump(), JumpSetup()]),
        Sequence(name="Idling", memory=True, children=[
            Idle()]),
    ])
    
    # routine  = Sequence(name="Routine", memory=False, children=[
    #     IsUserNotInteracting(),
    #     activity,
    # ])

    # ==================================================

    motion  = Sequence(name="Motion", memory=False, children=[
        IsUserNotInteracting(),
        dynamic,
        activity,
    ])

    # ==================================================

    actions = Selector(name="Actions", memory=True, children=[
        Sequence(name="Disturbing", memory=True, children=[
            IsInteraction(name="Disturb?"), Disturb()]),
        Sequence(name="Holding", memory=True, children=[
            IsInteraction(name="Hold?"), Hold()]),
        # Sequence(name="Assist", memory=True, children=[
        #     IsInteraction(name="IsAssist"), Assist()]),
    ])
    
    interaction  = Sequence(name="Interaction", memory=False, children=[
        IsOneInteraction(),
        actions,
    ])

    # ==================================================

    root.add_children(children=[
        Inverter(name="Inverter", child=
            Resetter()),
        motion,
        interaction
    ])

    return root