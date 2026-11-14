"""Real CC0 pack import; --in a directory containing kaykit-furniture.zip."""
import json
from pathlib import Path
import sys
import bkit as b
import bpy
from bkit._util import bounds, mesh_objects
out,inputs=map(Path,sys.argv[sys.argv.index('--')+1:][:2])
b.scene.new_scene()
license_url='https://github.com/KayKit-Game-Assets/KayKit-Furniture-Bits-1.0/blob/main/addons/kaykit_furniture_bits/Assets/LICENSE.txt'
root=b.assets.import_pack(inputs/'kaykit-furniture.zip',source='kaykit',license_url=license_url,height=3)
lo,hi=bounds(root)
assert abs(lo.z)<1e-5 and abs(hi.z-lo.z-3)<1e-4,(lo,hi)
assert mesh_objects(root)
images=[img for img in bpy.data.images if img.type=='IMAGE']
assert all(img.size[0]>0 for img in images),'missing pack image'
b.scene.add_camera(root,azimuth=30,elevation=18,margin=1.3)
b.scene.cyclorama(subject=root,color='#BCB6AB')
b.lighting.rig('studio_soft',root)
b.render.still(str(out/'kaykit_armchair.png'),quality='good')
result=dict(ok=True,height=hi.z-lo.z,base=lo.z,meshes=len(mesh_objects(root)),images=len(images),license_url=license_url)
for kind,path,source,url in [('obj',next(inputs.rglob('armchair.obj')),'kaykit',license_url),
                           ('blend',inputs/'polyhaven_model/wooden_crate_01_1k.blend','polyhaven','https://polyhaven.com/license')]:
    b.scene.new_scene()
    root=b.assets.import_pack(path,source=source,license_url=url,height=3)
    lo,hi=bounds(root,precise=True)
    assert abs(lo.z)<1e-4 and abs(hi.z-lo.z-3)<1e-4,(kind,lo,hi)
    b.scene.add_camera(root,azimuth=30,elevation=18,margin=1.3)
    b.scene.cyclorama(subject=root,color='#BCB6AB')
    b.lighting.rig('studio_soft',root)
    b.render.still(str(out/('cc0_'+kind+'.png')),quality='good')
    result[kind]=dict(height=hi.z-lo.z,base=lo.z,meshes=len(mesh_objects(root)))
(out/'pack.json').write_text(json.dumps(result,indent=2))
b.finish()
