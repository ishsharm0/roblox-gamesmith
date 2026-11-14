"""Modelling: bevelled primitives with weighted normals, lathe/extrude from a profile, joining,
and low-poly prop generators (trees, rocks, clouds, bushes, grass, crate, barrel, coin, duck,
and a castle/house building set).

Conventions
- Units are studs (or metres): a Roblox character is 5 tall. Z is up, the model's front faces -Y.
- Primitives: `location` is the CENTRE. Props and building pieces: `location` is the BASE centre
  (they stand on z = location.z).
- `mat` everywhere accepts a Material, or a colour spec ('#RRGGBB', 'palette.name') which becomes
  toy_plastic(colour).
- Bevels are live modifiers (Bevel + WeightedNormal) until you call join() or apply_modifiers();
  that is what makes hard edges catch light. Never leave a box unbevelled.
- Props are returned as ONE joined mesh object with a few material slots. For Roblox, run
  materials.atlas_from_materials(obj) to get one material + UVs in 0-1.
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from . import compat, materials
from ._util import link, select

BEVEL_ANGLE = 30.0          # edges sharper than this get bevelled
WEIGHTED_NORMAL_WEIGHT = 50


def _mat(spec, kind="toy_plastic"):
    if spec is None:
        return None
    if isinstance(spec, bpy.types.Material):
        return spec
    return materials.make(kind, spec)


def _from_bm(bm, name, location=(0, 0, 0), mat=None, rotation=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    ob.location = location
    ob.rotation_euler = [math.radians(a) for a in rotation]
    m = _mat(mat)
    if m:
        me.materials.append(m)
    return ob


def bevel(obj, width=0.05, segments=3, angle=BEVEL_ANGLE, weighted=True, profile=0.5):
    """Add a Bevel (+ WeightedNormal) modifier stack to any mesh object and smooth-shade it.
    width in scene units (rule of thumb: 4-8% of the smallest dimension; 0.05-0.1 on a 1-stud box);
    segments: 1 = chamfer (Roblox budget), 2 = default prop, 3 = hero. Returns obj."""
    compat.shade_smooth(obj)
    b = obj.modifiers.new("Bevel", "BEVEL")
    b.width = width
    b.segments = segments
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle)
    b.use_clamp_overlap = True
    b.profile = profile
    b.miter_outer = "MITER_ARC"
    if weighted:
        w = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        w.mode = "FACE_AREA"
        w.weight = WEIGHTED_NORMAL_WEIGHT
        w.keep_sharp = True
    return obj


def rounded_box(size=(1, 1, 1), radius=None, segments=3, location=(0, 0, 0), mat=None, name="Box",
                rotation=(0, 0, 0)):
    """Box with rounded edges. size (x, y, z); radius default 7% of the smallest side.
    Returns the object (origin at its centre)."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1)))
    ob = _from_bm(bm, name, location, mat, rotation)
    return bevel(ob, radius if radius is not None else 0.07 * min(size), segments)


def cylinder(radius=0.5, depth=1.0, verts=32, bevel_width=None, segments=3, location=(0, 0, 0), mat=None,
             name="Cylinder", rotation=(0, 0, 0), radius_top=None):
    """Upright cylinder (or tapered, with radius_top) with rounded rims. verts 24-48 smooth, 6-10 for
    low-poly. Returns the object (origin at its centre)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=radius,
                          radius2=radius if radius_top is None else radius_top, depth=depth)
    ob = _from_bm(bm, name, location, mat, rotation)
    w = bevel_width if bevel_width is not None else 0.08 * min(radius, depth)
    if w > 0:
        bevel(ob, w, segments, angle=50)
    else:
        compat.smooth_by_angle(ob, 40)
    return ob


def sphere(radius=0.5, segments=32, rings=16, location=(0, 0, 0), mat=None, name="Sphere", scale=(1, 1, 1),
           smooth=True, rotation=(0, 0, 0)):
    """UV sphere, smooth-shaded (smooth=False for faceted). scale squashes it into an ellipsoid."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius,
                              matrix=Matrix.Diagonal((*scale, 1)))
    ob = _from_bm(bm, name, location, mat, rotation)
    (compat.shade_smooth if smooth else compat.shade_flat)(ob)
    return ob


def ico(radius=0.5, subdivisions=2, location=(0, 0, 0), mat=None, name="Ico", scale=(1, 1, 1), jitter=0.0,
        seed=0, flat=True, flatten_bottom=None):
    """Icosphere, optionally jittered (seeded) and faceted: the building block of low-poly rocks,
    bushes and tree crowns. flatten_bottom: z (local) below which vertices are pressed flat."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius, matrix=Matrix.Diagonal((*scale, 1)))
    for v in bm.verts:
        if jitter:
            v.co += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jitter * radius
        if flatten_bottom is not None and v.co.z < flatten_bottom:
            v.co.z = flatten_bottom
    ob = _from_bm(bm, name, location, mat)
    (compat.shade_flat if flat else compat.shade_smooth)(ob)
    return ob


def capsule(radius=0.3, length=1.0, segments=24, location=(0, 0, 0), mat=None, name="Capsule", rotation=(0, 0, 0)):
    """Pill shape along Z: total height = length (including the round ends)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=max(8, segments // 2), radius=radius)
    half = max(length / 2 - radius, 0)
    for v in bm.verts:
        v.co.z += half if v.co.z > 1e-6 else (-half if v.co.z < -1e-6 else 0)
    ob = _from_bm(bm, name, location, mat, rotation)
    compat.shade_smooth(ob)
    return ob


def torus(major=0.5, minor=0.12, major_segments=32, minor_segments=12, location=(0, 0, 0), mat=None,
          name="Torus", rotation=(0, 0, 0)):
    """Ring/donut around the Z axis."""
    prof = [(major + minor * math.cos(a), minor * math.sin(a))
            for a in [2 * math.pi * i / minor_segments for i in range(minor_segments)]]
    return lathe(prof, major_segments, location=location, mat=mat, name=name, closed=True, rotation=rotation,
                 smooth_angle=180)


def lathe(profile, segments=32, location=(0, 0, 0), mat=None, name="Lathe", closed=False, smooth_angle=35.0,
          rotation=(0, 0, 0)):
    """Spin a profile around Z. profile: [(radius, z), ...] from bottom to top; points with radius 0
    close the ends. closed=True joins last point to first (a ring section, e.g. a torus). Corners
    sharper than smooth_angle stay crisp; add intermediate points to round them. Returns object."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in profile]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    if closed:
        es.append(bm.edges.new((vs[-1], vs[0])))
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=segments,
                   use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _from_bm(bm, name, location, mat, rotation)
    compat.smooth_by_angle(ob, smooth_angle)
    return ob


def extrude(profile, depth=0.2, location=(0, 0, 0), mat=None, name="Extrude", bevel_width=None, segments=2,
            rotation=(0, 0, 0)):
    """Extrude a 2D outline drawn in the front (X, Z) plane by `depth` along Y, centred on y = 0.
    profile: [(x, z), ...] counter-clockwise, not repeating the first point. Bevelled by default."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, -depth / 2, z)) for x, z in profile]
    f = bm.faces.new(vs)
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += depth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _from_bm(bm, name, location, mat, rotation)
    w = bevel_width if bevel_width is not None else 0.15 * depth
    if w > 0:
        bevel(ob, w, segments)
    return ob


def arch_profile(width=1.0, height=1.5, segments=10):
    """Outline for a door/window with a round top: [(x, z)], base at z = 0. Use with extrude()."""
    r = width / 2
    pts = [(-r, 0), (r, 0), (r, height - r)]
    pts += [(r * math.cos(math.pi * i / segments), height - r + r * math.sin(math.pi * i / segments))
            for i in range(1, segments)]
    pts += [(-r, height - r)]
    return pts


def apply_modifiers(obj):
    """Bake an object's modifiers into its mesh (keeps weighted normals). Returns obj."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def join(objs, name="Joined", origin="base"):
    """Apply modifiers and join objects into one mesh (materials kept as slots). origin: 'base'
    (bottom centre, for props that stand on the ground), 'center', or None (keep first's).
    Returns the joined object."""
    objs = [o for o in objs if o is not None and o.type == "MESH"]
    for o in objs:
        apply_modifiers(o)
    target = objs[0]
    if len(objs) > 1:
        with bpy.context.temp_override(active_object=target, object=target, selected_objects=objs,
                                       selected_editable_objects=objs):
            bpy.ops.object.join()
    target.name = name
    target.data.name = name
    if origin:
        set_origin(target, origin)
    return target


def set_origin(obj, where="base"):
    """Move the object's origin to its bounding-box 'base' (bottom centre) or 'center' without moving
    the geometry in the world."""
    me = obj.data
    mw = obj.matrix_world.copy()
    cos = [mw @ v.co for v in me.vertices]
    lo = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
    hi = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
    pivot = (lo + hi) / 2
    if where == "base":
        pivot.z = lo.z
    local = mw.inverted() @ pivot
    me.transform(Matrix.Translation(-local))
    obj.matrix_world = Matrix.Translation(pivot) @ mw.to_3x3().to_4x4()
    return obj


def place(obj, location=None, rotation=None, scale=None):
    """Set location / rotation (degrees) / scale in one call. Returns obj."""
    if location is not None:
        obj.location = location
    if rotation is not None:
        obj.rotation_euler = [math.radians(a) for a in rotation]
    if scale is not None:
        obj.scale = (scale,) * 3 if isinstance(scale, (int, float)) else scale
    return obj


def tri_count(obj):
    """Triangles in the evaluated (modifiers applied) mesh."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
    return n


# ---------------------------------------------------------------- low-poly nature

def _finish(parts, name, location, rotation_z=0.0):
    ob = join(parts, name, origin="base")
    ob.location = location
    ob.rotation_euler.z = math.radians(rotation_z)
    return ob


def tree(kind="round", height=4.0, seed=1, location=(0, 0, 0), palette="meadow", lean=None):
    """Low-poly faceted tree, `height` tall. kind: 'round' (broadleaf, 2-3 crown blobs), 'pine'
    (stacked cones), 'tall' (narrow poplar). seed varies shape within the family. ~300-900 tris."""
    rng = random.Random(seed)
    leaf = materials.make("clay", f"{palette}.leaf")
    leaf_dark = materials.make("clay", f"{palette}.pine")
    leaf_light = materials.make("clay", f"{palette}.grass")
    bark = materials.make("clay", f"{palette}.bark")
    lean = math.radians(rng.uniform(2, 6) if lean is None else lean)
    lean_dir = rng.uniform(0, 2 * math.pi)
    parts = []
    if kind == "pine":
        th = height * 0.22
        parts.append(cylinder(height * 0.06, th * 1.3, 7, 0, location=(0, 0, th * 0.6), mat=bark,
                              radius_top=height * 0.045, name="trunk"))
        levels = 3
        for i in range(levels):
            t = i / levels
            r = height * (0.30 - 0.08 * i) * rng.uniform(0.95, 1.05)
            h = height * (0.36 - 0.03 * i)
            z = th + height * 0.22 * i
            c = cylinder(r, h, 8, 0, location=(0, 0, z + h / 2), mat=leaf_dark if i == 0 else leaf,
                         radius_top=r * 0.08, name="tier")
            c.rotation_euler.z = rng.uniform(0, 1)
            compat.shade_flat(c)
            _jitter(c, 0.04 * r, rng)
            parts.append(c)
    else:
        tall = kind == "tall"
        th = height * (0.35 if not tall else 0.25)
        tr = height * (0.07 if not tall else 0.05)
        parts.append(cylinder(tr, th * 1.15, 7, 0, location=(0, 0, th * 0.55), mat=bark,
                              radius_top=tr * 0.7, name="trunk"))
        cr = height * (0.33 if not tall else 0.2)
        blobs = [((0, 0, th + cr * (2.2 if tall else 0.75)), (1.0, 1.0, 0.9 if not tall else 2.6), leaf)]
        if not tall:
            n = rng.choice((2, 3))
            for k in range(n):
                a = 2 * math.pi * k / n + rng.uniform(-0.4, 0.4)
                blobs.append(((math.cos(a) * cr * 0.65, math.sin(a) * cr * 0.65, th + cr * rng.uniform(0.35, 0.6)),
                              (0.68, 0.68, 0.62), leaf_dark if k == 0 else leaf_light))
        for loc, sc, m in blobs:
            parts.append(ico(cr * sc[0], 2, loc, m, "crown", scale=(1, 1, sc[2] / sc[0]), jitter=0.07,
                             seed=rng.randrange(1 << 30)))
    ob = join(parts, f"tree_{kind}", origin="base")
    ob.rotation_euler = Euler((lean * math.cos(lean_dir), lean * math.sin(lean_dir), rng.uniform(0, 6.28)))
    bpy.context.view_layer.update()
    set_origin(ob, "base")
    ob.location = location
    return ob


def blocky_character(**kwargs):
    """Build the bone-parented block figure; same arguments/return as character.blocky_character."""
    from .character import blocky_character as build
    return build(**kwargs)


def _jitter(obj, amount, rng):
    for v in obj.data.vertices:
        v.co += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.5, 0.5))) * amount


def rock(size=1.0, seed=1, location=(0, 0, 0), color="meadow.stone", chunky=True):
    """Faceted boulder about `size` across, sitting flat on the ground. chunky=True merges nearly
    coplanar facets into bigger planes (the stylised look). ~60-150 tris."""
    rng = random.Random(seed)
    m = materials.make("clay", color)
    sc = (rng.uniform(1.0, 1.3), rng.uniform(0.8, 1.0), rng.uniform(0.55, 0.75))
    ob = ico(size / 2, 2, (0, 0, 0), m, "rock", scale=sc, jitter=0.12, seed=seed, flatten_bottom=-size * 0.18)
    if chunky:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(14), verts=bm.verts, edges=bm.edges)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bm.to_mesh(ob.data)
        bm.free()
        compat.shade_flat(ob)
    set_origin(ob, "base")
    ob.location = location
    ob.rotation_euler.z = rng.uniform(0, 6.28)
    return ob


def bush(size=1.2, seed=1, location=(0, 0, 0), color="meadow.leaf", flowers=0):
    """Low-poly bush of 3-5 faceted blobs, `size` across. flowers: number of small accent dots."""
    rng = random.Random(seed)
    m1, m2 = materials.make("clay", color), materials.make("clay", "meadow.pine")
    parts = []
    n = rng.choice((3, 4, 5))
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
        d = size * 0.22
        r = size * rng.uniform(0.28, 0.36)
        parts.append(ico(r, 2, (math.cos(a) * d, math.sin(a) * d, r * 0.75), m1 if k % 3 else m2, "blob",
                         jitter=0.08, seed=rng.randrange(1 << 30)))
    parts.append(ico(size * 0.38, 2, (0, 0, size * 0.42), m1, "top", jitter=0.08, seed=seed))
    fm = materials.make("toy_plastic", "meadow.flower")
    for k in range(flowers):
        a = rng.uniform(0, 6.28)
        el = rng.uniform(0.3, 1.1)
        p = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))) * size * 0.45
        parts.append(ico(size * 0.06, 1, (p.x, p.y, p.z + size * 0.3), fm, "flower"))
    ob = join(parts, "bush")
    ob.location = location
    return ob


def cloud(size=3.0, seed=1, location=(0, 0, 8), color="#F4F6FA"):
    """Puffy smooth cloud of 5-7 overlapping spheres with a flat underside, `size` long."""
    rng = random.Random(seed)
    m = materials.principled(f"cloud_{color}", color, roughness=0.9, specular=0.2, sheen=0.3)
    parts = []
    n = rng.choice((5, 6, 7))
    for k in range(n):
        t = k / (n - 1) - 0.5
        r = size * (0.24 - 0.14 * abs(t) * 2 * 0.6) * rng.uniform(0.9, 1.1)
        parts.append(sphere(r, 20, 12, (t * size * 0.75, rng.uniform(-0.1, 0.1) * size, r * 0.55), m, "puff",
                            scale=(1, 0.85, 0.85)))
    ob = join(parts, "cloud", origin="base")
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    zmin = min(v.co.z for v in bm.verts)
    cut = zmin + size * 0.06
    for v in bm.verts:
        if v.co.z < cut:
            v.co.z = cut
    bm.to_mesh(ob.data)
    bm.free()
    set_origin(ob, "base")
    ob.location = location
    return ob


def grass_tuft(height=0.6, blades=7, seed=1, location=(0, 0, 0), color="meadow.grass"):
    """A tuft of tapered, outward-curving blades (3-sided, flat-shaded). ~15 tris per blade."""
    rng = random.Random(seed)
    m = materials.make("clay", color)
    bm = bmesh.new()
    for k in range(blades):
        a = 2 * math.pi * k / blades + rng.uniform(-0.3, 0.3)
        h = height * rng.uniform(0.6, 1.0)
        lean = rng.uniform(0.25, 0.6)
        w = height * 0.08
        base = Vector((math.cos(a), math.sin(a), 0)) * height * 0.08
        out = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-math.sin(a), math.cos(a), 0))
        rings = []
        for i, t in enumerate((0.0, 0.5, 1.0)):
            c = base + out * (lean * h * t * t) + Vector((0, 0, h * t))
            ww = w * (1 - t) + 0.002
            ring = [bm.verts.new(c + side * ww), bm.verts.new(c - side * ww), bm.verts.new(c + out * ww * 0.6)]
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(3):
                bm.faces.new((r0[j], r0[(j + 1) % 3], r1[(j + 1) % 3], r1[j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    ob = _from_bm(bm, "grass", location, m)
    compat.shade_flat(ob)
    return ob


# ---------------------------------------------------------------- props

def crate(size=1.0, location=(0, 0, 0), wood="fortress.wood", frame=None, segments=2):
    """Wooden crate with a bevelled frame on every edge and a diagonal brace on each side. ~2k tris
    (segments=1 for ~1k)."""
    sw = materials.make("painted_wood", wood)
    fw = materials.make("painted_wood", frame or "#8A5A30")
    s = size
    t = s * 0.13
    parts = [rounded_box((s * 0.94,) * 3, s * 0.03, segments, (0, 0, s / 2), sw, "core")]
    h = s / 2 - t / 2
    for ax in range(3):
        for a in (-1, 1):
            for b in (-1, 1):
                loc = [0, 0, 0]
                dims = [t, t, t]
                dims[ax] = s
                others = [i for i in range(3) if i != ax]
                loc[others[0]] = a * h
                loc[others[1]] = b * h
                loc[2] += s / 2
                parts.append(rounded_box(dims, t * 0.22, segments, loc, fw, "beam"))
    diag = (s - 2 * t) * math.sqrt(2) * 0.98
    for ax, sign in ((0, -1), (0, 1), (1, -1), (1, 1)):
        loc = [0, 0, s / 2]
        loc[1 - ax] = sign * (s / 2 - t * 0.25)
        dims = [diag, t * 0.7, t * 0.85] if ax == 0 else [t * 0.7, diag, t * 0.85]
        b = rounded_box(dims, t * 0.18, segments, loc, fw, "brace")
        if ax == 0:
            b.rotation_euler.y = math.radians(45 * sign)
        else:
            b.rotation_euler.x = math.radians(45 * sign)
        parts.append(b)
    ob = join(parts, "crate")
    ob.location = location
    return ob


def barrel(height=1.2, location=(0, 0, 0), wood="fortress.wood", hoops="#4A4A52", staves=14):
    """Bulging wooden barrel with three metal hoops. Staves read as facets (smooth angle 8 deg)."""
    r = height * 0.36
    prof = [(0, 0), (r * 0.82, 0), (r * 0.86, height * 0.02)]
    for i in range(1, 10):
        t = i / 10
        prof.append((r * (0.86 + 0.14 * math.sin(math.pi * t)), height * t))
    prof += [(r * 0.86, height * 0.98), (r * 0.8, height), (r * 0.7, height * 0.99), (0, height * 0.96)]
    body = lathe(prof, staves, mat=materials.make("painted_wood", wood), name="barrel", smooth_angle=8)
    parts = [body]
    hm = materials.make("metal_brushed", hoops)
    for t in (0.12, 0.5, 0.88):
        rr = r * (0.86 + 0.14 * math.sin(math.pi * t)) + height * 0.008
        hb = height * 0.055
        parts.append(lathe([(rr, -hb / 2), (rr + height * 0.018, -hb / 2 + 0.01 * height),
                            (rr + height * 0.018, hb / 2 - 0.01 * height), (rr, hb / 2)],
                           48, location=(0, 0, height * t), mat=hm, name="hoop", closed=True, smooth_angle=60))
    ob = join(parts, "barrel")
    ob.location = location
    return ob


def coin(radius=0.5, location=(0, 0, 0.5), color="#F2C14E", upright=True):
    """Chunky collectible coin: raised rim, inset face, centre boss. Stands upright facing -Y."""
    t = radius * 0.28
    prof = [(0, -t * 0.25), (radius * 0.55, -t * 0.25), (radius * 0.62, -t * 0.4), (radius * 0.78, -t * 0.4),
            (radius * 0.84, -t * 0.5), (radius * 0.97, -t * 0.5), (radius, -t * 0.35), (radius, t * 0.35),
            (radius * 0.97, t * 0.5), (radius * 0.84, t * 0.5), (radius * 0.78, t * 0.4), (radius * 0.62, t * 0.4),
            (radius * 0.55, t * 0.25), (0, t * 0.25)]
    m = materials.principled(f"coin_{color}", color, metallic=0.85, roughness=0.28)
    ob = lathe(prof, 40, location, m, "coin", smooth_angle=40)
    if upright:
        ob.rotation_euler.x = math.radians(90)
    return ob


def rubber_duck(size=1.0, location=(0, 0, 0), color="toybox.yellow", beak="toybox.orange", facing=0.0):
    """Classic rubber duck, `size` long, sitting on z = location.z, facing -Y rotated by `facing`
    degrees. Smooth rubber, black eyes with a highlight. ~5k tris."""
    s = size
    body_m = materials.make("rubber", color)
    beak_m = materials.make("rubber", beak)
    eye_m = materials.make("toy_plastic", "#141418")
    hi_m = materials.make("toy_plastic", "#F5F5F2")
    parts = [sphere(s * 0.5, 40, 24, (0, s * 0.05, s * 0.3), body_m, "body", scale=(0.82, 1.0, 0.62))]
    tail = sphere(s * 0.22, 24, 12, (0, s * 0.42, s * 0.48), body_m, "tail", scale=(0.9, 0.8, 1.1))
    tail.rotation_euler.x = math.radians(-35)
    parts.append(tail)
    parts.append(sphere(s * 0.27, 40, 24, (0, -s * 0.22, s * 0.78), body_m, "head"))
    parts.append(sphere(s * 0.16, 24, 12, (0, -s * 0.45, s * 0.73), beak_m, "beak", scale=(1.1, 1.0, 0.42)))
    for x in (-1, 1):
        parts.append(sphere(s * 0.055, 16, 10, (x * s * 0.12, -s * 0.42, s * 0.86), eye_m, "eye"))
        parts.append(sphere(s * 0.018, 10, 6, (x * s * 0.12 - s * 0.012, -s * 0.47, s * 0.885), hi_m, "glint"))
    for x in (-1, 1):
        w = sphere(s * 0.2, 24, 12, (x * s * 0.37, s * 0.12, s * 0.38), body_m, "wing", scale=(0.35, 1.0, 0.6))
        w.rotation_euler.x = math.radians(-15)
        parts.append(w)
    ob = join(parts, "duck")
    ob.location = location
    ob.rotation_euler.z = math.radians(facing)
    return ob


# ---------------------------------------------------------------- building set (castle / village)

def wall(length=6.0, height=3.0, thickness=0.9, crenels=True, location=(0, 0, 0), rotation=0.0,
         stone="fortress.stone", trim="fortress.stone_dark"):
    """Castle wall segment along X, base centred at location. crenels: merlons along the top.
    A darker plinth course at the bottom gives it weight."""
    sm, tm = materials.make("clay", stone), materials.make("clay", trim)
    parts = [rounded_box((length, thickness, height), 0.06, 2, (0, 0, height / 2), sm, "wall"),
             rounded_box((length + 0.04, thickness + 0.16, height * 0.12), 0.05, 2, (0, 0, height * 0.06), tm, "plinth"),
             rounded_box((length + 0.04, thickness + 0.1, height * 0.06), 0.03, 2, (0, 0, height * 0.97), tm, "cap")]
    if crenels:
        mw = thickness * 0.75
        n = max(2, int(length / (mw * 2)))
        step = length / n
        for i in range(n):
            x = -length / 2 + step * (i + 0.5)
            parts.append(rounded_box((mw, thickness + 0.06, mw * 0.8), 0.06, 2, (x, 0, height + mw * 0.4), sm, "merlon"))
    ob = join(parts, "wall")
    ob.location = location
    ob.rotation_euler.z = math.radians(rotation)
    return ob


def tower(radius=1.4, height=5.0, roof="cone", location=(0, 0, 0), stone="fortress.stone",
          roof_color="fortress.roof", trim="fortress.stone_dark", windows=2, flag=None):
    """Round tower. roof: 'cone' (overhanging pointed roof), 'crenel' (battlements), None.
    windows: arched slits on the front half. flag: colour spec for a pennant on the roof tip."""
    sm, tm = materials.make("clay", stone), materials.make("clay", trim)
    parts = [cylinder(radius, height, 24, 0.06, 2, (0, 0, height / 2), sm, "body"),
             cylinder(radius * 1.08, height * 0.1, 24, 0.05, 2, (0, 0, height * 0.05), tm, "plinth"),
             cylinder(radius * 1.12, height * 0.07, 24, 0.05, 2, (0, 0, height * 0.965), tm, "corbel")]
    dark = materials.make("clay", "#3B3540")
    for i in range(windows):
        a = math.radians(-90 + (i - (windows - 1) / 2) * 50)
        w = extrude(arch_profile(radius * 0.32, radius * 0.75), radius * 0.2,
                    location=(math.cos(a) * radius * 0.97, math.sin(a) * radius * 0.97, height * 0.55),
                    mat=dark, name="window", bevel_width=0.02)
        w.rotation_euler.z = a + math.pi / 2
        parts.append(w)
    top = height
    if roof == "cone":
        rh = radius * 2.2
        rm = materials.make("toy_plastic", roof_color)
        parts.append(cylinder(radius * 1.32, rh, 24, 0.0, 1, (0, 0, top + rh / 2), rm, "roof", radius_top=0.0))
        parts.append(cylinder(radius * 1.34, radius * 0.12, 24, 0.03, 2, (0, 0, top + radius * 0.06), rm, "eave"))
        top += rh
        if flag:
            parts.append(cylinder(0.04, radius * 0.9, 8, 0, 1, (0, 0, top + radius * 0.4), tm, "pole"))
            parts.append(_pennant(radius * 0.7, (0, 0, top + radius * 0.65), flag))
            parts.append(sphere(0.08, 12, 8, (0, 0, top + radius * 0.86), materials.make("toy_plastic", "fortress.gold"), "finial"))
    elif roof == "crenel":
        n = 8
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            parts.append(rounded_box((radius * 0.5, radius * 0.3, radius * 0.4), 0.05, 2,
                                     (math.cos(a) * radius * 0.95, math.sin(a) * radius * 0.95, top + radius * 0.2), sm,
                                     "merlon", rotation=(0, 0, math.degrees(a) + 90)))
    ob = join(parts, "tower")
    ob.location = location
    return ob


def _pennant(length, base, color):
    m = materials.make("fabric", color)
    pts = [(0, 0.0), (length, -length * 0.22), (0, -length * 0.44)]
    p = extrude(pts, 0.03, location=base, mat=m, name="pennant", bevel_width=0.008)
    p.location.z += 0
    return p


def flag(height=3.0, location=(0, 0, 0), color="fortress.banner", pole="fortress.stone_dark", wave=0.12):
    """Flag on a pole with a gentle wave in the cloth, base at location."""
    pm = materials.make("metal_brushed", pole)
    parts = [cylinder(0.06, height, 10, 0.01, 1, (0, 0, height / 2), pm, "pole"),
             sphere(0.12, 16, 10, (0, 0, height + 0.08), materials.make("toy_plastic", "fortress.gold"), "finial")]
    w, h = height * 0.5, height * 0.32
    bm = bmesh.new()
    nx, nz = 12, 4
    grid = [[bm.verts.new((w * i / nx, wave * math.sin(i / nx * 2 * math.pi) * (i / nx), height - 0.1 - h * j / nz))
             for j in range(nz + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    cloth = _from_bm(bm, "cloth", (0.05, 0, 0), materials.make("fabric", color))
    sol = cloth.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.03
    compat.shade_smooth(cloth)
    parts.append(cloth)
    ob = join(parts, "flag")
    ob.location = location
    return ob


def gate(width=2.4, height=3.2, location=(0, 0, 0), wood="fortress.wood", frame="fortress.stone_dark"):
    """Arched wooden gate set in a stone frame; front faces -Y. Place it in a wall gap."""
    fm, wm = materials.make("clay", frame), materials.make("painted_wood", wood)
    parts = [extrude(arch_profile(width + 0.6, height + 0.3), 1.1, (0, 0, 0), fm, "frame", 0.05),
             extrude(arch_profile(width, height), 1.2, (0, -0.02, 0), wm, "door", 0.03)]
    metal = materials.make("metal_brushed", "#3A3A40")
    for z in (height * 0.25, height * 0.6):
        parts.append(rounded_box((width * 0.9, 1.26, 0.14), 0.03, 2, (0, -0.02, z), metal, "strap"))
    ob = join(parts, "gate")
    ob.location = location
    return ob


def roof_gable(width=3.0, depth=3.0, height=1.5, overhang=0.25, location=(0, 0, 0), color="fortress.roof"):
    """Pitched roof: a prism along Y with eaves overhanging by `overhang`. Base at location."""
    w = width / 2 + overhang
    t = 0.18
    pts = [(-w, 0), (-w, t), (0, height + t), (w, t), (w, 0), (0, height)]
    r = extrude(pts, depth + 2 * overhang, (0, 0, 0), materials.make("toy_plastic", color), "roof", 0.03)
    r.location = location
    return r


def house(width=3.0, depth=3.0, height=2.6, location=(0, 0, 0), walls="#EDE3D0", roof="fortress.roof",
          trim="fortress.wood", door="fortress.banner", rotation=0.0):
    """Small toy house: plastered walls, wooden corner posts, gable roof, door and windows."""
    wm, tm = materials.make("clay", walls), materials.make("painted_wood", trim)
    parts = [rounded_box((width, depth, height), 0.06, 2, (0, 0, height / 2), wm, "walls")]
    for x in (-1, 1):
        for y in (-1, 1):
            parts.append(rounded_box((0.22, 0.22, height), 0.04, 2, (x * width / 2, y * depth / 2, height / 2), tm, "post"))
    gable = extrude([(-width / 2, 0), (width / 2, 0), (0, height * 0.55)], depth * 0.98, (0, 0, height), wm, "gable", 0.03)
    gable.rotation_euler.z = 0
    parts.append(gable)
    parts.append(roof_gable(width, depth, height * 0.55, 0.3, (0, 0, height - 0.05), roof))
    parts.append(extrude(arch_profile(width * 0.28, height * 0.62), 0.16, (0, -depth / 2, 0),
                         materials.make("toy_plastic", door), "door", 0.03))
    glass_m = materials.make("toy_plastic", "#9AD0F5")
    for x in (-1, 1):
        parts.append(rounded_box((width * 0.2, 0.12, height * 0.24), 0.03, 2, (x * width * 0.3, -depth / 2, height * 0.58), glass_m, "window"))
        parts.append(rounded_box((width * 0.26, 0.1, height * 0.3), 0.03, 2, (x * width * 0.3, -depth / 2 + 0.03, height * 0.58), tm, "frame"))
    ob = join(parts, "house")
    ob.location = location
    ob.rotation_euler.z = math.radians(rotation)
    return ob
