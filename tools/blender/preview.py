"""Headless turntable contact sheet, so an asset can be judged by eye before it goes to Roblox.

  Blender -b in.blend --python preview.py -- out.png [--views 4] [--size 512]
                                            [--engine eevee|workbench] [--no-ref] [--in file.fbx]

Renders N views (default 4, rotated 360/N about the vertical axis, camera 22 degrees up) at
size x size px each and tiles them (up to 4 per row) into out.png. A grey 5-stud blocky character
stands to the left for scale unless --no-ref. EEVEE by default (soft sun + sky, contact shadows);
--engine workbench is faster and needs no GPU. Never opens a window.
"""
import math
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import rbxblend as R  # noqa: E402


def _mat(name, hexcol, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    r, g, bb = (R.srgb_to_linear(c) for c in R.hex_rgb(hexcol))
    b.inputs["Base Color"].default_value = (r, g, bb, 1)
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (r, g, bb, 1)
    return m


def _box(name, size, loc, mat):
    me = bpy.data.meshes.new(name)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(loc) @ Matrix.Diagonal((*size, 1)))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def ref_figure(x):
    """Blocky 5.2-stud character (R6 proportions) at x, facing the camera (-Y)."""
    m = _mat("_ref", "B5B5BA")
    parts = [((2, 1, 2), (0, 0, 3)), ((1, 1, 2), (-0.5, 0, 1)), ((1, 1, 2), (0.5, 0, 1)),
             ((1, 1, 2), (-1.5, 0, 3)), ((1, 1, 2), (1.5, 0, 3)), ((1.2, 1.2, 1.2), (0, 0, 4.6))]
    return [_box("_ref", s, (x + l[0], l[1], l[2]), m) for s, l in parts]


def bounds(obs):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in obs:
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi


def setup(obs, engine, size, ref):
    s = bpy.context.scene
    lo, hi = bounds(obs)
    centre = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 0.5)
    extra = []
    if ref:
        rxy = math.hypot((hi.x - lo.x) / 2, (hi.y - lo.y) / 2)   # asset spins, so clear its swept circle
        extra = ref_figure(centre.x - rxy - 2.4)
    alo, ahi = bounds(obs + extra)
    acentre = (alo + ahi) / 2
    aradius = max((ahi - alo).length / 2, 0.5)

    ground = _box("_ground", (aradius * 12, aradius * 12, 0.02), (acentre.x, acentre.y, lo.z - 0.011),
                  _mat("_ground", "D8D6D0", 0.95))
    cam_data = bpy.data.cameras.new("_cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("_cam", cam_data)
    s.collection.objects.link(cam)
    elev = math.radians(22)
    fov = 2 * math.atan(36 / 2 / cam_data.lens)
    dist = aradius / math.sin(fov / 2) * 1.08
    cam.location = acentre + Vector((0, -math.cos(elev), math.sin(elev))) * dist
    cam.rotation_euler = (math.pi / 2 - elev, 0, 0)
    cam_data.clip_end = dist * 10
    s.camera = cam

    sun_data = bpy.data.lights.new("_sun", "SUN")
    sun_data.energy = 3.2
    sun_data.angle = math.radians(8)
    sun = bpy.data.objects.new("_sun", sun_data)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    s.collection.objects.link(sun)

    world = bpy.data.worlds.new("_world")
    s.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.62, 0.70, 0.82, 1)
    bg.inputs["Strength"].default_value = 0.9

    r = s.render
    r.resolution_x = r.resolution_y = size
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    r.film_transparent = False
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"
    if engine == "workbench":
        r.engine = "BLENDER_WORKBENCH"
        sh = s.display.shading
        sh.light = "STUDIO"
        sh.color_type = "TEXTURE"
        sh.show_shadows = True
        sh.show_cavity = True
        sh.background_type = "WORLD"
        s.display.render_aa = "16"
    else:
        r.engine = "BLENDER_EEVEE"
        s.eevee.taa_render_samples = 32
    return centre


def render(obs, out, views=4, size=512, engine="eevee", ref=True):
    """Render a turntable of objects `obs` (already in the scene) to contact sheet `out`."""
    centre = setup(obs, engine, size, ref)
    pivot = bpy.data.objects.new("_pivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    pivot.location = (centre.x, centre.y, 0)
    saved = {}
    for ob in obs:
        saved[ob.name] = (ob.parent, ob.matrix_world.copy())
        ob.parent = pivot
        ob.matrix_parent_inverse = pivot.matrix_world.inverted()
    tmp = tempfile.mkdtemp(prefix="rbxprev")
    frames = []
    for i in range(views):
        pivot.rotation_euler = (0, 0, 2 * math.pi * i / views)
        bpy.context.view_layer.update()
        p = os.path.join(tmp, f"v{i}.png")
        bpy.context.scene.render.filepath = p
        try:
            bpy.ops.render.render(write_still=True)
        except RuntimeError:
            if engine != "workbench":
                return render(obs, out, views, size, "workbench", ref)
            raise
        frames.append(p)
    for ob in obs:
        par, mw = saved[ob.name]
        ob.parent = par
        ob.matrix_world = mw
    _sheet(frames, out, size)
    return out


def _sheet(frames, out, size):
    cols = min(4, len(frames))
    rows = (len(frames) + cols - 1) // cols
    W, H = cols * size, rows * size
    canvas = np.ones((H, W, 4), dtype=np.float32)
    for i, p in enumerate(frames):
        im = bpy.data.images.load(p)
        px = np.empty(size * size * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        px = px.reshape(size, size, 4)            # rows bottom-up
        c, rr = i % cols, i // cols
        y0 = H - (rr + 1) * size                   # canvas is bottom-up too
        canvas[y0:y0 + size, c * size:(c + 1) * size] = px
        bpy.data.images.remove(im)
    sheet = bpy.data.images.new("_sheet", W, H, alpha=True)
    sheet.pixels.foreach_set(canvas.ravel())
    sheet.filepath_raw = os.path.abspath(out)
    sheet.file_format = "PNG"
    sheet.save()


def main():
    a = R.args()
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    opt = lambda f, d=None: a[a.index(f) + 1] if f in a else d   # noqa: E731
    if opt("--in"):
        R.import_any(os.path.abspath(opt("--in")))
    obs = R.mesh_objects()
    if not obs:
        raise SystemExit("no mesh objects to render")
    out = render(obs, os.path.abspath(a[0]), int(opt("--views", 4)), int(opt("--size", 512)),
                 opt("--engine", "eevee"), "--no-ref" not in a)
    print(f"preview -> {out}")


if __name__ == "__main__":
    try:
        main()
    finally:
        R.finish()
