"""Eight walk phases, fixed camera and lighting; exports the animated GLB too."""
from pathlib import Path
import sys
import bkit as b
import bpy
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene(resolution=(640,640))
hero=b.character.blocky_character()
b.animation.walk(hero,start=1,end=25)
# A hidden proxy reserves the full motion envelope in a fixed frame.
proxy=b.modelling.rounded_box((4.5,3.5,5.3),location=(0,0,2.6))
cam=b.scene.add_camera(proxy,azimuth=30,elevation=10,margin=1.16)
bpy.data.objects.remove(proxy,do_unlink=True)
b.scene.cyclorama(subject=hero.rig,color='#BCB6AB')
b.lighting.rig('studio_soft',hero.rig)
paths=[]
for frame in range(1,25,3):
    bpy.context.scene.frame_set(frame)
    path=str(out/f'walk_{frame:02d}.png')
    b.render.still(path,quality='good')
    paths.append(path)
b.render.contact_sheet(paths,str(out/'walk.png'),cols=4,tile=(360,360),labels=[str(f) for f in range(1,25,3)],title='WALK - 24 FRAME CYCLE')
b.export.glb(hero.rig,str(out/'walk.glb'))
b.finish()
