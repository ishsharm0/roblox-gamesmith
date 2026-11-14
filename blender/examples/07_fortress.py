"""Toy block fortress with rubber ducks, on a round wooden table."""
from pathlib import Path
import sys
import math
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
m=b.modelling
parts=[]
parts.append(m.cylinder(6.2,.55,96,location=(0,0,1.1),mat=b.materials.painted_wood('#B9956C')))
parts.append(m.cylinder(5.9,.12,96,location=(0,0,.79),mat='fortress.wood'))
for angle in (30,150,270):
    a=math.radians(angle)
    parts.append(m.cylinder(.42,.85,24,location=(3.8*math.cos(a),3.8*math.sin(a),.42),mat='fortress.wood'))
z=1.375
for x in (-3.1,3.1):
    parts.append(m.tower(.78,2.5,location=(x,1.55,z),flag='fortress.banner'))
parts.append(m.wall(6.2,1.8,.65,location=(0,1.55,z)))
for x in (-3.1,3.1):
    parts.append(m.wall(3.3,1.6,.65,location=(x,0,z),rotation=90))
for x in (-2.15,2.15):
    parts.append(m.wall(1.9,1.6,.65,location=(x,-1.65,z)))
parts.append(m.gate(1.9,2.3,location=(0,-1.65,z)))
parts.append(m.house(2.7,2.1,1.8,location=(0,.25,z),door='fortress.banner'))
for size,loc,facing in [(1.2,(-2,-3.5,z),-20),(.9,(.1,-3.7,z),15),(1.05,(3.7,-2.6,z),-35),
                        (.85,(-1.6,0,z),15),(.75,(2,.15,z),-20)]:
    parts.append(m.rubber_duck(size,loc,facing=facing))
for x,y in ((-4.5,.4),(4.45,.2)):
    parts.append(m.bush(.9,location=(x,y,z),flowers=3))
subject=parts
b.scene.add_camera(subject,azimuth=24,elevation=27,lens=75,margin=1.25)
b.scene.cyclorama(subject=subject,color='#B7B0A1')
b.lighting.rig('toy_bright',subject,strength=.9)
b.render.still(str(out/'fortress.png'),quality='hero')
b.finish()
