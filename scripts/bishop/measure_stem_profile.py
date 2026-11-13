"""Sample the actual turned stem meridian and its slope at fixed height."""
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
p.add_argument('--source', required=True); p.add_argument('--profile', required=True)
p.add_argument('--out', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / a.source; digest = hashlib.sha256(source.read_bytes()).hexdigest()
cfg = json.loads((ROOT / a.profile).read_text())
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
factor = 1254 / 300 / al['scale'] / cfg['scale']; co = math.cos(math.radians(54))
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False); bpy.context.view_layer.update()
body = bpy.data.objects['Bishop - continuous turned body'].evaluated_get(bpy.context.evaluated_depsgraph_get())
inverse = body.matrix_world.inverted()
ys = np.linspace(125, 163, 761); radii = []
for y in ys:
    start = inverse @ Vector((4, 0, (cfg['y0'] - float(y)) * factor / co))
    direction = inverse.to_3x3() @ Vector((-1, 0, 0))
    hit, point, normal, face = body.ray_cast(start, direction.normalized())
    assert hit
    world = body.matrix_world @ point
    radii.append(math.hypot(world.x, world.y) / factor)
radii = np.array(radii); rows = []
for i, y in enumerate(ys):
    if not 126 <= y <= 162: continue
    nearby = abs(ys - y) <= .80001
    fit = np.polynomial.polynomial.polyfit(ys[nearby] - y, radii[nearby], 3)
    rows.append({'axis_y': float(y), 'radius': float(radii[i]),
                 'slope': float(fit[1]), 'second_derivative': float(2 * fit[2]),
                 'tangent_angle_from_vertical_degrees': math.degrees(math.atan(co * fit[1]))})
angles = np.array([r['tangent_angle_from_vertical_degrees'] for r in rows])
report = {'source': a.source, 'source_sha256': digest, 'profile': a.profile,
    'method': 'First-hit horizontal rays on actual evaluated side meridian. Cubic fits over +/-0.8 original-axis units suppress facet noise. No shader or camera fitting.',
    'radius_monotone_over_full_sampled_range': bool(np.min(np.diff(radii)) >= -1e-5),
    'waist_axis_y': float(ys[np.argmin(radii)]),
    'minimum_radius': float(np.min(radii)),
    'radius_monotone_after_measured_waist': bool(np.min(np.diff(radii[np.argmin(radii):])) >= -1e-5),
    'maximum_tangent_angle_degrees': float(angles.max()),
    'steepest_tangent_at_axis_y': rows[int(np.argmax(angles))]['axis_y'],
    'rows': rows, 'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
    'limitation': 'The full sampled range includes the approach to the waist, so monotonicity over that entire range is not a pass criterion. Slope statistics characterize taper changes; they do not certify visual fidelity or establish a unique recovered profile.'}
assert report['source_unchanged']
out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
