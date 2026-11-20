"""Test a continuous artistic reflected fill across the middle collar."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/150-separated-collar-fills/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;cfg=json.loads(s['mission_material_config']);fills=[]
for spec in cfg['lights']:
 if spec['name'].startswith('Collar crescent ') and 6<=int(spec['name'].split()[-1])<=16:
  bpy.data.objects[spec['name']].data.use_shadow=False;spec['use_shadow']=False;fills.append(spec['name'])
cfg['subdivided_collar_receivers']['nonshadowing_fills']=fills
cfg['subdivided_collar_receivers']['method']='Exact evaluated face subdivision preserves geometry, UVs and normals. Eleven reflected middle-collar fills omit cast shadows; the inferred reflection directions lie below adjacent collars. This is an explicit artistic lighting approximation. All other lights retain shadows.'
cfg['full_collar_fill']={'source_sha256':digest,'reason':'Test whether neighboring rings block the remaining middle-collar crescent; retain narrow per-ring light links.'}
cfg['variant']='152-complete-collar-fill';s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('FULL_COLLAR_FILL_PREPARED',flush=True)
