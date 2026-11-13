"""Fit a bounded height adjustment for the rounded flare to the original.

The actual baseline render corrects a simple subdivision proxy's bias.
The original registration and camera stay fixed; Blender must verify the fit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--family', choices=['coupled', 'smooth'], default='coupled')
a = p.parse_args()
out = ROOT / 'build/bishop-mission/172-base-audit'
cfg = json.loads((out / 'flare-round.json').read_text())
base = json.loads((ROOT / cfg['profile']).read_text())
profile = np.array(base['profile'], dtype=float)
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
F = 1254 / 300 / al['scale']
sn = math.sin(math.radians(54))
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE, (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
ar = np.array(original)
mask = (ar[:, :, 3] > 127) & (ar[:, :, :3].max(2) > 12)
render = np.array(Image.open(ROOT / 'history/bishop-mission-022/render.png').convert('RGBA'))[:, :, 3] > 127
ys = np.arange(630, 1040, 2)
def widths(m):
    return np.array([(lambda x: (x[-1] - x[0] + 1) / 2)(np.flatnonzero(m[y])) for y in ys])
target, actual = widths(mask), widths(render)
def outline(pro):
    pro = pro[:40]
    smooth = pro.copy()
    smooth[1:-1] = .125 * pro[:-2] + .75 * pro[1:-1] + .125 * pro[2:]
    q = np.empty((len(pro) * 2 - 1, 2))
    q[::2] = smooth
    q[1::2] = (pro[:-1] + pro[1:]) / 2
    t = np.linspace(0, 1, 20, endpoint=False)
    q = (q[:-1, None] * (1 - t[None, :, None]) + q[1:, None] * t[None, :, None]).reshape(-1, 2)
    r, cy = q[:, 0] * F, (q[:, 1] - al['y'] * 3) * F
    return np.sqrt(np.maximum(r[None]**2 - ((ys[:, None] - cy[None]) / sn)**2, 0)).max(1)
bias = actual - outline(profile)
def proposed(coupling):
    q = profile.copy()
    for key, (radius, y) in cfg['body_rings'].items():
        i = int(key)
        t = (y - profile[20, 1]) / (profile[14, 1] - profile[20, 1])
        delta_y = coupling * ((radius - profile[i, 0]) if a.family == 'coupled' else t * (1 - t))
        q[i] = [radius, y + delta_y]
    return q
trials = []
for coupling in np.linspace(0, 1.5 if a.family == 'coupled' else 4.5, 61):
    q = proposed(coupling)
    if np.any(np.diff(q[14:21, 1]) >= -.2):
        continue
    error = outline(q) + bias - target
    trials.append({'coupling': float(coupling), 'mean_absolute_original_half_width_error': float(abs(error).mean()),
                   'rms': float(np.sqrt(np.mean(error**2)))})
best = min(trials, key=lambda row: row['rms'])
q = proposed(best['coupling'])
cfg.update(variant='174-rounded-flare-refit' if a.family == 'coupled' else '175-smooth-flare-refit', body_rings={str(i): q[i].tolist() for i in range(15, 20)},
           interpretation='Unaccepted smooth flare with locally lowered profile controls to refit the original-white outline. Only radii/heights 15-19 change; fixed endpoints, socket, groove, foot, other controls, camera, materials and source registration remain exact. Actual render and physical surface determine acceptance.',
           height_fit={'family': a.family, 'coupling': best['coupling'],
                       'formula': 'new_y = old_y + coupling * ' + ('(new_radius - old_radius)' if a.family == 'coupled' else 't*(1-t)'),
                       'source': 'authoritative original white', 'proxy_only': True})
prefix = 'flare-refit' if a.family == 'coupled' else 'flare-smooth-refit'
(out / (prefix + '.json')).write_text(json.dumps(cfg, indent=2) + '\n')
report = {'best': best, 'baseline_mean_absolute_original_half_width_error': float(abs(actual - target).mean()),
          'baseline_rms': float(np.sqrt(np.mean((actual - target)**2))), 'rows': ys.tolist(),
          'original_half_width': target.tolist(), 'baseline_half_width': actual.tolist(),
          'predicted_half_width': (outline(q) + bias).tolist(), 'trials': trials,
          'note': 'One bounded geometry coupling, not reference/camera manipulation. A biased analytical proxy proposes a trial; it cannot certify fidelity.'}
(out / (prefix + '-prediction.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['best', 'baseline_mean_absolute_original_half_width_error', 'baseline_rms']}, indent=2))
