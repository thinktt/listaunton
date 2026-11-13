"""Trace actual front-meridian turning at each collar under the saved camera.

A local maximum followed by a minimum in projected vertical position is a
potential overhang/occlusion interval. This is distinct from a bright glint
or dark pigment band. Keep the model and all render settings unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--profile', default='scripts/bishop/profile.json')
p.add_argument('--out', default='build/bishop-mission/169-collar-occlusion/current.json')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = ROOT / a.source
digest = hashlib.sha256(source.read_bytes()).hexdigest()
cfg = json.loads((ROOT / a.profile).read_text())
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
factor = 1254 / 300 / al['scale'] / cfg['scale']
co = math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
bpy.context.view_layer.update()
scene = bpy.context.scene
direction = scene.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
elevation = math.degrees(math.asin(-direction.normalized().z))
assert scene.camera.data.type == 'ORTHO' and abs(elevation - 54) < 1e-4
body = bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get())
inverse = body.matrix_world.inverted()
bands = {'upper': [92, 99], 'middle': [99, 106.05], 'lower': [106.5, 118]}
results = {}
for name, (y0, y1) in bands.items():
    axis = np.linspace(y0, y1, round((y1 - y0) / .01) + 1)
    rows = []
    for yy in axis:
        start = inverse @ Vector((0, -4, (cfg['y0'] - float(yy)) * factor / co))
        direction = inverse.to_3x3() @ Vector((0, 1, 0))
        hit, point, normal, face = body.ray_cast(start, direction.normalized())
        assert hit
        world = body.matrix_world @ point
        pixel = world_to_camera_view(scene, scene.camera, world)
        rows.append({'axis_y': float(yy), 'radius': float(math.hypot(world.x, world.y) / factor),
                     'pixel_y': float((1 - pixel.y) * 1254)})
    py = np.array([row['pixel_y'] for row in rows])
    # Average over 0.05 original units to suppress polygon/floating-point jitter.
    smooth = np.convolve(np.pad(py, (2, 2), mode='edge'), np.ones(5) / 5, mode='valid')
    derivative = np.diff(smooth)
    peaks = np.flatnonzero((derivative[:-1] > 1e-5) & (derivative[1:] <= 0)) + 1
    valleys = np.flatnonzero((derivative[:-1] < -1e-5) & (derivative[1:] >= 0)) + 1
    intervals = []
    for peak in peaks:
        following = valleys[valleys > peak]
        if len(following):
            valley = int(following[0])
            amount = float(smooth[peak] - smooth[valley])
            if amount > .005:
                intervals.append({'crest': rows[int(peak)], 'following_neck': rows[valley],
                                  'projected_overhang_px': amount})
    results[name] = {'axis_range': [y0, y1], 'samples': rows, 'overhang_intervals': intervals}
report = {
    'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'method': 'Evaluated-body front radial rays, projected through the exact saved camera. Turning extrema are based on geometry alone, without materials or image edges.',
    'camera_degrees_measured': elevation, 'bands': results,
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'caution': 'Center-meridian occlusion potential is not a complete visibility map or a photographic match score. Confirm full arcs and fixed/side renders before acceptance.'
}
assert report['source_unchanged']
out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({name: row['overhang_intervals'] for name, row in results.items()}, indent=2))
