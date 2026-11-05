"""Test subtler varnished wood relief and capture fresh reflection responses."""
from pathlib import Path
import hashlib, json, math, sys
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'models/queen/queen-rebuilt.blend'
source_hash = '82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e'
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
old_manifest = json.loads((ROOT / 'build/queen-mission/directional-reflections-006/manifest.json').read_text())
assert old_manifest['source_sha256'] == source_hash
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
obj = next(o for o in scene.objects if o.type == 'MESH' and not o.hide_render)
bsdf = obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
bump = bsdf.inputs['Normal'].links[0].from_node
assert bump.type == 'BUMP'
assert bsdf.inputs['Coat Normal'].links[0].from_node == bump
bump.inputs['Strength'].default_value = .2
bump.inputs['Distance'].default_value = .003
bsdf.inputs['Roughness'].default_value = .16
bsdf.inputs['Coat Roughness'].default_value = .06
settings = json.loads(scene['mission_material_config'])
settings['subtle_relief'] = {'source_sha256': source_hash, 'strength': .2, 'distance': .003,
    'roughness': .16, 'coat_roughness': .06,
    'hypothesis': 'The prior relief bends polished highlights too strongly. Reduce height response before fitting a new light rig.'}
settings['variant'] = '079-subtle-relief'
scene['mission_material_config'] = json.dumps(settings, sort_keys=True)
trial = ROOT / 'build/queen-mission/079-subtle-relief'
trial.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(trial / 'wood.png')
scene.render.use_persistent_data = True
scene.cycles.samples = 64
scene.cycles.use_denoising = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(trial / 'queen.blend'))
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
if any(device.use for device in prefs.devices):
    scene.cycles.device = 'GPU'
bpy.ops.render.render(write_still=True)
(trial / 'parameters.json').write_text(json.dumps(settings, indent=2) + '\n')
print('SUBTLE_RELIEF_RENDERED', flush=True)

out = ROOT / 'build/queen-mission/directional-reflections-079'
out.mkdir(parents=True, exist_ok=True)
scene.render.resolution_x = scene.render.resolution_y = 418
scene.cycles.use_denoising = False
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.image_settings.color_mode = 'RGBA'

def render(name):
    path = out / (name + '.exr')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    pixels = np.empty(418 * 418 * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    np.save(out / (name + '.npy'), pixels.reshape(418, 418, 4)[::-1].copy())

for light in scene.objects:
    if light.type == 'LIGHT':
        light.visible_glossy = False
render('diffuse-baseline')
for light in list(scene.objects):
    if light.type == 'LIGHT':
        bpy.data.objects.remove(light, do_unlink=True)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0
links = obj.data.materials[0].node_tree.links
for link in list(bsdf.inputs['Base Color'].links):
    links.remove(link)
bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
for index, spec in enumerate(old_manifest['specs']):
    data = bpy.data.lights.new(spec['name'], 'SUN')
    data.energy, data.angle = 1, math.radians(spec['angle_degrees'])
    light = bpy.data.objects.new(spec['name'], data)
    scene.collection.objects.link(light)
    light.location = spec['position']
    light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    light.visible_diffuse, light.visible_glossy = False, True
    render(spec['name'])
    bpy.data.objects.remove(light, do_unlink=True)
    print('SUBTLE_DIRECTIONAL_RESPONSE', index + 1, len(old_manifest['specs']), flush=True)
manifest = dict(old_manifest)
manifest.update({'source': (trial / 'queen.blend').relative_to(ROOT).as_posix(),
    'source_sha256': hashlib.sha256((trial / 'queen.blend').read_bytes()).hexdigest(),
    'directions_reused_from': 'build/queen-mission/directional-reflections-006/manifest.json',
    'geometry_unchanged_from': source_hash, 'subtle_relief': settings['subtle_relief']})
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
print('SUBTLE_RELIEF_CAPTURE_DONE', flush=True)
