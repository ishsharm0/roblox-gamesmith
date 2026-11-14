"""Every material on an identical test ball, same studio."""
import json
from pathlib import Path
import sys
import bkit as b

out = Path(sys.argv[sys.argv.index('--')+1])
args = sys.argv[sys.argv.index('--')+3:]
engine = args[0] if args else 'EEVEE'
records, paths = {}, []
for kind in b.materials.KINDS:
    if len(args)>1 and kind!=args[1]:
        continue
    b.scene.new_scene(engine=engine)
    if len(args)>2 and args[2]=='CPU':
        import bpy
        b.compat.set_engine(kind='CYCLES',gpu=False)
        bpy.context.scene.render.threads_mode='FIXED'
        bpy.context.scene.render.threads=8
    mat = b.materials.make(kind, '#D68C55' if kind not in ('chrome','metal_brushed','glass') else '#D6DEE6')
    ball = b.modelling.sphere(1, segments=64, rings=32, location=(0,0,1.28), mat=mat)
    base = b.modelling.cylinder(1.05,.28,verts=64,location=(0,0,.14),mat='product.graphite')
    subject = [ball,base]
    b.scene.add_camera(subject,azimuth=25,elevation=18,margin=1.3)
    b.scene.cyclorama(subject=subject,color='#BCB6AB')
    b.lighting.rig('studio_soft',subject)
    path = out / (kind+'.png')
    records[kind] = b.render.still(str(path),quality='fast' if len(args)>2 and args[2]=='CPU' else 'good')
    records[kind].pop('path')
    records[kind].update(b.render.measure(str(path),crop=.65))
    paths.append(str(path))
b.render.contact_sheet(paths,str(out/'materials.png'),cols=5,tile=(320,320),labels=list(records),title=engine+' MATERIALS')
(out/'metrics.json').write_text(json.dumps(records,indent=2))
b.finish()
