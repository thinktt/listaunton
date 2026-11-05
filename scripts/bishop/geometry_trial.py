"""Edit measured bishop lathe rings in an isolated trial, keeping the 54-degree camera."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('config', type=Path)
parser.add_argument('--no-render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
spec = json.loads(args.config.read_text())
source = ROOT/spec['source']
if 'source_sha256' in spec:
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['source_sha256'], 'Geometry trial source differs from its recorded baseline.'
out = ROOT/'build/bishop-mission'/spec['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True, exist_ok=True)
profile = json.loads((ROOT/spec.get('profile', 'scripts/bishop/profile.json')).read_text())
alignment = json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
factor = 1254/300/alignment['scale']/profile['scale']
cosine = math.cos(math.radians(profile['elevation']))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
camera_before = [float(x) for row in scene.camera.matrix_world for x in row]
body = bpy.data.objects['Bishop - continuous turned body']
button = bpy.data.objects['Bishop - domed button finial']
for index, radius_y in spec.get('body_rings', {}).items():
    index = int(index)
    old_radius, old_y = profile['profile'][index]
    radius, axis_y = radius_y
    for vertex in body.data.vertices[index*128:(index+1)*128]:
        vertex.co.x *= radius/old_radius
        vertex.co.y *= radius/old_radius
        vertex.co.z += (old_y-axis_y)*factor/cosine
    profile['profile'][index] = [radius, axis_y]
button_scale = spec.get('button_scale_xy', 1)
for vertex in button.data.vertices:
    vertex.co.x *= button_scale
    vertex.co.y *= button_scale
for point in profile['finial']['profile']:
    point[0] *= button_scale
profile['revision'] = spec['variant']
declaration_key = spec.get('declaration_key', 'mission_geometry')
assert declaration_key in {'mission_geometry', 'mission_base_curvature'}
profile[declaration_key] = {
    'baseline_model': spec['source'],
    'baseline_profile': spec.get('profile', 'scripts/bishop/profile.json'),
    'changed_body_rings': sorted(int(index) for index in spec.get('body_rings', {})),
    'button_scale_xy': button_scale,
    'body_rings': spec.get('body_rings', {}),
    'interpretation': spec.get('interpretation', 'Slightly broader shallow button and flatter lower foot; fixed camera, head, slit, flare, socket, stem and collars preserved.')
}
if declaration_key == 'mission_base_curvature':
    assert spec.get('declaration_config'), 'Base curvature edits require an explicit tracked reproduction config.'
    profile[declaration_key]['config'] = spec['declaration_config']
    profile[declaration_key]['baseline_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
body.data.update();button.data.update();bpy.context.view_layer.update()
assert camera_before == [float(x) for row in scene.camera.matrix_world for x in row]
scene.cycles.samples = spec.get('samples', 32)
scene.render.resolution_percentage = 100
scene.render.filepath = str(out/'wood.png')
scene['bishop_geometry_trial'] = json.dumps(spec, sort_keys=True)
spec['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
spec['fixed_camera'] = camera_before
spec['note'] = 'Pigment UVs and lighting retained for isolated shape comparison; reproject/rebake after geometry acceptance.'
(out/'parameters.json').write_text(json.dumps(spec, indent=2)+'\n')
(out/'profile.json').write_text(json.dumps(profile, indent=2)+'\n')
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
try:
    preferences = bpy.context.preferences.addons['cycles'].preferences
    preferences.compute_device_type = 'OPTIX';preferences.get_devices()
    for device in preferences.devices:device.use = device.type=='OPTIX'
    if any(device.use for device in preferences.devices):scene.cycles.device = 'GPU'
except Exception as error:
    print('CPU fallback', error)
if not args.no_render:bpy.ops.render.render(write_still=True)
print('BISHOP_GEOMETRY_TRIAL_COMPLETE', spec['variant'], flush=True)
