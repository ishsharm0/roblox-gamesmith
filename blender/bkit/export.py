"""File export and evaluated Roblox budget reports. Does not upload or touch Studio."""
import json
import re
from pathlib import Path
import bpy
from ._util import as_list, descendants, mesh_objects, select

def report(objects, path=None):
    """Check evaluated meshes: <=20k triangles, exactly one material, one UV set in 0..1.
    Return {'ok', 'meshes':[{name,triangles,materials,uv_sets,issues}]}; optional JSON sidecar.
    This is the mesh import budget, not Marketplace avatar certification."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    meshes = []
    for ob in mesh_objects(objects):
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        try:
            tris = sum(len(p.vertices)-2 for p in me.polygons)
            issues = []
            if tris > 20000:
                issues.append('over 20000 triangles')
            if len(me.materials) != 1 or me.materials[0] is None:
                issues.append('requires exactly one material')
            if len(me.uv_layers) != 1:
                issues.append('requires exactly one UV set')
            if me.uv_layers and any(not (-1e-6 <= d.uv.x <= 1.000001 and -1e-6 <= d.uv.y <= 1.000001)
                                    for d in me.uv_layers.active.data):
                issues.append('UVs outside 0..1')
            meshes.append(dict(name=ob.name, triangles=tris, materials=len(me.materials),
                               uv_sets=len(me.uv_layers), issues=issues))
        finally:
            ev.to_mesh_clear()
    result = dict(ok=bool(meshes) and all(not m['issues'] for m in meshes), meshes=meshes)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(result, indent=2), encoding='utf8')
    return result

def _selected(objects):
    objs = []
    for ob in as_list(objects):
        for d in descendants(ob):
            if d not in objs:
                objs.append(d)
    select(objs)
    return objs

def _output(path):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)

def _save_generated_images(objects, directory):
    """FBX/OBJ require file-backed images, even when GLB accepts generated pixel buffers."""
    for obj in mesh_objects(objects):
        for material in obj.data.materials:
            if material is None or material.node_tree is None:
                continue
            for node in material.node_tree.nodes:
                if node.type != 'TEX_IMAGE' or node.image is None:
                    continue
                image = node.image
                if not image.filepath or not Path(bpy.path.abspath(image.filepath)).is_file():
                    filename = re.sub(r'[^A-Za-z0-9_.-]', '_', image.name) + '.png'
                    image.filepath_raw = str(directory / filename)
                    image.file_format = 'PNG'
                    image.save()

def glb(objects, path, animation=True):
    """Export selection + descendants as a GLB, including bone-parented animation and images.
    Procedural textures do not bake automatically. Return file Path after verifying it exists."""
    _selected(objects)
    path = _output(path)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=not animation, export_yup=True, export_animations=animation)
    if not Path(path).is_file() or Path(path).stat().st_size < 20:
        raise RuntimeError('GLB exporter produced no file')
    return Path(path)

def roblox(objects, path, format='FBX', strict=True, animation=False):
    """Export FBX or OBJ with a .report.json next to it. strict=True refuses failed budgets.
    First use materials.atlas_from_materials(objects, join=False) for color-only game meshes.
    Bone-parented boxes are an animation authoring rig; Roblox skinning needs a skinned rig."""
    path = _output(path)
    result = report(objects, path + '.report.json')
    if strict and not result['ok']:
        raise ValueError('Roblox mesh validation failed; inspect .report.json')
    _save_generated_images(objects, Path(path).parent)
    _selected(objects)
    if format.upper() == 'FBX':
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, path_mode='COPY', embed_textures=True,
                                 apply_scale_options='FBX_SCALE_UNITS', add_leaf_bones=False,
                                 bake_anim=animation, axis_forward='-Z', axis_up='Y')
    elif format.upper() == 'OBJ':
        bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, apply_modifiers=True,
                              forward_axis='NEGATIVE_Z', up_axis='Y', path_mode='COPY')
    else:
        raise ValueError('Roblox export format must be FBX or OBJ')
    if not Path(path).is_file() or Path(path).stat().st_size == 0:
        raise RuntimeError('exporter produced no file')
    return result

def fbx(objects, path, strict=True, animation=False):
    """Roblox FBX with report (Copy/embed textures, unit scaling, no leaf bones)."""
    return roblox(objects, path, 'FBX', strict, animation)

def obj(objects, path, strict=True):
    """Roblox static OBJ with report and accompanying MTL/images."""
    return roblox(objects, path, 'OBJ', strict)
