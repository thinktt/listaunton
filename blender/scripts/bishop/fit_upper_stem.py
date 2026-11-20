"""Fit the exposed neck immediately below the lowest collar, at fixed 54 degrees."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'build/bishop-mission/176-neck-audit'
out.mkdir(exist_ok=True)
archive = ROOT / 'history/bishop-mission-022'
cfg = json.loads((archive / 'profile.json').read_text())
profile = np.array(cfg['profile'], dtype=float)
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
F = 1254 / 300 / al['scale']; sn = math.sin(math.radians(54))
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE, (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
ar = np.array(original)
mask = (ar[:, :, 3] > 127) & (ar[:, :, :3].max(2) > 12)
render = np.array(Image.open(archive / 'render.png').convert('RGBA'))[:, :, 3] > 127
ys = np.arange(608, 635)
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
indices = np.array([33, 34, 35, 36])
start = profile[indices, 0].copy()
def proposed(v):
    q = profile.copy()
    q[indices, 0] = v
    return q
def residual(v):
    q = proposed(v)
    part = q[33:38][::-1]
    slopes = np.diff(part[:, 0]) / np.diff(part[:, 1])
    return np.r_[outline(q) + bias - target, .7 * (v - start), 1.5 * np.diff(v - start, 2),
                 30 * np.minimum(np.diff(slopes), 0), 30 * np.minimum(np.diff(part[:, 0]) - .05, 0)]
v = start.copy(); trials = []
for iteration in range(25):
    error = residual(v)
    J = np.stack([(residual(v + np.eye(len(v))[i] * .025) - error) / .025 for i in range(len(v))], axis=1)
    delta = np.linalg.solve(J.T @ J + np.eye(len(v)) * .5, -J.T @ error)
    found = False
    for scale in [1, .5, .25, .125, .0625]:
        candidate = np.clip(v + scale * delta, start - 1.5, start + 1.5)
        if np.linalg.norm(residual(candidate)) < np.linalg.norm(error) - 1e-8:
            v = candidate; found = True; break
    trials.append({'iteration': iteration, 'loss': float(np.mean(residual(v)**2))})
    if not found: break
q = proposed(v)
best = {'radii': v.tolist(), 'mean_absolute_half_width_error': float(abs(outline(q) + bias - target).mean()),
        'loss': float(np.mean(residual(v)**2))}
spec = {'variant': '176-narrower-upper-stem', 'source': 'history/bishop-mission-022/bishop-rebuilt.blend',
        'source_sha256': hashlib.sha256((archive / 'bishop-rebuilt.blend').read_bytes()).hexdigest(),
        'profile': 'history/bishop-mission-022/profile.json', 'samples': 64,
        'body_rings': {str(i): q[i].tolist() for i in indices},
        'interpretation': 'Unaccepted local stem taper fit. The low part of the taper forms the elevated outline below the collar; controls 38-40 do not affect this boundary. Change radii 33-36 only, regularized for a smooth concave taper. All heights, collar rims, socket/base and head remain exact. Original white is the fitting target; actual neutral and level views govern acceptance.',
        'proposal': best}
(out / 'neck-fit.json').write_text(json.dumps(spec, indent=2) + '\n')
report = {'baseline_error': float(abs(actual - target).mean()), 'proposal': best,
          'rows': ys.tolist(), 'original_half_width': target.tolist(), 'baseline_half_width': actual.tolist(),
          'predicted_half_width': (outline(q) + bias).tolist(), 'trials': trials,
          'limitation': 'Analytical outline proxy, bias-corrected from actual baseline. No camera or reference change, and no acceptance from this fit alone.'}
(out / 'prediction.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'baseline': report['baseline_error'], 'proposal': best, 'rings': spec['body_rings']}, indent=2))
