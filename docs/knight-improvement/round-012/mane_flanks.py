"""Inspect the equivalent left and right surfaces of the long mane in unposed head coordinates."""
from pathlib import Path
import sys,json,hashlib
import bpy,numpy as np
from mathutils.bvhtree import BVHTree
root,model,out=map(lambda x:Path(x).resolve(),sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(root/'scripts/knight'))
from lower_carving_fit import rest_coords
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(model)
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
scene=bpy.context.scene;pose=json.loads(scene['knight_mission_pose']);graph=bpy.context.evaluated_depsgraph_get()
def skin_tree(name):
    ob=scene.objects[name].evaluated_get(graph);m=ob.to_mesh()
    try:
        xyz=np.empty((len(m.vertices),3),dtype=np.float32);m.vertices.foreach_get('co',xyz.ravel())
        world=np.asarray(ob.matrix_world)
        xyz=rest_coords(xyz@world[:3,:3].T+world[:3,3],[pose[k] for k in ('dx','dy','twist_degrees')])
        m.calc_loop_triangles();tris=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tris.ravel())
        return BVHTree.FromPolygons(xyz.tolist(),tris.tolist(),all_triangles=True)
    finally: ob.to_mesh_clear()
trees=[skin_tree('Knight | '+part) for part in ['swept rounded mane','continuous horse head and neck']]
xs=np.linspace(-1.55,-.28,128);zs=np.linspace(4.38,2.43,196)
shape=(len(zs),len(xs));both={}
for sign,key in [(-1,'near'),(1,'far')]:
    y=np.full(shape,np.nan,dtype=np.float32);owner=np.zeros(shape,dtype=np.uint8)
    for iy,z in enumerate(zs):
        for ix,x in enumerate(xs):
            start=(x,sign*2.5,z);direction=(0,-sign,0)
            hits=[(sign*p.y,i+1) for i,t in enumerate(trees) if (p:=t.ray_cast(start,direction)[0]) is not None]
            if hits:y[iy,ix],owner[iy,ix]=max(hits)
    both[key]=y;both[key+'_owner']=owner
valid=np.isfinite(both['near'])&np.isfinite(both['far'])
mirror=np.abs(both['near'][valid]-both['far'][valid])
def enclosed(row):
    hit=np.flatnonzero(np.isfinite(row))
    return int((~np.isfinite(row[hit[0]:hit[-1]+1])).sum()) if len(hit)>1 else 0
m={'source_sha256':source,'grid_step':.01,'x_limits':[float(xs[0]),float(xs[-1])],'z_limits':[float(zs[-1]),float(zs[0])],
   'mirrored_side_depth_mean':round(float(mirror.mean()),5),'mirrored_side_depth_p95':round(float(np.percentile(mirror,95)),5),
   'enclosed_side_gap_samples':{k:sum(enclosed(row) for row in both[k]) for k in ['near','far']},
   'parts':['mane','continuous head and neck'],'method':'Opposed horizontal rays sample the outermost physical surface in the common unposed frame. Values are distances from the midplane. Missing samples between two occupied points on one row count openings. The study covers the hanging mane and adjacent neck below the crown; feature shape is judged from the actual renders.'}
assert source==sha(model)
out.parent.mkdir(parents=True,exist_ok=True);out.with_suffix('.json').write_text(json.dumps(m,indent=2)+'\n')
np.savez_compressed(out.with_suffix('.npz'),x=xs,z=zs,**both)
print(m)
