"""Record feature circles from the current queen and its fitted camera."""
from pathlib import Path
import json,sys
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
def write(scene,obj,fit):
    n=int(obj['ring_segments'])
    coords=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
    obj.data.vertices.foreach_get('co',coords);rings=coords.reshape((-1,n,3))
    indices={'foot_groove':11,'foot_lower_lip':10,'base_shoulder':16,
             'socket_shoulder':33,'stem_seat':38,'lowest_collar':55,
             'middle_collar':67,'small_bead':78,'egg_base':int(obj['finial_first_ring'])}
    values={name:[float(np.linalg.norm(rings[i,:,:2],axis=1).mean()),float(rings[i,:,2].mean())] for name,i in indices.items()}
    record={'scale':fit['camera_scale'],'elevation':54,'cx':fit['camera_cx'],
            'y0':fit['camera_floor'],'rings':values,
            'method':'Mean control-ring radii and heights for the current 54-degree model.'}
    (ROOT/'assets/queen/profile-landmarks.json').write_text(json.dumps(record,indent=2)+'\n')
    return record

if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/queen/queen-rebuilt.blend'),load_ui=False)
    obj=editable_mesh(bpy.context.scene)
    print(json.dumps(write(bpy.context.scene,obj,json.loads((ROOT/'assets/queen/finish-fit.json').read_text())),indent=2))
