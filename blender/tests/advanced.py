"""Version probes and render-only features; --in CC0 cache (see manual)."""
import json
from pathlib import Path
import sys
import bkit as b
import bpy

out,inputs=map(Path,sys.argv[sys.argv.index('--')+1:][:2])
facts={'version':bpy.app.version_string}
b.scene.new_scene(engine='CYCLES')
facts['backend']=b.compat.enable_gpu()
facts['bsdf_sockets']=[s.name for s in b.materials.bsdf(b.materials.metal_brushed()).inputs]
facts['gltf_color_enums']=[e.identifier for e in bpy.ops.export_scene.gltf.get_rna_type().properties['export_vertex_color'].enum_items]
ball=b.modelling.sphere(1,location=(0,0,1),mat=b.materials.glass())
cam=b.scene.add_camera(ball,azimuth=30,elevation=18,margin=1.4)
b.scene.dof(cam,ball,fstop=8)
b.scene.shadow_catcher()
b.lighting.rig('studio_soft',ball)
options=sys.argv[sys.argv.index('--')+3:]
if not options or options[0]!='worlds':
    facts['cycles_shadow']=b.render.still(str(out/'shadow_catcher.png'),quality='fast')
    facts['cycles_shadow'].pop('path')
b.scene.new_scene()
ball=b.modelling.sphere(1,location=(0,0,1),mat=b.materials.chrome())
b.scene.add_camera(ball,azimuth=30,elevation=18,margin=1.3)
b.scene.world_hdri(inputs/'polyhaven/studio_small_08/studio_small_08_1k.hdr',background='#C8C0B2')
b.scene.ground(size=1000,color='#C8C0B2')
b.render.still(str(out/'hdri.png'),quality='good')
b.scene.new_scene()
tree=b.modelling.tree()
b.scene.add_camera(tree,azimuth=30,elevation=18,margin=1.3)
b.scene.ground(size=1000,color='meadow.sand')
b.lighting.rig('sunny_outdoor',tree,world=False)
b.scene.world_sky()
nt,rl,sock=b.compat.compositor_io()
nt.links.new(rl.outputs['Image'],sock)
b.render.still(str(out/'sky_compositor.png'),quality='good')
b.render.outline(tree,method='freestyle',thickness=1.5)
b.render.still(str(out/'freestyle.png'),quality='fast')
(out/'advanced.json').write_text(json.dumps(facts,indent=2))
b.finish()
