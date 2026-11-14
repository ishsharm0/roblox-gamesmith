"""Scene setup: clean scene, units, colour management, world (colour, gradient, sky, HDRI),
backdrops (cyclorama, ground, shadow catcher) and cameras.

Typical start of every script:
    import bkit
    scene = bkit.scene.new_scene(look="toy")
    ...build...
    cam = bkit.scene.add_camera(subject, azimuth=35, elevation=22, lens=70)
"""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import compat
from ._util import as_list, bounds, center_radius, link, look_at, rgba, spherical

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# view transform, look, exposure, gamma per preset; first accepted name wins.
LOOKS = {
    # Vivid toy colours that still roll off gracefully in highlights.
    "toy": (("AgX",), ("AgX - Punchy", "Punchy"), 0.0),
    # Palette-accurate: what you author is what you get (matches three.js NeutralToneMapping).
    "neutral": (("Khronos PBR Neutral", "Standard"), ("None",), 0.0),
    # Realistic product/archviz: wide dynamic range, desaturated highlights.
    "product": (("AgX",), ("AgX - Base Contrast", "None"), 0.0),
    # Exact sRGB, no tone mapping (UI-like flat colour, sprites). Clips harshly with bright lights.
    "flat": (("Standard",), ("None",), 0.0),
}


def clear():
    """Remove every object and data-block from the current file in place.
    (read_factory_settings from inside a script crashes some 5.x builds, so this is used instead.)"""
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights,
                 bpy.data.curves, bpy.data.armatures, bpy.data.actions, bpy.data.node_groups, bpy.data.textures):
        for block in list(coll):
            coll.remove(block)
    for img in list(bpy.data.images):
        if img.type != "RENDER_RESULT":
            bpy.data.images.remove(img)
    for w in list(bpy.data.worlds):
        bpy.data.worlds.remove(w)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    bpy.context.view_layer.update()


def new_scene(units="studs", look="neutral", engine="EEVEE", fps=30, resolution=(960, 960)):
    """Start clean: remove everything, set units, colour look, engine, fps and resolution.
    units: 'studs' (1 BU = 1 Roblox stud; character ~5 tall) or 'metric' (1 BU = 1 m).
    look: 'neutral' (default: authored colours stay vivid) | 'toy' | 'product' | 'flat' (see set_look). engine: 'EEVEE' | 'CYCLES'.
    Also sets a neutral grey world so nothing renders black. Returns the scene."""
    clear()
    scene = bpy.context.scene
    us = scene.unit_settings
    if units == "metric":
        us.system, us.scale_length = "METRIC", 1.0
    else:
        us.system, us.scale_length = "NONE", 1.0
    scene.render.fps = fps
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.use_freestyle = False
    scene.frame_start, scene.frame_end = 1, fps * 3
    set_look(look, scene)
    compat.set_engine(scene, engine)
    from . import render
    render.quality("good", scene)
    world_color("#B8BCC4", 0.4)
    return scene


def set_look(preset="toy", scene=None, exposure=None):
    """Colour management preset: 'toy' (AgX Punchy: vivid, highlights roll off), 'neutral'
    (Khronos PBR Neutral: authored colours preserved, matches three.js Neutral), 'product'
    (AgX Base Contrast), 'flat' (Standard: raw sRGB). Returns (view_transform, look) actually set."""
    scene = scene or bpy.context.scene
    views, looks, exp = LOOKS[preset]
    vs = scene.view_settings
    scene.display_settings.display_device = compat.set_enum(scene.display_settings, "display_device", "sRGB") or scene.display_settings.display_device
    v = compat.set_enum(vs, "view_transform", *views)
    lk = compat.set_enum(vs, "look", *looks, "None")
    vs.exposure = exp if exposure is None else exposure
    vs.gamma = 1.0
    return v, lk


# ---------------------------------------------------------------- world

def _world():
    w = bpy.context.scene.world
    if w is None:
        w = bpy.data.worlds.new("World")
        bpy.context.scene.world = w
    nt = compat.world_nodes(w)
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    return w, nt, out


def world_color(color="#B8BCC4", strength=0.4):
    """Uniform world colour: soft ambient fill and plain background. Returns the World."""
    w, nt, out = _world()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = rgba(color)
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    w.color = rgba(color)[:3]
    return w


def world_gradient(top="#9CC9F0", bottom="#F2E8D5", strength=0.8, horizon=0.0):
    """Sky-to-ground gradient world (cheap outdoor ambient; bottom colour bounces up). Returns World."""
    w, nt, out = _world()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.5 + horizon / 2 - 0.05
    ramp.color_ramp.elements[0].color = rgba(bottom)
    ramp.color_ramp.elements[1].position = 0.5 + horizon / 2 + 0.35
    ramp.color_ramp.elements[1].color = rgba(top)
    mapr = nt.nodes.new("ShaderNodeMapRange")
    mapr.inputs["From Min"].default_value = -1.0
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mapr.inputs["Value"])
    nt.links.new(mapr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    return w


def world_sky(sun_elevation=35.0, sun_rotation=30.0, strength=0.35, sun_disc=False):
    """Physical sky texture (Nishita / multiple scattering). Pair with lighting.rig('sunny_outdoor').
    strength ~0.3 for fill under a separate sun lamp. Returns the World."""
    w, nt, out = _world()
    sky = nt.nodes.new("ShaderNodeTexSky")
    compat.set_enum(sky, "sky_type", "MULTIPLE_SCATTERING", "NISHITA", "HOSEK_WILKIE")
    for prop, val in (("sun_elevation", math.radians(sun_elevation)), ("sun_rotation", math.radians(sun_rotation)),
                      ("sun_disc", sun_disc)):
        if hasattr(sky, prop):
            setattr(sky, prop, val)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    return w


def world_hdri(path=None, strength=1.0, rotation=0.0, background=None, background_strength=1.0):
    """Light the scene with an equirectangular HDRI. path=None fetches/caches the CC0 studio HDRI
    studio_small_08 (Poly Haven). background: a colour spec to show instead of the HDRI
    to the camera (keeps the lighting and reflections, hides the photo). Returns the World."""
    if path is None:
        from .assets import fetch
        path = str(fetch("studio_small_08"))
    path = str(path)
    w, nt, out = _world()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(rotation))
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(path, check_existing=True)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    if background is None:
        nt.links.new(bg.outputs[0], out.inputs["Surface"])
        return w
    lp = nt.nodes.new("ShaderNodeLightPath")
    bg2 = nt.nodes.new("ShaderNodeBackground")
    bg2.inputs["Color"].default_value = rgba(background)
    bg2.inputs["Strength"].default_value = background_strength
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return w


# ---------------------------------------------------------------- backdrops

def cyclorama(width=None, depth=None, height=None, radius=None, color="#D9D4CC", subject=None,
              roughness=0.9, name="Cyclorama"):
    """Seamless studio backdrop: a floor that curves up into a back wall (no visible horizon).
    Sized from `subject` (objects) when given: about 8x its radius wide, floor at its lowest point.
    Colour value 0.6-0.85 reads as a clean studio; darker for hero_rim. Returns the object."""
    z0 = 0.0
    if subject is not None:
        c, r = center_radius(subject)
        lo, _ = bounds(subject, precise=True)
        z0 = lo.z
        width = width or r * 16
        depth = depth or r * 8
        height = height or r * 8
        radius = radius or r * 2.5
        cx, cy = c.x, c.y
    else:
        width, depth, height, radius = width or 20, depth or 10, height or 10, radius or 3
        cx = cy = 0.0
    back = cy + depth * 0.5
    prof = [(cy - depth, z0), (back - radius, z0)]
    for i in range(1, 12):
        a = (math.pi / 2) * i / 12
        prof.append((back - radius + math.sin(a) * radius, z0 + radius - math.cos(a) * radius))
    prof += [(back, z0 + radius), (back, z0 + height)]
    bm = bmesh.new()
    left = [bm.verts.new((cx - width / 2, y, z)) for y, z in prof]
    right = [bm.verts.new((cx + width / 2, y, z)) for y, z in prof]
    for i in range(len(prof) - 1):
        bm.faces.new((left[i], left[i + 1], right[i + 1], right[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < -0.01 or f.normal.y > 0.01:
            f.normal_flip()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    compat.shade_smooth(ob)
    from . import materials
    materials.assign(ob, materials.matte(color, name=f"{name}_mat", roughness=roughness))
    return ob


def ground(size=40.0, color="#C8C2B6", z=0.0, name="Ground", roughness=0.95):
    """A flat square ground plane at height z. Returns the object."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2, matrix=Matrix.Translation((0, 0, z)))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    from . import materials
    materials.assign(ob, materials.matte(color, name=f"{name}_mat", roughness=roughness))
    return ob


def shadow_catcher(size=40.0, z=0.0):
    """Invisible ground that only keeps shadows, over a transparent film (Cycles only; EEVEE renders
    it as a plain ground). Composite the PNG over any background. Returns the object."""
    ob = ground(size, "#808080", z, name="ShadowCatcher")
    if hasattr(ob, "is_shadow_catcher"):
        ob.is_shadow_catcher = True
    bpy.context.scene.render.film_transparent = True
    return ob


# ---------------------------------------------------------------- camera

def add_camera(subject=None, azimuth=30.0, elevation=20.0, lens=70.0, margin=1.12, target=None,
               distance=None, name="Camera", ortho=False, set_active=True):
    """Add a camera aimed at `subject` (objects) or `target` (point), framing it automatically.
    azimuth: 0 = front (-Y), 90 = right side, 180 = back; elevation: degrees above horizon.
    lens (mm, 36 mm sensor): 35-50 environments, 70-100 products/characters (less distortion).
    margin: 1.0 = touching the frame edges; 1.1-1.25 normal. Returns the camera object."""
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.sensor_width = 36
    cam_data.clip_start = 0.01
    cam_data.clip_end = 10000
    cam = link(bpy.data.objects.new(name, cam_data))
    if set_active:
        bpy.context.scene.camera = cam
    aim(cam, subject, azimuth, elevation, margin=margin, target=target, distance=distance, ortho=ortho)
    return cam


def aim(cam, subject=None, azimuth=30.0, elevation=20.0, margin=1.12, target=None, distance=None, ortho=False):
    """Re-place an existing camera around subject/target (same arguments as add_camera).
    Framing is tight: the subject's bounding-box corners are fitted to the frame, times margin."""
    scene = bpy.context.scene
    if subject is not None:
        lo, hi = bounds(subject)
        c = (lo + hi) / 2
        corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    else:
        c = Vector(target or (0, 0, 0))
        corners = [c + Vector((x, y, z)) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    if target is not None:
        c = Vector(target)
    view = (c - spherical(c, 1.0, azimuth, elevation)).normalized()       # camera looks along this
    right = Vector((1, 0, 0)) if abs(view.z) > .999999 else view.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(view)
    aspect = (scene.render.resolution_x * scene.render.pixel_aspect_x /
              (scene.render.resolution_y * scene.render.pixel_aspect_y))
    t = 18 / cam.data.lens                     # tan(half fov) on the sensor's fitted (larger) axis
    tx, ty = (t, t / aspect) if aspect >= 1 else (t * aspect, t)
    need = 0.0
    ext = 0.0
    for p in corners:
        v = p - c
        x, y, z = v.dot(right), v.dot(up), v.dot(view)
        need = max(need, -z + abs(x) * margin / tx, -z + abs(y) * margin / ty)
        ext = max(ext, abs(x) * margin / tx * t, abs(y) * margin / ty * t)
    d = distance or max(need, 1e-3)
    cam.location = c - view * d
    look_at(cam, c)
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = 2 * ext
    cam["bkit_target"] = list(c)
    return cam


def dof(cam, focus=None, fstop=2.8):
    """Depth of field: focus on an object (or point/distance) at f-stop `fstop` (lower = blurrier;
    2-4 for toys, which reads as miniature). Returns the camera."""
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = fstop
    if isinstance(focus, bpy.types.Object):
        cam.data.dof.focus_object = focus
    elif focus is not None and not isinstance(focus, (int, float)):
        cam.data.dof.focus_distance = (Vector(focus) - cam.location).length
    elif isinstance(focus, (int, float)):
        cam.data.dof.focus_distance = focus
    return cam
