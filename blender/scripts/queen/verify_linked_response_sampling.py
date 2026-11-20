"""Check whether many-light sampling noise explains transport disagreement."""
from pathlib import Path
import json
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'build/queen-mission/linked-wood-responses-083'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/queen-mission/083-linked-reflections/queen.blend'),load_ui=False)
scene=bpy.context.scene
scene.render.resolution_x=scene.render.resolution_y=418
scene.cycles.samples=4096;scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=False
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
scene.render.filepath=str(out/'all-lights-4096.exr')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
image=bpy.data.images.load(scene.render.filepath,check_existing=False)
pixels=np.empty(418*418*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(418,418,4)[::-1].copy()
np.savez_compressed(out/'all-lights-4096.npz',pixels=pixels)
manifest=json.loads((out/'manifest.json').read_text());summed=np.load(out/'diffuse-baseline.npz')['pixels'][:,:,:3].copy()
for record in manifest['responses']:summed+=np.load(out/record['file'])['pixels'][:,:,:3]
mask=pixels[:,:,3]>.995;error=abs(summed-pixels[:,:,:3])[mask]
report={'samples':4096,'adaptive_sampling':False,'foreground_mae':float(error.mean()),'p95':float(np.percentile(error,95)),'max':float(error.max()),'reference_mean':float(pixels[:,:,:3][mask].mean())}
(out/'sampling-check.json').write_text(json.dumps(report,indent=2)+'\n')
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
bpy.data.images['Render Result'].save_render(str(out/'all-lights-4096.png'),scene=scene)
print('LINKED_SAMPLING_CHECK',report,flush=True)
