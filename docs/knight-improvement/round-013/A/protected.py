from pathlib import Path
import json,hashlib,sys
import bpy,numpy as np
from mathutils.kdtree import KDTree
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from sculpt import chart
from mission_scene import visible_meshes,world_vertices,sha
from lower_carving_fit import rest_coords
def digest(v):return hashlib.sha256(v.tobytes()).hexdigest()
def record(p):
    bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);s=bpy.context.scene
    q=json.loads(s['knight_mission_pose']);pose=[q[k] for k in ('dx','dy','twist_degrees')]
    lights={o.name:[np.array(o.matrix_world).tolist(),o.data.color[:],o.data.energy,o.data.size,o.data.size_y,o.data.spread] for o in s.objects if o.type=='LIGHT'}
    cameras={o.name:[np.array(o.matrix_world).tolist(),o.data.ortho_scale,o.data.shift_x,o.data.shift_y] for o in s.objects if o.type=='CAMERA'}
    objs={};alluv=[];skin=None
    for o in visible_meshes(s):
        v=world_vertices(o);uv=np.empty((len(o.data.loops),2),np.float32);o.data.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
        alluv.append(bool(np.isfinite(uv).all()));objs[o.name]=[digest(v),digest(uv)]
        if o.name.endswith('continuous horse head and neck'):skin=rest_coords(v,pose)
    return {'lights':lights,'cameras':cameras,'sha':sha(p),'valid_uv':all(alluv),'parts':objs,'pose':pose},skin
a,old=record(D/'parent.blend');b,new=record(D/'knight.blend')
axis,level=chart(old);protected=(axis<-.59)|(axis>.72)|(level<-.28)|(level>.37)|(abs(old[:,1])<.095)
tree=KDTree(len(new))
for i,p in enumerate(new):tree.insert(p,i)
tree.balance()
dist=[tree.find(p)[2] for p in old[protected]]
res={'parent':a,'candidate':b,'unchanged_visible_parts':[k for k in a['parts'] if a['parts'][k]==b['parts'][k]],'changed_lamps':[k for k in a['lights'] if a['lights'][k]!=b['lights'][k]],'cameras_equal':a['cameras']==b['cameras'],'outside_orbit_skull_vertices':len(dist),'maximum_outside_orbit_nearest_distance':max(dist)}
(D/'protected.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items() if k not in ['parent','candidate']})
