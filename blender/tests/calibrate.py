"""Diagnose dark moonlight, record geometry and shader values, and regress export defaults."""
import json
from pathlib import Path
import sys
import traceback
import bkit as b
import bpy
out=Path(sys.argv[sys.argv.index('--')+1])
records={}
for case in ('cyclorama','ground','fill'):
    b.scene.new_scene()
    duck=b.modelling.rubber_duck(2,location=(-.45,-.25,.5))
    box=b.modelling.rounded_box((2.8,2.4,.5),location=(0,0,.25),mat='toybox.blue')
    ball=b.modelling.sphere(.43,location=(1,.55,.93),mat=b.materials.chrome())
    subject=[duck,box,ball]
    b.scene.add_camera(subject,azimuth=32,elevation=23,margin=1.28)
    if case=='cyclorama':
        b.scene.cyclorama(subject=subject,color='#BCB6AB')
    else:
        b.scene.ground(color='#BCB6AB')
    lights=b.lighting.rig('night_moon',subject)
    if case=='fill':
        lights['fill'].data.energy*=4
    path=str(out/(case+'.png'))
    b.render.still(path,quality='good')
    records[case]=b.render.measure(path,crop=.65)
    records[case]['lights']={k:dict(energy=o.data.energy,color=list(o.data.color),location=list(o.location)) for k,o in lights.items()}
records['sockets']=[s.name for s in b.materials.bsdf(b.materials.metal_brushed()).inputs]
try:
    a=b.materials.atlas_from_materials(b.modelling.rounded_box(mat='toybox.red'))
    image=next(n.image for n in a.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
    c=b.materials.atlas_from_materials(b.modelling.rounded_box(mat='toybox.blue'))
    assert image.name in bpy.data.images and next(n.image for n in a.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')==image,'atlas changed an earlier prop'
    records['independent_atlas']='PASS'
except Exception:
    records['independent_atlas']=traceback.format_exc()
try:
    obj=b.materials.atlas_from_materials(b.modelling.crate(),name='Generated')
    b.export.fbx(obj,str(out/'generated.fbx'))
    b.export.obj(obj,str(out/'generated.obj'))
    mtl=(out/'generated.mtl').read_text()
    assert 'map_Kd' in mtl,'no atlas texture referenced'
    texture=next(line.split(' ',1)[1].strip() for line in mtl.splitlines() if line.startswith('map_Kd '))
    assert (out/texture).is_file(),'MTL points to a missing atlas image'
    records['generated_export']='PASS'
except Exception:
    records['generated_export']=traceback.format_exc()
(out/'calibrate.json').write_text(json.dumps(records,indent=2))
b.finish(0 if records['independent_atlas']=='PASS' and records['generated_export']=='PASS' else 1)
