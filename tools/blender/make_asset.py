"""Stylised low-poly game assets, built in studs, origin at base, palette coloured.

  Blender -b --python make_asset.py -- <kind> [--seed N] [--scale S] [--smooth] [--out DIR]
                                       [--fbx] [--glb] [--luau] [--preview]

kinds: tree, pine, bush, rock, crate, barrel, coin, gem, platform, fence   (or `all`)
Writes DIR/<kind>.blend (and .fbx/.glb/.luau/.png when asked). Default DIR: ./assets.
--seed varies the shape; --scale multiplies the authored size (sizes below are in studs; a Roblox
character is ~5 studs tall).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import rbxblend as R  # noqa: E402


def tree(b):
    """Broadleaf tree, ~14 studs tall: tapered 6-sided trunk, three faceted canopy blobs."""
    rng = b.rng
    h = rng.uniform(5.5, 7)
    trunk = R.bm_cylinder(0.9, 0.55, h, segs=6)
    for v in trunk.verts:   # slight lean
        v.co.x += 0.08 * v.co.z
    b.add(trunk, lambda f: "bark_dark" if f.normal.x < -0.3 else "bark")
    top = Vector((0.08 * h, 0, h))
    blobs = [(top + Vector((0, 0, 2.6)), 4.2), (top + Vector((2.2, 0.8, 1.4)), 3.0), (top + Vector((-1.9, -1.0, 1.6)), 2.9)]
    for i, (c, r) in enumerate(blobs[: 2 + rng.randint(0, 1)] if rng.random() < 0.3 else blobs):
        bm = R.bm_ico(r, 1, center=c, scale=(1, 1, 0.82))
        b.jitter(bm, r * 0.12, keep_base=False)
        b.add(bm, lambda f: "leaf_light" if f.normal.z > 0.55 else ("leaf_dark" if f.normal.z < -0.2 else "leaf"))


def pine(b):
    """Conifer, ~16 studs: short trunk and three stacked 8-sided cones."""
    rng = b.rng
    b.add(R.bm_cylinder(0.7, 0.5, 3.0, segs=6), "bark")
    z, r = 2.2, 4.4
    for i in range(3):
        h = 5.2 - i * 0.6
        bm = R.bm_cylinder(r, 0.25 if i < 2 else 0.0, h, segs=8, z0=z)
        b.jitter(bm, 0.18, keep_base=False)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rng.uniform(0, 1), 3, "Z"))
        b.add(bm, lambda f: "pine_dark" if f.normal.z < 0 else ("pine" if f.normal.x + f.normal.y < 0.4 else "leaf_dark"))
        z += h * 0.55; r *= 0.72


def bush(b):
    """Low shrub, ~3 studs tall: two or three squashed blobs."""
    rng = b.rng
    for i in range(rng.randint(2, 3)):
        c = Vector((rng.uniform(-1.2, 1.2), rng.uniform(-0.8, 0.8), 1.3))
        bm = R.bm_ico(rng.uniform(1.4, 1.9), 1, center=c, scale=(1, 1, 0.75))
        b.jitter(bm, 0.2, keep_base=False)
        b.add(bm, lambda f: "leaf_light" if f.normal.z > 0.55 else "leaf")


def rock(b):
    """Boulder, ~4 studs: flattened icosphere, faceted, flat bottom, moss on top faces."""
    rng = b.rng
    bm = R.bm_ico(2.4, 1, center=(0, 0, 1.6), scale=(rng.uniform(1.0, 1.4), rng.uniform(0.8, 1.1), 0.75))
    b.jitter(bm, 0.35, keep_base=False)
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    moss = rng.random() < 0.6
    b.add(bm, lambda f: ("moss" if moss and f.normal.z > 0.8 else
                         "rock_light" if f.normal.z > 0.45 else "rock_dark" if f.normal.z < -0.1 else "rock"))


def crate(b):
    """Wooden crate, 4 studs cube: dark core and 12 lighter edge planks."""
    s, t = 4.0, 0.5
    b.add(R.bm_box(s - 0.2, s - 0.2, s - 0.2, (0, 0, s / 2)), "wood_dark")
    h = s / 2 - t / 2
    for a in (-1, 1):
        for c in (-1, 1):
            b.add(R.bm_box(s, t, t, (0, a * h, s / 2 + c * h)), "wood")
            b.add(R.bm_box(t, s, t, (a * h, 0, s / 2 + c * h)), "wood")
            b.add(R.bm_box(t, t, s - 2 * t, (a * h, c * h, s / 2)), "wood_light")
    # one diagonal brace on front and back
    for y in (-s / 2 + 0.05, s / 2 - 0.05):
        bm = R.bm_box(t * 0.8, 0.12, (s - t) * 1.38, (0, 0, 0))
        bm.transform(Matrix.Translation((0, y, s / 2)) @ Matrix.Rotation(math.radians(45), 4, "Y"))
        b.add(bm, "wood")


def barrel(b):
    """Barrel, ~4 studs: 10-sided bulged body and two metal hoops."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.4, radius2=1.4, depth=4.0,
                          matrix=Matrix.Translation((0, 0, 2)))
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1],
                              cuts=2, use_grid_fill=False)
    for v in bm.verts:
        if 0.01 < v.co.z < 3.99:
            v.co.x *= 1.14; v.co.y *= 1.14
    b.add(bm, lambda f: "wood_dark" if f.normal.z > 0.9 else "wood")
    for z in (0.7, 3.3):
        b.add(R.bm_cylinder(1.62, 1.62, 0.3, segs=10, z0=z - 0.15), "metal")


def coin(b):
    """Collectible coin, 3 studs across, standing upright facing -Y (Roblox front)."""
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=1.5)
    face = bm.faces[0]
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=[e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)], vec=(0, 0, 0.35))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    caps = [f for f in bm.faces if abs(f.normal.z) > 0.9]
    bmesh.ops.inset_individual(bm, faces=caps, thickness=0.28, depth=-0.06)
    bm.transform(Matrix.Translation((0, 0, 1.5)) @ Matrix.Rotation(math.radians(90), 4, "X") @
                 Matrix.Translation((0, 0, -0.175)))
    b.add(bm, lambda f: "gold_light" if abs(f.normal.y) > 0.9 and f.calc_area() > 3 else
          ("gold_dark" if abs(f.normal.y) < 0.9 else "gold"))


def gem(b):
    """Cut gem, ~2.5 studs: 8-sided crown and pointed pavilion. --seed picks the colour."""
    rng = b.rng
    hue = rng.choice(["gem_blue", "gem_pink", "gem_purple", "gem_green"])
    bm = bmesh.new()
    n, rw, rt = 8, 1.1, 0.62
    tip = bm.verts.new((0, 0, 0))
    girdle = [bm.verts.new((rw * math.cos(2 * math.pi * i / n), rw * math.sin(2 * math.pi * i / n), 1.3)) for i in range(n)]
    table = [bm.verts.new((rt * math.cos(2 * math.pi * (i + .5) / n), rt * math.sin(2 * math.pi * (i + .5) / n), 2.1)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((tip, girdle[j], girdle[i]))
        bm.faces.new((girdle[i], girdle[j], table[i]))
        bm.faces.new((table[i], girdle[j], table[j]))
    bm.faces.new(table)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    b.add(bm, lambda f: "white" if f.normal.z > 0.95 else (hue if f.normal.z > 0 else hue + "_dark"))


def platform(b):
    """Floating island platform, 12 studs across: grass top, dirt band, rocky underside cone."""
    rng = b.rng
    segs, r = 9, 6.0
    top = R.bm_cylinder(r, r * 1.02, 0.8, segs=segs, z0=5.2)
    b.jitter(top, 0.12, keep_base=False)
    for v in top.verts:
        v.co.z = 6.0 if v.co.z > 5.6 else 5.2
    b.add(top, lambda f: "grass" if f.normal.z > 0.5 else "leaf")
    band = R.bm_cylinder(r * 0.98, r * 0.95, 1.0, segs=segs, z0=4.3)
    b.add(band, "dirt")
    under = R.bm_cylinder(0.6, r * 0.93, 4.3, segs=segs, z0=0.0)
    bmesh.ops.subdivide_edges(under, edges=[e for e in under.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1],
                              cuts=1, use_grid_fill=False)
    b.jitter(under, 0.35, keep_base=False)
    b.add(under, lambda f: "rock_dark" if f.normal.z < -0.6 else ("dirt_dark" if rng.random() < 0.5 else "rock"))


def fence(b):
    """Fence section, 8 studs long, 3.5 tall: two posts and two rails."""
    for x in (-3.7, 3.7):
        bm = R.bm_box(0.6, 0.6, 3.5, (x, 0, 1.75))
        b.add(bm, "wood_dark")
        b.add(_post_cap(x), "wood_dark")
    for z in (1.2, 2.6):
        b.add(R.bm_box(8.0, 0.3, 0.5, (0, 0, z)), "wood")


def _post_cap(x):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.42, radius2=0.0, depth=0.5,
                          matrix=Matrix.Translation((x, 0, 3.75)) @ Matrix.Rotation(math.radians(45), 4, "Z"))
    return bm


KINDS = {"tree": tree, "pine": pine, "bush": bush, "rock": rock, "crate": crate, "barrel": barrel,
         "coin": coin, "gem": gem, "platform": platform, "fence": fence}


def build(kind, seed=1, scale=1.0, smooth=False):
    b = R.Builder(kind.capitalize(), seed)
    KINDS[kind](b)
    ob = b.finish(smooth=smooth)
    if scale != 1.0:
        ob.data.transform(Matrix.Scale(scale, 4))
    return ob


def main():
    a = R.args()
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    kinds = list(KINDS) if a[0] == "all" else [a[0]]
    for k in kinds:
        if k not in KINDS:
            raise SystemExit(f"unknown kind {k}; one of {', '.join(KINDS)}")
    opt = lambda f, d=None: a[a.index(f) + 1] if f in a else d   # noqa: E731
    seed, scale = int(opt("--seed", 1)), float(opt("--scale", 1.0))
    out = os.path.abspath(opt("--out", "assets"))
    os.makedirs(out, exist_ok=True)
    for k in kinds:
        R.reset_scene()
        ob = build(k, seed, scale, "--smooth" in a)
        R.palette_image(os.path.join(out, "palette.png"))
        base = os.path.join(out, k)
        tris = R.tri_count(ob)
        bpy_save(base + ".blend")
        line = [f"{k}: {tris} tris, size {_size(ob)} studs -> {base}.blend"]
        if "--luau" in a:
            import to_luau_mesh
            to_luau_mesh.write([ob], base + ".luau", ob.name)
            line.append(".luau")
        if "--fbx" in a:
            R.export_fbx(base + ".fbx", [ob]); line.append(".fbx")
        if "--glb" in a:
            R.export_glb(base + ".glb", [ob]); line.append(".glb")
        if "--preview" in a:
            import preview
            preview.render([ob], base + ".png"); line.append(".png")
        print(" ".join(line))


def _size(ob):
    lo, hi = R.roblox_bounds([ob])
    return "x".join(f"{hi[i] - lo[i]:.1f}" for i in range(3))


def bpy_save(path):
    import bpy
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    try:
        os.remove(path + "1")   # Blender's backup copy
    except OSError:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        R.finish()
