"""Measure folded returns in the native hidden eye shell during shape selection."""
from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import *
def overlap(s):
    out={}
    for side in ['near','far']:
        name=side+' eye';ob=s.objects['Knight | '+name];me=ob.data
        raw=rest_coords(world_vertices(ob),pose(s));u,v=chart(raw)
        me.calc_loop_triangles();f=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',f.ravel())
        tree=BVHTree.FromPolygons(raw.tolist(),f.tolist(),all_triangles=True)
        pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not np.any(f[i][:,None]==f[j])]
        vids=np.unique(f[np.array(pairs).ravel()]) if pairs else []
        out[name]={'crossed':len(pairs),'pairs':pairs[:6],'verts':[[int(i),round(float(u[i]),4),round(float(v[i]),4),round(float(abs(raw[i,1])),4)] for i in vids[:35]]}
    return out
if __name__=='__main__':
    results={}
    for scale in [1,.92,.84,.72,.56,.35,.18]:
        s=load('parent.blend');design=(*DESIGNS[12],scale);sculpt(s,design);results[scale]=overlap(s)
        print(scale,[i['crossed'] for i in results[scale].values()],flush=True)
    (D/'safe-scales.json').write_text(json.dumps(results,indent=2)+'\n')
