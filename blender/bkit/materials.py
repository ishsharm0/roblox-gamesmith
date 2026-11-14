"""Materials with calibrated Principled BSDF settings, plus Roblox-safe colouring.

Every function takes `color` as '#RRGGBB', 'palette.name' (see palettes.py) or an sRGB tuple, and
returns a bpy Material (reused when called again with the same name). Assign with assign(obj, mat).

Only the Principled basics (base colour, metallic, roughness, emission, alpha, one image) survive
GLB/FBX export. The procedural extras here (wood grain, fabric noise, brushed streaks) are
render-only: for export use atlas_from_materials().
"""
import bpy
import numpy as np

from . import compat
from ._util import rgb, rgba, srgb, srgb_to_linear, mesh_objects

# Calibrated on Blender 5.3 (EEVEE and Cycles), studio_soft and toy_bright rigs, AgX view.
PRESETS = {
    "toy_plastic":   dict(roughness=0.32, specular=0.5, coat=0.0, subsurface=0.0),
    "clay":          dict(roughness=0.75, specular=0.25, sheen=0.25),
    "rubber":        dict(roughness=0.48, specular=0.35, coat=0.15, coat_roughness=0.25),
    "painted_wood":  dict(roughness=0.55, specular=0.4),
    "metal_brushed": dict(metallic=1.0, roughness=0.32, anisotropic=0.6),
    "chrome":        dict(metallic=1.0, roughness=0.06),
    "glass":         dict(roughness=0.02, transmission=1.0, ior=1.45),
    "car_paint":     dict(metallic=0.55, roughness=0.38, coat=1.0, coat_roughness=0.03),
    "fabric":        dict(roughness=0.92, specular=0.15, sheen=0.7, sheen_roughness=0.35),
}

_SOCKETS = {
    "metallic": ("Metallic",), "roughness": ("Roughness",), "ior": ("IOR",),
    "specular": ("Specular IOR Level", "Specular"), "coat": ("Coat Weight", "Clearcoat"),
    "coat_roughness": ("Coat Roughness", "Clearcoat Roughness"),
    "subsurface": ("Subsurface Weight", "Subsurface"), "sheen": ("Sheen Weight", "Sheen"),
    "sheen_roughness": ("Sheen Roughness",), "transmission": ("Transmission Weight", "Transmission"),
    "anisotropic": ("Anisotropic",), "alpha": ("Alpha",),
}


def principled(name, color="#BBBBBB", reuse=True, **params):
    """A plain Principled BSDF material. params: metallic, roughness, specular, coat, coat_roughness,
    subsurface, sheen, sheen_roughness, transmission, anisotropic, ior, alpha, emission (strength),
    emission_color. Returns the material."""
    if reuse and name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    nt = compat.material_nodes(m)
    b = bsdf(m)
    b.inputs["Base Color"].default_value = rgba(color)
    for k, v in params.items():
        if k in ("emission", "emission_color"):
            continue
        s = compat.socket(b, *_SOCKETS[k])
        if s is not None:
            s.default_value = v
    if params.get("emission"):
        compat.socket(b, "Emission Color", "Emission").default_value = rgba(params.get("emission_color", color))
        compat.socket(b, "Emission Strength").default_value = params["emission"]
    if params.get("subsurface"):
        s = compat.socket(b, "Subsurface Radius")
        if s is not None:
            s.default_value = (0.3, 0.15, 0.08)
        s = compat.socket(b, "Subsurface Scale")
        if s is not None:
            s.default_value = 0.05
    m.diffuse_color = rgba(color)  # viewport/workbench colour
    m.roughness = params.get("roughness", 0.5)
    return m


def bsdf(mat):
    """The Principled BSDF node of a material (found by type, not by name)."""
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _named(kind, color, name):
    return name or f"{kind}_{_hexname(color)}"


def _hexname(color):
    return "".join(f"{round(c * 255):02X}" for c in srgb(color))


def toy_plastic(color="toybox.red", name=None):
    """Glossy injection-moulded plastic (LEGO, toy figures). Best default for stylised props."""
    return principled(_named("toy_plastic", color, name), color, **PRESETS["toy_plastic"])


def clay(color="#C9B8A6", name=None):
    """Matte clay/plasticine: soft highlight, faint sheen. Good for 'claymation' looks and form checks."""
    return principled(_named("clay", color, name), color, **PRESETS["clay"])


def rubber(color="toybox.yellow", name=None):
    """Bath-toy rubber/vinyl: satin, slightly softer than plastic."""
    return principled(_named("rubber", color, name), color, **PRESETS["rubber"])


def painted_wood(color="fortress.wood", name=None, grain=0.12):
    """Painted or stained wood with a faint procedural grain (render only; exports as flat colour).
    grain 0 = no grain, 0.1-0.2 = subtle."""
    name = _named("painted_wood", color, name)
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = principled(name, color, **PRESETS["painted_wood"])
    if grain > 0:
        nt = m.node_tree
        b = bsdf(m)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1.0, 1.0, 12.0)
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"
        wave.inputs["Scale"].default_value = 2.0
        wave.inputs["Distortion"].default_value = 6.0
        wave.inputs["Detail"].default_value = 2.0
        mixn = nt.nodes.new("ShaderNodeMix")
        mixn.data_type = "RGBA"
        mixn.blend_type = "MULTIPLY"
        mixn.inputs["Factor"].default_value = grain
        mixn.inputs["A"].default_value = rgba(color)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
        nt.links.new(wave.outputs["Color"], mixn.inputs["B"])
        nt.links.new(mixn.outputs["Result"], b.inputs["Base Color"])
    return m


def metal_brushed(color="#B8BCC2", name=None):
    """Brushed steel/aluminium: metallic, anisotropic streaks along the object's X axis."""
    return principled(_named("metal_brushed", color, name), color, **PRESETS["metal_brushed"])


def chrome(color="#E6E8EB", name=None):
    """Mirror chrome. Needs something to reflect: use an HDRI world or a bright backdrop."""
    return principled(_named("chrome", color, name), color, **PRESETS["chrome"])


def glass(color="#DDEFF5", name=None):
    """Clear glass (tint with color). EEVEE: uses ray-traced refraction; Cycles: physically correct."""
    name = _named("glass", color, name)
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = principled(name, color, **PRESETS["glass"])
    compat.set_blend_transparent(m, refraction=True)
    return m


def emissive(color="toybox.yellow", strength=4.0, name=None):
    """Self-lit surface (lamps, screens, magic). strength 2-6 glows under AgX; >8 blows out to white."""
    return principled(_named(f"emissive{strength:g}", color, name), color, roughness=0.5,
                      emission=strength, emission_color=color)


def car_paint(color="toybox.red", name=None):
    """Metallic paint under a mirror clearcoat (cars, hero props)."""
    return principled(_named("car_paint", color, name), color, **PRESETS["car_paint"])


def fabric(color="toybox.blue", name=None):
    """Cloth/felt: very rough with sheen at grazing angles (flags, cushions, clothes)."""
    return principled(_named("fabric", color, name), color, **PRESETS["fabric"])


def matte(color="#BDB7AE", name=None, roughness=0.95):
    """Plain matte surface (backdrops, ground, tables)."""
    return principled(_named(f"matte{roughness:g}", color, name), color, roughness=roughness, specular=0.3)


KINDS = {"toy_plastic": toy_plastic, "clay": clay, "rubber": rubber, "painted_wood": painted_wood,
         "metal_brushed": metal_brushed, "chrome": chrome, "glass": glass, "emissive": emissive,
         "car_paint": car_paint, "fabric": fabric, "matte": matte}


def make(kind, color, name=None):
    """Material by kind name: make('toy_plastic', 'toybox.red'). Kinds: see KINDS."""
    return KINDS[kind](color, name=name)


def assign(objs, mat, slot=0):
    """Give each mesh object `mat` (replacing material slot `slot`, adding it if missing)."""
    for o in mesh_objects(objs):
        mats = o.data.materials
        if len(mats) > slot:
            mats[slot] = mat
        else:
            mats.append(mat)
    return mat


# ---------------------------------------------------------------- Roblox / export colouring

def _material_color(mat):
    if mat is None:
        return (0.7, 0.7, 0.7)
    try:
        c = bsdf(mat).inputs["Base Color"].default_value
        lin = (c[0], c[1], c[2])
    except (StopIteration, AttributeError, KeyError):
        lin = tuple(mat.diffuse_color[:3])
    return tuple(_linear_to_srgb(v) for v in lin)


def _linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def palette_image(colors, name="bkit_atlas", cell=8, path=None):
    """Build a square atlas image of flat colour swatches (sRGB tuples/specs), `cell` px each.
    Returns (image, uv_of(index)) where uv_of gives the UV centre of a swatch."""
    n = len(colors)
    grid = 1
    while grid * grid < n:
        grid *= 2
    size = grid * cell
    px = np.ones((size, size, 4), dtype=np.float32)
    for i, c in enumerate(colors):
        col, row = i % grid, i // grid
        r, g, b = srgb(c)
        y0 = size - (row + 1) * cell  # image rows go bottom-up
        px[y0:y0 + cell, col * cell:(col + 1) * cell, :3] = (r, g, b)
    img = bpy.data.images.new(name, size, size, alpha=False)
    img.pixels.foreach_set(px.ravel())
    if path:
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()

    def uv_of(i):
        return ((i % grid + 0.5) / grid, 1 - (i // grid + 0.5) / grid)
    return img, uv_of


def atlas_from_materials(objs, name="Atlas", join=True, image_path=None, roughness=0.6):
    """Make objs Roblox/three.js-ready: every face's material base colour goes into one small swatch
    atlas (one image, one material), each face is UV'd into its swatch (all UVs inside 0-1), and a
    white 'Col' vertex-colour attribute can modulate it (no duplicate colour multiplication).
    With join=True the objects are joined
    into one mesh (modifiers applied first). Returns the resulting object(s)."""
    objs = mesh_objects(objs)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    swatches, index = [], {}
    results = []
    for o in objs:
        # apply modifiers into new mesh data
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        cols = []
        for p in me.polygons:
            mat = o.material_slots[p.material_index].material if o.material_slots else None
            c = tuple(round(v, 3) for v in _material_color(mat))
            if c not in index:
                index[c] = len(swatches)
                swatches.append(c)
            cols.append(index[c])
        o.modifiers.clear()
        o.data = me
        me["bkit_swatch"] = cols
        results.append(o)
    img, uv_of = palette_image(swatches, name=name + "_img", path=image_path)
    mat = principled(name, "#FFFFFF", reuse=False, roughness=roughness, specular=0.4)
    nt = mat.node_tree
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf(mat).inputs["Base Color"])
    for o in results:
        me = o.data
        cols = list(me["bkit_swatch"])
        del me["bkit_swatch"]
        while me.uv_layers:
            me.uv_layers.remove(me.uv_layers[0])
        uv = me.uv_layers.new(name="UVMap")
        for old_color in list(me.color_attributes):
            me.color_attributes.remove(old_color)
        ca = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
        me.color_attributes.active_color = ca
        for p, si in zip(me.polygons, cols):
            u, v = uv_of(si)
            r, g, b = swatches[si]
            for li in p.loop_indices:
                uv.data[li].uv = (u, v)
                ca.data[li].color_srgb = (1.0, 1.0, 1.0, 1.0)
            p.material_index = 0
        me.materials.clear()
        me.materials.append(mat)
    if join and len(results) > 1:
        from ._util import select
        select(results, results[0])
        bpy.ops.object.join()
        return results[0]
    return results[0] if len(results) == 1 else results


def vertex_gradient(objs, bottom=0.72, top=1.08, attr="Col"):
    """Darken the bottom and lighten the top of each object's 'Col' vertex colours (cheap baked
    ambient occlusion, the Kenney/Synty trick). Run after atlas_from_materials()."""
    for o in mesh_objects(objs):
        me = o.data
        ca = me.color_attributes.get(attr)
        if ca is None:
            continue
        zs = [v.co.z for v in me.vertices]
        z0, z1 = min(zs), max(zs)
        h = max(z1 - z0, 1e-6)
        for p in me.polygons:
            for li in p.loop_indices:
                vi = me.loops[li].vertex_index
                t = (me.vertices[vi].co.z - z0) / h
                f = bottom + (top - bottom) * t
                c = ca.data[li].color_srgb
                ca.data[li].color_srgb = (min(c[0] * f, 1), min(c[1] * f, 1), min(c[2] * f, 1), 1.0)
