"""Compare a local stem trial at the original framing and common level view."""
from pathlib import Path
import argparse
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--trial', default='176-narrower-upper-stem')
a = p.parse_args()
trial = ROOT / 'build/bishop-mission' / a.trial
out = ROOT / 'build/bishop-mission/176-neck-audit'
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE, (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
for kind, current, prior in [('neutral', 'neutral.png', 'render-clay.png'), ('wood', 'wood.png', 'render.png')]:
    items = [('Original white', original),
             ('Selected white 3', Image.open(ROOT / 'assets/bishop/reference.png')),
             ('Accepted 022', Image.open(ROOT / ('history/bishop-mission-022/' + prior))),
             (a.trial, Image.open(trial / current))]
    for region, box in [('stem', (310, 580, 680, 850)), ('neck', (380, 595, 610, 665))]:
        w, h = box[2] - box[0], box[3] - box[1]
        zoom = 2 if region == 'neck' else 1
        canvas = Image.new('RGB', (w * zoom * len(items), h * zoom + 30), '#14181c')
        draw = ImageDraw.Draw(canvas)
        for i, (name, im) in enumerate(items):
            im = im.convert('RGBA').crop(box).resize((w * zoom, h * zoom), Image.Resampling.LANCZOS)
            canvas.paste(im, (i * w * zoom, 30), im)
            draw.text((i * w * zoom + 10, 8), name, fill='white')
        canvas.save(out / (a.trial + '-' + kind + '-' + region + '.png'))
paths = [('Accepted 022', ROOT / 'build/bishop-mission/171-studio/side.png'),
         (a.trial, trial / 'studio/side.png')]
if all(path.exists() for _, path in paths):
    canvas = Image.new('RGB', (1000, 1030), '#14181c')
    draw = ImageDraw.Draw(canvas)
    for i, (name, path) in enumerate(paths):
        im = Image.open(path).convert('RGBA').crop((250, 0, 750, 1000))
        canvas.paste(im, (i * 500, 30), im)
        draw.text((i * 500 + 10, 8), name, fill='white')
    canvas.save(out / (a.trial + '-side.png'))
print('Saved fixed-registration stem comparisons.')
