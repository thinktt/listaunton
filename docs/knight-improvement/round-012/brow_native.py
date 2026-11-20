"""Locate a photographed crease on the real knight in two registered cameras."""
from pathlib import Path
import hashlib,json,sys
import bpy
from bpy_extras.object_utils import world_to_camera_view
r,model,trace,output=map(lambda v:Path(v).resolve(),sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(r/'scripts/knight'))
from probe_carving import point_probe
from mission_scene import use_side_camera
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene;fixed=point_probe(s)
anchors=json.loads(trace.read_bytes())['anchor_points']
samples=[]
for x,y in anchors:
    hit=fixed(x+.5,y+.5)
    if hit:samples.append((x,y,*hit[1:]))
use_side_camera(s)
bpy.context.view_layer.update()
side=point_probe(s);record=[]
for x,y,part,point,normal in samples:
    uv=world_to_camera_view(s,s.camera,point);sx,sy=uv.x*1254,1254*(1-uv.y)
    first=side(sx,sy)
    if not first:continue
    record.append({'fixed':[x,y],'side':[round(sx,2),round(sy,2)],'source_hit':part,
                   'visible_in_side':(first[2]-point).length<.01,'side_first_hit':first[1],'occlusion_distance':round((first[2]-point).length,4)})
output.write_text(json.dumps({'model':hashlib.sha256(model.read_bytes()).hexdigest(),'trace':hashlib.sha256(trace.read_bytes()).hexdigest(),'samples':record,'method':'Each photographed anchor is ray cast against the accepted sculpt at 54 degrees and projected to its actual side camera. Hidden correspondences are recorded. These are locations on this sculpt, dependent on its existing geometry.'},indent=2)+'\n')
print([(row['fixed'],row['side'],row['source_hit'],row['visible_in_side']) for row in record])
