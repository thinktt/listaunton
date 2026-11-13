"""Test a real middle-collar undercut without compressing its rounded rim."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
archive = ROOT / 'history/bishop-mission-021'
profile = json.loads((archive / 'profile.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(archive / 'bishop-rebuilt.blend') == json.loads(
    (ROOT / 'docs/bishop-mission/iteration-021/checkpoint.json').read_text())['accepted_model_sha256']
out = ROOT / 'build/bishop-mission/169-collar-occlusion'
out.mkdir(exist_ok=True)
rings = {}
for i, change in [(49, -.4), (50, -1.2)]:
    radius, y = profile['profile'][i]
    rings[str(i)] = [radius + change, y]
cfg = {
    'variant': '170-middle-undercut',
    'source': 'history/bishop-mission-021/bishop-rebuilt.blend',
    'source_sha256': sha(archive / 'bishop-rebuilt.blend'),
    'profile': 'history/bishop-mission-021/profile.json',
    'samples': 64,
    'body_rings': rings,
    'interpretation': 'Unaccepted middle-collar underside hypothesis based on measured near-zero projected overhang: narrow only the two neck controls below the rim. Preserve every height, the outer rim, upper deck, other collar crests, head, button/slit, stem/socket/base, saved camera, registration, UVs, pigment and lights. Check actual occlusion, neutral and level views; a stronger shadow alone is not acceptance.'
}
(out / 'middle-undercut.json').write_text(json.dumps(cfg, indent=2) + '\n')
print('Prepared two-control middle-collar undercut test from archived 021.')
