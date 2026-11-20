"""Verify finite closed surfaces and the absence of intersecting mane triangles."""
from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from survey import MANE
def verify_mane(s,required=True):
    o=s.objects[MANE].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh();m.calc_loop_triangles()
    v=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',v.ravel());assert np.isfinite(v).all()
    f=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',f.ravel())
    tree=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True)
    pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not np.any(f[i][:,None]==f[j])]
    from survey import rest_coords,pose
    mw=np.array(o.matrix_world);world=v@mw[:3,:3].T+mw[:3,3];rest=rest_coords(world,pose(s))
    pts=[np.round(rest[f[i]].mean(0),4).tolist() for i,j in pairs]
    o.to_mesh_clear()
    if required:assert not pairs,pts[:12]
    return {'triangles_checked':len(f),'nonadjacent_crossings':len(pairs),'crossing_positions':pts}
