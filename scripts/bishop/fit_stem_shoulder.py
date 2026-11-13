"""Fit the stem/base contour crossover without inventing a lower-stem bulge.

Actual first-hit contour probes identify two surfaces. A bounded stem-radius
reduction and a front-pinned rear-shoulder change fit those surfaces separately.
The proxy proposes geometry only; actual rendered/level evidence is required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--max-stem', type=float, default=.8)
p.add_argument('--label', choices=['fit', 'stronger'], default='fit')
a = p.parse_args()
assert 0 < a.max_stem <= 1.5
out = ROOT / 'build/bishop-mission/178-contour-audit'
out.mkdir(exist_ok=True)
archive = ROOT / 'history/bishop-mission-022'
source = archive / 'bishop-rebuilt.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
cfg = json.loads((archive / 'profile.json').read_text())
capture = json.loads((out / 'meridians.json').read_text())
assert capture['source_sha256'] == sha(source) and capture['source_unchanged']
profile = np.array(cfg['profile'], dtype=float)
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
F = 1254 / 300 / al['scale']; sn = math.sin(math.radians(54))
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE, (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
ar = np.array(original)
mask = (ar[:, :, 3] > 127) & (ar[:, :, :3].max(2) > 12)
render = np.array(Image.open(archive / 'render.png').convert('RGBA'))[:, :, 3] > 127
ys = np.arange(590, 796, 1)
def widths(m):
    return np.array([(lambda x: (x[-1] - x[0] + 1) / 2)(np.flatnonzero(m[y])) for y in ys])
target, actual = widths(mask), widths(render)
def outline(pro):
    pro = pro[:65]
    smooth = pro.copy()
    smooth[1:-1] = .125 * pro[:-2] + .75 * pro[1:-1] + .125 * pro[2:]
    q = np.empty((len(pro) * 2 - 1, 2)); q[::2] = smooth; q[1::2] = (pro[:-1] + pro[1:]) / 2
    t = np.linspace(0, 1, 20, endpoint=False)
    q = (q[:-1, None] * (1 - t[None, :, None]) + q[1:, None] * t[None, :, None]).reshape(-1, 2)
    r, cy = q[:, 0] * F, (q[:, 1] - al['y'] * 3) * F
    return np.sqrt(np.maximum(r[None]**2 - ((ys[:, None] - cy[None]) / sn)**2, 0)).max(1)
bias = actual - outline(profile)
stem_weights = {34: 1., 35: .45, 36: .10}
base_weights = {18: .4, 19: 1., 20: .7, 21: .2}
def proposed(v):
    q = profile.copy()
    for i, weight in stem_weights.items(): q[i, 0] -= weight * v[0]
    for i, weight in base_weights.items():
        dr = weight * v[1]
        q[i] += [dr, -sn * dr]
        assert abs(q[i, 1] + sn * q[i, 0] - profile[i, 1] - sn * profile[i, 0]) < 1e-8
    return q
def residual(v):
    error = outline(proposed(v)) + bias - target
    return np.r_[error * np.where(ys < 636, math.sqrt(2), 1), .5 * v]
v = np.zeros(2); trace = []
for step in range(25):
    e = residual(v)
    J = np.stack([(residual(v + np.eye(2)[i] * .02) - e) / .02 for i in range(2)], axis=1)
    delta = np.linalg.solve(J.T @ J + np.eye(2) * .5, -J.T @ e)
    found = False
    for amount in [1, .5, .25, .125, .0625]:
        candidate = np.clip(v + delta * amount, [0, -.8], [a.max_stem, .8])
        if np.linalg.norm(residual(candidate)) < np.linalg.norm(e) - 1e-8:
            v = candidate; found = True; break
    trace.append({'parameters': v.tolist(), 'loss': float(np.mean(residual(v)**2))})
    if not found: break
q = proposed(v)
indices = sorted(set(stem_weights) | set(base_weights))
spec = {'variant': '179-stem-shoulder-crossover' if a.label == 'fit' else '180-stem-shoulder-stronger', 'source': 'history/bishop-mission-022/bishop-rebuilt.blend',
        'source_sha256': sha(source), 'profile': 'history/bishop-mission-022/profile.json', 'samples': 64,
        'body_rings': {str(i): q[i].tolist() for i in indices},
        'interpretation': 'Unaccepted two-surface fit. Narrow stem controls 34-36 conservatively, retaining lower stem 33 and root. Adjust rear-shoulder controls 18-21 with y + r*sin(54) pinned per control. Actual contour probes identify the branch switch; camera/reference registration, collar/socket/foot/head and unlisted controls remain exact.',
        'parameters': {'stem_narrowing': float(v[0]), 'rear_shoulder_radial_amplitude': float(v[1])},
        'front_meridian_constraint': 'axis_y + radius*sin(54 degrees), exact at changed base controls'}
(out / ('crossover-' + a.label + '.json')).write_text(json.dumps(spec, indent=2) + '\n')
report = {'source_sha256': sha(source), 'rows': ys.tolist(), 'original_half_width': target.tolist(),
          'baseline_half_width': actual.tolist(), 'predicted_half_width': (outline(q) + bias).tolist(),
          'before_mean_absolute_error': float(abs(actual - target).mean()),
          'proposal_mean_absolute_error': float(abs(outline(q) + bias - target).mean()),
          'parameters': spec['parameters'], 'trace': trace,
          'note': 'Measured current surface provenance motivates two bounded modes. Bias-corrected analytical outlines are proposals; no shader, source transform or camera is fitted.'}
(out / ('crossover-prediction' + ('' if a.label == 'fit' else '-' + a.label) + '.json')).write_text(json.dumps(report, indent=2) + '\n')
colors = {'stem': '#45e6ff', 'base': '#ff6eae', 'collars': '#ffe07a', 'socket': '#a1e581', 'foot': '#dfb3ff'}
canvas = Image.new('RGB', (2000, 530), '#14181c')
for col, (name, im) in enumerate([('Original white + current contour provenance', original),
                                ('Current neutral + actual contour provenance', Image.open(archive / 'render-clay.png'))]):
    im = im.convert('RGBA'); draw = ImageDraw.Draw(im)
    for row in capture['rows']:
        if not 580 <= row['pixel_y'] <= 810: continue
        for side in row['sides'].values():
            x, y = side['pixel_x'], row['pixel_y']
            draw.ellipse((x-1.1, y-1.1, x+1.1, y+1.1), fill=colors[side['region']])
    im = im.crop((240, 570, 740, 810)).resize((1000, 480), Image.Resampling.LANCZOS)
    canvas.paste(im, (col*1000, 30), im)
    ImageDraw.Draw(canvas).text((col*1000+8, 8), name, fill='white')
ImageDraw.Draw(canvas).text((12, 513), 'Cyan: actual stem surface. Pink: rear base. Yellow: collar. Sources and registration unchanged.', fill='white')
canvas.save(out / 'contour-provenance.png')
print(json.dumps({k: report[k] for k in ['before_mean_absolute_error', 'proposal_mean_absolute_error', 'parameters']}, indent=2))
