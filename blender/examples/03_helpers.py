"""Each procedural helper alone: see the silhouette and joins."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
m=b.modelling
factories={'tree_round':lambda:m.tree(), 'tree_pine':lambda:m.tree('pine'),
           'tree_tall':lambda:m.tree('tall'), 'rock':m.rock,
           'cloud':lambda:m.cloud(location=(0,0,0)), 'bush':lambda:m.bush(flowers=5),
           'grass_tuft':m.grass_tuft,'crate':m.crate,'barrel':m.barrel,
           'coin':m.coin,'rubber_duck':m.rubber_duck, 'wall':m.wall,
           'tower':lambda:m.tower(flag='fortress.banner'), 'gate':m.gate,
           'flag':m.flag,'house':m.house,'roof_gable':m.roof_gable,
           'lathe':lambda:m.lathe([(0,0),(.6,0),(.7,.1),(.5,.7),(.7,1),(0,1)],mat='toybox.blue'),
           'extrude':lambda:m.extrude(m.arch_profile(),mat='toybox.red')}
paths,labels=[],[]
for name,make in factories.items():
    args=sys.argv[sys.argv.index('--')+3:]
    if args and name not in args:
        continue
    b.scene.new_scene()
    obj=make()
    b.scene.add_camera(obj,azimuth=30,elevation=22,margin=1.3)
    b.scene.cyclorama(subject=obj,color='#BCB6AB')
    b.lighting.rig('studio_soft',obj)
    path=str(out/(name+'.png'))
    b.render.still(path,quality='good')
    paths.append(path)
    labels.append(name)
b.render.contact_sheet(paths,str(out/'helpers.png'),cols=5,tile=(300,300),labels=labels,title='PROCEDURAL HELPERS')
b.finish()
