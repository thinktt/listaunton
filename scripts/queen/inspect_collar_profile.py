"""Project actual collar control rings for comparison with fixed reference contours."""
from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'models/queen/queen-rebuilt.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=editable_mesh(s)
co=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',co);co=co.reshape(-1,192,3)
def pixel(v):
 p=world_to_camera_view(s,s.camera,o.matrix_world@Vector(v));return [float(p.x*s.render.resolution_x),float((1-p.y)*s.render.resolution_y)]
profile=[]
for i,ring in enumerate(co):
 r=float(np.linalg.norm(ring[:,:2],axis=1).mean());z=float(ring[:,2].mean())
 profile.append({'ring':i,'r':r,'z':z,'front':pixel((0,-r,z)),'side':pixel((r,0,z)),'curve':[pixel((r*math.cos(a),r*math.sin(a),z)) for a in np.linspace(-math.pi,0,121)] if 50<=i<85 else []})
out=ROOT/'build/queen-mission/collar-profile-015';out.mkdir(parents=True,exist_ok=True)
(out/'profile.json').write_text(json.dumps({'source_sha256':digest,'profile':profile,'origin':pixel((0,0,0)),'axis_x':pixel((1,0,0)),'axis_y':pixel((0,1,0)),'axis_z':pixel((0,0,1))},indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
for i in [55,67,78]:print('COLLAR_RING',i,{k:v for k,v in profile[i].items() if k!='curve'},flush=True)
print('COLLAR_PROFILE_INSPECTED',flush=True)
