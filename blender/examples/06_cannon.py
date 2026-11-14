"""Hero product still, assembled only from kit functions."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
m=b.modelling
red=b.materials.toy_plastic('toybox.red')
blue=b.materials.toy_plastic('#284D59')
gold=b.materials.metal_brushed('#DDA849')
cream=b.materials.toy_plastic('toybox.cream')
parts=[]
parts.append(m.rounded_box((1.75,2.45,.45),location=(0,.1,.78),mat=blue))
for x in (-.72,.72):
    parts.append(m.extrude([(-1.2,0),(1.2,0),(.8,.9),(-.5,1.2),(-1.1,.9)],depth=.25,
                           location=(x,.12,.85),rotation=(0,0,90),mat=blue))
for x in (-1.15,1.15):
    parts.append(m.cylinder(.76,.26,48,location=(x,.35,.76),rotation=(0,90,0),mat=cream))
    parts.append(m.cylinder(.57,.29,48,location=(x,.35,.76),rotation=(0,90,0),mat=red))
    parts.append(m.cylinder(.21,.34,32,location=(x,.35,.76),rotation=(0,90,0),mat=gold))
profile=[(0,-1.05),(.36,-1.05),(.56,-.85),(.59,-.6),(.48,1.45),(.6,1.48),
         (.61,1.66),(.56,1.75),(.39,1.75),(.36,1.59),(.32,.6),(0,.6)]
parts.append(m.lathe(profile,64,location=(0,0,1.9),rotation=(75,0,0),mat=red))
parts.append(m.sphere(.2,location=(0,1.17,1.65),mat=gold))
for y,z in ((-.1,1.92),(.64,1.73)):
    parts.append(m.torus(.53,.055,location=(0,y,z),rotation=(75,0,0),mat=gold))
for x,y in ((1.7,-1.2),(2.25,-.7),(1.95,-.2)):
    parts.append(m.sphere(.28,location=(x,y,.28),mat=b.materials.metal_brushed('#505C66')))
subject=m.join(parts,'ToyCannon')
b.scene.add_camera(subject,azimuth=34,elevation=18,margin=1.28,lens=80)
b.scene.cyclorama(subject=subject,color='#B8B0A2')
b.lighting.rig('studio_soft',subject)
b.render.still(str(out/'cannon.png'),quality='hero')
b.export.glb(subject,str(out/'cannon.glb'),animation=False)
b.finish()
