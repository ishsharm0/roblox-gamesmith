"""Named lighting rigs, placed and scaled to the subject and aimed relative to the camera.

    bkit.lighting.rig("studio_soft", subject=objs)          # after add_camera()

Rigs: studio_soft (neutral 3-point, soft), toy_bright (high-key, cheerful, low contrast),
hero_rim (dark, dramatic edge lights for products), sunny_outdoor (sun + sky), night_moon
(cool moonlight + optional warm practical light).

Light levels are written as irradiance at the subject (the same unit as a Sun lamp's strength,
W/m2), so they do not change with subject size: each light's wattage is computed from its
distance. The levels below were calibrated on Blender 5.3 renders (EEVEE and Cycles) with the
'toy' look, measuring mean subject brightness and clipping; see references/blender-kit.md.
"""
import math

import bpy
from mathutils import Vector

from . import compat, scene as _scene
from ._util import center_radius, link, look_at, rgb, spherical

# Each light: type, azimuth (deg, relative to the camera: 0 = from the camera, -90 = camera-left,
# 180 = behind subject), elevation (deg), distance and size (x subject radius), level (irradiance),
# colour. World: (kind, args).
RIGS = {
    "studio_soft": {
        "lights": [
            ("key",  "AREA", -45, 40, 5.0, 3.0, 3.2, "#FFF1E0"),
            ("fill", "AREA",  60, 15, 5.0, 5.0, 0.9, "#E3ECFF"),
            ("rim",  "AREA", 165, 45, 5.0, 2.0, 2.6, "#FFFFFF"),
        ],
        "world": ("color", "#C9CDD4", 0.25),
    },
    "toy_bright": {
        "lights": [
            ("key",  "AREA", -30, 55, 5.0, 5.0, 3.2, "#FFF0DC"),
            ("fill", "AREA",  55, 20, 5.0, 6.0, 1.2, "#EAF2FF"),
            ("rim",  "AREA", 180, 50, 5.0, 3.0, 2.0, "#FFFFFF"),
        ],
        "world": ("color", "#F3EBDD", 0.55),
    },
    "hero_rim": {
        "lights": [
            ("key",   "AREA", -60, 30, 5.0, 2.0, 2.4, "#FFF4E8"),
            ("rim_l", "AREA", -140, 20, 4.0, 1.2, 6.0, "#FFE7CC"),
            ("rim_r", "AREA",  140, 25, 4.0, 1.2, 6.0, "#D6E6FF"),
            ("top",   "AREA",   0, 85, 5.0, 3.0, 0.6, "#FFFFFF"),
        ],
        "world": ("color", "#1C1E24", 0.15),
    },
    "sunny_outdoor": {
        "lights": [
            ("sun", "SUN", -50, 42, 0, 2.5, 3.6, "#FFF0D8"),
        ],
        "world": ("gradient", "#8EC3F0", "#E9DEC6", 0.75),
    },
    "night_moon": {
        "lights": [
            ("moon", "SUN", -35, 40, 0, 3.0, 2.0, "#B7C9FF"),
            ("fill", "AREA", 55, 25, 5.0, 4.0, 0.8, "#8DA7DD"),
        ],
        "world": ("color", "#435574", 0.3),
    },
}

# Multiplier per engine applied on top of the levels above (measured: see the manual).
ENGINE_GAIN = {"EEVEE": 1.0, "CYCLES": 1.0}


def _engine_kind():
    e = bpy.context.scene.render.engine
    return "CYCLES" if e == "CYCLES" else "EEVEE"


def add_light(kind="AREA", level=3.0, color="#FFFFFF", target=(0, 0, 0), azimuth=-45, elevation=40,
              distance=5.0, size=1.0, name="Light", size_y=None):
    """Add one light aimed at `target`. level = irradiance at the target (sun strength units, 3-4
    is a bright key); azimuth/elevation in world degrees (0 = from the front, -Y). Returns the object."""
    t = Vector(target)
    data = bpy.data.lights.new(name, kind)
    data.color = rgb(color)
    if kind == "SUN":
        data.energy = level
        data.angle = math.radians(size)
    elif kind == "AREA":
        data.shape = "RECTANGLE" if size_y else "SQUARE"
        data.size = size
        if size_y:
            data.size_y = size_y
        data.energy = level * math.pi * distance ** 2
    else:  # POINT / SPOT
        data.shadow_soft_size = size / 2
        data.energy = level * 4 * math.pi * distance ** 2
    ob = link(bpy.data.objects.new(name, data))
    ob.location = spherical(t, distance if kind != "SUN" else 10.0, azimuth, elevation)
    look_at(ob, t)
    ob["bkit_level"] = level
    return ob


def rig(name="studio_soft", subject=None, camera=None, strength=1.0, world=True, warmth=0.0):
    """Light `subject` (objects; default everything) with a named rig, relative to `camera`
    (default scene camera; azimuth 0 = from the camera). strength scales every light (1.0 =
    calibrated). world=False keeps your own world. warmth -1..1 tints key warmer (+) or cooler (-).
    Returns {role: light_object}."""
    spec = RIGS[name]
    c, r = center_radius(subject)
    cam = camera or bpy.context.scene.camera
    cam_az = 0.0
    if cam is not None:
        d = cam.location - c
        cam_az = math.degrees(math.atan2(d.x, -d.y))
    gain = strength * ENGINE_GAIN[_engine_kind()]
    lights = {}
    for role, kind, az, el, dist, size, level, color in spec["lights"]:
        col = Vector(rgb(color))
        if warmth and role in ("key", "sun", "moon"):
            col = col * 1.0
            col.x *= 1 + 0.15 * warmth
            col.z *= 1 - 0.15 * warmth
        lights[role] = add_light(kind, level * gain, tuple(_to_srgb(v) for v in col), c, cam_az + az, el,
                                 dist * r, size * r if kind != "SUN" else size,
                                 name=f"{name}_{role}",
                                 size_y=(size * r * 3 if role.startswith("rim_") else None))
    if world:
        w = spec["world"]
        if w[0] == "color":
            _scene.world_color(w[1], w[2])
        elif w[0] == "gradient":
            _scene.world_gradient(w[1], w[2], w[3])
    return lights


def _to_srgb(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def scale(lights, factor):
    """Multiply the energy of every light in a rig dict (brighten/darken the whole rig)."""
    for ob in lights.values():
        ob.data.energy *= factor


def practical(location, color="#FFB066", level=2.0, radius=0.1, reach=2.0, name="Practical"):
    """A small warm point light in the scene (lantern, window, campfire). level is irradiance at
    distance `reach`. Pair with emissive() on the lamp mesh. Returns the object."""
    data = bpy.data.lights.new(name, "POINT")
    data.color = rgb(color)
    data.shadow_soft_size = radius
    data.energy = level * 4 * math.pi * reach ** 2
    ob = link(bpy.data.objects.new(name, data))
    ob.location = location
    return ob
