"""Measure lower-head curvature on the evaluated surface, not control outlines.

An internal ridge can be hidden by an unchanged external silhouette. Sample
the side meridian below the slit, then estimate curvature over a documented
physical window larger than the evaluated polygon spacing. Diagnostic only.
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
yy = np.linspace(81.5, 89.5, 321)
radii = []
for y in yy:
    start = inverse @ Vector((4, 0, (cfg['y0'] - float(y)) * factor / co))
    direction = inverse.to_3x3() @ Vector((-1, 0, 0))
    hit, point, normal, face = body.ray_cast(start, direction.normalized())
    assert hit
    world = body.matrix_world @ point
    radii.append(math.hypot(world.x, world.y) / factor)
radii = np.array(radii)
measurements = []
for i, y in enumerate(yy):
    if not 82 <= y <= 89:
        continue
    nearby = abs(yy - y) <= .40001
    fit = np.polynomial.polynomial.polyfit(yy[nearby] - y, radii[nearby], 3)
    measurements.append({'axis_y': float(y), 'radius': float(radii[i]),
                         'radius_slope': float(fit[1]), 'radius_second_derivative': float(2 * fit[2])})
# For an outward-convex lathed bulb, radius is concave as a function of axis
# height. Positive second derivative identifies the unwanted inward flex.
second = np.array([r['radius_second_derivative'] for r in measurements])
positive = second > .02
longest = run = 0
for flag in positive:
    run = run + 1 if flag else 0
    longest = max(longest, run)
report = {
    'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'sample_axis_y_range': [81.5, 89.5], 'evaluated_axis_y_range': [82, 89],
    'sample_spacing': .025, 'cubic_fit_half_window': .4,
    'method': 'First-hit horizontal rays against the actual evaluated side meridian below the cut. Local cubic fits reduce polygon-facet noise. Camera, textures and lighting are unused and unchanged.',
    'minimum_second_derivative': float(second.min()),
    'maximum_second_derivative': float(second.max()),
    'longest_inward_flex_interval_over_0p02': float(longest * .025),
    'samples': measurements,
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'note': 'Curvature is a geometry diagnostic, not a photo-match score. The sampled band excludes the intended collar/head valley.'
}
assert report['source_unchanged']
out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}, indent=2))
