"""Test whether secondary reflections explain the linked-fit gray spill."""
from pathlib import Path
import hashlib,json
import bpy
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/083-linked-reflections/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
scene.cycles.max_bounces=1
scene.cycles.diffuse_bounces=1
scene.cycles.glossy_bounces=1
scene.cycles.transmission_bounces=0
scene.cycles.volume_bounces=0
settings=json.loads(scene['mission_material_config'])
settings['variant']='084-direct-linked-reflections'
settings['direct_light_trial']={'source_sha256':digest,'max_bounces':1,'diffuse_bounces':1,'glossy_bounces':1,
    'hypothesis':'The masked global basis misses indirect cross-region reflections. Test a direct-only Cycles render before fitting new linked responses.'}
scene['mission_material_config']=json.dumps(settings,sort_keys=True)
out=ROOT/'build/queen-mission'/settings['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
print('DIRECT_LINKED_LIGHT_RENDER_DONE',flush=True)
