"""Extract the upper geometry and orthographic camera for contour fitting."""
import bpy,sys,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import visible_meshes
from lower_carving_fit import rest_coords
bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
s=bpy.context.scene;c=s.camera;g=bpy.context.evaluated_depsgraph_get()
cfg=json.loads(s['knight_mission_pose'])
pose=[cfg[k] for k in ('dx','dy','twist_degrees')]
mx=np.asarray(c.calc_matrix_camera(g,x=1254,y=1254))@np.asarray(c.matrix_world.inverted())
vlist=[];elist=[];offset=0
for o in visible_meshes(s):
    ev=o.evaluated_get(g);m=ev.to_mesh()
    v=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',v.ravel())
    mat=np.array(ev.matrix_world);v=v@mat[:3,:3].T+mat[:3,3];rest=rest_coords(v,pose)
    e=np.empty((len(m.edges),2),np.int32);m.edges.foreach_get('vertices',e.ravel())
    e=e[(rest[e,2].max(1)>3.95)&(rest[e,0].min(1)<1.8)]
    if len(e):
        selected,rev=np.unique(e,return_inverse=True)
        vlist.append(rest[selected]);elist.append(offset+rev.reshape(-1,2));offset+=len(selected)
    ev.to_mesh_clear()
np.savez_compressed(D/'surface.npz',points=np.vstack(vlist),edges=np.vstack(elist),matrix=mx,pose=pose)
print(offset,len(np.vstack(elist)))
