"""Small shared helpers: colour parsing, object linking, bounds, selection."""
import math

import bpy
from mathutils import Vector


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb(spec):
    """Parse a colour spec to sRGB floats (r, g, b) in 0-1.
    Accepts '#D7463F', 'D7463F', 'toybox.red' (palette.colour), or a tuple of floats 0-1 / ints 0-255."""
    if isinstance(spec, str):
        s = spec.strip()
        if "." in s and not s.startswith("#"):
            from . import palettes
            pal, name = s.split(".", 1)
            s = palettes.get(pal)[name]
        s = s.lstrip("#")
        if len(s) != 6:
            raise ValueError(f"colour {spec!r}: want #RRGGBB or palette.name")
        return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
    t = tuple(spec)[:3]
    if any(v > 1.0 for v in t):
        t = tuple(v / 255 for v in t)
    return t


def rgb(spec):
    """Colour spec -> linear RGB tuple (what shader sockets want)."""
    return tuple(srgb_to_linear(c) for c in srgb(spec))


def rgba(spec, alpha=1.0):
    """Colour spec -> linear RGBA tuple."""
    return (*rgb(spec), alpha)


def mix(a, b, t):
    """Blend two colour specs in sRGB space; returns sRGB floats usable as a spec."""
    a, b = srgb(a), srgb(b)
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def shade(spec, factor):
    """Darken (factor < 1) or lighten (factor > 1, towards white) a colour; returns sRGB floats."""
    c = srgb(spec)
    if factor <= 1:
        return tuple(x * factor for x in c)
    t = min(factor - 1, 1)
    return tuple(x + (1 - x) * t for x in c)


def link(obj, collection=None):
    """Link an object into `collection` (default: the scene collection). Returns obj."""
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def as_list(objs):
    if objs is None:
        return []
    if isinstance(objs, bpy.types.Object):
        return [objs]
    return [o for o in objs if o is not None]


def descendants(obj):
    """obj plus all its children, recursively."""
    out = [obj]
    for c in obj.children:
        out.extend(descendants(c))
    return out


def mesh_objects(objs=None):
    """Mesh objects among objs (and their children); default: all visible meshes in the scene."""
    if objs is None:
        return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]
    seen, out = set(), []
    for o in as_list(objs):
        for d in descendants(o):
            if d.type == "MESH" and d.name not in seen:
                seen.add(d.name)
                out.append(d)
    return out


def bounds(objs=None, precise=False):
    """World (min,max) over evaluated meshes; precise=True tests vertices for exact floor contact."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for o in mesh_objects(objs):
        ev = o.evaluated_get(dg)
        points = (v.co for v in ev.data.vertices) if precise else ev.bound_box
        for c in points:
            w = ev.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    if lo.x == math.inf:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    return lo, hi


def center_radius(objs=None):
    """(centre Vector, bounding-sphere radius) of objs."""
    lo, hi = bounds(objs)
    return (lo + hi) / 2, max((hi - lo).length / 2, 1e-3)


def select(objs, active=None):
    """Deselect everything, select objs, make `active` (default first) the active object."""
    objs = as_list(objs)
    bpy.context.view_layer.update()
    for o in bpy.context.view_layer.objects:
        if o is not None:
            o.select_set(False)
    for o in objs:
        o.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = active or objs[0]


def look_at(obj, target):
    """Rotate obj (camera/light) so its -Z axis points at target (a Vector or tuple)."""
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def spherical(center, radius, azimuth, elevation):
    """Point at `radius` from center. azimuth 0 = in front (-Y, Blender Front view), 90 = right (+X);
    elevation in degrees above the horizon."""
    a, e = math.radians(azimuth), math.radians(elevation)
    return Vector(center) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * radius
