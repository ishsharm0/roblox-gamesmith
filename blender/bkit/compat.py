"""Version guards for Blender 4.2 - 5.3 (tested on 5.3.0).

Use these instead of touching the APIs that moved between versions:
EEVEE engine id, auto-smooth, the compositor node tree, the action/fcurve API,
and colour-management enum names.
"""
import math

import bpy

VERSION = bpy.app.version


def engine_id(kind="EEVEE"):
    """Return the render-engine identifier for kind 'EEVEE', 'CYCLES' or 'WORKBENCH'.
    EEVEE is 'BLENDER_EEVEE_NEXT' on 4.2-4.5 and 'BLENDER_EEVEE' on 5.x."""
    kind = kind.upper()
    if kind == "CYCLES":
        return "CYCLES"
    if kind == "WORKBENCH":
        return "BLENDER_WORKBENCH"
    items = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    for ident in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        if ident in items:
            return ident
    return "BLENDER_EEVEE"


def set_engine(scene=None, kind="EEVEE", gpu=True):
    """Switch the scene to 'EEVEE', 'CYCLES' or 'WORKBENCH'. For Cycles, enable the best GPU backend
    found (OPTIX, then CUDA, HIP, METAL, ONEAPI) unless gpu=False. Returns the engine id."""
    scene = scene or bpy.context.scene
    ident = engine_id(kind)
    scene.render.engine = ident
    if ident == "CYCLES" and gpu:
        enable_gpu(scene)
    elif ident == "CYCLES":
        scene.cycles.device = "CPU"
    return ident


def enable_gpu(scene=None):
    """Point Cycles at the GPU. Returns the backend name used, or 'CPU' when none is available."""
    scene = scene or bpy.context.scene
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except KeyError:
        return "CPU"
    for backend in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
        except (TypeError, AttributeError):
            continue
        devs = [d for d in prefs.devices if d.type == backend]
        if devs:
            for d in prefs.devices:
                d.use = d.type == backend
            scene.cycles.device = "GPU"
            return backend
    scene.cycles.device = "CPU"
    return "CPU"


def smooth_by_angle(obj, angle=30.0):
    """Smooth-shade a mesh object but keep edges sharper than `angle` degrees sharp.
    4.1+: Mesh.shade_smooth + set_sharp_from_angle. Older: use_auto_smooth."""
    me = obj.data
    if hasattr(me, "set_sharp_from_angle"):
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(angle))
    else:
        for p in me.polygons:
            p.use_smooth = True
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.radians(angle)


def shade_smooth(obj):
    """Smooth-shade every face (no sharp edges). Use before a Bevel + WeightedNormal stack."""
    me = obj.data
    if hasattr(me, "shade_smooth"):
        me.shade_smooth()
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.pi)
    else:
        for p in me.polygons:
            p.use_smooth = True
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.pi


def shade_flat(obj):
    """Flat-shade every face (faceted low-poly look)."""
    me = obj.data
    if hasattr(me, "shade_flat"):
        me.shade_flat()
    else:
        for p in me.polygons:
            p.use_smooth = False


def compositor(scene=None):
    """Return the scene's compositor node tree, creating it if needed.
    5.x: a CompositorNodeTree assigned to scene.compositing_node_group (with an Image output socket).
    4.x: scene.use_nodes + scene.node_tree."""
    scene = scene or bpy.context.scene
    if hasattr(scene, "compositing_node_group"):
        ng = scene.compositing_node_group
        if ng is None:
            ng = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            scene.compositing_node_group = ng
        if not any(s.in_out == "OUTPUT" for s in ng.interface.items_tree if getattr(s, "item_type", "SOCKET") == "SOCKET"):
            ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        return ng
    scene.use_nodes = True
    return scene.node_tree


def compositor_io(scene=None):
    """Return (tree, render_layers_node, output_input_socket). Link your last node's image into
    output_input_socket. Works on 4.x (Composite node) and 5.x (Group Output)."""
    scene = scene or bpy.context.scene
    nt = compositor(scene)
    rl = next((n for n in nt.nodes if n.bl_idname == "CompositorNodeRLayers"), None) or nt.nodes.new("CompositorNodeRLayers")
    if hasattr(scene, "compositing_node_group"):
        out = next((n for n in nt.nodes if n.bl_idname == "NodeGroupOutput"), None) or nt.nodes.new("NodeGroupOutput")
        sock = out.inputs[0]
    else:
        out = next((n for n in nt.nodes if n.bl_idname == "CompositorNodeComposite"), None) or nt.nodes.new("CompositorNodeComposite")
        sock = out.inputs["Image"]
    rl.location = (-400, 0)
    out.location = (400, 0)
    return nt, rl, sock


def fcurves(id_data):
    """All F-curves of an object's (or armature's) active action, on any version.
    5.x actions are layered: curves live in a channelbag per slot; 4.x: action.fcurves."""
    ad = getattr(id_data, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and not getattr(act, "is_action_layered", False):
        return list(act.fcurves)
    slot = getattr(ad, "action_slot", None)
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, slot)
        if cb is not None:
            return list(cb.fcurves)
    except (ImportError, AttributeError):
        pass
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            cb = strip.channelbag(slot) if slot is not None else None
            if cb:
                out.extend(cb.fcurves)
    return out


def set_enum(owner, prop, *candidates):
    """Set owner.prop to the first candidate value Blender accepts (enum names differ by version and
    OCIO config). Returns the value set, or None if none were accepted."""
    for c in candidates:
        try:
            setattr(owner, prop, c)
            return c
        except (TypeError, ValueError):
            continue
    return None


def socket(node, *names):
    """First input socket of `node` matching any of `names` (Principled names changed in 4.0)."""
    for n in names:
        s = node.inputs.get(n)
        if s is not None:
            return s
    return None


def material_nodes(mat):
    """Turn on nodes for a material (always on in 5.x) and return its node tree."""
    if not getattr(mat, "use_nodes", True):
        try:
            mat.use_nodes = True
        except AttributeError:
            pass
    return mat.node_tree


def world_nodes(world):
    """Same as material_nodes for a World."""
    if not getattr(world, "use_nodes", True):
        try:
            world.use_nodes = True
        except AttributeError:
            pass
    return world.node_tree


def set_blend_transparent(mat, refraction=False):
    """Make a material render transparency in EEVEE (blended, or ray-traced refraction for glass)."""
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED" if refraction else "BLENDED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    if refraction:
        for p in ("use_raytrace_refraction", "use_screen_refraction"):
            if hasattr(mat, p):
                setattr(mat, p, True)
