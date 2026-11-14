"""Blender-only regression checks. Run with --in blender/tests. No Mac Blender."""
import json
import os
from pathlib import Path
import struct
import sys
import traceback
import bpy
import bkit as b
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

out, inputs = sys.argv[sys.argv.index('--')+1:][:2]
sys.path.insert(0, inputs)
results = {}
def check(name, fn):
    try:
        fn()
        results[name] = 'PASS'
    except Exception:
        results[name] = traceback.format_exc()
    print(name, results[name], flush=True)

def character():
    from character_checks import run
    run(out)

def camera():
    b.scene.new_scene()
    ob = b.modelling.rounded_box((2,3,5),location=(0,0,2.5))
    for res in [(960,960),(1080,1920),(1920,1080)]:
        bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y = res
        for ortho in (False,True):
            cam = b.scene.add_camera(ob,azimuth=35,elevation=23,ortho=ortho,margin=1.12)
            bpy.context.view_layer.update()
            vs = [world_to_camera_view(bpy.context.scene,cam,ob.matrix_world @ Vector(v)) for v in ob.bound_box]
            assert all(0 <= v.x <= 1 and 0 <= v.y <= 1 and v.z>0 for v in vs), (res,ortho,[(tuple(v)) for v in vs])
    bpy.context.scene.render.resolution_x=bpy.context.scene.render.resolution_y=960
    ob=b.modelling.rounded_box((2,2,2))
    cam=b.scene.add_camera(ob,azimuth=0,elevation=0,margin=1,target=(0,2,0))
    bpy.context.view_layer.update()
    vs=[world_to_camera_view(bpy.context.scene,cam,ob.matrix_world @ Vector(v)) for v in ob.bound_box]
    assert all(-1e-5<=v.x<=1.00001 and -1e-5<=v.y<=1.00001 and v.z>0 for v in vs), 'off-center target clips'
    b.scene.aim(cam,ob,ortho=True)
    b.scene.aim(cam,ob,ortho=False)
    assert cam.data.type=='PERSP'

def wood():
    b.scene.new_scene()
    mat=b.materials.painted_wood()
    shader=b.materials.bsdf(mat)
    link=shader.inputs['Base Color'].links[0]
    assert link.from_socket.type=='RGBA', 'wood connected to float output'
    assert all(not l.from_socket.is_unavailable and not l.to_socket.is_unavailable for l in mat.node_tree.links)

def atlas_exports():
    b.scene.new_scene()
    ob = b.modelling.crate()
    assert not b.export.report(ob)['ok']
    ob = b.materials.atlas_from_materials(ob, image_path=os.path.join(out,'atlas.png'))
    assert b.export.report(ob)['ok']
    assert all(all(abs(v-1)<.01 for v in d.color_srgb) for d in ob.data.color_attributes['Col'].data), 'atlas must not tint twice'
    b.materials.vertex_gradient(ob)
    b.export.glb(ob,os.path.join(out,'crate.glb'),animation=False)
    b.export.fbx(ob,os.path.join(out,'crate.fbx'))
    b.export.obj(ob,os.path.join(out,'crate.obj'))
    # Re-import our authored test exports directly; no third-party provenance is invented.
    for filename, importer in [('crate.glb',bpy.ops.import_scene.gltf),
                               ('crate.fbx',bpy.ops.import_scene.fbx),
                               ('crate.obj',bpy.ops.wm.obj_import)]:
        before=set(bpy.data.objects)
        importer(filepath=os.path.join(out,filename))
        meshes=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
        assert meshes and all(b.modelling.tri_count(o)>0 for o in meshes),filename
        assert all(len(o.data.materials)==1 and o.data.uv_layers for o in meshes),filename
    # Invalid UVs must actually fail the validator and strict export.
    ob.data.uv_layers.active.data[0].uv=(2,-1)
    assert not b.export.report(ob)['ok']
    try:
        b.export.fbx(ob,os.path.join(out,'invalid.fbx'))
    except ValueError:
        pass
    else:
        raise AssertionError('invalid UVs exported')

def animation_glb():
    b.scene.new_scene()
    ch = b.character.blocky_character()
    b.animation.walk(ch,start=1,end=25)
    path = b.export.glb(ch.rig,os.path.join(out,'walk.glb'))
    data=path.read_bytes()
    size,kind=struct.unpack_from('<II',data,12)
    doc=json.loads(data[20:20+size])
    assert doc.get('animations') and len(doc['animations'][0]['channels'])>0
    bpy.ops.import_scene.gltf(filepath=str(path))
    assert any(o.animation_data and b.compat.fcurves(o) for o in bpy.context.scene.objects)

def nodes():
    b.scene.new_scene()
    for look in b.scene.LOOKS:
        assert b.scene.set_look(look)[0]
    b.scene.world_gradient()
    b.scene.world_sky()
    nt,rl,sock=b.compat.compositor_io()
    nt.links.new(rl.outputs['Image'],sock)
    b.scene.shadow_catcher()

def misc():
    b.scene.new_scene(units='metric',fps=24,look='product')
    from bkit import _util as u
    assert u.srgb((255,0,0))==(1,0,0)
    assert u.mix('#000000','#FFFFFF',.5)==(.5,.5,.5)
    assert u.shade('#808080',.5)[0]<.3
    for palette in b.palettes.names():
        assert all(len(u.rgb(c))==3 for c in b.palettes.colors(palette))
    capsule=b.modelling.capsule(mat='toybox.red')
    b.modelling.place(capsule,location=(1,2,3),rotation=(10,20,30),scale=2)
    assert b.modelling.tri_count(capsule)>0
    hero=b.modelling.blocky_character(name='Extra')
    b.animation.key_pose(hero,1)
    assert b.compat.fcurves(hero.rig)
    lights=b.lighting.rig('studio_soft',capsule,warmth=.5)
    before=lights['key'].data.energy
    b.lighting.scale(lights,.5)
    assert abs(lights['key'].data.energy-before/2)<1e-4
    b.lighting.practical((0,0,3))
    b.lighting.add_light('POINT')
    b.lighting.add_light('SPOT')
    for quality in b.render.QUALITY:
        b.render.quality(quality)
    b.compat.set_engine(kind='CYCLES',gpu=False)
    assert bpy.context.scene.cycles.device=='CPU'
    tree=b.modelling.tree('pine')
    backdrop=b.scene.cyclorama(subject=tree)
    low,_=u.bounds(tree,precise=True)
    ground,_=u.bounds(backdrop,precise=True)
    assert abs(low.z-ground.z)<1e-5
    # Triangle and UV-set limits must fail independently.
    high=b.modelling.sphere(segments=128,rings=128,mat='toybox.blue')
    result=b.export.report(high)
    assert any('20000' in issue for mesh in result['meshes'] for issue in mesh['issues'])
    while high.data.uv_layers:
        high.data.uv_layers.remove(high.data.uv_layers[0])
    high.data.uv_layers.new(name='First')
    high.data.uv_layers.new(name='Second')
    assert any('UV set' in issue for mesh in b.export.report(high)['meshes'] for issue in mesh['issues'])

check('character_animation',character)
check('camera_fit',camera)
check('wood_shader',wood)
check('atlas_exports_roundtrip',atlas_exports)
check('animation_glb',animation_glb)
check('world_compositor',nodes)
check('public_helpers_limits',misc)
Path(out,'integration.json').write_text(json.dumps(dict(blender=bpy.app.version_string,checks=results),indent=2))
b.finish(0 if all(v=='PASS' for v in results.values()) else 1)
