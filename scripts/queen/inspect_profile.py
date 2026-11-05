"""Read control-ring positions and their saved-camera projections."""
from pathlib import Path
import json,sys
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/queen/queen-rebuilt.blend'),load_ui=False)
s=bpy.context.scene;o=editable_mesh(s)
a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);a=a.reshape(-1,192,3)
out=[]
for i,ring in enumerate(a):
 r=float(np.linalg.norm(ring[:,:2],axis=1).mean());z=float(ring[:,2].mean());p=[]
 for c in [(0,-r,z),(0,r,z),(r,0,z)]:
  q=world_to_camera_view(s,s.camera,Vector(c));p.append([round(q.x*s.render.resolution_x,2),round((1-q.y)*s.render.resolution_y,2)])
 out.append(dict(index=i,r=r,z=z,front=p[0],back=p[1],side=p[2]))
(ROOT/'build/queen-mission/control-profile.json').write_text(json.dumps(out,indent=2))
for row in out:print(row)
