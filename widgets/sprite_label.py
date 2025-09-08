# Basic
import json

# Application
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QBitmap, QTransform
from PyQt6.QtCore import QTimer

# Custom modules
from modules.core import PathManager
from modules.settings import companion_settings



class SpriteLabel(QLabel):
    def __init__(self, parent, companion_name: str):
        super().__init__(parent)

        self.animations = self._loadSprites(companion_name)

        # Animation control
        self.animation: str = None
        self.repeats: int = -1
        self.frame_id: int = 0
        self.direction: int = 1

        
        self.animator = QTimer()
        self.animator.timeout.connect(self._playAnimation)

    @staticmethod
    def _is_fully_transparent(qimage: QImage) -> bool:
        """
        Checks if all pixels in the image are fully transparent
        (alpha channel = 0)

        Args:
            qimage (QImage): Image to check

        Returns:
            bool: True if image is fully transparent, False otherwise

        Notes:
            - This function could be optimized using NumPy,
            but is that really necessary for this use case
            with a few low-resolution frames?
        """
        image = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        
        # Get pointer to raw bytes of the image
        ptr = image.constBits()

        # RGBA = 4 bytes per pixel
        ptr.setsize(image.width() * image.height() * 4)

        data = memoryview(ptr)
        # Check if all alpha channels are zero
        for i in range(3, len(data), 4):
            if data[i] != 0:
                return False
        return True
    
    def _loadSprites(self, companion_name: str) -> dict:
        """
        Loads all sprites from .png file

        Args:
            companion_name (str): Name of companion folder
        
        Returns:
            dict: Dictionary with frames, alpha masks and corresponding mirrored frames
        """
        assets_dir = PathManager.get_companions_dir() / companion_name / "assets"
        static = QPixmap(str(assets_dir / "sprite_static.png"))

        # Size of sprite frame
        frame_w, frame_h = static.size().width(), static.size().height()

        if companion_settings.model_scale != 1:
            static = static.scaled(
                int(static.width() * companion_settings.model_scale),
                int(static.height() * companion_settings.model_scale)
            )

        self.setFixedSize(static.width(), static.height())
        self.setPixmap(static)

        sprites = {}

        with open(assets_dir / "sprites_metadata.json", "r") as f:
            metadata = json.load(f)

        sheet = QImage(str(assets_dir / "sprites_sheet.png"))
        for key, value in metadata.items():
            # === Collecting frames for animation ===
            frames = []
            for col in range(sheet.width() // frame_w):
                frame = sheet.copy(
                    col * frame_w,
                    (value["row"] - 1) * frame_h,
                    frame_w,
                    frame_h
                )
                
                # Check if frame is fully transparent
                # and treat it like it's the last frame
                if self._is_fully_transparent(frame):
                    break

                if companion_settings.model_scale != 1:
                    frame = frame.scaled(
                        int(frame.width() * companion_settings.model_scale),
                        int(frame.height() * companion_settings.model_scale)
                    )
                
                frames.append(frame)
            
            # === Creating title for animation ===
            sprites[key] = {}
            sprites[key]["n_frames"] = len(frames)
            sprites[key]["duration"] = value["frame_duration"]
            # Cashed frames for faster access and rendering
            sprites[key]["frames"] = {1: [], -1: []}
            # Alpha masks to determine interactive area of a sprite
            sprites[key]["alphas"] = {1: [], -1: []}

            # === Creating two directions and alpha masks for animation ===
            for frame in frames:
                sprites[key]["frames"][1].append(QPixmap.fromImage(frame))
                sprites[key]["alphas"][1].append(QBitmap.fromImage(frame.createAlphaMask()))
                
                mirrored_frame = frame.transformed(QTransform().scale(-1, 1))
                sprites[key]["frames"][-1].append(QPixmap.fromImage(mirrored_frame))
                sprites[key]["alphas"][-1].append(QBitmap.fromImage(mirrored_frame.createAlphaMask()))
        
        return sprites

    def setSprite(self, animation: str, frame_id: int) -> None:
        frame = self.animations[animation]["frames"][self.direction][frame_id]
        alpha = self.animations[animation]["alphas"][self.direction][frame_id]

        self.setPixmap(frame)
        self.parentWidget().setMask(alpha)
    
    def _playAnimation(self) -> None:
        """
        Set current animation sprite and updates 
        internal state for the next iteration.

        `repeats` is used to determine if the animation
        should stop after certain number of cycles.
        If `repeats` is -1, it means the animation will play indefinitely.
        """
        animation = self.animations[self.animation]

        # Handle limited repeats
        if self.repeats > 0:
            checker = self.frame_id // (animation["n_frames"])
            if checker >= self.repeats:
                self.animator.stop()
                return

        curr_frame_id = self.frame_id % (animation["n_frames"])
        self.setSprite(self.animation, curr_frame_id)

        # Set duration for current frame
        self.animator.setInterval(animation["duration"])

        print(f"  {self.frame_id:>3} {curr_frame_id:>2} | {animation['n_frames']:>2}   ({self.animation})")

        self.frame_id += 1