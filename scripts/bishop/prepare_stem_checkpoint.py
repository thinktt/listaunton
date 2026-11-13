"""Finalize the supported stem adjustment, omitting a subpixel shoulder fit."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
trial = json.loads((ROOT / 'build/bishop-mission/180-stem-shoulder-stronger/trial-audit.json').read_text())
cfg = trial['config']
assert trial['saved_and_reopened'] and trial['source_unchanged']
source = ROOT / cfg['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['source_sha256']
baseline = json.loads((ROOT / cfg['profile']).read_text())
changes = {k: v for k, v in cfg['body_rings'].items() if int(k) in [34, 35, 36]}
assert len(changes) == 3
for k, (radius, y) in changes.items():
    assert y == baseline['profile'][int(k)][1]
    assert 0 < baseline['profile'][int(k)][0] - radius < 1.5
final = {'variant': '181-stem-checkpoint', 'source': cfg['source'], 'source_sha256': cfg['source_sha256'],
         'profile': cfg['profile'], 'samples': 512, 'body_rings': changes,
         'interpretation': 'Final verification of a narrower mid-stem against the authoritative original, supported by evaluated contour provenance and selected-white detail. Only radii 34-36 change. Every height, lower stem 31-33, upper stem from 37, socket/base/foot, collars/head/button/slit, camera, material, UVs, source registration and lights stay exact from 022. The tiny rear-shoulder proposal is deliberately omitted as unsupported subpixel fitting.'}
out = ROOT / 'docs/bishop-mission/iteration-024'
out.mkdir(exist_ok=True)
(out / 'profile-fit.json').write_text(json.dumps(final, indent=2) + '\n')
print(json.dumps({'variant': final['variant'], 'radial_changes': changes, 'all_heights_preserved': True}, indent=2))
