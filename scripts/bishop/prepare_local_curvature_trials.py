"""Propose isolated socket-join and lower-collar underside geometry changes.

Keep the accepted 020 scene exact as the source. These are test hypotheses,
not measured truth or accepted public geometry. No camera or pigment fitting.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
archive = ROOT / 'history/bishop-mission-020'
archive.mkdir(exist_ok=True)
accepted = json.loads((ROOT / 'docs/bishop-mission/iteration-020/checkpoint.json').read_text())
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
out = ROOT / 'build/bishop-mission/159-curvature-audit'
out.mkdir(exist_ok=True)
base = {
    'source': 'history/bishop-mission-020/bishop-rebuilt.blend',
    'source_sha256': sha(archive / 'bishop-rebuilt.blend'),
    'profile': 'history/bishop-mission-020/profile.json',
    'samples': 64,
}
# The current socket top first dips then rises as it leaves the stem. The
# photo suggests a simple rounded join. Test removing only this small concavity,
# retaining radii, outer socket wall, stem, base, button and all collar controls.
target = {29: 162.8, 30: 162.6, 31: 161.6}
for label, amount in [('half', .5), ('full', 1.)]:
    cfg = dict(base, variant='160-socket-' + label,
        body_rings={str(i): [profile['profile'][i][0],
                            profile['profile'][i][1] + amount * (yy - profile['profile'][i][1])]
                    for i, yy in target.items()},
        interpretation='Unaccepted socket-join hypothesis: remove the small inward height reversal between stem and socket crest; preserve outer wall, all radii, collar/head controls, bounds, camera, UVs, pigment and lights.')
    (out / ('socket-' + label + '.json')).write_text(json.dumps(cfg, indent=2) + '\n')

# The full lift removes the dip but raises the visible stem seating point.
# A separate hypothesis keeps that seating point and instead lowers the small
# inward ridge at the socket top. Do not reuse the translated-root variant.
cfg = dict(base, variant='162-socket-crest',
    body_rings={str(i): [profile['profile'][i][0], yy]
                for i, yy in [(28, 163.8), (29, 163.6), (30, 163.55)]},
    interpretation='Unaccepted socket-crest hypothesis: remove the inward height reversal by lowering only the inner crest; preserve the stem seating control, outer wall, all radii and every other part. Source, camera, pigment and lighting stay fixed.')
(out / 'socket-crest.json').write_text(json.dumps(cfg, indent=2) + '\n')

# This differs from the rejected all-three-roll compression: the lower crest
# and entire top/outer roll stay exact. Only three underside controls lift.
# The physical front edge currently reaches about y608; the reference suggests
# a shallower underside near y604, with uncertainty from edge blur/reflection.
cfg = dict(base, variant='161-lower-underside',
    body_rings={str(i): [profile['profile'][i][0], yy]
                for i, yy in [(41, 112.9), (42, 112.5), (43, 111.4)]},
    interpretation='Unaccepted lower-collar underside hypothesis: lift three underside controls while preserving the crest and entire upper roll, all other collars, head, socket, stem, base, bounds and saved 54-degree camera. Not the rejected compression of all three collars.')
(out / 'lower-underside.json').write_text(json.dumps(cfg, indent=2) + '\n')
print('Preserved 020; prepared socket-join and lower-underside tests.')
