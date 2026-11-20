"""Measure reflection symmetry and one-peakedness of the actual subdivided crest."""
from pathlib import Path
import json,sys
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import pose,rest_coords
def sections(scene):
    p=pose(scene)
    ob=scene.objects['Knight | swept rounded mane'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=ob.to_mesh();me.calc_loop_triangles()
    co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel())
    t=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',t.ravel())
    m=np.asarray(ob.matrix_world)
    xyz=rest_coords(co@m[:3,:3].T+m[:3,3],p)
    tree=BVHTree.FromPolygons(xyz.tolist(),t.tolist(),all_triangles=True)
    ob.to_mesh_clear()
    outputs={};all_diffs=[]
    for x in [-.8,-.6,-.4,-.2,0.,.14]:
        v={}
        for key in range(-65,66):
            hit=tree.ray_cast((x,key/100,6.),(0.,0.,-1.),1.6)[0]
            if hit is not None:v[key]=float(hit.z)
        diffs=[abs(v[i]-v[-i]) for i in range(5,18) if i in v and -i in v]
        all_diffs+=diffs
        max_z=max(v.values());top=[key for key,z in v.items() if z>=max_z-.004]
        caps={sign:[v[sign*a] for a in range(0,18) if sign*a in v] for sign in [-1,1]}
        outputs[x]={'mean_mirrored_difference':float(np.mean(diffs)),'max_mirrored_difference':max(diffs),
            'top_midpoint':(max(top)+min(top))*.005,'top_width_at_004':(max(top)-min(top))*.01,
            'medial_height_shortfall':max_z-v[0],'maximum_rise_away_from_midplane':max(np.diff(c).max() for c in caps.values()),
            'profile':[[k/100,round(z,6)] for k,z in v.items()]}
    return {'stations':outputs,'mean_mirror_abs':float(np.mean(all_diffs)),'max_mirror_abs':max(all_diffs),
            'max_medial_shortfall':max(q['medial_height_shortfall'] for q in outputs.values()),
            'max_positive_step_outward':max(0,max(q['maximum_rise_away_from_midplane'] for q in outputs.values())),
            'maximum_absolute_top_midpoint':max(abs(q['top_midpoint']) for q in outputs.values()),
            'median_width_at_004':float(np.median([q['top_width_at_004'] for q in outputs.values()]))}
