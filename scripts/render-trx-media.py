"""Render the two TRX exercises as 3D figures, in the bundled dataset's visual language.

Run headless (Blender 4.2+; tested on 5.2):
    blender --background --python scripts/render-trx-media.py -- <out_dir>
then assemble the GIFs with:
    python3 scripts/build-trx-gif.py <out_dir> frontend/src/assets/trx

Builds a mannequin out of tapered limb solids placed at joint coordinates, poses it across
12 frames, and renders each with Freestyle outlines over flat toon shading — so the result
reads like the dataset's rendered figures rather than a line drawing. Frames land as PNGs;
build-trx-gif.py assembles the GIF.

Coordinates are the same ones the 2D generator uses, mapped from its 180x180 canvas onto
the XZ plane, so poses stay in sync between the two implementations.
"""
import bpy
import math
import os
import sys

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS else "/tmp/trx"
RES = 360                      # rendered at 2x, downscaled to 180 when the GIF is built

# --- canvas mapping: 180x180 pixels -> metres, y grows downward on the canvas ------------
SCALE = 1.0 / 18.0


def P(x, y, depth=0.0):
    return (x * SCALE, depth, (180.0 - y) * SCALE)


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def along(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def ik(root, end, l1, l2, sign):
    dx, dy = end[0] - root[0], end[1] - root[1]
    d = math.hypot(dx, dy)
    d = max(abs(l1 - l2) + 0.01, min(l1 + l2 - 0.01, d))
    ux, uy = dx / max(d, 1e-6), dy / max(d, 1e-6)
    x = (d * d + l1 * l1 - l2 * l2) / (2 * d)
    y = math.sqrt(max(0.0, l1 * l1 - x * x)) * sign
    return (root[0] + ux * x - uy * y, root[1] + uy * x + ux * y)


# --- scene helpers -----------------------------------------------------------------------
def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for b in list(block):
            block.remove(b)


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.1
    return m


def limb(p1, p2, r1, r2, material, depth1=0.0, depth2=0.0):
    """A tapered solid between two joints, capped with spheres so the joint stays round."""
    a, b = P(*p1, depth1), P(*p2, depth2)
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-6
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, radius1=r1 * SCALE, radius2=r2 * SCALE, depth=length,
        location=((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2))
    obj = bpy.context.object
    obj.rotation_euler = (math.acos(max(-1.0, min(1.0, dz / length))),
                          0.0, math.atan2(dy, dx) + math.pi / 2)
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    for pt, r in ((a, r1), (b, r2)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12,
                                             radius=r * SCALE, location=pt)
        bpy.context.object.data.materials.append(material)
        bpy.ops.object.shade_smooth()


def sphere(p, r, material, depth=0.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=16,
                                         radius=r * SCALE, location=P(*p, depth))
    bpy.context.object.data.materials.append(material)
    bpy.ops.object.shade_smooth()


def box(x0, y0, x1, y1, material, depth=0.0, thickness=26.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=P((x0 + x1) / 2, (y0 + y1) / 2, depth))
    o = bpy.context.object
    o.scale = ((x1 - x0) * SCALE, thickness * SCALE, (y1 - y0) * SCALE)
    o.data.materials.append(material)


def strap(p1, p2, material, r=0.9, depth=-13.0):
    limb(p1, p2, r, r, material, depth, depth)


# --- poses -------------------------------------------------------------------------------
PU_ANKLE, PU_BODY, PU_HAND = (46.0, 110.0), 88.0, (118.0, 162.0)
PU_ANGLE = (16.0, 27.0)
LC_SHOULDER = (56.0, 160.0)
LC_HIP = ((96.0, 138.0), (96.0, 127.0))
LC_ANKLE = ((150.0, 120.0), (119.0, 120.0))


def build_pushup(t, skin, gear, prop):
    box(8, 112, 52, 166, prop, 0.0, 34.0)
    strap((118.0, 12.0), PU_HAND, gear)
    limb((PU_HAND[0] - 7, PU_HAND[1]), (PU_HAND[0] + 7, PU_HAND[1]), 2.4, 2.4, gear, -13, -13)
    ang = math.radians(PU_ANGLE[0] + (PU_ANGLE[1] - PU_ANGLE[0]) * t)
    ca, sa = math.cos(ang), math.sin(ang)
    sh = (PU_ANKLE[0] + PU_BODY * ca, PU_ANKLE[1] + PU_BODY * sa)
    hip, knee = along(PU_ANKLE, sh, 0.45), along(PU_ANKLE, sh, 0.22)
    elbow = ik(sh, PU_HAND, 16.0, 16.0, 1)
    hd = (sh[0] + ca * 19 + sa * 5, sh[1] + sa * 19 - ca * 5)
    limb((PU_ANKLE[0] - 14, PU_ANKLE[1] + 2), PU_ANKLE, 2.8, 3.6, skin, 5, 5)
    limb(PU_ANKLE, knee, 3.6, 5.4, skin, 5, 3)
    limb(knee, hip, 5.4, 6.8, skin, 3, 0)
    limb(hip, sh, 7.0, 7.8, skin)
    limb(sh, hd, 3.6, 3.6, skin)
    sphere(hd, 8.6, skin)
    limb(sh, elbow, 4.6, 3.6, skin, -6, -8)
    limb(elbow, PU_HAND, 3.6, 2.8, skin, -8, -8)


def build_legcurl(t, skin, gear, prop):
    hip = lerp(LC_HIP[0], LC_HIP[1], t)
    ankle = lerp(LC_ANKLE[0], LC_ANKLE[1], t)
    knee = ik(hip, ankle, 30.0, 30.0, -1)
    strap((150.0, 12.0), ankle, gear)
    limb((ankle[0] - 6, ankle[1] + 4), (ankle[0] + 6, ankle[1] + 4), 2.2, 2.2, gear, -13, -13)
    limb(LC_SHOULDER, (86.0, 165.0), 3.8, 2.8, skin, -7, -7)
    limb(LC_SHOULDER, hip, 7.8, 7.0, skin)
    limb(hip, knee, 6.8, 5.2, skin, -4, -6)
    limb(knee, ankle, 5.2, 3.6, skin, -6, -6)
    limb(LC_SHOULDER, (41.0, 157.0), 3.8, 3.6, skin)
    sphere((34.0, 156.0), 8.6, skin)


# --- render ------------------------------------------------------------------------------
def setup_world():
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE"
    scn.render.resolution_x = scn.render.resolution_y = RES
    scn.render.film_transparent = False
    # Without this the default view transform tone-maps white down to mid grey, so the
    # dataset's flat white ground would come out as a grey card.
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "None"
    scn.world = bpy.data.worlds.new("W")
    scn.world.use_nodes = True
    scn.world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    scn.world.node_tree.nodes["Background"].inputs[1].default_value = 1.05

    bpy.ops.object.camera_add(location=(5.0, -14.0, 5.0))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 10.0
    cam.rotation_euler = (math.pi / 2, 0, 0)
    scn.camera = cam

    bpy.ops.object.light_add(type="SUN", location=(-4, -10, 12))
    bpy.context.object.data.energy = 2.6
    bpy.context.object.rotation_euler = (math.radians(52), 0, math.radians(28))

    scn.render.use_freestyle = True
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.as_render_pass = False
    lineset = fs.linesets.new("outline") if not fs.linesets else fs.linesets[0]
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = True
    ls = bpy.data.linestyles.new("thick")
    lineset.linestyle = ls
    ls.color = (0.16, 0.16, 0.16)
    ls.thickness = 2.6


def render_set(builder, stem):
    os.makedirs(OUT, exist_ok=True)
    for i in range(12):
        t = ease(i / 6 if i <= 6 else (12 - i) / 6)
        clear()
        setup_world()
        skin = mat("skin", (0.80, 0.80, 0.80))
        gear = mat("gear", (0.42, 0.42, 0.42))
        prop = mat("prop", (0.90, 0.90, 0.90))
        box(10, 168, 170, 171, prop, 0.0, 40.0)          # floor
        box(16, 11, 164, 14, gear, -13.0, 6.0)           # bar
        builder(t, skin, gear, prop)
        bpy.context.scene.render.filepath = f"{OUT}/{stem}_{i:02d}.png"
        bpy.ops.render.render(write_still=True)
    print(f"OK {stem}: 12 frames -> {OUT}")


render_set(build_pushup, "9001")
render_set(build_legcurl, "9002")
