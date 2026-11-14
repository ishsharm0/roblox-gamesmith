"""Run with blender-pc; deliberately records each independent failure before exiting."""
import json
import os
import sys
import traceback
import bpy
import bkit

out = sys.argv[sys.argv.index('--') + 1]
results = {}

def check(name, fn):
    try:
        fn()
        results[name] = 'PASS'
    except Exception:
        results[name] = traceback.format_exc()

def existing():
    bkit.scene.new_scene()
    m = bkit.modelling
    objs = [m.rounded_box(), m.cylinder(location=(2,0,0)), m.sphere(location=(-2,0,0)),
            m.lathe([(0,0),(.5,0),(.6,1),(0,1)]), m.extrude(m.arch_profile()),
            m.tree(), m.tree('pine'), m.tree('tall'), m.rock(), m.cloud(), m.bush(),
            m.grass_tuft(), m.crate(), m.barrel(), m.coin(), m.rubber_duck(), m.wall(),
            m.tower(), m.gate(), m.flag(), m.house(), m.roof_gable()]
    assert all(m.tri_count(o) > 0 for o in objs)
    for kind in bkit.materials.KINDS:
        bkit.materials.make(kind, '#B8A394')
    bkit.scene.add_camera(objs[:3])
    for rig in bkit.lighting.RIGS:
        bkit.lighting.rig(rig, objs[:3])

def picture():
    bkit.scene.new_scene()
    o = bkit.modelling.rounded_box(mat='toybox.red', location=(0,0,.5))
    bkit.scene.add_camera(o, elevation=25)
    bkit.scene.cyclorama(subject=o)
    bkit.lighting.rig('studio_soft', o)
    bkit.render.still(os.path.join(out,'smoke.png'), quality='fast')

check('existing constructors', existing)
for module in ('character','animation','export','assets'):
    check(module, lambda module=module: getattr(bkit,module))
check('render', picture)
with open(os.path.join(out,'smoke.json'),'w') as f:
    json.dump({'blender':bpy.app.version_string,'checks':results},f,indent=2)
print(json.dumps(results),flush=True)
bkit.finish(0 if all(v=='PASS' for v in results.values()) else 1)
