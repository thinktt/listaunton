"""Record the accepted 024 stem change and its contour-provenance evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'docs/bishop-mission/iteration-024'; out.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before_model = ROOT / 'history/bishop-mission-022/bishop-rebuilt.blend'
after_model = ROOT / 'models/bishop/bishop-rebuilt.blend'
final_trial = ROOT / 'build/bishop-mission/181-stem-checkpoint'
assert sha(after_model) == sha(final_trial / 'bishop.blend')
cfg = json.loads((out / 'profile-fit.json').read_text())
assert set(cfg['body_rings']) == {'34', '35', '36'} and cfg['source_sha256'] == sha(before_model)

def cp(relative, target):
    dest = out / target; dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, dest)

audit_root = ROOT / 'build/bishop-mission/178-contour-audit'
reports = {}
for label, model, filename in [('before', before_model, 'meridians.json'), ('after', after_model, 'meridians-after.json')]:
    contour = json.loads((audit_root / filename).read_text())
    stem = json.loads((audit_root / ('final-stem-' + label + '.json')).read_text())
    assert contour['source_sha256'] == stem['source_sha256'] == sha(model)
    assert contour['source_unchanged'] and stem['source_unchanged']
    assert abs(contour['camera_degrees_measured'] - 54) < 1e-4
    reports[label] = {'contour': contour, 'stem': stem}
    cp((audit_root / filename).relative_to(ROOT), 'geometry/contour-' + label + '.json')
    cp((audit_root / ('final-stem-' + label + '.json')).relative_to(ROOT), 'geometry/stem-' + label + '.json')
assert reports['before']['contour']['camera_matrix'] == reports['after']['contour']['camera_matrix']
summary = {}
for label, report in reports.items():
    row = next(r for r in report['contour']['rows'] if r['sides']['right']['region'] == 'base')
    stem = report['stem']
    summary[label] = {'first_base_contour_sample_y': row['pixel_y'],
        'maximum_stem_tangent_angle_degrees': stem['maximum_tangent_angle_degrees'],
        'steepest_tangent_at_axis_y': stem['steepest_tangent_at_axis_y'],
        'radius_monotone_after_measured_waist': stem['radius_monotone_after_measured_waist']}

al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text()); s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform((1254, 1254),
    Image.Transform.AFFINE, (s, 0, al['x']*3, 0, s, al['y']*3), Image.Resampling.BILINEAR)
arr = np.array(original); refmask = (arr[:, :, 3] > 127) & (arr[:, :, :3].max(2) > 12)
regions = {'exposed_stem': [592, 616], 'stem_base_crossover': [616, 636], 'rear_base_shoulder': [636, 796]}
for label, path in [('before', ROOT / 'history/bishop-mission-022/render.png'), ('after', ROOT / 'assets/bishop/render.png')]:
    mask = np.array(Image.open(path).convert('RGBA'))[:, :, 3] > 127
    summary[label]['regions'] = {}
    for name, (y0, y1) in regions.items():
        errors = []
        for y in range(y0, y1):
            rx, mx = np.flatnonzero(refmask[y]), np.flatnonzero(mask[y])
            errors += [abs(int(rx[0])-int(mx[0])), abs(int(rx[-1])-int(mx[-1]))]
        summary[label]['regions'][name] = {'rows': [y0, y1], 'mean_absolute_edge_error_px': float(np.mean(errors)),
                                        'max_absolute_edge_error_px': int(max(errors))}
(out / 'stem-feature-comparison.json').write_text(json.dumps(summary, indent=2) + '\n')

for name in ['contour-provenance.png', 'inverse-sections.json', 'crossover-prediction.json', 'crossover-prediction-stronger.json']:
    cp((audit_root / name).relative_to(ROOT), 'investigation/' + name)
for variant, decision in [('179-stem-shoulder-crossover', 'Milder supported stem test; tiny shoulder mode not adopted.'),
                          ('180-stem-shoulder-stronger', 'Chosen stem radii, with the subpixel rear-shoulder mode omitted from the final model.')]:
    base = ROOT / 'build/bishop-mission' / variant
    audit = json.loads((base / 'trial-audit.json').read_text())
    dest = out / 'trials' / variant; dest.mkdir(parents=True, exist_ok=True)
    (dest / 'config.json').write_text(json.dumps(audit['config'], indent=2) + '\n')
    (dest / 'decision.txt').write_text(decision + '\n')
    for name in ['wood.png', 'neutral.png', 'profile.json', 'trial-audit.json', 'comparison/metrics.json', 'geometry-rows.json', 'studio/side.png', 'studio/studio.json']:
        cp((base / name).relative_to(ROOT), Path('trials') / variant / name)
cp((final_trial / 'trial-audit.json').relative_to(ROOT), 'final-trial-audit.json')

for name in ['neutral-stem', 'neutral-neck', 'wood-stem', 'wood-neck', 'side']:
    cp('build/bishop-mission/176-neck-audit/181-stem-checkpoint-' + name + '.png', 'comparison/stem-' + name + '.png')
for name in ['side.png', 'studio.json']:
    cp('build/bishop-mission/181-studio/' + name, 'unfitted-studio/' + name)

# Use the same physical side view to compare the accepted shape to the rejected bulge.
cases = [('Accepted 022', ROOT / 'build/bishop-mission/171-studio/side.png'),
         ('Rejected 176: lower bulge', ROOT / 'build/bishop-mission/176-narrower-upper-stem/studio/side.png'),
         ('Accepted 024', ROOT / 'build/bishop-mission/181-studio/side.png')]
canvas = Image.new('RGB', (1200, 670), '#14181c'); d = ImageDraw.Draw(canvas)
for i, (label, path) in enumerate(cases):
    im = Image.open(path).convert('RGBA').crop((250, 200, 750, 1000)).resize((400, 640), Image.Resampling.LANCZOS)
    canvas.paste(im, (i*400, 30), im); d.text((i*400+10, 9), label, fill='white')
canvas.save(out / 'taper-side-comparison.png')
print(json.dumps(summary, indent=2))
