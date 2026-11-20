"""Record checkpoint 021 socket geometry and the rejected neighboring edits."""
from pathlib import Path
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'docs/bishop-mission/iteration-021'
out.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def cp(source, target):
    dest = out / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / source, dest)

def rgb(im):
    im = im.convert('RGBA')
    canvas = Image.new('RGB', im.size, 'black')
    canvas.paste(im, (0, 0), im)
    return canvas

measurements = {}
for label, filename, model in [
    ('before', '159-curvature-audit/socket-before.json', 'history/bishop-mission-020/bishop-rebuilt.blend'),
    ('after', '163-socket-after.json', 'models/bishop/bishop-rebuilt.blend'),
]:
    p = ROOT / 'build/bishop-mission' / filename
    data = json.loads(p.read_text())
    assert data['source_unchanged'] and data['source_sha256'] == sha(ROOT / model)
    measurements[label] = data
    cp(p.relative_to(ROOT).as_posix(), 'geometry/socket-' + label + '.json')
assert measurements['before']['maximum_outward_height_reversal_original_axis_units'] > .5
assert measurements['after']['maximum_outward_height_reversal_original_axis_units'] < .001

cases = [
    ('raised-root', '160-socket-full', 'socket-full.json',
     'Rejected: removes the recess but raises the visible stem seating point unnecessarily.'),
    ('lower-collar', '161-lower-underside', 'lower-underside.json',
     'Rejected: shallower underside worsens the authoritative original outline and does not convincingly improve interior form.'),
    ('lowered-crest', '162-socket-crest', 'socket-crest.json',
     'Chosen: removes the extra socket-top reversal while preserving stem seating control, radii and all other anatomy.'),
]
decisions = []
for label, variant, config, decision in cases:
    base = ROOT / 'build/bishop-mission' / variant
    for name in ['wood.png', 'neutral.png', 'profile.json', 'trial-audit.json',
                 'scope-validation.json', 'anatomy-validation.json', 'geometry-validation.json',
                 'comparison/metrics.json', 'geometry/geometry-rows.json']:
        if (base / name).exists():
            cp((base / name).relative_to(ROOT).as_posix(), f'trials/{label}/{name}')
    cp('build/bishop-mission/159-curvature-audit/' + config, f'trials/{label}/config.json')
    decisions.append({'variant': variant, 'decision': decision})
(out / 'trials/decisions.json').write_text(json.dumps(decisions, indent=2) + '\n')
cp('build/bishop-mission/163-socket-checkpoint/trial-audit.json', 'final-trial-audit.json')
for name in ['socket-sources.png', 'socket-comparison.png', 'socket-crest-comparison.png',
             'lower-underside-comparison.png', 'collars-control-arcs.png',
             'socket-control-arcs.png', 'base-control-arcs.png', 'control-landmarks.json']:
    cp('build/bishop-mission/159-curvature-audit/' + name, 'investigation/' + name)

al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE,
    (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
items = [
    ('Original white', original),
    ('Selected white 3', Image.open(ROOT / 'assets/bishop/reference.png')),
    ('Previous neutral', Image.open(ROOT / 'history/bishop-mission-020/render-clay.png')),
    ('Current neutral', Image.open(ROOT / 'assets/bishop/render-clay.png')),
]
box = (270, 680, 720, 870)
w, h = box[2] - box[0], box[3] - box[1]
sheet = Image.new('RGB', (w * 2, (h + 32) * 2), '#15191e')
draw = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(items):
    x, y = (i % 2) * w, (i // 2) * (h + 32)
    sheet.paste(rgb(im).crop(box), (x, y + 30))
    draw.text((x + 10, y + 8), label, fill='white')
sheet.save(out / 'socket-neutral-comparison.png')

# Actual meridian samples, no photograph fitting or reference modification.
chart = Image.new('RGB', (900, 380), '#15191e')
draw = ImageDraw.Draw(chart)
draw.text((20, 12), 'Socket top: measured surface descends outward without the previous inner trough', fill='white')
x0, x1, y0, y1 = 80, 850, 55, 310
def pixel(radius, axis_y):
    return x0 + (radius - 24.8) / 5.5 * (x1 - x0), y0 + (axis_y - 161.5) / 4.0 * (y1 - y0)
for yy in [162, 163, 164, 165]:
    py = pixel(24.8, yy)[1]
    draw.line((x0, py, x1, py), fill='#343a41')
    draw.text((35, py - 6), str(yy), fill='#c5cbd0')
for rr in [25, 26, 27, 28, 29, 30]:
    px = pixel(rr, 161.5)[0]
    draw.line((px, y0, px, y1), fill='#343a41')
    draw.text((px - 6, y1 + 10), str(rr), fill='#c5cbd0')
for label, color in [('before', '#ff68c2'), ('after', '#35eeee')]:
    draw.line([pixel(r['radius'], r['axis_y']) for r in measurements[label]['rows']], fill=color, width=3)
draw.text((110, 345), 'Pink: previous    Cyan: current    Horizontal: radius; vertical: axis coordinate (original profile units)', fill='white')
chart.save(out / 'socket-meridian.png')

for label in ['before', 'after']:
    base = ROOT / 'build/bishop-mission/163-studio' / label
    assert (base / 'studio.json').exists()
    meta = json.loads((base / 'studio.json').read_text())
    expected = ROOT / ('history/bishop-mission-020/bishop-rebuilt.blend' if label == 'before' else 'models/bishop/bishop-rebuilt.blend')
    assert meta['source_sha256'] == sha(expected)
    for name in ['side.png', 'studio.json']:
        cp((base / name).relative_to(ROOT).as_posix(), 'studio/' + label + '/' + name)
sheet = Image.new('RGB', (1000, 420), '#15191e')
draw = ImageDraw.Draw(sheet)
for i, label in enumerate(['before', 'after']):
    im = rgb(Image.open(ROOT / 'build/bishop-mission/163-studio' / label / 'side.png'))
    sheet.paste(im.crop((280, 650, 720, 820)).resize((500, 193)), (i * 500, 30))
    draw.text((i * 500 + 10, 10), label + ': same level camera and unfitted neutral lighting', fill='white')
draw.text((10, 245), 'The side guide is interpretive; the original 54-degree sprite remains authoritative.', fill='white')
sheet = sheet.crop((0, 0, 1000, 280))
sheet.save(out / 'socket-studio-comparison.png')
print(json.dumps({'recorded': True, 'maximum_height_reversal': {
    k: v['maximum_outward_height_reversal_original_axis_units'] for k, v in measurements.items()}}, indent=2))
