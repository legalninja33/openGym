"""Assemble the frames rendered by render-trx-media.py into the app's exercise media.

    python3 scripts/build-trx-gif.py <frames_dir> frontend/src/assets/trx

Timing copies the bundled dataset's: 12 frames, 1000 ms held on each end position and
100 ms across the five transitions between them, looping forever. Frames are rendered at
2x and downscaled here, which is where the anti-aliasing comes from.

Needs Pillow in the system Python — Blender's bundled interpreter does not ship it, which
is why this is a separate step rather than the tail of the render script.
"""
import sys
from PIL import Image

SIZE = 180
DURATIONS = [1000, 100, 100, 100, 100, 100, 1000, 100, 100, 100, 100, 100]
STEMS = ("9001", "9002")


def build(frames_dir, out_dir, stem):
    frames = [
        Image.open(f"{frames_dir}/{stem}_{i:02d}.png").convert("RGB")
             .resize((SIZE, SIZE), Image.LANCZOS)
        for i in range(len(DURATIONS))
    ]
    gif = f"{out_dir}/{stem}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], loop=0,
                   duration=DURATIONS, optimize=True, disposal=2)
    frames[0].save(f"{out_dir}/{stem}.jpg", quality=92)
    print(f"{stem}: {len(frames)} frames -> {gif}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    for stem in STEMS:
        build(sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"), stem)
