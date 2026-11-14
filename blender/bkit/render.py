"""Rendering: quality presets, stills, turntables, model sheets, PNG-sequence animation,
outlines, contact sheets, and a brightness meter for checking exposure.

    bkit.render.still(os.path.join(out, "hero.png"))                     # EEVEE 'good'
    bkit.render.still(path, engine="CYCLES", quality="hero")              # best, slower
    stats = bkit.render.measure(path)       # {'mean': .., 'clip_white': .., 'clip_black': ..}
"""
import math
import os
import time

import bpy
import numpy as np
from mathutils import Vector

from . import compat, _font
from ._util import as_list, bounds, center_radius, link, mesh_objects, rgba

# Calibrated on a GTX 1050 Ti (Blender 5.3): seconds per 960x960 frame in the manual.
QUALITY = {
    # EEVEE: taa samples, raytracing, fast GI, shadow rays/steps
    "draft": dict(eevee_samples=16, raytrace=False, fast_gi=False, shadow_rays=1, shadow_steps=4,
                  cycles_samples=24),
    "fast":  dict(eevee_samples=24, raytrace=True, fast_gi=True, shadow_rays=1, shadow_steps=6,
                  cycles_samples=48),
    "good":  dict(eevee_samples=64, raytrace=True, fast_gi=True, shadow_rays=2, shadow_steps=8,
                  cycles_samples=96),
    "hero":  dict(eevee_samples=128, raytrace=True, fast_gi=True, shadow_rays=3, shadow_steps=12,
                  cycles_samples=256),
}

RESOLUTIONS = {"vertical": (1080, 1920), "horizontal": (1920, 1080), "square": (1080, 1080)}


def quality(preset="good", scene=None):
    """Apply a quality preset ('draft' | 'fast' | 'good' | 'hero') to EEVEE and Cycles settings."""
    scene = scene or bpy.context.scene
    q = QUALITY[preset]
    ee = scene.eevee
    ee.taa_render_samples = q["eevee_samples"]
    for prop, val in (("use_raytracing", q["raytrace"]), ("use_fast_gi", q["fast_gi"]),
                      ("shadow_ray_count", q["shadow_rays"]), ("shadow_step_count", q["shadow_steps"]),
                      ("use_shadows", True)):
        if hasattr(ee, prop):
            setattr(ee, prop, val)
    if hasattr(ee, "fast_gi_method"):
        compat.set_enum(ee, "fast_gi_method", "GLOBAL_ILLUMINATION")
    if hasattr(ee, "ray_tracing_options"):
        try:
            ee.ray_tracing_options.resolution_scale = "2" if preset in ("draft", "fast") else "1"
        except (TypeError, AttributeError):
            pass
    cy = scene.cycles
    cy.samples = q["cycles_samples"]
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02 if preset in ("good", "hero") else 0.05
    cy.use_denoising = True
    compat.set_enum(cy, "denoiser", "OPENIMAGEDENOISE", "OPTIX")
    cy.max_bounces = 8
    cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 4, 8
    cy.caustics_reflective = cy.caustics_refractive = False
    cy.seed = 1
    cy.use_animated_seed = False
    # Bound sampling on modest shared GPUs; shader compilation/denoising are additional.
    cy.time_limit = 120.0
    scene.render.filter_size = 1.5
    return scene


def _prep(path, resolution, engine, quality_preset, transparent):
    scene = bpy.context.scene
    if engine:
        compat.set_engine(scene, engine)
    if quality_preset:
        quality(quality_preset, scene)
    if resolution:
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.resolution_percentage = 100
    if transparent is not None:
        scene.render.film_transparent = transparent
    s = scene.render.image_settings
    s.file_format = "PNG"
    s.color_mode = "RGBA" if scene.render.film_transparent else "RGB"
    s.color_depth = "8"
    s.compression = 15
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    return scene


def still(path, resolution=None, engine=None, quality=None, transparent=None, camera=None):
    """Render the current frame to a PNG at `path`. resolution e.g. (960, 960); engine 'EEVEE' |
    'CYCLES' | None (keep); quality 'draft' | 'fast' | 'good' | 'hero' | None (keep).
    Returns {'path', 'seconds'}. Always Read/look at the PNG afterwards."""
    scene = _prep(path, resolution, engine, quality, transparent)
    if camera is not None:
        scene.camera = camera
    if scene.camera is None:
        raise RuntimeError("no camera: call bkit.scene.add_camera(subject) first")
    scene.render.filepath = path
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"[bkit] still {os.path.basename(path)} {scene.render.resolution_x}x{scene.render.resolution_y} "
          f"{scene.render.engine} {dt:.1f}s")
    return {"path": path, "seconds": round(dt, 2)}


def animation(out_dir, orientation="vertical", engine="EEVEE", quality="fast", frames=None, prefix="frame_",
              resolution=None, percentage=100):
    """Render the frame range to out_dir/frame_0001.png ... at 1080x1920 ('vertical'), 1920x1080
    ('horizontal') or 1080x1080 ('square'). frames=(start, end) overrides the scene range.
    percentage < 100 renders smaller previews. Returns {'dir', 'frames', 'seconds_per_frame'}.
    Encode on the Mac: ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 16 out.mp4"""
    scene = bpy.context.scene
    _prep(os.path.join(out_dir, "x.png"), resolution or RESOLUTIONS[orientation], engine, quality, None)
    scene.render.resolution_percentage = percentage
    if frames:
        scene.frame_start, scene.frame_end = frames
    scene.render.filepath = os.path.join(out_dir, prefix)
    scene.render.use_file_extension = True
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    n = scene.frame_end - scene.frame_start + 1
    spf = (time.time() - t0) / max(n, 1)
    print(f"[bkit] animation {n} frames {spf:.2f}s/frame -> {out_dir}")
    return {"dir": out_dir, "frames": n, "seconds_per_frame": round(spf, 2)}


# ---------------------------------------------------------------- image helpers (numpy)

def load_pixels(path):
    """PNG -> float32 array (h, w, 4), rows bottom-up (Blender order), display-referred values."""
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)


def save_pixels(px, path):
    """float RGBA array (rows bottom-up) -> 8-bit PNG."""
    h, w = px.shape[:2]
    img = bpy.data.images.new("bkit_tmp_save", w, h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(px, dtype=np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    return path


def _resize(px, w, h):
    sh, sw = px.shape[:2]
    ys = (np.arange(h) * sh / h).astype(int)
    xs = (np.arange(w) * sw / w).astype(int)
    # 2x2 box average on the way down for less aliasing
    if sw >= 2 * w:
        px = (px[:-1:2, :-1:2] + px[1::2, :-1:2] + px[:-1:2, 1::2] + px[1::2, 1::2]) / 4 if sh > 1 else px
        sh, sw = px.shape[:2]
        ys = (np.arange(h) * sh / h).astype(int)
        xs = (np.arange(w) * sw / w).astype(int)
    return px[ys][:, xs]


def measure(path, crop=1.0):
    """Exposure check of a rendered PNG. crop < 1 measures only the centre fraction (the subject).
    Returns {'mean', 'p5', 'p95', 'clip_white' (% of pixels > 0.98), 'clip_black' (% < 0.02),
    'saturation'}. Targets for stylised stills: mean 0.40-0.60, p95 < 0.95, clip_white < 2%."""
    px = load_pixels(path)
    h, w = px.shape[:2]
    if crop < 1:
        ch, cw = int(h * crop), int(w * crop)
        px = px[(h - ch) // 2:(h + ch) // 2, (w - cw) // 2:(w + cw) // 2]
    rgb = px[..., :3]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
    return {"mean": round(float(luma.mean()), 3), "p5": round(float(np.percentile(luma, 5)), 3),
            "p95": round(float(np.percentile(luma, 95)), 3),
            "clip_white": round(float((rgb.max(-1) > 0.98).mean() * 100), 2),
            "clip_black": round(float((luma < 0.02).mean() * 100), 2),
            "saturation": round(float(sat.mean()), 3)}


def contact_sheet(paths, out, cols=None, tile=None, labels=None, title=None, bg=(0.93, 0.92, 0.9), gap=8):
    """Tile images into one PNG. paths: list of PNGs; cols: tiles per row (default ~square);
    tile: (w, h) per tile (default first image size, max 480 wide); labels: one string per tile
    (A-Z 0-9 and - . / : % ( ) + = _ ,); title: a line across the top. Returns out."""
    paths = [p for p in paths if p and os.path.exists(p)]
    if not paths:
        raise ValueError("contact_sheet: no images")
    n = len(paths)
    cols = cols or math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    first = load_pixels(paths[0])
    if tile is None:
        fh, fw = first.shape[:2]
        tw = min(fw, 480)
        tile = (tw, int(fh * tw / fw))
    tw, th = tile
    lab_h = 22 if labels else 0
    top = 34 if title else 0
    W = cols * tw + (cols + 1) * gap
    H = top + rows * (th + lab_h) + (rows + 1) * gap
    sheet = np.ones((H, W, 4), dtype=np.float32)
    sheet[..., :3] = bg
    for i, p in enumerate(paths):
        px = first if i == 0 else load_pixels(p)
        px = _resize(px, tw, th)
        if px.shape[2] == 4:
            a = px[..., 3:4]
            px = np.concatenate([px[..., :3] * a + np.array(bg, dtype=np.float32) * (1 - a), np.ones_like(a)], -1)
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y_top = top + gap + r * (th + lab_h + gap)
        y0 = H - (y_top + th)
        sheet[y0:y0 + th, x:x + tw] = px
        if labels and i < len(labels) and labels[i]:
            _font.draw(sheet, labels[i], x + 2, y_top + th + 5, scale=2)
    if title:
        _font.draw(sheet, title, gap, 10, scale=2)
    save_pixels(sheet, out)
    return out


# ---------------------------------------------------------------- turntable / model sheet

def _subject_roots(objs):
    names = {o.name for o in objs}
    return [o for o in objs if o.parent is None or o.parent.name not in names]


def turntable(subject, out_dir, angles=8, elevation=18.0, lens=70.0, resolution=(480, 480), sheet=True,
              engine=None, quality=None, margin=1.15):
    """Spin the subject (not the camera, so the lighting stays put) and render `angles` stills
    plus a contact sheet out_dir/turntable.png. Uses the scene camera (creates one if missing);
    lights stay where they are. Returns the list of PNG paths (sheet last)."""
    from . import scene as _scene
    objs = as_list(subject)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = resolution
    sc.render.resolution_percentage = 100
    c, r = center_radius(objs)
    lo, _ = bounds(objs)
    piv = link(bpy.data.objects.new("bkit_turntable", None))
    piv.location = (c.x, c.y, lo.z)
    bpy.context.view_layer.update()
    roots = _subject_roots(objs)
    saved = [(o, o.parent, o.matrix_world.copy()) for o in roots]
    for o in roots:
        mw = o.matrix_world.copy()
        o.parent = piv
        o.matrix_parent_inverse = piv.matrix_world.inverted()
        o.matrix_world = mw
    cam = sc.camera or _scene.add_camera(objs, 0, elevation, lens, margin)
    # one distance for all angles: the largest needed
    dists = []
    for k in range(angles):
        piv.rotation_euler.z = math.radians(360 * k / angles)
        bpy.context.view_layer.update()
        _scene.aim(cam, objs, 0, elevation, margin)
        dists.append((cam.location - Vector(cam["bkit_target"])).length)
    piv.rotation_euler.z = 0
    bpy.context.view_layer.update()
    _scene.aim(cam, objs, 0, elevation, margin, distance=max(dists))
    paths = []
    for k in range(angles):
        piv.rotation_euler.z = math.radians(360 * k / angles)
        p = os.path.join(out_dir, f"turn_{k:02d}.png")
        still(p, resolution, engine, quality)
        paths.append(p)
    if sheet:
        paths.append(contact_sheet(paths, os.path.join(out_dir, "turntable.png"), cols=min(angles, 4),
                                   labels=[f"{int(360 * k / angles)}" for k in range(angles)]))
    for o, parent, mw in saved:
        o.parent = parent
        o.matrix_world = mw
    bpy.data.objects.remove(piv)
    return paths


def _workbench(scene, light, color_type, single=(0.0, 0.0, 0.0), bg=(1, 1, 1)):
    compat.set_engine(scene, "WORKBENCH")
    sh = scene.display.shading
    sh.light = light
    sh.color_type = color_type
    sh.single_color = single
    sh.show_shadows = False
    sh.show_cavity = False
    sh.background_type = "WORLD"
    if hasattr(sh, "show_object_outline"):
        sh.show_object_outline = False
    scene.display.render_aa = "8"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = bg
    scene.render.film_transparent = False


def model_sheet(subject, path, tile=(480, 480), engine=None, quality="fast", title=None, wire=True):
    """One PNG with FRONT, SIDE, BACK 3/4, 3/4, TOP (ortho/perspective beauty renders in the current
    lighting), SILHOUETTE (black on white) and WIRE (clay + wireframe with the triangle count).
    The judge's sheet: name the object from the silhouette, check bevels and topology on the wire.
    Returns path."""
    from . import scene as _scene
    objs = as_list(subject)
    meshes = mesh_objects(objs)
    sc = bpy.context.scene
    keep = (sc.render.engine, sc.camera, sc.render.film_transparent, sc.render.resolution_x, sc.render.resolution_y)
    sc.render.resolution_x, sc.render.resolution_y = tile
    sc.render.resolution_percentage = 100
    tmp = os.path.join(os.path.dirname(os.path.abspath(path)), "_sheet_tiles")
    os.makedirs(tmp, exist_ok=True)
    cam = _scene.add_camera(objs, 0, 0, 85, 1.1, name="bkit_sheet_cam", set_active=True)
    views = [("FRONT", 0, 0, True), ("SIDE", 90, 0, True), ("3/4", 35, 22, False),
             ("BACK 3/4", 215, 22, False), ("TOP", 0, 89.9, True)]
    paths, labels = [], []
    hidden = []
    names = {o.name for o in meshes}
    for ob in sc.objects:
        if ob.type == "MESH" and ob.name not in names and not ob.hide_render:
            ob.hide_render = True
            hidden.append(ob)
    sc.render.film_transparent = True
    for label, az, el, ortho in views:
        cam.data.type = "PERSP"
        _scene.aim(cam, objs, az, el, 1.1, ortho=ortho)
        p = os.path.join(tmp, f"{label.replace('/', '').replace(' ', '_').lower()}.png")
        still(p, tile, keep[0] if engine is None else engine, quality)
        paths.append(p)
        labels.append(label)
    # silhouette and wire: only the subject is visible
    cam.data.type = "PERSP"
    _scene.aim(cam, objs, 35, 22, 1.1)
    world_col = tuple(sc.world.color) if sc.world else None
    _workbench(sc, "FLAT", "SINGLE", (0.02, 0.02, 0.02))
    p = os.path.join(tmp, "silhouette.png")
    still(p, tile, None, None)
    paths.append(p)
    labels.append("SILHOUETTE")
    tris = 0
    if wire:
        dg = bpy.context.evaluated_depsgraph_get()
        _, r = center_radius(objs)
        dups = []
        for o in meshes:
            ev = o.evaluated_get(dg)
            tris += sum(len(pl.vertices) - 2 for pl in ev.data.polygons)
            d = o.copy()
            d.data = bpy.data.meshes.new_from_object(ev)
            d.modifiers.clear()
            d.parent = None
            d.matrix_world = o.matrix_world
            link(d)
            m = d.modifiers.new("wire", "WIREFRAME")
            m.thickness = r * 0.006
            m.use_replace = True
            m.use_even_offset = True
            d.color = (0.08, 0.08, 0.1, 1)
            dups.append(d)
        cols = {}
        for o in meshes:
            cols[o.name] = tuple(o.color)
            o.color = (0.78, 0.76, 0.73, 1)
        _workbench(sc, "STUDIO", "OBJECT")
        p = os.path.join(tmp, "wire.png")
        still(p, tile, None, None)
        paths.append(p)
        labels.append(f"WIRE {tris} TRIS")
        for d in dups:
            me = d.data
            bpy.data.objects.remove(d)
            bpy.data.meshes.remove(me)
        for o in meshes:
            o.color = cols[o.name]
    for o in hidden:
        o.hide_render = False
    if world_col and sc.world:
        sc.world.color = world_col
    sc.render.engine = keep[0]
    sc.camera = keep[1]
    sc.render.film_transparent = keep[2]
    sc.render.resolution_x, sc.render.resolution_y = keep[3], keep[4]
    bpy.data.objects.remove(cam)
    contact_sheet(paths, path, cols=4, tile=tile, labels=labels, title=title)
    return path


# ---------------------------------------------------------------- outlines

def outline(objs, thickness=None, color="#1E1E24", method="hull"):
    """Cartoon outlines. method 'hull' (inverted hull: a Solidify shell with flipped normals; works in
    EEVEE and Cycles; remove its modifier before mesh export) or 'freestyle' (render-time
    lines, all objects). thickness: hull width in scene units (default 1.2% of the object size);
    for freestyle it is the line width in pixels (default 2.0). Returns the outline material or None."""
    sc = bpy.context.scene
    if method == "freestyle":
        sc.render.use_freestyle = True
        sc.render.line_thickness_mode = "ABSOLUTE"
        sc.render.line_thickness = thickness or 2.0
        vl = bpy.context.view_layer
        vl.use_freestyle = True
        fs = vl.freestyle_settings
        ls = fs.linesets[0] if fs.linesets else fs.linesets.new("bkit")
        ls.select_by_visibility = True
        ls.select_silhouette = ls.select_border = ls.select_crease = True
        fs.crease_angle = math.radians(120)
        ls.linestyle.color = rgba(color)[:3]
        ls.linestyle.thickness = thickness or 2.0
        return None
    mat = bpy.data.materials.get("bkit_outline")
    if mat is None:
        mat = bpy.data.materials.new("bkit_outline")
        nt = compat.material_nodes(mat)
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = rgba(color)
        em.inputs["Strength"].default_value = 1.0
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
        nt.links.new(em.outputs[0], mix.inputs[1])
        nt.links.new(tr.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        mat.use_backface_culling = True
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "DITHERED"
    for o in mesh_objects(objs):
        size = max(o.dimensions) or 1.0
        if mat.name not in o.data.materials:
            o.data.materials.append(mat)
        m = o.modifiers.get("bkit_outline") or o.modifiers.new("bkit_outline", "SOLIDIFY")
        m.thickness = thickness or size * 0.012
        m.offset = 1.0
        m.use_flip_normals = True
        m.use_rim = False
        m.material_offset = len(o.data.materials) - 1
        m.use_quality_normals = True
    return mat
