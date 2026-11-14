"""Model sheet, turntable, outlines, real full-HD PNG sequences and Roblox export reports."""
from pathlib import Path
import sys
import bkit as b
out=Path(sys.argv[sys.argv.index('--')+1])
b.scene.new_scene()
obj=b.modelling.rubber_duck(2)
b.scene.add_camera(obj,azimuth=30,elevation=20,margin=1.3)
b.scene.cyclorama(subject=obj,color='#BCB6AB')
b.lighting.rig('studio_soft',obj)
b.render.model_sheet(obj,str(out/'model_sheet.png'),tile=(320,320),title='DUCK - FORM AND TOPOLOGY')
b.render.turntable(obj,str(out/'turntable'),angles=4,resolution=(320,320),quality='fast')
b.render.outline(obj,method='hull',thickness=.018)
b.render.still(str(out/'outline.png'),resolution=(960,960),quality='good')
# Outline is a render effect; remove before export.
obj.modifiers.remove(obj.modifiers['bkit_outline'])
obj=b.materials.atlas_from_materials(obj,image_path=str(out/'duck_atlas.png'))
b.export.fbx(obj,str(out/'duck.fbx'))
b.export.obj(obj,str(out/'duck.obj'))
b.animation.key_rotation(obj,1,(0,0,0))
b.animation.key_rotation(obj,2,(0,0,5))
for orientation in ('vertical','horizontal'):
    # Refit at the actual aspect ratio before rendering.
    import bpy
    bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=b.render.RESOLUTIONS[orientation]
    b.scene.aim(bpy.context.scene.camera,obj,azimuth=30,elevation=20,margin=1.3)
    b.render.animation(str(out/orientation),orientation=orientation,frames=(1,2),quality='fast')
b.finish()
