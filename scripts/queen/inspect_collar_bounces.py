"""Separate direct collar glints from secondary reflected light; diagnostic only."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/144-retained-fitted-collars/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;out=ROOT/'build/queen-mission/collar-bounces-144';out.mkdir(exist_ok=True,parents=True)
before={key:getattr(s.cycles,key) for key in ['max_bounces','diffuse_bounces','glossy_bounces','sample_clamp_indirect']}
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=(290+.01)/1254;s.render.border_max_x=(680+.01)/1254
s.render.border_min_y=(1254-565+.01)/1254;s.render.border_max_y=(1254-350+.01)/1254
s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for depth in [0,1]:
 s.cycles.glossy_bounces=depth;s.render.filepath=str(out/('glossy-'+str(depth)+'.png'));bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source_sha256':digest,'source_unchanged':True,'original_light_paths':before,'samples':256},indent=2)+'\n')
print('COLLAR_BOUNCE_PROBE_DONE',before,flush=True)
