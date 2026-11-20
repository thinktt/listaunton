"""Measure actual middle-flare curvature independently of wood and lighting."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', required=True)
p.add_argument('--profile', required=True)
p.add_argument('--out', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / a.source
digest = hashlib.sha256(source.read_bytes()).hexdigest()
cfg = json.loads((ROOT / a.profile).read_text())
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
factor = 1254 / 300 / al['scale'] / cfg['scale']
co = math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
bpy.context.view_layer.update()
body = bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get())
inverse = body.matrix_world.inverted()
yy = np.linspace(178, 192, 561)
radii = []
for y in yy:
    start = inverse @ Vector((4, 0, (cfg['y0'] - float(y)) * factor / co))
    direction = inverse.to_3x3() @ Vector((-1, 0, 0))
    hit, point, normal, face = body.ray_cast(start, direction.normalized())
    assert hit
    world = body.matrix_world @ point
    radii.append(math.hypot(world.x, world.y) / factor)
radii = np.array(radii)
samples = []
for i, y in enumerate(yy):
    if not 178.5 <= y <= 191.5:
        continue
    nearby = abs(yy - y) <= .50001
    fit = np.polynomial.polynomial.polyfit(yy[nearby] - y, radii[nearby], 3)
    samples.append({'axis_y': float(y), 'radius': float(radii[i]),
                    'radius_slope': float(fit[1]),
                    'radius_second_derivative': float(2 * fit[2])})
second = np.array([r['radius_second_derivative'] for r in samples])
report = {
    'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'sample_axis_y_range': [178, 192], 'evaluated_axis_y_range': [178.5, 191.5],
    'sample_spacing': .025, 'cubic_fit_half_window': .5,
    'minimum_second_derivative': float(second.min()),
    'maximum_second_derivative': float(second.max()),
    'positive_curvature_fraction_above_0p01': float(np.mean(second > .01)),
    'nearly_straight_fraction_abs_below_0p01': float(np.mean(abs(second) < .01)),
    'samples': samples,
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'method': 'First-hit rays on the actual evaluated side meridian. A local cubic fit suppresses polygon noise. No camera adjustment, texture or light is involved.',
    'limitation': 'Curvature measures the hypothesis, not fidelity to an unknowable original cross-section. Use original and selected images, actual fixed renders and level views to judge acceptance.'
}
assert report['source_unchanged']
out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, indent=2))
