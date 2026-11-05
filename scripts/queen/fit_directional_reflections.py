"""Fit measured distant-light powers, then render the actual wood material."""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
import numpy as np
import PyOpenColorIO as ocio

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from configure_rig import configure
parser = argparse.ArgumentParser()
parser.add_argument('--variant', default='078-directional-reflections')
parser.add_argument('--directory', default='build/queen-mission/directional-reflections-006')
parser.add_argument('--include-accepted-lights', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
directory = ROOT / args.directory
manifest = json.loads((directory / 'manifest.json').read_text())
source = ROOT / manifest['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
settings = json.loads(scene['mission_material_config'])
out = ROOT / 'build/queen-mission' / args.variant
out.mkdir(parents=True, exist_ok=True)
diffuse = np.load(directory / 'diffuse-baseline.npy')
mask = diffuse[:, :, 3] > .995
baseline = diffuse[:, :, :3][mask].astype(np.float64)
specs, responses, inputs = [], [], []
for spec in manifest['specs']:
    path = directory / (spec['name'] + '.npy')
    responses.append(np.load(path)[:, :, :3].mean(2)[mask])
    specs.append(dict(spec))
    inputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
if args.include_accepted_lights:
    assert directory.name == 'directional-reflections-006', 'Old responses require their exact original material.'
    old_dir = ROOT / 'build/queen-mission/specular-expanded-039'
    old_specs = {v['name']: v for v in json.loads((old_dir / 'manifest.json').read_text())['specs']}
    for spec in settings['lights']:
        if spec.get('diffuse_factor', 1) != 0:
            continue
        name = spec['name'].removeprefix('Display fitted ')
        path = old_dir / (name + '.npy')
        if name == 'base-key':
            path = ROOT / 'build/queen-mission/071-limited-base-reflector/diagnostic-limited-reflector.npy'
        responses.append(np.load(path)[:, :, :3].mean(2)[mask])
        candidate = dict(spec)
        candidate['energy'] = old_specs[name]['energy']
        specs.append(candidate)
        inputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
matrix = np.stack(responses, axis=1).astype(np.float64)
full_reference = np.load(ROOT / 'build/queen-mission/pigment-fit-039/reference-srgb.npy')
reference = full_reference.reshape(418, 3, 418, 3, 3).mean((1, 3))[mask]
weight = .35 + np.clip(reference.min(1) * 3, 0, 1)
color = np.array([1, .7, .5])
config = ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL')) / 'datafiles/colormanagement/config.ocio'))
processor = config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR, display='sRGB', view='AgX')).getDefaultCPUProcessor()

def display(values):
    values = np.asarray(values, dtype=np.float32).copy()
    processor.applyRGB(values)
    return values.astype(np.float64)

def loss(powers):
    predicted = display(baseline + (matrix @ powers)[:, None] * color)
    return float(np.mean(weight[:, None] * (predicted - reference) ** 2)), predicted

powers = np.zeros(len(specs))
history = []
for step in range(30):
    value, predicted = loss(powers)
    amplitude = matrix @ powers
    linear = baseline + amplitude[:, None] * color
    epsilon = np.maximum(.0001, amplitude * .005)
    derivative = (display(linear + epsilon[:, None] * color) - display(np.maximum(linear - epsilon[:, None] * color, 0))) / (2 * epsilon[:, None])
    norm = (derivative ** 2).sum(1) * weight
    pixel_rhs = ((reference - predicted) * derivative).sum(1) * weight + norm * amplitude
    scale = np.maximum(np.sqrt((matrix * matrix * norm[:, None]).sum(0)), 1e-6)
    normalized = matrix / scale
    gram = normalized.T @ (normalized * norm[:, None]) + np.eye(len(specs)) * 1e-4
    rhs = normalized.T @ pixel_rhs
    proposal = powers * scale
    for iteration in range(500):
        previous = proposal.copy()
        for index in range(len(specs)):
            proposal[index] = max(0, proposal[index] + (rhs[index] - gram[index] @ proposal) / gram[index, index])
        if np.max(abs(proposal - previous)) < 1e-6:
            break
    target, chosen, new_value = proposal / scale, powers, value
    for rate in (1, .5, .25, .125, .0625):
        trial = powers + (target - powers) * rate
        trial_value, _ = loss(trial)
        if trial_value < new_value:
            chosen, new_value = trial, trial_value
            break
    history.append({'step': step, 'loss': value, 'accepted_loss': new_value})
    powers = chosen
    print('DIRECTIONAL_FIT', history[-1], flush=True)
    if value - new_value < 1e-8:
        break
lights = [dict(spec) for spec in settings['lights'] if spec.get('diffuse_factor', 1) == 1]
for spec, power in zip(specs, powers):
    if power < 1e-7:
        continue
    light = dict(spec)
    light['energy'] *= float(power)
    light['color'] = list(color)
    lights.append(light)
settings['lights'] = lights
settings['variant'] = args.variant
settings['directional_fit'] = {'source': manifest['source'], 'source_sha256': manifest['source_sha256'],
    'manifest': (directory / 'manifest.json').relative_to(ROOT).as_posix(), 'response_inputs': inputs,
    'history': history, 'include_accepted_lights': args.include_accepted_lights,
    'active_gloss_lights': len(lights) - 3,
    'caveat': 'Art-directed distant reflectors fitted through AgX. The reference chooses directions and powers, not composited beauty pixels. Judge the actual saved-model render, not the fit loss.'}
configure(scene, settings)
scene['mission_material_config'] = json.dumps(settings, sort_keys=True)
scene.render.resolution_x = scene.render.resolution_y = 1254
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '8'
scene.render.image_settings.color_mode = 'RGBA'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.filepath = str(out / 'wood.png')
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'queen.blend'))
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
if any(device.use for device in prefs.devices):
    scene.cycles.device = 'GPU'
bpy.ops.render.render(write_still=True)
(out / 'parameters.json').write_text(json.dumps(settings, indent=2) + '\n')
assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['source_sha256']
print('DIRECTIONAL_FIT_RENDER_DONE', args.variant, flush=True)
