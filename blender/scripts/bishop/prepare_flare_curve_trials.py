"""Bracket the nearly straight middle flare with two rounded meridians.

Only radii 15--19 change. The saved camera, all heights, socket, groove,
foot and widest roll remain fixed. These are hypotheses, not accepted fits.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
archive = ROOT / 'history/bishop-mission-022'
archive.mkdir(exist_ok=True)
accepted = json.loads((ROOT / 'docs/bishop-mission/iteration-022/checkpoint.json').read_text())
assert sha(ROOT / 'models/bishop/bishop-rebuilt.blend') == accepted['accepted_model_sha256']
files = [('models/bishop/bishop-rebuilt.blend', 'bishop-rebuilt.blend'),
         ('scripts/bishop/profile.json', 'profile.json')]
files += [('assets/bishop/' + name, name) for name in [
    'render.png', 'render-clay.png', 'side-profile.png', 'head-side.png',
    'rear-oblique.png', 'camera.json', 'mesh.json', 'mesh.bin', 'bishop-boxwood-albedo.png']]
for original, name in files:
    source, target = ROOT / original, archive / name
    if target.exists():
        assert sha(source) == sha(target), name
    else:
        shutil.copy2(source, target)

profile = json.loads((archive / 'profile.json').read_text())
out = ROOT / 'build/bishop-mission/172-base-audit'
out.mkdir(exist_ok=True)
r0, y0 = profile['profile'][20]
r1, y1 = profile['profile'][14]
for name, bow in [('gentle', 4.5), ('round', 8.0)]:
    rings = {}
    for i in range(15, 20):
        old_radius, y = profile['profile'][i]
        t = (y - y0) / (y1 - y0)
        radius = r0 + (r1 - r0) * t + bow * t * (1 - t)
        rings[str(i)] = [radius, y]
    cfg = {
        'variant': '173-flare-' + name,
        'source': 'history/bishop-mission-022/bishop-rebuilt.blend',
        'source_sha256': sha(archive / 'bishop-rebuilt.blend'),
        'profile': 'history/bishop-mission-022/profile.json',
        'samples': 64,
        'body_rings': rings,
        'interpretation': 'Unaccepted rounded middle-flare hypothesis. Replace the nearly conical band with a concave-down radius-versus-axis meridian between unchanged controls 20 and 14. All heights and unlisted radii, socket, groove, foot, head and collars stay exact. Save/reopen and inspect the fixed view, authoritative original outline and level view before deciding.',
        'radius_curve': {'formula': 'r0 + (r1-r0)*t + bow*t*(1-t)',
                         'top_ring': 20, 'bottom_ring': 14, 'bow': bow},
    }
    (out / ('flare-' + name + '.json')).write_text(json.dumps(cfg, indent=2) + '\n')
    print(name, {i: round(pair[0] - profile['profile'][int(i)][0], 5) for i, pair in rings.items()})
