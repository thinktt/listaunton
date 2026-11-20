"""Record checkpoint 022's actual collar overhang and rejected head studies."""
from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'docs/bishop-mission/iteration-022'
out.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def cp(relative, target):
    dest = out / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, dest)

def rgb(im):
    im = im.convert('RGBA')
    canvas = Image.new('RGB', im.size, 'black')
    canvas.paste(im, (0, 0), im)
    return canvas

occlusion = {}
for label, path, model in [
    ('before', '169-collar-occlusion/current.json', 'history/bishop-mission-021/bishop-rebuilt.blend'),
    ('after', '171-occlusion.json', 'models/bishop/bishop-rebuilt.blend'),
]:
    source = ROOT / 'build/bishop-mission' / path
    data = json.loads(source.read_text())
    assert data['source_sha256'] == sha(ROOT / model) and data['source_unchanged']
    assert abs(data['camera_degrees_measured'] - 54) < 1e-4
    occlusion[label] = data
    cp(source.relative_to(ROOT).as_posix(), 'geometry/occlusion-' + label + '.json')
old = occlusion['before']['bands']['middle']['overhang_intervals'][0]
new = occlusion['after']['bands']['middle']['overhang_intervals'][0]
assert .15 < old['projected_overhang_px'] < .25
assert 2 < new['projected_overhang_px'] < 3
assert abs(old['crest']['pixel_y'] - new['crest']['pixel_y']) < .5
for band in ['upper', 'lower']:
    a = occlusion['before']['bands'][band]['overhang_intervals'][0]
    b = occlusion['after']['bands'][band]['overhang_intervals'][0]
    assert abs(a['crest']['pixel_y'] - b['crest']['pixel_y']) < .0001, band
    assert abs(a['projected_overhang_px'] - b['projected_overhang_px']) < .0001, band

cases = [
    ('head-short', '165-head-turn-gentle', 'Rejected: adds an unsupported flattened band above the collar despite preserving the outline.'),
    ('head-fuller', '165-head-turn-fuller', 'Rejected: more obvious extra ridge/cuff in the true level view.'),
    ('head-wide-transition', '168-head-turn-convex', 'Rejected: a convex control polygon still produces an unwanted band in the evaluated surface; no convincing reference improvement.'),
    ('middle-undercut', '170-middle-undercut', 'Chosen: real middle-lip overhang, almost unchanged front-edge position, retained rounded crest and better-separated plates.'),
]
decisions = []
for label, variant, decision in cases:
    base = ROOT / 'build/bishop-mission' / variant
    audit = json.loads((base / 'trial-audit.json').read_text())
    target = out / 'trials' / label
    target.mkdir(parents=True, exist_ok=True)
    # Preserve the exact configuration actually used, even if a proposal
    # generator later acquired new descriptive or diagnostic fields.
    (target / 'config.json').write_text(json.dumps(audit['config'], indent=2) + '\n')
    for name in ['wood.png', 'neutral.png', 'profile.json', 'trial-audit.json',
                 'scope-validation.json', 'anatomy-validation.json', 'geometry-validation.json',
                 'curvature.json', 'occlusion.json', 'comparison/metrics.json',
                 'geometry/geometry-rows.json', 'studio/head.png', 'studio/side.png', 'studio/studio.json']:
        if (base / name).exists():
            cp((base / name).relative_to(ROOT).as_posix(), f'trials/{label}/{name}')
    decisions.append({'variant': variant, 'decision': decision})
(out / 'trials/decisions.json').write_text(json.dumps(decisions, indent=2) + '\n')
cp('build/bishop-mission/171-middle-undercut-checkpoint/trial-audit.json', 'final-trial-audit.json')
for name in ['head-profile-control-arcs.png', 'slit-boundary-comparison.png', 'slit-boundary.json',
             'gentle-comparison.png', 'fuller-comparison.png', 'convex-comparison.png',
             'side-comparison.png', 'curvature.json']:
    cp('build/bishop-mission/164-head-audit/' + name, 'head-investigation/' + name)
for variant in ['166-opposite-pose', '167-opposite-refine']:
    base = ROOT / 'build/bishop-mission' / variant
    meta = json.loads((base / 'capture.json').read_text())
    assert meta['source_sha256'] == sha(ROOT / 'history/bishop-mission-021/bishop-rebuilt.blend')
    for name in ['capture.json', 'surface-labels.npz', 'orientation-comparison.png']:
        cp((base / name).relative_to(ROOT).as_posix(), f'opposite-pose/{variant}/{name}')
for name in ['undercut-comparison.png', 'side-comparison.png']:
    cp('build/bishop-mission/169-collar-occlusion/' + name, 'trial-comparison/' + name)

chart = Image.new('RGB', (1000, 390), '#15191e')
draw = ImageDraw.Draw(chart)
draw.text((20, 12), 'Middle collar: actual front-meridian projection through the unchanged 54-degree camera', fill='white')
def pt(x, y):
    return 80 + (x - 102) / 4.05 * 850, 60 + (y - 555) / 14 * 260
for yy in [556, 560, 564, 568]:
    sy = pt(102, yy)[1]
    draw.line((80, sy, 930, sy), fill='#343a41')
    draw.text((30, sy - 6), str(yy), fill='#c7ccd1')
for xx in [102, 103, 104, 105, 106]:
    sx = pt(xx, 555)[0]
    draw.line((sx, 60, sx, 320), fill='#343a41')
    draw.text((sx - 10, 330), str(xx), fill='#c7ccd1')
for label, color in [('before', '#ff68c2'), ('after', '#35eeee')]:
    rows = occlusion[label]['bands']['middle']['samples']
    draw.line([pt(r['axis_y'], r['pixel_y']) for r in rows if r['axis_y'] >= 102], fill=color, width=3)
draw.text((20, 365), 'Pink: previous. Cyan: current. Horizontal: profile axis coordinate; vertical: rendered pixel row.', fill='white')
chart.save(out / 'middle-overhang.png')
summary = {
    'before': old, 'after': new,
    'upper_and_lower_crest_extrema_unchanged_within_0p0001_px': True,
    'front_edge_shift_px': new['crest']['pixel_y'] - old['crest']['pixel_y'],
    'interpretation': 'A real overhang beneath the middle rim replaces almost coincident rim/neck projections. Source photographs support a distinct lip but do not provide an exact recovered cross-section.'
}
(out / 'middle-overhang.json').write_text(json.dumps(summary, indent=2) + '\n')

studio = [('before', ROOT / 'build/bishop-mission/163-studio/after',
           ROOT / 'history/bishop-mission-021/bishop-rebuilt.blend'),
          ('after', ROOT / 'build/bishop-mission/171-studio', ROOT / 'models/bishop/bishop-rebuilt.blend')]
sheet = Image.new('RGB', (1000, 285), '#15191e')
draw = ImageDraw.Draw(sheet)
for i, (label, directory, model) in enumerate(studio):
    meta = json.loads((directory / 'studio.json').read_text())
    assert meta['source_sha256'] == sha(model) and meta['source_unchanged']
    for name in ['side.png', 'studio.json']:
        cp((directory / name).relative_to(ROOT).as_posix(), 'studio/' + label + '/' + name)
    im = rgb(Image.open(directory / 'side.png')).crop((335, 270, 665, 430)).resize((500, 242))
    sheet.paste(im, (i * 500, 32))
    draw.text((i * 500 + 10, 10), label + ': same level camera and unfitted neutral lights', fill='white')
sheet.save(out / 'collar-studio-comparison.png')
print(json.dumps({'recorded': True, 'middle_overhang_px': {
    'before': old['projected_overhang_px'], 'after': new['projected_overhang_px']},
    'front_edge_shift_px': summary['front_edge_shift_px']}, indent=2))
