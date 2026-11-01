"""Record inspection rings from the current fresh queen controls."""
from pathlib import Path
import json,sys
import numpy as np
import bpy
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from scratch_profile import PROFILE
fit=json.loads((root/'assets/queen/scratch-fit.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(root/'models/queen/queen-rebuilt.blend'),load_ui=False)
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render)
points=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',points)
rings=points.reshape((-1,int(obj['ring_segments']),3))
levels={'foot_groove':.315,'foot_lower_lip':.29,'base_shoulder':.405,'socket_shoulder':1.30,
        'stem_seat':1.36,'lowest_collar':2.69,'middle_collar':2.84,'small_bead':2.98}
indices={name:min(range(len(PROFILE)),key=lambda i:abs(PROFILE[i][0]-z)) for name,z in levels.items()}
indices['egg_base']=int(obj['finial_first_ring'])
values={name:[float(np.linalg.norm(rings[i,:,:2],axis=1).mean()),float(rings[i,:,2].mean())] for name,i in indices.items()}
record={'scale':fit['camera_scale'],'elevation':54,'cx':fit['camera_cx'],'y0':fit['camera_floor'],
        'rings':values,'method':'Mean radii and heights of the new control rings.'}
(root/'assets/queen/profile-landmarks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
