# ==================================================
#    OLD SPRITES LOADER FROM .gif FILES
# ==================================================
def _loadSprites(self, sprites_dir) -> dict:
    from PyQt6.QtGui import QMovie
    from PyQt6.QtGui import QBitmap, QTransform

    sprites = {}

    for file_path in sprites_dir.rglob("*.gif"):

        movie = QMovie(str(file_path))

        sprites[file_path.stem] = {}
        sprites[file_path.stem]["n_frames"] = movie.frameCount()
        sprites[file_path.stem]["frames"] = {1: [], -1: []}
        sprites[file_path.stem]["alpha"] = {1: [], -1: []}

        for _ in range(movie.frameCount()):
            movie.jumpToNextFrame()
            frame = movie.currentPixmap()
            sprites[file_path.stem]["frames"][1].append(frame)
            sprites[file_path.stem]["frames"][-1].append(frame.transformed(QTransform().scale(-1, 1)))
            sprites[file_path.stem]["alpha"][1].append(QBitmap.fromImage(frame.toImage().createAlphaMask()))
            sprites[file_path.stem]["alpha"][-1].append(QBitmap.fromImage(
                frame.transformed(QTransform().scale(-1, 1)).toImage().createAlphaMask())
            )

        sprites[file_path.stem]["duration"] = movie.nextFrameDelay()

    return sprites