"""Blender meshes -> a Luau ModuleScript that MeshLoader.luau rebuilds as MeshParts at runtime.

  Blender -b in.blend --python to_luau_mesh.py -- out.luau [--name Name] [--objects A,B]
                                                [--material SmoothPlastic]
  (also accepts .fbx/.glb/.obj via --in path instead of a .blend)

No upload, no API key: the mesh lives in the place as source text and persists with it. Each mesh
object becomes one MeshPart (one Model when there are several). Per mesh: <= 20,000 triangles and
<= 60,000 vertices (EditableMesh limits).

Blob layout (little endian, base64 in the module), format "rbxmesh/1":
  "RBM1", u32 nV nN nC nU nT, f32 min[3] max[3]
  nV x u16[3] positions quantised into [min, max]  (Roblox axes, studs, relative to the asset origin)
  nN x i8[3]  normals * 127
  nC x u8[4]  sRGB colour + alpha
  nU x u16[2] UV (Roblox: v down)
  nT x u16[12] per triangle: 3 vertex, 3 normal, 3 colour, 3 uv indices (0-based), counter-clockwise
Custom object properties honoured: rbx_material (Enum.Material name), rbx_name.
"""
import base64
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import rbxblend as R  # noqa: E402


def _q16(x, lo, hi):
    return 0 if hi - lo < 1e-9 else max(0, min(65535, round((x - lo) / (hi - lo) * 65535)))


def _material_colour(ob, poly):
    if poly.material_index < len(ob.material_slots):
        m = ob.material_slots[poly.material_index].material
        if m:
            c = m.diffuse_color
            if m.use_nodes:
                bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                if bsdf and not bsdf.inputs["Base Color"].is_linked:
                    c = bsdf.inputs["Base Color"].default_value
            lin = [c[0], c[1], c[2]]
            srgb = [x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055 for x in lin]
            return tuple(max(0, min(255, round(x * 255))) for x in srgb) + (255,)
    return (255, 255, 255, 255)


def encode(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    mw = ob.matrix_world
    rot = mw.to_3x3().inverted().transposed()
    col_attr = me.color_attributes.active_color
    uv_layer = me.uv_layers.active
    corner_normals = me.corner_normals if hasattr(me, "corner_normals") else None

    vmap, verts = {}, []
    nmap, norms = {}, []
    cmap, cols = {}, []
    umap, uvs = {}, []
    tris = []

    def idx(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i

    for lt in me.loop_triangles:
        poly = me.polygons[lt.polygon_index]
        vi, ni, ci, ui = [], [], [], []
        for k in range(3):
            v, li = lt.vertices[k], lt.loops[k]
            if v not in vmap:
                w = mw @ me.vertices[v].co
                vmap[v] = len(verts)
                verts.append((-w.x, w.z, w.y))
            vi.append(vmap[v])
            if poly.use_smooth and corner_normals is not None:
                n = corner_normals[li].vector
            else:
                n = poly.normal
            n = (rot @ n).normalized()
            ni.append(idx(nmap, norms, tuple(max(-127, min(127, round(c * 127))) for c in (-n.x, n.z, n.y))))
            if col_attr is not None:
                d = col_attr.data[li if col_attr.domain == "CORNER" else v]
                c = d.color_srgb
                ci.append(idx(cmap, cols, tuple(max(0, min(255, round(x * 255))) for x in c)))
            else:
                ci.append(idx(cmap, cols, _material_colour(ob, poly)))
            if uv_layer is not None:
                u, vv = uv_layer.uv[li].vector
                ui.append(idx(umap, uvs, (max(0, min(65535, round(u * 65535))), max(0, min(65535, round((1 - vv) * 65535))))))
            else:
                ui.append(idx(umap, uvs, (0, 0)))
        tris.append(vi + ni + ci + ui)
    ev.to_mesh_clear()

    nV, nT = len(verts), len(tris)
    if nT > R.MAX_TRIS or nV > R.MAX_VERTS:
        raise SystemExit(f"{ob.name}: {nT} tris / {nV} verts is over the EditableMesh limit "
                         f"({R.MAX_TRIS} / {R.MAX_VERTS}); decimate or split it")
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    out = bytearray(b"RBM1")
    out += struct.pack("<5I", nV, len(norms), len(cols), len(uvs), nT)
    out += struct.pack("<6f", *lo, *hi)
    for v in verts:
        out += struct.pack("<3H", *(_q16(v[i], lo[i], hi[i]) for i in range(3)))
    for n in norms:
        out += struct.pack("<3b", *n)
    for c in cols:
        out += struct.pack("<4B", *c)
    for u in uvs:
        out += struct.pack("<2H", *u)
    for t in tris:
        out += struct.pack("<12H", *t)
    return bytes(out), nT, lo, hi


def write(obs, path, name=None, material=None):
    meshes, lo, hi, total = [], [1e9] * 3, [-1e9] * 3, 0
    for ob in obs:
        blob, nT, mlo, mhi = encode(ob)
        total += nT
        lo = [min(lo[i], mlo[i]) for i in range(3)]
        hi = [max(hi[i], mhi[i]) for i in range(3)]
        b64 = base64.b64encode(blob).decode()
        chunks = ",\n\t\t\t\t".join(f'"{b64[i:i + 1000]}"' for i in range(0, len(b64), 1000))
        mat = material or ob.get("rbx_material", "SmoothPlastic")
        meshes.append(f'\t\t{{\n\t\t\tname = "{ob.get("rbx_name", ob.name)}",\n\t\t\tmaterial = "{mat}",\n'
                      f'\t\t\ttris = {nT},\n\t\t\tdata = table.concat({{\n\t\t\t\t{chunks},\n\t\t\t}}),\n\t\t}},')
    name = name or (obs[0].name if len(obs) == 1 else os.path.splitext(os.path.basename(path))[0])
    size = [round(hi[i] - lo[i], 3) for i in range(3)]
    src = os.path.basename(bpy.data.filepath) or "generated scene"
    text = (f"-- Generated by tools/blender/to_luau_mesh.py from {src}; rebuild with MeshLoader.\n"
            f"-- {name}: {len(meshes)} mesh(es), {total} triangles, {size[0]} x {size[1]} x {size[2]} studs\n"
            f"return {{\n\tformat = \"rbxmesh/1\",\n\tname = \"{name}\",\n"
            f"\tsize = {{ {size[0]}, {size[1]}, {size[2]} }},\n\tmeshes = {{\n" + "\n".join(meshes) + "\n\t},\n}\n")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    return total, len(text)


def main():
    a = R.args()
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    opt = lambda f, d=None: a[a.index(f) + 1] if f in a else d   # noqa: E731
    if opt("--in"):
        R.import_any(os.path.abspath(opt("--in")))
    obs = R.mesh_objects()
    if opt("--objects"):
        want = opt("--objects").split(",")
        obs = [o for o in obs if o.name in want]
    if not obs:
        raise SystemExit("no mesh objects to export")
    tris, nbytes = write(obs, os.path.abspath(a[0]), opt("--name"), opt("--material"))
    print(f"wrote {a[0]}: {len(obs)} mesh(es), {tris} tris, {nbytes / 1024:.1f} KB of source")


if __name__ == "__main__":
    try:
        main()
    finally:
        R.finish()
