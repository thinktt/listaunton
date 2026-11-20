"""Measure one existing collar reflector at surface-derived positions.

These EXR response passes are diagnostics, not candidate beauty renders.
The accepted source, geometry, camera, pigment and other lamps stay unchanged.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', default='history/bishop-mission-013/bishop-rebuilt.blend')
p.add_argument('--out', default='build/bishop-mission/109-collar-basis')
p.add_argument('--samples', type=int, default=96)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / a.source
out = ROOT / a.out
assert out.resolve().is_relative_to((ROOT / 'build/bishop-mission').resolve())
out.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
measurements = ROOT / 'build/bishop-mission/108-collar-normals'
geometry = json.loads((measurements / 'geometry.json').read_text())
normal = json.loads((measurements / 'manifest.json').read_text())
assert geometry['_provenance']['source_sha256'] == normal['source_sha256'] == digest
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
s = bpy.context.scene
lamp = bpy.data.objects['collars reflection']
assert lamp.visible_glossy and not lamp.visible_diffuse
view = np.array(s.camera.matrix_world.to_3x3() @ Vector((0, 0, 1)))
view /= np.linalg.norm(view)

def measured(names, width, height):
    target = np.mean([geometry[name]['surface'] for name in names], axis=0)
    directions = []
    for name in names:
        n = np.array(normal['points'][name]['normal'])
        directions.append(2 * np.dot(n, view) * n - view)
    direction = np.mean(directions, axis=0)
    direction /= np.linalg.norm(direction)
    return dict(name=lamp.name, position=(target + 7 * direction).tolist(),
                target=target.tolist(), shape='RECTANGLE', size=width, size_y=height)

original = dict(name=lamp.name, position=list(lamp.location),
                target=list(lamp.location + lamp.rotation_euler.to_matrix() @ Vector((0, 0, -7))),
                shape=lamp.data.shape, size=lamp.data.size, size_y=lamp.data.size_y)
cases = {
    'old-placement': original,
    'right-arc': measured(['middle right', 'lower right'], 3.2, .7),
    'right-wide': measured(['middle right', 'lower right'], 6, .7),
    'right-tall': measured(['middle right', 'lower right'], 3.2, 2),
    'lower-left': measured(['lower left', 'lower middle'], 3.2, .7),
}
s.render.resolution_percentage = 100
s.render.use_border = True
s.render.use_crop_to_border = False
box = [290, 405, 690, 630]
w, h = s.render.resolution_x, s.render.resolution_y
s.render.border_min_x = box[0] / w
s.render.border_max_x = box[2] / w
s.render.border_min_y = 1 - box[3] / h
s.render.border_max_y = 1 - box[1] / h
s.render.image_settings.file_format = 'OPEN_EXR'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.color_depth = '32'
s.cycles.samples = a.samples
s.cycles.use_adaptive_sampling = False
s.cycles.use_denoising = True
s.render.use_persistent_data = True
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == 'OPTIX'
s.cycles.device = 'GPU' if any(d.use for d in prefs.devices) else 'CPU'

def render(label):
    path = out / (label + '.exr')
    s.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(str(path), check_existing=False)
    pixels = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
    np.save(out / (label + '.npy'), pixels)
    bpy.data.images.remove(im)
    print('COLLAR_BASIS_RENDERED', label, flush=True)

render('accepted')
lamp.data.energy = 0
render('off')
for label, spec in cases.items():
    lamp.location = spec['position']
    lamp.rotation_euler = (Vector(spec['target']) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
    for key in ['shape', 'size', 'size_y']:
        setattr(lamp.data, key, spec[key])
    lamp.data.color = (1, 1, 1)
    lamp.data.energy = 200
    render(label)
assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
record = dict(source=a.source, source_sha256=digest, source_unchanged=True,
              basis_energy=200, samples=a.samples, fixed_samples=True, border=box,
              cases=cases, landmarks='scripts/bishop/collar-landmarks-108.json',
              normal_measurement='build/bishop-mission/108-collar-normals/manifest.json',
              note='Unsaved real-BSDF response passes; only the existing collar lamp changes.')
(out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n', newline='\n')
print('COLLAR_BASIS_COMPLETE', flush=True)
