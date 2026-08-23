"""Generate 180x180 exercise animations for the two TRX entries in exercises-extra.js.

Matches the bundled dataset's format so the app treats them like any other exercise:
180x180, 12 frames, white background, 1000 ms held at each end position and 100 ms
across the five transition frames in between.

The figure is posed kinematically rather than drawn frame by frame: the two end
positions are defined as joint coordinates, every in-between frame interpolates with a
cosine ease, and the elbow/knee is solved by two-link IK so the bend stays anatomical.
"""
import math
from PIL import Image, ImageDraw

W = H = 180
BG = (255, 255, 255)
OUTLINE = (40, 40, 40)
FILL = (208, 208, 208)
GEAR = (120, 120, 120)
PROP_LINE = (150, 150, 150)
PROP_FILL = (238, 238, 238)
DURATIONS = [1000, 100, 100, 100, 100, 100, 1000, 100, 100, 100, 100, 100]
FLOOR_Y = 168
BAR_Y = 12


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def along(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def ik(root, end, l1, l2, sign):
    """Middle joint of a two-link chain: circle-circle intersection, `sign` picks the bend."""
    dx, dy = end[0] - root[0], end[1] - root[1]
    d = math.hypot(dx, dy)
    d = max(abs(l1 - l2) + 0.01, min(l1 + l2 - 0.01, d))
    ux, uy = dx / max(d, 1e-6), dy / max(d, 1e-6)
    x = (d * d + l1 * l1 - l2 * l2) / (2 * d)
    y = math.sqrt(max(0.0, l1 * l1 - x * x)) * sign
    return (root[0] + ux * x - uy * y, root[1] + uy * x + ux * y)


def limb(d, p1, p2, w):
    d.line([p1, p2], fill=OUTLINE, width=w + 4)
    d.line([p1, p2], fill=FILL, width=w)


def joint(d, p, r):
    d.ellipse([p[0] - r - 2, p[1] - r - 2, p[0] + r + 2, p[1] + r + 2], fill=OUTLINE)
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=FILL)


def head(d, c, r=9):
    d.ellipse([c[0] - r - 2, c[1] - r - 2, c[0] + r + 2, c[1] + r + 2], fill=OUTLINE)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=FILL)


def strap(d, anchor, handle, cradle=False):
    d.line([anchor, handle], fill=GEAR, width=2)
    if cradle:
        d.arc([handle[0] - 8, handle[1] - 6, handle[0] + 8, handle[1] + 10], 200, 340, fill=GEAR, width=3)
    else:
        d.rounded_rectangle([handle[0] - 7, handle[1] - 3, handle[0] + 7, handle[1] + 3], 3,
                            fill=PROP_FILL, outline=GEAR, width=2)


def bar_and_floor(d):
    d.line([(16, BAR_Y), (164, BAR_Y)], fill=GEAR, width=4)
    d.line([(10, FLOOR_Y), (170, FLOOR_Y)], fill=PROP_LINE, width=3)


# ---------------------------------------------------------------- push-up
# Body is rigid and pivots about the ankles on the bench; the hands stay on the
# handles, so the elbow angle falls out of the shoulder travel.
PU_ANKLE = (46.0, 110.0)
PU_BODY = 88.0
PU_ANGLE = (16.0, 27.0)       # degrees, top -> bottom (shoulder drops toward the handles)
PU_HAND = (118.0, 162.0)
PU_ANCHOR = (118.0, BAR_Y)
PU_UPPER, PU_FORE = 16.0, 16.0


def pushup(t):
    ang = math.radians(PU_ANGLE[0] + (PU_ANGLE[1] - PU_ANGLE[0]) * t)
    ca, sa = math.cos(ang), math.sin(ang)
    sh = (PU_ANKLE[0] + PU_BODY * ca, PU_ANKLE[1] + PU_BODY * sa)
    hip = along(PU_ANKLE, sh, 0.45)
    knee = along(PU_ANKLE, sh, 0.22)
    elbow = ik(sh, PU_HAND, PU_UPPER, PU_FORE, 1)
    hd = (sh[0] + ca * 19 + sa * 5, sh[1] + sa * 19 - ca * 5)
    return sh, hip, knee, elbow, hd


def draw_pushup(t):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    bar_and_floor(d)
    d.rounded_rectangle([8, 112, 52, 166], 3, fill=PROP_FILL, outline=PROP_LINE, width=3)
    strap(d, PU_ANCHOR, PU_HAND)
    sh, hip, knee, elbow, hd = pushup(t)
    limb(d, (32.0, 112.0), PU_ANKLE, 6)
    limb(d, PU_ANKLE, knee, 7)
    limb(d, knee, hip, 8)
    limb(d, hip, sh, 11)
    limb(d, sh, hd, 8)
    head(d, hd, 8)
    limb(d, sh, elbow, 7)
    limb(d, elbow, PU_HAND, 6)
    joint(d, sh, 4)
    joint(d, hip, 4)
    joint(d, elbow, 3)
    return im


# ---------------------------------------------------------------- leg curl
# Shoulders stay on the floor, the hips ride up as the knees fold, and the ankles
# swing on the strap: they stay at cradle height while travelling towards the hips.
LC_SHOULDER = (56.0, 160.0)
LC_HIP = ((96.0, 138.0), (96.0, 127.0))
LC_ANKLE = ((150.0, 120.0), (119.0, 120.0))
LC_ANCHOR = (150.0, BAR_Y)
LC_THIGH, LC_SHIN = 30.0, 30.0


def draw_legcurl(t):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    bar_and_floor(d)
    hip = lerp(LC_HIP[0], LC_HIP[1], t)
    ankle = lerp(LC_ANKLE[0], LC_ANKLE[1], t)
    knee = ik(hip, ankle, LC_THIGH, LC_SHIN, -1)
    strap(d, LC_ANCHOR, ankle, cradle=True)
    limb(d, LC_SHOULDER, (86.0, 164.0), 6)          # arm resting on the floor
    limb(d, LC_SHOULDER, hip, 12)
    limb(d, hip, knee, 9)
    limb(d, knee, ankle, 7)
    limb(d, LC_SHOULDER, (40.0, 157.0), 8)          # neck
    head(d, (34.0, 156.0))
    joint(d, hip, 4)
    joint(d, knee, 4)
    return im


def build(draw_fn, stem, out_gif, out_jpg):
    frames = []
    for i in range(12):
        t = i / 6 if i <= 6 else (12 - i) / 6
        frames.append(draw_fn(ease(t)))
    frames[0].save(out_gif, save_all=True, append_images=frames[1:], loop=0,
                   duration=DURATIONS, optimize=True, disposal=2)
    frames[0].convert("RGB").save(out_jpg, quality=90)
    g = Image.open(out_gif)
    print(f"{stem}: gif {g.size} {g.n_frames} frames | jpg {Image.open(out_jpg).size}")


if __name__ == "__main__":
    import sys
    out = sys.argv[1].rstrip("/")
    build(draw_pushup, "9001 TRX push-up", f"{out}/9001.gif", f"{out}/9001.jpg")
    build(draw_legcurl, "9002 TRX leg curl", f"{out}/9002.gif", f"{out}/9002.jpg")
