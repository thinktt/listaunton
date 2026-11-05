"""Isolate Cycles light-tree sampling as a source of repeatability variance."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/174-portable-finial/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
cfg=json.loads(s['mission_material_config']);cfg['variant']='176-standard-light-sampling';cfg['render_sampling']['light_tree']=False
s.cycles.use_light_tree=False;s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):bpy.context.scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('STANDARD_LIGHT_SAMPLING_DONE',flush=True)
