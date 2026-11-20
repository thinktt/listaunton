"""Check the evaluated native blade and its carrier for folded triangles."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from carve import load,sculpt,pose,rest_coords,MANE,HEAD,sha

def inspect(s):
    data={}
    for name in [MANE,HEAD]:
        ob=s.objects['Knight | '+name].evaluated_get(bpy.context.evaluated_depsgraph_get())
        me=ob.to_mesh();me.calc_loop_triangles();m=np.asarray(ob.matrix_world)
        v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel())
        v=rest_coords(v@m[:3,:3].T+m[:3,3],pose(s))
        tris=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',tris.ravel())
        if name==HEAD:
            region=(v[:,0]<.0)&(v[:,2]>1.65)&(v[:,2]<4.77)
            tris=tris[np.any(region[tris],axis=1)]
        tree=BVHTree.FromPolygons(v.tolist(),tris.tolist(),all_triangles=True)
        folds=[(i,j) for i,j in tree.overlap(tree) if i<j and not (tris[i][:,None]==tris[j]).any()]
        data[name]={'triangles':len(tris),'folds':len(folds),'sample_positions':[np.round(v[tris[i]].mean(0),3).tolist() for i,j in folds[:6]]}
        ob.to_mesh_clear()
    return data

if __name__=='__main__':
    for key in sys.argv[sys.argv.index('--')+1:]:
        s=load('knight.blend' if key=='knight' else 'parent.blend')
        if key.isdigit():sculpt(s,int(key))
        q=inspect(s);print(key,q,flush=True)
        (D/f'qa-{key}.json').write_text(json.dumps(q,indent=2)+'\n')
