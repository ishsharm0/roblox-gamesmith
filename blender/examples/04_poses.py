"""A bone-parented figure in all four named poses."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
paths=[]
for pose in b.character.POSES:
    b.scene.new_scene()
    hero=b.character.blocky_character(shirt='toybox.blue',pants='product.graphite')
    hero.pose(pose)
    b.scene.add_camera(hero.rig,azimuth=18,elevation=10,margin=1.3)
    b.scene.cyclorama(subject=hero.rig,color='#BCB6AB')
    b.lighting.rig('studio_soft',hero.rig)
    path=str(out/(pose+'.png'))
    b.render.still(path,quality='good')
    paths.append(path)
b.render.contact_sheet(paths,str(out/'poses.png'),cols=4,tile=(360,360),labels=list(b.character.POSES),title='RIG POSES')
b.finish()
