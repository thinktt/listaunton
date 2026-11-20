from pathlib import Path
import json, math
import bpy
import numpy as np
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'models/queen/queen-rebuilt.blend'),load_ui=False)
scene=bpy.context.scene
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
obj.data.vertices.foreach_get('co',coords)
rings=coords.reshape((-1,192,3))
out=root/'build/queen-mission';out.mkdir(parents=True,exist_ok=True)
np.save(out/'baseline-controls.npy',rings)
fit=json.loads((root/'assets/queen/finish-fit.json').read_text())
scale=fit['camera_scale'];y0=fit['camera_floor'];e=math.radians(54)
data=[]
for i,ring in enumerate(rings):
    r=float(np.linalg.norm(ring[:,:2],axis=1).mean()); z=float(ring[:,2].mean())
    data.append({'ring':i,'r':round(r,6),'z':round(z,6),'front_y':round(y0-scale*z*math.cos(e)+scale*r*math.sin(e),2),'back_y':round(y0-scale*z*math.cos(e)-scale*r*math.sin(e),2)})
(out/'control-profile.json').write_text(json.dumps(data,indent=2))
print('CUSTOM',dict(obj.items()))
print('PROFILE',json.dumps(data))
print('LIGHTS',json.dumps([{'name':o.name,'location':list(o.location),'energy':o.data.energy,'size':o.data.size} for o in scene.objects if o.type=='LIGHT']))
