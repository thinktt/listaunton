"""Measure actual colored-wood transport for the existing linked emitters.

Unlike a masked black-BSDF approximation, these responses include the real
receiver links, the unchanged pigment and the scene's secondary reflections.
"""
from pathlib import Path
import hashlib,json
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/083-linked-reflections/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
settings=json.loads(scene['mission_material_config'])
out=ROOT/'build/queen-mission/linked-wood-responses-083';out.mkdir(parents=True,exist_ok=True)
gloss_specs=[v for v in settings['lights'] if v.get('receiver_parts')]
diffuse_specs=[v for v in settings['lights'] if not v.get('receiver_parts')]
scene.render.resolution_x=scene.render.resolution_y=418
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';scene.render.image_settings.color_mode='RGBA'
scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
def render(name):
    scene.render.filepath=str(out/'response-temporary.exr')
    bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(scene.render.filepath,check_existing=False)
    pixels=np.empty(418*418*4,dtype=np.float32);image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image);pixels=pixels.reshape(418,418,4)[::-1].copy()
    np.savez_compressed(out/(name+'.npz'),pixels=pixels)
    return pixels
full=render('all-lights')
for spec in gloss_specs:bpy.data.objects[spec['name']].data.energy=0
baseline=render('diffuse-baseline')
for spec in diffuse_specs:bpy.data.objects[spec['name']].data.energy=0
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
summed=baseline[:,:,:3].copy();records=[]
for index,spec in enumerate(gloss_specs):
    light=bpy.data.objects[spec['name']];light.data.energy=spec['energy']
    name=f'response-{index:03d}';pixels=render(name)
    summed+=pixels[:,:,:3];light.data.energy=0
    records.append({'spec':spec,'file':name+'.npz','sha256':hashlib.sha256((out/(name+'.npz')).read_bytes()).hexdigest()})
    print('LINKED_WOOD_RESPONSE',index+1,len(gloss_specs),spec['name'],flush=True)
mask=full[:,:,3]>.995
error=abs(summed-full[:,:,:3])[mask]
report={'source':source.relative_to(ROOT).as_posix(),'source_sha256':digest,
        'width':418,'height':418,'samples':64,'denoising':False,'responses':records,
        'baseline':diffuse_specs,'world':settings['world'],
        'linear_superposition_check':{'foreground_mae':float(error.mean()),'p95':float(np.percentile(error,95)),'max':float(error.max()),'reference_mean':float(full[:,:,:3][mask].mean())},
        'method':'Actual full colored-wood BSDF and actual light linking. Each response uses its recorded existing light power/color. Coefficients scale those powers.'}
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('LINKED_WOOD_RESPONSES_DONE',report['linear_superposition_check'],flush=True)
