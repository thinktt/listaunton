"""Preserve rejected geometry experiments without replacing accepted assets."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'docs/bishop-mission/iteration-023'
out.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((ROOT / 'docs/bishop-mission/iteration-022/checkpoint.json').read_text())
assert sha(ROOT / 'models/bishop/bishop-rebuilt.blend') == baseline['accepted_model_sha256']
assert sha(ROOT / 'assets/bishop/render.png') == baseline['accepted_render_sha256']
assert sha(ROOT / 'history/bishop-mission-022/bishop-rebuilt.blend') == baseline['accepted_model_sha256']

def cp(relative, destination):
    path = ROOT / relative
    target = out / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)

cases = [
    ('173-flare-gentle', 'A smoother base meridian, but the original-white outline worsens and fixed-view improvement is too small to justify replacing the accepted shape.'),
    ('173-flare-round', 'Clearer rounding in profile, but the rear shoulder grows beyond the original and fixed-view highlights become more conspicuous. No convincing overall fit improvement.'),
    ('174-rounded-flare-refit', 'A slightly better outline hides renewed inward curvature and a nearly straight band. Reject the physical shape despite the higher overlap.'),
    ('175-smooth-flare-refit', 'Avoids the inward bend but remains nearly straight through much of the sampled flare. Slightly worse original outline and no convincing fixed-view gain.'),
    ('176-narrower-upper-stem', 'Reduces the exposed-neck outline error, but the lower stem develops a visible bulge and abrupt bend. Reject despite higher overlap against all three images.'),
]
decisions = []
for variant, reason in cases:
    trial = ROOT / 'build/bishop-mission' / variant
    audit = json.loads((trial / 'trial-audit.json').read_text())
    assert audit['source_unchanged'] and audit['saved_and_reopened']
    assert audit['materials_lighting_camera_uvs_topology_and_cutter_preserved']
    assert audit['config']['source_sha256'] == baseline['accepted_model_sha256']
    assert sha(trial / 'bishop.blend') == audit['model_sha256']
    target = out / 'trials' / variant
    target.mkdir(parents=True, exist_ok=True)
    (target / 'config.json').write_text(json.dumps(audit['config'], indent=2) + '\n')
    for name in ['wood.png', 'neutral.png', 'profile.json', 'trial-audit.json', 'flare-curve.json',
                 'comparison/metrics.json', 'geometry-rows.json', 'row-coordinates.json', 'studio/side.png', 'studio/studio.json']:
        if (trial / name).exists():
            cp((trial / name).relative_to(ROOT), Path('trials') / variant / name)
    metrics = json.loads((trial / 'comparison/metrics.json').read_text())
    assert metrics['render_sha256'] == sha(trial / 'wood.png')
    studio = json.loads((trial / 'studio/studio.json').read_text())
    assert studio['source_sha256'] == audit['model_sha256'] and studio['source_unchanged']
    row = {'variant': variant, 'accepted': False, 'reason': reason,
           'model_sha256': audit['model_sha256'],
           'outline_iou': {k: v['silhouette_iou'] for k, v in metrics['images'].items()}}
    if (trial / 'flare-curve.json').exists():
        curve = json.loads((trial / 'flare-curve.json').read_text())
        assert curve['source_sha256'] == audit['model_sha256'] and curve['source_unchanged']
        row['curvature'] = {k: curve[k] for k in ['maximum_second_derivative',
            'positive_curvature_fraction_above_0p01', 'nearly_straight_fraction_abs_below_0p01']}
    decisions.append(row)

for name in ['curve-before.json', 'base-control-arcs.png', 'socket-control-arcs.png',
             'flare-wood.png', 'flare-neutral.png', 'flare-side.png',
             'flare-refit-prediction.json', 'flare-smooth-refit-prediction.json']:
    cp('build/bishop-mission/172-base-audit/' + name, 'base-study/' + name)
for path in (ROOT / 'build/bishop-mission/176-neck-audit').glob('*'):
    if path.is_file(): cp(path.relative_to(ROOT), Path('stem-study') / path.name)

# A single common-camera row makes the worse stem transition easy to inspect.
paths = [('Accepted 022', ROOT / 'build/bishop-mission/171-studio/side.png')]
paths += [(variant, ROOT / 'build/bishop-mission' / variant / 'studio/side.png') for variant, _ in cases]
canvas = Image.new('RGB', (330 * len(paths), 690), '#14181c')
draw = ImageDraw.Draw(canvas)
for i, (label, path) in enumerate(paths):
    im = Image.open(path).convert('RGBA').crop((250, 0, 750, 1000)).resize((330, 660), Image.Resampling.LANCZOS)
    canvas.paste(im, (i * 330, 30), im)
    draw.text((i * 330 + 8, 8), label, fill='white')
canvas.save(out / 'level-trial-overview.png')
report = {'classification': 'Completed rejected geometry study; no accepted model change',
          'accepted_checkpoint': '022', 'accepted_model_sha256': baseline['accepted_model_sha256'],
          'accepted_render_sha256': baseline['accepted_render_sha256'],
          'source_camera_degrees': 54, 'public_assets_changed': False,
          'mission_statements_changed': False, 'native_browser_inspection': False,
          'decisions': decisions, 'geometry_phase_complete': False, 'goal_status': 'active',
          'scores_retained_from_accepted_checkpoint': baseline['scores_percent'],
          'assessment': 'The owner recording still supports the apparent-fullness concern. Rejected fits are evidence, not improvements. Only outline IoU is measured; inherited subjective ratings and finish remain uncertain and incomplete.',
          'next_action': 'Constrain the stem as a smooth meridian and measure the actual surfaces that generate the elevated outline. Avoid independent radius fitting that creates an S-shaped lower bulge. Continue internal feature comparisons without fitting reference grain bands as geometry.'}
(out / 'study.json').write_text(json.dumps(report, indent=2) + '\n')
for relative, digest in baseline['public_stage_canonical_preview_identical_files'].items():
    assert sha(ROOT / relative) == digest, ('Public stage asset changed', relative)
print(json.dumps({'recorded': len(cases), 'accepted': 0, 'public_model_unchanged': True,
                  'accepted_model_sha256': baseline['accepted_model_sha256']}, indent=2))
