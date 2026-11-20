"""Check fixed camera, bilateral protected eye region, and exact lower coordinates."""
from pathlib import Path
import bpy,sys,json,hashlib
import numpy as np
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from mission_scene import world_vertices,visible_meshes
from lower_carving_fit import rest_coords
def read(filename):
    bpy.ops.wm.open_mainfile(filepath=str(D/filename),load_ui=False)
    s=bpy.context.scene;c=s.camera;p=json.loads(s['knight_mission_pose'])
    pose=[p[k] for k in ('dx','dy','twist_degrees')]
    objs={}
    for o in visible_meshes(s):
        uv={}
        for layer in o.data.uv_layers:
            a=np.empty(len(layer.uv)*2,np.float32);layer.uv.foreach_get('vector',a)
            uv[layer.name]=hashlib.sha256(a.tobytes()).hexdigest()
        v=np.empty(len(o.data.attributes['Knight varnish coverage'].data),np.float32)
        o.data.attributes['Knight varnish coverage'].data.foreach_get('value',v)
        objs[o.name]=(rest_coords(world_vertices(o),pose),uv,hashlib.sha256(v.tobytes()).hexdigest())
    return {'matrix':np.array(c.matrix_world).tolist(),'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y]},objs
old,meshes=read('parent.blend');new,other=read('knight.blend')
out={'camera_exact':old==new,'parts':{}}
for name,(v,uv,attr) in meshes.items():
    w,uv2,attr2=other[name]
    d=np.linalg.norm(v-w,axis=1);below=v[:,2]<=4.254
    a={'moved_vertices_above_1e-6':int((d>1e-6).sum()),'uv_exact':uv==uv2,'varnish_exact':attr==attr2,
       'max_displacement_at_or_below_4_254':float(max(d[below],default=0.))}
    if 'head and neck' in name:
        x,z=v[:,0]-.412,v[:,2]-4.158
        u=(x-.76*z)/np.hypot(1,.76);t=(.76*x+z)/np.hypot(1,.76)
        mask=np.hypot(u/.31,t/.15)<=1.56;a['eye_envelope_vertices']=int(mask.sum());a['eye_envelope_max_displacement']=float(max(d[mask]))
    out['parts'][name]=a
(D/'registration.json').write_text(json.dumps(out,indent=2)+'\n')
assert out['camera_exact']
assert all(s['uv_exact'] and s['varnish_exact'] and s['max_displacement_at_or_below_4_254']<1e-6 for s in out['parts'].values())
print(out['parts']['Knight | continuous horse head and neck'])
