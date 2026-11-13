"""Test the lower-head depth interpretation at a pinned front meridian.

These proposals are not accepted geometry. A coupled radius/height adjustment
preserves each changed control's projected front-meridian position at 54
degrees, while altering the actual turned surface's lower cross-section.
Saved renders, original outline, slit boundary and level views decide fit.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
archive = ROOT / 'history/bishop-mission-021'
archive.mkdir(exist_ok=True)
accepted = json.loads((ROOT / 'docs/bishop-mission/iteration-021/checkpoint.json').read_text())
assert sha(ROOT / 'models/bishop/bishop-rebuilt.blend') == accepted['accepted_model_sha256']
files = [('models/bishop/bishop-rebuilt.blend', 'bishop-rebuilt.blend'),
         ('scripts/bishop/profile.json', 'profile.json')]
files += [('assets/bishop/' + name, name) for name in [
    'render.png', 'render-clay.png', 'side-profile.png', 'head-side.png',
    'rear-oblique.png', 'camera.json', 'mesh.json', 'mesh.bin', 'bishop-boxwood-albedo.png']]
for original, name in files:
    source, destination = ROOT / original, archive / name
    if destination.exists():
        assert sha(source) == sha(destination), name
    else:
        shutil.copy2(source, destination)

profile = json.loads((archive / 'profile.json').read_text())
out = ROOT / 'build/bishop-mission/164-head-audit'
out.mkdir(exist_ok=True)
sn = math.sin(math.radians(54))
for label, amplitude, width in [('gentle', 1.25, 6), ('fuller', 2.5, 6), ('convex', 1.25, 10)]:
    rings = {}
    for i in range(65, 65 + width):
        t = (i - 65) / width
        weight = 1 - 10 * t**3 + 15 * t**4 - 6 * t**5
        delta = amplitude * weight
        radius, y = profile['profile'][i]
        rings[str(i)] = [radius + delta, y - sn * delta]
        assert abs((radius + delta) * sn + y - sn * delta - (radius * sn + y)) < 1e-9
    cfg = {
        'variant': ('168-head-turn-' if label == 'convex' else '165-head-turn-') + label,
        'source': 'history/bishop-mission-021/bishop-rebuilt.blend',
        'source_sha256': sha(archive / 'bishop-rebuilt.blend'),
        'profile': 'history/bishop-mission-021/profile.json',
        'samples': 64,
        'body_rings': rings,
        'interpretation': 'Unaccepted lower-head turn hypothesis: reduce the inward tuck into the upper collar using a fuller lower meridian. Coupled radius/height edits pin each front control projection at the saved 54-degree camera. Unlisted controls, cutter, button, collars, lower body, UVs, pigment and lights stay fixed. This is a depth interpretation, not an alignment change.',
        'radial_amplitude': amplitude,
        'transition_width_controls': width,
        'projection_constraint': 'axis_y + radius * sin(54 degrees), preserved per edited control',
    }
    q = np.array(profile['profile'], dtype=float)
    for i, pair in rings.items():
        q[int(i)] = pair
    d = np.diff(q[65:84] * [1, -1 / math.cos(math.radians(54))], axis=0)
    cross = d[:-1, 0] * d[1:, 1] - d[:-1, 1] * d[1:, 0]
    cfg['lower_head_control_polygon_curvature_cross_products'] = cross.tolist()
    if label == 'convex':
        assert np.min(cross) > 0, 'The lower-head proposal must not add an inflection.'
    (out / ('head-' + label + '.json')).write_text(json.dumps(cfg, indent=2) + '\n')
print('Preserved 021; prepared lower-head turn hypotheses, including a convex transition.')
