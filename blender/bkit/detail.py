"""Mid-detail builders: the house level of detail for stylised props and sets.

The rule this module encodes: a surface that is brick, plank, tile or stone in real life is MADE of
bricks, planks, tiles or stones here (separate bevelled solids with a 2-4% gap and three or four tints),
never one smooth box with a colour. That is the difference between "cute low poly" and "cheap".
`Batch` makes that affordable: thousands of small solids in one mesh with one bevel modifier.

    import bkit as b, bkit.detail as d
    b.scene.new_scene(look="neutral")            # 'neutral' keeps authored colours vivid
    parts = d.base_disc() + [d.tower(0.8, 2.7, (0, 0, 0.1)), d.wall(5, 1.8, 0.62, (0, 2, 0.1))]

Every builder returns one joined object standing on z = loc.z (gate(): see its docstring). Colours come
from the module constants below; assign new values before building to re-theme a whole set.
Organic shapes (duck): overlap spheres, voxel-remesh, smooth: one skin, no visible seams.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import compat, materials as M, modelling as m
from ._util import link

rng = random.Random(7)

STONE, MORTAR, TRIM = "#F6EAD4", "#BFA683", "#D9C4A0"
ROOF, WOOD, BLUE, GOLD, IRON = "#FF5545", "#C98146", "#2F7BEA", "#FFC533", "#4A5263"


def shade(c, f):
    c = c.lstrip('#')
    return '#' + ''.join('%02X' % max(0, min(255, round(int(c[i:i + 2], 16) * f))) for i in (0, 2, 4))


def tints(kind, color, fs=(1.0, 1.05, 0.93, 0.97)):
    return [M.make(kind, shade(color, f)) for f in fs]


class Batch:
    """Many small solids in one mesh, one bevel: the cheap way to get real courses, planks and tiles."""

    def __init__(self, mats):
        self.bm = bmesh.new()
        self.mats = mats

    def _mi(self, verts, mi):
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = mi

    def box(self, size, loc, rz=0.0, mi=0, rx=0.0, ry=0.0):
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        mat = (Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(ry, 4, 'Y')
               @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((*size, 1)))
        bmesh.ops.transform(self.bm, matrix=mat, verts=r['verts'])
        self._mi(r['verts'], mi)

    def arc(self, r0, r1, a0, a1, z0, z1, mi=0, n=3):
        """Curved block around the Z axis between two radii, two angles and two heights."""
        secs = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            c, s = math.cos(a), math.sin(a)
            secs.append([self.bm.verts.new((r * c, r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
        for i in range(n):
            p, q = secs[i], secs[i + 1]
            for k in range(4):
                self.bm.faces.new((p[k], p[(k + 1) % 4], q[(k + 1) % 4], q[k]))
        self.bm.faces.new(secs[0])
        self.bm.faces.new(list(reversed(secs[-1])))
        self._mi([v for s in secs for v in s], mi)

    def prism(self, pts, z0, z1, mi=0):
        lo = [self.bm.verts.new((x, y, z0)) for x, y in pts]
        hi = [self.bm.verts.new((x, y, z1)) for x, y in pts]
        n = len(pts)
        self.bm.faces.new(list(reversed(lo)))
        self.bm.faces.new(hi)
        for i in range(n):
            self.bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
        self._mi(lo + hi, mi)

    def bricks(self, length, height, thick, origin=(0, 0, 0), rz=0.0, ch=0.3, bl=0.62, plinth=True, gap=0.035):
        """Running-bond courses along local X, through the full thickness."""
        nc = max(1, round(height / ch)); ch = height / nc
        nb = max(1, round(length / bl)); bl = length / nb
        T = Matrix.Translation(origin) @ Matrix.Rotation(rz, 4, 'Z')
        for j in range(nc):
            cuts = [-length / 2 + bl * i for i in range(nb + 1)]
            if j % 2:
                cuts = [-length / 2] + [c + bl / 2 for c in cuts[:-1]] + [length / 2]
            for x0, x1 in zip(cuts, cuts[1:]):
                bump = rng.uniform(0, 0.035) + (0.1 if plinth and j == 0 else 0)
                mi = 2 if plinth and j == 0 else rng.choice((0, 0, 0, 1, 2, 3))
                p = T @ Vector(((x0 + x1) / 2, 0, (j + 0.5) * ch))
                self.box((x1 - x0 - gap, thick + bump, ch - gap), p, rz, mi)

    def obj(self, name, bevel=0.03, seg=2):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me); self.bm.free()
        for mt in self.mats:
            me.materials.append(mt)
        ob = link(bpy.data.objects.new(name, me))
        if bevel:
            m.bevel(ob, bevel, seg)
        return ob


def done(parts, name, loc=(0, 0, 0), rot=0.0):
    ob = m.join(parts, name)
    ob.rotation_euler.z = math.radians(rot)
    ob.location = Vector(loc) + (Matrix.Rotation(math.radians(rot), 3, 'Z') @ ob.location)
    return ob


def stone_mats():
    return tints("clay", STONE) + [M.make("clay", MORTAR), M.make("clay", TRIM)]


def wall(length, height, thick, loc, rot=0.0, crenels=True):
    B = Batch(stone_mats())
    B.box((length - 0.05, thick - 0.05, height), (0, 0, height / 2), mi=4)
    B.bricks(length, height, thick)
    B.box((length + 0.04, thick + 0.16, 0.09), (0, 0, height + 0.045), mi=5)
    if crenels:
        mw = 0.44
        n = max(2, round(length / (mw * 1.9))); step = length / n
        for i in range(n):
            x = -length / 2 + step * (i + 0.5)
            B.box((mw, thick + 0.04, 0.36), (x, 0, height + 0.27), mi=rng.choice((0, 1, 3)))
            B.box((mw + 0.07, thick + 0.11, 0.07), (x, 0, height + 0.485), mi=5)
    return done([B.obj("wall")], "wall", loc, rot)


def shingle_cone(R, h, tiers, mats):
    """Rings of separate round-bottomed tiles, each ring overlapping the one below; a plain cap on top."""
    obs = []
    for k in range(tiers - 1):
        z0, z1 = h * k / tiers, h * min(1.0, (k + 1.3) / tiers)
        rb, rt = R * (1 - z0 / h) + 0.07, max(R * (1 - z1 / h), 0.0) + 0.02
        ns = max(6, round(2 * math.pi * rb / 0.34)); n = 8
        bm = bmesh.new()
        for t in range(ns):
            a0 = 2 * math.pi * (t + 0.5 * (k % 2)) / ns; da = 2 * math.pi / ns * 0.96
            lo, hi = [], []
            for i in range(n + 1):
                u = i / n * 2 - 1; a = a0 + da * i / n
                r = rb + 0.03 * (1 - u * u)
                lo.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z0 + 0.11 * (1 - math.sqrt(max(1 - u * u, 0))))))
                hi.append(bm.verts.new((rt * math.cos(a), rt * math.sin(a), z1)))
            for i in range(n):
                bm.faces.new((lo[i], lo[i + 1], hi[i + 1], hi[i]))
        ob = m._from_bm(bm, "shingles", (0, 0, 0), mats[k % len(mats)])
        sol = ob.modifiers.new("t", "SOLIDIFY"); sol.thickness = 0.06; sol.offset = 1
        compat.smooth_by_angle(ob, 40)
        obs.append(ob)
    ch = h * 1.25 / tiers
    obs.append(m.cylinder(R * ch / h + 0.07, ch, 32, 0, 1, (0, 0, h - ch / 2), mats[(tiers - 1) % len(mats)], "cap", radius_top=0.02))
    return obs


def tower(radius, height, loc, flag=BLUE):
    sm = stone_mats()
    parts = [m.cylinder(radius - 0.04, height, 32, 0, 1, (0, 0, height / 2), sm[4], "core")]
    B = Batch(sm)
    nc = round(height / 0.3); ch = height / nc
    nb = max(8, round(2 * math.pi * radius / 0.56))
    for j in range(nc):
        for i in range(nb):
            a0 = 2 * math.pi * (i + 0.5 * (j % 2)) / nb
            a1 = a0 + 2 * math.pi / nb - 0.035 / radius
            bump = rng.uniform(0, 0.03) + (0.09 if j == 0 else 0)
            B.arc(radius - 0.14, radius + bump, a0, a1, j * ch + 0.017, (j + 1) * ch - 0.017,
                  2 if j == 0 else rng.choice((0, 0, 0, 1, 2, 3)))
    nk = 14
    for i in range(nk):
        a0 = 2 * math.pi * i / nk
        B.arc(radius - 0.05, radius + 0.17, a0, a0 + math.pi / nk, height - 0.2, height, 5, 2)
    parts.append(B.obj("stones", 0.028))
    parts.append(m.cylinder(radius + 0.22, 0.1, 40, 0.03, 2, (0, 0, height + 0.05), sm[5], "ring"))
    dark = M.make("clay", "#33303C")
    for deg in (-118, -62, 0):
        a = math.radians(deg)
        for w, h, d, mt, zz in ((radius * 0.5, radius * 0.95, 0.16, sm[5], 0.0), (radius * 0.3, radius * 0.75, 0.2, dark, 0.03)):
            o = m.extrude(m.arch_profile(w, h), d, (math.cos(a) * radius, math.sin(a) * radius, height * 0.5 + zz), mt, "win", 0.025)
            o.rotation_euler.z = a + math.pi / 2
            parts.append(o)
        s = m.rounded_box((radius * 0.62, 0.24, 0.07), 0.02, 2, (math.cos(a) * radius, math.sin(a) * radius, height * 0.5 - 0.02), sm[5], "sill")
        s.rotation_euler.z = a + math.pi / 2
        parts.append(s)
    rh = radius * 2.35
    rm = [M.make("toy_plastic", ROOF), M.make("toy_plastic", shade(ROOF, 0.9))]
    for o in shingle_cone(radius * 1.42, rh, 7, rm):
        o.location.z = height + 0.1
        parts.append(o)
    top = height + 0.1 + rh
    parts.append(m.sphere(0.1, 20, 12, (0, 0, top + 0.02), M.make("toy_plastic", GOLD), "ball"))
    if flag:
        parts.append(m.flag(radius * 1.25, (0, 0, top), flag, "#6B6F7A"))
    return done(parts, "tower", loc)


def gate(width, height, loc=(0, 0, 0), depth=0.9):
    """Arched stone gateway with a planked, iron-strapped door, front facing -Y, base at loc."""
    r = width / 2; sm = stone_mats()
    B = Batch(sm)                      # drawn lying down (arch in XY), stood up afterwards
    nv = 9
    for i in range(nv):
        a0 = math.pi * i / nv
        key = i == nv // 2
        B.arc(r, r + (0.42 if key else 0.34), a0 + 0.012, a0 + math.pi / nv - 0.012, -depth / 2 - (0.04 if key else 0),
              depth / 2 + (0.04 if key else 0), 5 if key else (i % 2) * 3, 3)
    sy = height - r
    for v in B.bm.verts:               # arch blocks were made around the origin: lift to the springing line
        v.co.y += sy
    nj = max(2, round(sy / 0.34)); jh = sy / nj
    for sx in (-1, 1):
        for j in range(nj):
            B.box((0.36 + (0.06 if j == 0 else 0), jh - 0.03, depth + (0.08 if j == 0 else 0)),
                  (sx * (r + 0.17), (j + 0.5) * jh, 0), mi=2 if j == 0 else (j % 2) * 3)
    stone = B.obj("arch", 0.035)
    wm = tints("painted_wood", WOOD, (1.0, 1.07, 0.92, 0.97))
    D = Batch(wm)
    npl = 6; pw = width / npl
    for i in range(npl):
        x0, x1 = -r + pw * i, -r + pw * (i + 1)
        xm = min(abs(x0), abs(x1))
        top = sy + math.sqrt(max(r * r - xm * xm, 0)) + 0.05
        D.box((pw - 0.025, top, 0.16), ((x0 + x1) / 2, top / 2, 0), mi=i % 4)
    door = D.obj("door", 0.02)
    I = Batch([M.make("metal_brushed", "#3C404A")])
    for y in (height * 0.22, height * 0.58):
        I.box((width * 0.98, 0.13, 0.05), (0, y, 0.1))
        for i in range(npl):
            I.box((0.07, 0.07, 0.05), (-r + pw * (i + 0.5), y, 0.13))
    iron = I.obj("iron", 0.02)
    ring = m.torus(0.13, 0.03, 24, 10, (r * 0.35, height * 0.42, 0.15), M.make("metal_brushed", "#3C404A"), "ring")
    g = m.join([stone, door, iron, ring], "gate", origin=None)
    stand_up(g)
    g.location = loc
    return g


def stand_up(ob):
    """Local (x, y, z) -> (x, -z, y): something drawn flat becomes upright, front facing -Y."""
    ob.data.transform(Matrix.Rotation(math.radians(90), 4, 'X'))
    return ob


def gable_tiles(width, depth, rise, z, over=0.3):
    hw = width / 2 + over; sl = math.hypot(hw, rise); th = math.atan2(rise, hw)
    T = Batch(tints("toy_plastic", ROOF, (1.0, 0.93, 1.04, 0.88)))
    nrow = max(3, round(sl / 0.4)); L = depth + 2 * over; nt = max(3, round(L / 0.42)); tw = L / nt
    for s in (-1, 1):
        for i in range(nrow):
            t = (i + 0.5) / nrow
            cuts = [-L / 2 + tw * k for k in range(nt + 1)]
            if i % 2:
                cuts = [-L / 2] + [c + tw / 2 for c in cuts[:-1]] + [L / 2]
            for y0, y1 in zip(cuts, cuts[1:]):
                T.box((sl / nrow * 1.3, y1 - y0 - 0.025, 0.075),
                      (s * hw * (1 - t) + s * 0.03, (y0 + y1) / 2, z + rise * t + 0.1), ry=s * (th - 0.09),
                      mi=rng.choice((0, 0, 1, 2, 3)))
    return T.obj("tiles", 0.022)


def house(width, depth, height, loc):
    sm = stone_mats(); wm = tints("painted_wood", shade(WOOD, 0.82))
    plaster = M.make("clay", "#FFF7E8")
    parts = [m.rounded_box((width, depth, height), 0.05, 2, (0, 0, height / 2), plaster, "walls")]
    S = Batch(sm)
    for (ln, o, rz) in ((width + 0.12, (0, -depth / 2, 0), 0), (width + 0.12, (0, depth / 2, 0), 0),
                        (depth + 0.12, (-width / 2, 0, 0), math.pi / 2), (depth + 0.12, (width / 2, 0, 0), math.pi / 2)):
        S.bricks(ln, 0.5, 0.16, o, rz, ch=0.25, bl=0.5, plinth=False)
    parts.append(S.obj("base", 0.025))
    W = Batch(wm)
    for x in (-1, 1):
        for y in (-1, 1):
            W.box((0.2, 0.2, height - 0.5), (x * width / 2, y * depth / 2, 0.5 + (height - 0.5) / 2), mi=0)
    for zz in (height - 0.09, 0.5 + (height - 0.5) * 0.48):
        W.box((width, 0.1, 0.15), (0, -depth / 2 - 0.02, zz), mi=1)
        W.box((0.1, depth, 0.15), (width / 2 + 0.02, 0, zz), mi=1)
    for x in (-1, 1):
        W.box((0.11, 0.09, (height - 0.5) * 0.62), (x * width * 0.3, -depth / 2 - 0.02, height - (height - 0.5) * 0.27), ry=x * 0.62, mi=2)
    parts.append(W.obj("timber", 0.02))
    rise = height * 0.62
    parts.append(m.extrude([(-width / 2, 0), (width / 2, 0), (0, rise * width / (width + 0.6))], depth * 0.98, (0, 0, height), plaster, "gable", 0.03))
    parts.append(m.roof_gable(width, depth, rise, 0.26, (0, 0, height - 0.04), shade(ROOF, 0.75)))
    parts.append(gable_tiles(width, depth, rise, height))
    parts.append(m.cylinder(0.1, depth + 0.7, 14, 0.02, 2, (0, 0, height + rise + 0.2), M.make("toy_plastic", shade(ROOF, 0.85)), "ridge", rotation=(90, 0, 0)))
    C = Batch(tints("clay", "#E58A6B") + [M.make("clay", "#A9624C"), M.make("clay", TRIM)])
    cz = height + rise * 0.35
    for rz, o in ((0, (0, -0.2, 0)), (0, (0, 0.2, 0)), (math.pi / 2, (-0.2, 0, 0)), (math.pi / 2, (0.2, 0, 0))):
        C.bricks(0.52, 1.2, 0.12, (width * 0.24 + o[0], depth * 0.2 + o[1], cz), rz, ch=0.15, bl=0.26, plinth=False, gap=0.02)
    C.box((0.36, 0.36, 1.2), (width * 0.24, depth * 0.2, cz + 0.6), mi=4)
    C.box((0.66, 0.66, 0.09), (width * 0.24, depth * 0.2, cz + 1.24), mi=5)
    parts.append(C.obj("chimney", 0.015))
    bm_ = M.make("toy_plastic", BLUE)
    parts.append(m.extrude(m.arch_profile(0.78, 1.5), 0.14, (0, -depth / 2 - 0.02, 0), wm[2], "doorframe", 0.03))
    parts.append(m.extrude(m.arch_profile(0.6, 1.38), 0.2, (0, -depth / 2 - 0.03, 0), bm_, "door", 0.03))
    parts.append(m.sphere(0.045, 12, 8, (0.18, -depth / 2 - 0.15, 0.68), M.make("toy_plastic", GOLD), "knob"))
    glass = M.make("emissive", "#FFE08A")
    F = Batch(wm + [bm_])
    for x in (-1, 1):
        cx, cz2, y = x * width * 0.31, height * 0.6, -depth / 2
        parts.append(m.rounded_box((0.5, 0.1, 0.56), 0.02, 2, (cx, y - 0.01, cz2), glass, "glass"))
        F.box((0.62, 0.12, 0.07), (cx, y - 0.03, cz2 + 0.31), mi=0); F.box((0.7, 0.2, 0.07), (cx, y - 0.06, cz2 - 0.31), mi=1)
        for sx in (-1, 1):
            F.box((0.07, 0.12, 0.62), (cx + sx * 0.28, y - 0.03, cz2), mi=0)
        F.box((0.045, 0.13, 0.56), (cx, y - 0.04, cz2), mi=2); F.box((0.5, 0.13, 0.045), (cx, y - 0.04, cz2), mi=2)
    parts.append(F.obj("frames", 0.015))
    return done(parts, "house", loc)


def duck(size, loc, facing=0.0):
    s = size
    body_m, beak_m = M.make("rubber", "#FFD21F"), M.make("rubber", "#FF8A1F")
    sp = lambda r, p, sc=(1, 1, 1), rot=(0, 0, 0): m.sphere(s * r, 32, 20, tuple(s * c for c in p), body_m, "p", scale=sc, rotation=rot)
    blob = [sp(0.5, (0, 0.05, 0.31), (0.8, 1.0, 0.64)), sp(0.3, (0, -0.2, 0.36), (1.0, 1.0, 0.95)),
            sp(0.2, (0, 0.4, 0.47)), sp(0.13, (0, 0.52, 0.6)), sp(0.07, (0, 0.59, 0.7)),
            sp(0.3, (0, -0.2, 0.82)), sp(0.26, (0, -0.2, 0.6), (0.9, 0.9, 1.0)),
            sp(0.06, (0, -0.12, 1.12)), sp(0.04, (0, -0.05, 1.17)),
            sp(0.25, (0.37, 0.12, 0.4), (0.36, 1.0, 0.58), (-18, 0, 0)), sp(0.25, (-0.37, 0.12, 0.4), (0.36, 1.0, 0.58), (-18, 0, 0))]
    body = m.join(blob, "body", origin=None)
    rem = body.modifiers.new("r", "REMESH"); rem.mode = "VOXEL"; rem.voxel_size = s * 0.02; rem.use_smooth_shade = True
    smo = body.modifiers.new("s", "SMOOTH"); smo.factor = 0.8; smo.iterations = 24
    m.apply_modifiers(body)
    compat.shade_smooth(body)
    eye_m, hi_m = M.make("toy_plastic", "#17171C"), M.make("emissive", "#FFFFFF")
    parts = [body,
             m.sphere(s * 0.16, 28, 14, (0, -s * 0.47, s * 0.77), beak_m, "beak", scale=(1.15, 1.0, 0.36)),
             m.sphere(s * 0.115, 24, 12, (0, -s * 0.45, s * 0.715), beak_m, "beak2", scale=(1.0, 0.9, 0.3))]
    for x in (-1, 1):
        parts.append(m.sphere(s * 0.062, 20, 12, (x * s * 0.13, -s * 0.44, s * 0.89), eye_m, "eye", scale=(1, 0.7, 1.15)))
        parts.append(m.sphere(s * 0.02, 10, 6, (x * s * 0.13 - s * 0.018, -s * 0.48, s * 0.915), hi_m, "glint"))
    return done(parts, "duck", loc, facing)


def cannon(loc, aim=0.0, s=1.0):
    iron = M.make("toy_plastic", IRON); gold = M.make("toy_plastic", GOLD)
    wm = tints("painted_wood", WOOD)
    prof = [(0, -0.07), (0.06, -0.06), (0.09, -0.01), (0.06, 0.05), (0.19, 0.08), (0.22, 0.1), (0.22, 0.16), (0.2, 0.18),
            (0.185, 0.5), (0.21, 0.52), (0.21, 0.58), (0.18, 0.6), (0.155, 1.12), (0.185, 1.14), (0.2, 1.17), (0.2, 1.25),
            (0.18, 1.28), (0.125, 1.28), (0.12, 1.05), (0, 1.05)]
    barrel = m.lathe(prof, 36, (0, -0.42, 0.56), iron, "barrel", rotation=(-72, 0, 0))
    bands = [m.lathe([(0.2, 0.5), (0.225, 0.515), (0.225, 0.585), (0.2, 0.6)], 36, (0, -0.42, 0.56), gold, "band", rotation=(-72, 0, 0))]
    W = Batch(wm)
    for x in (-1, 1):
        W.box((0.09, 1.25, 0.2), (x * 0.26, 0.0, 0.42), rx=0.1, mi=0)
        W.box((0.09, 0.5, 0.2), (x * 0.26, -0.2, 0.56), mi=1)
    W.box((0.5, 0.14, 0.14), (0, -0.55, 0.34), mi=2)
    W.box((0.5, 0.16, 0.1), (0, 0.5, 0.52), mi=2)
    parts = [barrel] + bands + [W.obj("carriage", 0.02)]
    parts.append(m.cylinder(0.05, 0.86, 12, 0.01, 1, (0, -0.15, 0.36), iron, "axle", rotation=(0, 90, 0)))
    for x in (-1, 1):
        parts.append(m.torus(0.32, 0.045, 32, 10, (x * 0.4, -0.15, 0.36), iron, "tyre", rotation=(0, 90, 0)))
        parts.append(m.torus(0.26, 0.04, 32, 10, (x * 0.4, -0.15, 0.36), wm[1], "rim", rotation=(0, 90, 0)))
        parts.append(m.cylinder(0.09, 0.14, 16, 0.02, 2, (x * 0.4, -0.15, 0.36), gold, "hub", rotation=(0, 90, 0)))
        Sp = Batch([wm[0]])
        for k in range(4):
            Sp.box((0.06, 0.05, 0.52), (x * 0.4, -0.15, 0.36), rx=math.pi * k / 4)
        parts.append(Sp.obj("spokes", 0.012))
    ob = done(parts, "cannon", loc, aim)
    ob.scale = (s, s, s)
    return ob


def base_disc(R=6.6, thick=0.5):
    """Round plank board with a felt play mat on top (top of the mat at z = 0.1). Returns [board, mat]."""
    wm = tints("painted_wood", "#E3A862", (1.0, 1.05, 0.94, 0.98))
    B = Batch(wm)
    pw = 1.1; n = math.ceil(2 * R / pw); x = -n * pw / 2
    for i in range(n):
        x0, x1 = max(x, -R), min(x + pw, R); x += pw
        if x1 - x0 < 0.05:
            continue
        xs = [x0 + (x1 - x0) * k / 8 for k in range(9)]
        y = lambda v: math.sqrt(max(R * R - v * v, 0.0004))
        pts = [(v + (0.012 if v == x0 else -0.012 if v == x1 else 0), -y(v)) for v in xs] + [(v + (0.012 if v == x0 else -0.012 if v == x1 else 0), y(v)) for v in reversed(xs)]
        B.prism(pts, -thick, 0, i % 4)
    top = B.obj("table", 0.04, 2)
    mat_ = m.cylinder(5.7, 0.1, 96, 0.04, 3, (0, 0, 0.05), M.make("fabric", "#7BD650"), "mat")
    return [top, mat_]


def cobbles(path):
    C = Batch(tints("clay", "#D8D2C4", (1.0, 1.06, 0.9, 0.96)))
    for (x, y) in path:
        for k in range(3):
            C.box((rng.uniform(0.3, 0.46), rng.uniform(0.26, 0.4), 0.09), (x + (k - 1) * 0.47 + rng.uniform(-0.04, 0.04), y + rng.uniform(-0.05, 0.05), 0.13),
                  rz=rng.uniform(-0.4, 0.4), mi=rng.randrange(4))
    return C.obj("cobbles", 0.05, 3)
