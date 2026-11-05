"""Test direct glossy lighting without secondary specular interreflection."""
from pathlib import Path
import bpy,json,hashlib
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/144-retained-fitted-collars/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;cfg=json.loads(s['mission_material_config']);previous=s.cycles.glossy_bounces
s.cycles.glossy_bounces=0;s.cycles.samples=64;s.cycles.use_denoising=True
cfg['variant']='145-direct-glossy-collars'
cfg['glossy_interreflection']={'source_sha256':digest,'previous_bounces':previous,'glossy_bounces':0,
 'method':'Keep actual BSDF direct diffuse/glossy lighting and four diffuse bounces; omit secondary glossy interreflection after diagnostic identified crown-body stripe as reflection of illuminated collars. An artistic render approximation, not a recovered original setting.'}
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('DIRECT_GLOSSY_TRIAL_DONE',flush=True)
