"""Sample the two outer eyelid surfaces in an unposed coordinate system."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode=True
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

parser=argparse.ArgumentParser()
parser.add_argument('root',type=Path)
parser.add_argument('model',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(args.root.resolve()/'scripts/knight'))
from lower_carving_fit import rest_coords
bpy.ops.wm.open_mainfile(filepath=str(args.model.resolve()),load_ui=False)
scene=bpy.context.scene
config=json.loads(scene['knight_mission_pose'])
pose=[config[k] for k in ('dx','dy','twist_degrees')]
graph=bpy.context.evaluated_depsgraph_get()

def tree(obj):
    ev=obj.evaluated_get(graph)
    mesh=ev.to_mesh()
    try:
        points=np.empty((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get('co',points.ravel())
        transform=np.asarray(ev.matrix_world)
        points=points@transform[:3,:3].T+transform[:3,3]
        points=rest_coords(points,pose)
        mesh.calc_loop_triangles()
        triangles=np.empty((len(mesh.loop_triangles),3),np.int32)
        mesh.loop_triangles.foreach_get('vertices',triangles.ravel())
        return BVHTree.FromPolygons(points.tolist(),triangles.tolist(),all_triangles=True)
    finally:
        ev.to_mesh_clear()

center=np.array([.412,4.158])
axis=np.array([1.,-.76]);axis/=np.linalg.norm(axis)
up=np.array([-axis[1],axis[0]])
u,v=np.meshgrid(np.linspace(-.36,.36,145),np.linspace(.16,-.16,65))
pos=center+u[:,:,None]*axis+v[:,:,None]*up
head=tree(scene.objects['Knight | continuous horse head and neck'])
def sample(name,side):
    eye=tree(scene.objects[f'Knight | {name} eye'])
    depth=np.full(u.shape,np.nan)
    exposed=np.zeros(u.shape,bool)
    for row,col in np.ndindex(u.shape):
        x,z=pos[row,col];origin=(x,3*side,z);direction=(0,-side,0)
        hit=head.ray_cast(origin,direction)[0]
        inset=eye.ray_cast(origin,direction)[0]
        if hit is None:continue
        depth[row,col]=hit.y*side
        if inset is not None and side*inset.y>depth[row,col]:
            exposed[row,col]=True
            depth[row,col]=inset.y*side
    return depth,exposed

left,visible_left=sample('near',-1)
right,visible_right=sample('far',1)
usable=np.isfinite(left)&np.isfinite(right)
left_right=left-right
# Eye relief is measured relative to a plane fitted to neighboring cheek samples.
# This preserves differences within the lids but removes a broad lean of the face.
rim=usable&((abs(u)>.305)|(abs(v)>.135))
basis=np.stack([u,v,np.ones_like(u)],axis=2)
tilt=np.linalg.lstsq(basis[rim],left_right[rim],rcond=None)[0]
difference=left_right-basis@tilt
win=usable&(abs(u)<.26)&(abs(v)<.085)
def aperture(mask):
    y,x=np.nonzero(mask)
    if not len(y):return {'samples':0}
    return {'samples':len(y),'centroid_u_v':[round(float(u[y,x].mean()),4),round(float(v[y,x].mean()),4)],
            'extent_u_v':[[round(float(t.min()),4),round(float(t.max()),4)] for t in (u[y,x],v[y,x])]}
def percentile(values,q):
    return round(float(np.percentile(values,q)),5)
union=visible_left|visible_right
metrics={'source_sha256':hashlib.sha256(args.model.read_bytes()).hexdigest(),'pose':pose,
         'spacing_model_units':.005,'sampled_sides':['near','far'],
         'near_exposed_insert':aperture(visible_left),'far_exposed_insert':aperture(visible_right),
         'exposed_insert_mirrored_iou':round(float((visible_left&visible_right).sum()/max(1,union.sum())),4),
         'raw_near_far_depth_difference_p95':percentile(abs(left_right[win]),95),
         'local_near_far_relief_difference_p95':percentile(abs(difference[win]),95),
         'fitted_near_minus_far_plane':tilt.tolist(),
         'method':'Side rays through the evaluated skull and eye in the shared unposed x,z frame. The exposed insert includes only the surface in front of the skull on that side. Relief difference subtracts the plane fitted to the outer margin and is reported in model units, over the central lid region. This describes symmetry, not aesthetic quality.'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.with_suffix('.json').write_text(json.dumps(metrics,indent=2)+'\n')
np.savez_compressed(args.output.with_suffix('.npz'),u=u,v=v,near=left,far=right,near_insert=visible_left,far_insert=visible_right,relief_difference=difference)
print(metrics)
