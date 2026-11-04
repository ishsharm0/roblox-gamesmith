"""Shared bpy helpers for the Blender -> Roblox scripts in this folder.

Conventions (see references/blender-pipeline.md):
  * 1 Blender unit = 1 stud. Scene unit system None, scale 1.0. (1 stud = 0.28 m.)
  * Blender is Z-up, model faces -Y (Blender's Front view). Roblox is Y-up, faces -Z.
    Blender (x, y, z) -> Roblox (-x, z, y). Same mapping as FBX export with Forward=Z, Up=Y.
  * Origin at the base centre of the asset.
  * Colour is per face: a vertex-colour attribute "Col" (corner domain, sRGB bytes) AND a UV into
    an 8x8 palette texture, so the same asset works with vertex colours (EditableMesh route) and
    with a texture (FBX/glTF upload route).

Run only inside Blender, headless:  Blender -b --python <script>.py -- args
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TRIS = 20000          # Roblox mesh import limit and EditableMesh limit (per mesh)
MAX_VERTS = 60000         # EditableMesh vertex limit

# Palette: 8x8 cells. Index -> (name, hex). Tuned as one family: warm greens, warm wood, cool stone.
PALETTE = [
    ("leaf", "5DAA4B"), ("leaf_dark", "3F8A3E"), ("leaf_light", "8CCB5E"), ("pine", "2F7A4F"),
    ("pine_dark", "235E3D"), ("bark", "7A4E2D"), ("bark_dark", "5A3720"), ("grass", "79C25A"),
    ("rock", "9A9AA0"), ("rock_dark", "74767E"), ("rock_light", "B9B8BC"), ("moss", "6F9A4A"),
    ("dirt", "8A5A3B"), ("dirt_dark", "6A422B"), ("sand", "E3C98F"), ("stone", "B8B2A7"),
    ("wood", "C08A4E"), ("wood_dark", "8E5E33"), ("wood_light", "D9A866"), ("metal", "5B5F66"),
    ("metal_light", "8C9199"), ("gold", "F2C14E"), ("gold_dark", "C9922E"), ("gold_light", "FFE08A"),
    ("gem_blue", "4FC3F7"), ("gem_blue_dark", "1E88C8"), ("gem_pink", "E0569B"), ("gem_pink_dark", "A8326E"),
    ("gem_purple", "8E6CF0"), ("gem_purple_dark", "5E43B8"), ("gem_green", "4FD69C"), ("gem_green_dark", "22A06B"),
    ("white", "F4F1EA"), ("black", "2A2A2E"), ("red", "D9534F"), ("orange", "F0913A"),
    ("yellow", "F5D547"), ("blue", "4A7BD0"), ("purple", "8A5CC2"), ("teal", "3BB3A6"),
]
PAL_INDEX = {n: i for i, (n, _) in enumerate(PALETTE)}
PAL_GRID = 8


def args():
    """Arguments after the `--` separator."""
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def pal_uv(idx):
    """UV of the centre of palette cell idx (Blender UV space, origin bottom-left)."""
    col, row = idx % PAL_GRID, idx // PAL_GRID
    return ((col + 0.5) / PAL_GRID, 1 - (row + 0.5) / PAL_GRID)


# ---------------------------------------------------------------- scene

def reset_scene():
    """Empty the current scene in place. (wm.read_factory_settings from a running script crashes
    Blender 5.0 on the next operator call, so data-blocks are removed instead.)"""
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras,
                 bpy.data.lights, bpy.data.worlds, bpy.data.armatures, bpy.data.actions):
        for block in list(coll):
            coll.remove(block)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    s = bpy.context.scene
    s.unit_settings.system = "NONE"
    s.unit_settings.scale_length = 1.0
    return s


def palette_image(path=None, cell=8):
    """The 64x64 palette texture (8x8 cells of 8 px). Saved to `path` if given."""
    name = "rbx_palette"
    img = bpy.data.images.get(name)
    size = PAL_GRID * cell
    if img is None:
        img = bpy.data.images.new(name, size, size, alpha=False)
        px = [0.0] * (size * size * 4)
        for i, (_, h) in enumerate(PALETTE):
            r, g, b = (srgb_to_linear(c) for c in hex_rgb(h))
            col, row = i % PAL_GRID, i // PAL_GRID
            for y in range(cell):
                for x in range(cell):
                    py = size - 1 - (row * cell + y)   # Blender pixel rows go bottom-up
                    o = (py * size + col * cell + x) * 4
                    px[o:o + 4] = (r, g, b, 1.0)
        img.pixels = px
    if path:
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
    return img


def palette_material():
    m = bpy.data.materials.get("Palette")
    if m:
        return m
    m = bpy.data.materials.new("Palette")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = palette_image()
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    return m


# ---------------------------------------------------------------- building

class Builder:
    """Accumulates coloured geometry in one bmesh; finish() makes the object."""

    def __init__(self, name, seed=1):
        self.name = name
        self.bm = bmesh.new()
        self.rng = random.Random(seed)

    def add(self, other_bm, col, matrix=None):
        """Merge a temporary bmesh in, colouring each new face `col`: a palette name, or a
        callable(face) -> name evaluated on the face as built (normals are valid)."""
        if matrix is not None:
            other_bm.transform(matrix)
        bmesh.ops.recalc_face_normals(other_bm, faces=other_bm.faces)
        other_bm.normal_update()
        cols = [col(f) if callable(col) else col for f in other_bm.faces]
        # The palette index rides along as an int face attribute "pal". Write it on the incoming
        # bmesh so from_mesh merges it; a layer handle held across from_mesh goes stale.
        lay = other_bm.faces.layers.int.new("pal")
        for f, c in zip(other_bm.faces, cols):
            f[lay] = PAL_INDEX[c]
        me = bpy.data.meshes.new("tmp")
        other_bm.to_mesh(me)
        other_bm.free()
        self.bm.from_mesh(me)
        bpy.data.meshes.remove(me)

    def jitter(self, bm, amount, keep_base=True):
        for v in bm.verts:
            if keep_base and v.co.z <= 1e-4:
                v.co.x += self.rng.uniform(-amount, amount)
                v.co.y += self.rng.uniform(-amount, amount)
                continue
            v.co += Vector([self.rng.uniform(-amount, amount) for _ in range(3)])

    def finish(self, smooth=False, base_origin=True):
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        apply_palette(ob)
        for p in me.polygons:
            p.use_smooth = smooth
        if base_origin:
            origin_to_base(ob)
        ob.data.materials.append(palette_material())
        return ob


def apply_palette(ob):
    """From the int face attribute 'pal': write corner colours 'Col' and palette UVs 'UVMap'."""
    me = ob.data
    pal = me.attributes.get("pal")
    if pal is None:
        return
    uv = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    col = me.color_attributes.get("Col") or me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
    for p in me.polygons:
        idx = pal.data[p.index].value
        r, g, b = hex_rgb(PALETTE[idx][1])
        u, v = pal_uv(idx)
        for li in p.loop_indices:
            uv.data[li].uv = (u, v)
            col.data[li].color_srgb = (r, g, b, 1.0)
    me.color_attributes.active_color = col
    me.color_attributes.render_color_index = me.color_attributes.find("Col")


def origin_to_base(ob):
    """Put the object origin at the centre of its bounding-box floor and the object at world 0."""
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    me.transform(Matrix.Translation(-off))
    ob.location = (0, 0, 0)


# primitives returning bmesh (Blender units = studs, Z up)

def bm_cylinder(r1, r2, h, segs=8, z0=0.0, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=h,
                          matrix=Matrix.Translation((0, 0, z0 + h / 2)))
    return bm


def bm_box(sx, sy, sz, center=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(center) @ Matrix.Diagonal((sx, sy, sz, 1)))
    return bm


def bm_ico(radius, subdiv=1, center=(0, 0, 0), scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius,
                               matrix=Matrix.Translation(center) @ Matrix.Diagonal((*scale, 1)))
    return bm


# ---------------------------------------------------------------- inspection

def mesh_objects(selected_only=False):
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]
    if selected_only:
        obs = [o for o in obs if o.select_get()] or obs
    return obs


def tri_count(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ob.evaluated_get(dg).to_mesh_clear()
    return n


def roblox_bounds(obs):
    """World-space bounds of objects in Roblox axes/studs: (min, max) as lists."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo = [math.inf] * 3; hi = [-math.inf] * 3
    for ob in obs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            w = ob.matrix_world @ v.co
            r = (-w.x, w.z, w.y)
            for i in range(3):
                lo[i] = min(lo[i], r[i]); hi[i] = max(hi[i], r[i])
        ev.to_mesh_clear()
    return lo, hi


def check_limits(obs, max_tris=MAX_TRIS):
    report, bad = [], []
    for ob in obs:
        n = tri_count(ob)
        report.append({"object": ob.name, "tris": n})
        if n > max_tris:
            bad.append(f"{ob.name}: {n} triangles > {max_tris} (decimate or split it)")
    return report, bad


def apply_transforms(obs):
    """Bake rotation/scale into mesh data so the exported mesh matches what you see."""
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def write_sidecar(out_path, obs, fmt):
    lo, hi = roblox_bounds(obs)
    report, _ = check_limits(obs)
    info = {"file": os.path.basename(out_path), "format": fmt,
            "size_studs": [round(hi[i] - lo[i], 3) for i in range(3)],
            "min_studs": [round(x, 3) for x in lo], "max_studs": [round(x, 3) for x in hi],
            "meshes": report}
    with open(os.path.splitext(out_path)[0] + ".rbx.json", "w") as f:
        json.dump(info, f, indent=1)
    return info


# ---------------------------------------------------------------- export

def _select(obs):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
        # parents/armatures come along for skinned meshes
        if ob.parent:
            ob.parent.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]


def export_fbx(path, obs=None):
    obs = obs or mesh_objects()
    _, bad = check_limits(obs)
    if bad:
        raise SystemExit("over the limit:\n  " + "\n  ".join(bad))
    apply_transforms(obs)
    _select(obs)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"MESH", "ARMATURE", "EMPTY"},
        global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="Z", axis_up="Y", use_space_transform=True, bake_space_transform=False,
        use_mesh_modifiers=True, mesh_smooth_type="FACE", colors_type="SRGB", use_tspace=False,
        add_leaf_bones=False, use_armature_deform_only=True, bake_anim=False,
        path_mode="COPY", embed_textures=True)
    return write_sidecar(path, obs, "fbx")


def export_glb(path, obs=None):
    obs = obs or mesh_objects()
    _, bad = check_limits(obs)
    if bad:
        raise SystemExit("over the limit:\n  " + "\n  ".join(bad))
    apply_transforms(obs)
    _select(obs)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_yup=True, export_apply=True,
              export_texcoords=True, export_normals=True, export_materials="EXPORT", export_animations=False)
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    if "export_vertex_color" in props:          # Blender 4.2+
        kw["export_vertex_color"] = "ACTIVE"
    elif "export_colors" in props:
        kw["export_colors"] = True
    bpy.ops.export_scene.gltf(**{k: v for k, v in kw.items() if k in props})
    return write_sidecar(path, obs, "glb")


def import_any(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
    elif ext == ".fbx":
        reset_scene(); bpy.ops.import_scene.fbx(filepath=path)
    elif ext in (".glb", ".gltf"):
        reset_scene(); bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".obj":
        reset_scene(); bpy.ops.wm.obj_import(filepath=path)
    else:
        raise SystemExit(f"can't read {path}")


def finish(code=0):
    """Leave Blender without its teardown. Blender 5.0.1 can double-free mesh data while freeing the
    scene on exit (CustomDataLayerImplicitSharing::delete_self_with_data), and each crash puts a
    "Blender quit unexpectedly" alert in front of the person using this Mac. Outputs are written
    before this is called, so skipping teardown loses nothing."""
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
