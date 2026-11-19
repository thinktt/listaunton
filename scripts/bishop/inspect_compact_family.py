"""Saved-surface measurements and constant-scale neutral views for bishop 031."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from inspect_shared_turning import measure
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-031'
cfg=json.loads((DOC/'compact-family.json').read_text())
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out={}
for key,source in [('before',cfg['source']),('after','build/bishop-mission/'+cfg['variant']+'/bishop.blend')]:
    path=ROOT/source
    if key=='before' and '--after-only' in args:
        prior=json.loads((DOC/'measurements.json').read_text())['before']
        assert prior['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        out[key]=prior;continue
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    body=bpy.data.objects['Bishop - continuous turned body']
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
    bpy.context.view_layer.update()
    values,curve=measure(bpy.context.scene,body,True)
    points=np.array([tuple(v.co) for v in body.data.vertices]).reshape(-1,128,3)
    radius=np.linalg.norm(points[:,:,:2],axis=2).mean(1);z=points[:,:,2].mean(1)
    values.update(source=source,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        socket_top_control_z=float(z[31]),socket_wall_mid_z=float(z[25]),
        flare_shoulder_control_z=float(z[22]),inner_flare_radius=float(radius[18]),
        upper_collar_crest_control_z=float(z[62]),upper_collar_crest_radius=float(radius[62]),
        control_rz=np.column_stack((radius,z)).tolist(),evaluated_base_rz=curve.tolist())
    out[key]=values
    if '--measure-only' not in args and not(key=='before' and '--after-only' in args):
        script=Path(__file__).with_name('render_geometry_studio.py')
        sys.argv=[str(script),'--','--source',source,'--out',f'docs/bishop-mission/iteration-031/{key}','--views','side','fixed']
        runpy.run_path(str(script),run_name='__main__')
(DOC/'measurements.json').write_text(json.dumps(out,indent=2)+'\n',newline='\n')
print(json.dumps({k:{n:v[n] for n in ['height','foot_diameter','socket_top_control_z','inner_flare_radius','upper_collar_crest_control_z','front_collar_rim_rows','front_groove_row','source_sha256']} for k,v in out.items()},indent=2),flush=True)
