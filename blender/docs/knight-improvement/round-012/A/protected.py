"""Evaluate native model, tilt, camera, UV finiteness and upper mane geometry."""
from pathlib import Path
import sys,hashlib,json,bpy,numpy as np
from mathutils.kdtree import KDTree
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import visible_meshes
from lower_carving_fit import rest_coords
def digest(a):return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()
def state(name):
    bpy.ops.wm.open_mainfile(filepath=str(D/(name+'.blend')),load_ui=False);s=bpy.context.scene
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    lights={o.name:[list(map(list,o.matrix_world)),o.data.energy,o.data.size,o.data.size_y,o.hide_render,
             o.light_linking.receiver_collection.name if o.light_linking.receiver_collection else None] for o in s.objects if o.type=='LIGHT'}
    cams={o.name:[list(map(list,o.matrix_world)),o.data.type,o.data.ortho_scale,o.data.shift_x,o.data.shift_y] for o in s.objects if o.type=='CAMERA'}
    parts={};fields={};meshes={}
    for obj in visible_meshes(s):
        ob=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ob.to_mesh();verts=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',verts.ravel())
        T=np.asarray(ob.matrix_world);r=rest_coords(verts@T[:3,:3].T+T[:3,3],pose)
        m.calc_loop_triangles();uv=np.empty((len(m.loops),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
        fields[obj.name]={'geometry':digest(verts),'uv':digest(uv),'uv_finite':bool(np.isfinite(uv).all()),'vertices':len(r),'triangles':len(m.loop_triangles)}
        if obj.name.endswith('swept rounded mane') or obj.name.endswith('continuous horse head and neck'):meshes[obj.name]=(r,np.round([r.min(axis=0),r.max(axis=0)],5).tolist())
        ob.to_mesh_clear()
    return lights,cams,fields,meshes
a,b=state('parent'),state('knight');L='Knight | swept rounded mane';H='Knight | continuous horse head and neck'
def distance(p,q):
    tree=KDTree(len(q))
    for i,v in enumerate(q):tree.insert(v,i)
    tree.balance()
    return np.array([tree.find(v)[2] for v in p])
p,q=a[3][L][0],b[3][L][0];above=4.64
delta=np.r_[distance(p[p[:,2]>above],q),distance(q[q[:,2]>above],p)]
h1,h2=a[3][H][0],b[3][H][0];mask=h1[:,0]>.24
report={'lights_identical':a[0]==b[0],'cameras_identical':a[1]==b[1],
        'geometry_identical_outside_sculpt':[k for k in a[2] if k not in [L,H] and a[2][k]['geometry']==b[2][k]['geometry']],
        'all_other_geometry_protected':all(a[2][k]['geometry']==b[2][k]['geometry'] for k in a[2] if k not in [L,H]),
        'all_uv_finite':all(q['uv_finite'] for q in b[2].values()),
        'full_object_bounds':{k:{'parent':a[3][k][1],'candidate':b[3][k][1]} for k in [L,H]},
        'mane_all_eval_max_nearest_above_4_64':float(delta.max()),'mane_p95_above_4_64':float(np.quantile(delta,.95)),
        'protected_skull_max_xyz_displacement_on_x_greater_than_0_24':float(np.linalg.norm(h2[mask]-h1[mask],axis=1).max()),'parent':a[2],'candidate':b[2]}
(D/'protected.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['parent','candidate']})
