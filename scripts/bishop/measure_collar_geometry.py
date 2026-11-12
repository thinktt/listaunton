"""Measure the actual upper-collar front boundary independently of pigment."""
from pathlib import Path
import argparse,json,math,sys
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--profile',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads((ROOT/a.profile).read_text());al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
factor=1254/300/al['scale']/cfg['scale'];co=math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/a.model),load_ui=False);s=bpy.context.scene;bpy.context.view_layer.update()
ev=bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
yy=[cfg['profile'][i][1] for i in range(59,65)]
zlo=(cfg['y0']-max(yy))*factor/co;zhi=(cfg['y0']-min(yy))*factor/co
points=[]
for v in me.vertices:
    pos=ev.matrix_world@v.co
    if not(zlo<=pos.z<=zhi) or abs(pos.x)>.004 or pos.y>=0:continue
    ndc=world_to_camera_view(s,s.camera,pos)
    points.append({'x':ndc.x*1254,'y':(1-ndc.y)*1254,'world':list(pos)})
assert points
edge=max(points,key=lambda row:row['y'])
report={'model':a.model,'profile':a.profile,'upper_collar_front_boundary':edge,
        'sample_count':len(points),'method':'Maximum projected front-meridian extent of the evaluated upper collar between control rings 59–64. No shader, bump, color texture or shadow used.',
        'caution':'Photographic shadow troughs lie beyond a rim and are not identical to geometric boundaries.'}
(ROOT/a.out).write_text(json.dumps(report,indent=2)+'\n');ev.to_mesh_clear();print(json.dumps(report),flush=True)
