"""Every rig on exactly the same toy subject; optional -- CYCLES."""
import json
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
args=sys.argv[sys.argv.index('--')+3:]
engine=args[0] if args else 'EEVEE'
records,paths={},[]
for name in b.lighting.RIGS:
    if len(args)>1 and name!=args[1]:
        continue
    b.scene.new_scene(engine=engine)
    duck=b.modelling.rubber_duck(2,location=(-.45,-.25,.5))
    box=b.modelling.rounded_box((2.8,2.4,.5),location=(0,0,.25),mat='toybox.blue')
    ball=b.modelling.sphere(.43,location=(1,.55,.93),mat=b.materials.chrome())
    subject=[duck,box,ball]
    b.scene.add_camera(subject,azimuth=32,elevation=23,margin=1.28)
    b.scene.cyclorama(subject=subject,color='#BCB6AB')
    lights=b.lighting.rig(name,subject)
    path=out/(name+'.png')
    records[name]=b.render.still(str(path),quality='good')
    records[name].pop('path')
    records[name].update(b.render.measure(str(path),crop=.65))
    records[name]['watts']={k:round(v.data.energy,2) for k,v in lights.items()}
    paths.append(str(path))
b.render.contact_sheet(paths,str(out/'lighting.png'),cols=5,tile=(320,320),labels=list(records),title=engine+' LIGHTING')
(out/'metrics.json').write_text(json.dumps(records,indent=2))
b.finish()
