"""Record evaluated helper budgets and base placement, without rendering."""
import json
from pathlib import Path
import sys
import bkit as b
from bkit._util import bounds
out=Path(sys.argv[sys.argv.index('--')+1])
m=b.modelling
factories={'tree_round':lambda:m.tree(),'tree_pine':lambda:m.tree('pine'),
 'tree_tall':lambda:m.tree('tall'),'rock':m.rock,'cloud':lambda:m.cloud(location=(0,0,0)),
 'bush':m.bush,'grass':m.grass_tuft,'crate':m.crate,'barrel':m.barrel,'coin':m.coin,
 'duck':m.rubber_duck,'wall':m.wall,'tower':m.tower,'gate':m.gate,'flag':m.flag,'house':m.house,
 'roof':m.roof_gable,'capsule':m.capsule,'torus':m.torus}
result={}
for name,make in factories.items():
    b.scene.new_scene()
    obj=make()
    lo,hi=bounds(obj,precise=True)
    result[name]=dict(triangles=m.tri_count(obj),dimensions=[round(v,4) for v in hi-lo],base=round(lo.z,5))
    assert result[name]['triangles']>0
    if name not in ('capsule','torus'):
        assert abs(lo.z)<.05,(name,lo.z)
(out/'geometry.json').write_text(json.dumps(result,indent=2))
b.finish()
