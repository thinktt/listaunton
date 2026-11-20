"""Registered fixed-view and common-camera level crops for flare hypotheses."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'build/bishop-mission/172-base-audit'
al = json.loads((ROOT / 'assets/bishop/original-alignment.json').read_text())
s = al['scale'] * 300 / 1254
original = Image.open(ROOT / 'assets/bishop/original.png').convert('RGBA').transform(
    (1254, 1254), Image.Transform.AFFINE, (s, 0, al['x'] * 3, 0, s, al['y'] * 3), Image.Resampling.BILINEAR)
for kind, filename in [('wood', 'wood.png'), ('neutral', 'neutral.png')]:
    before = 'render.png' if kind == 'wood' else 'render-clay.png'
    items = [('Original white', original),
             ('Selected white 3', Image.open(ROOT / 'assets/bishop/reference.png')),
             ('Accepted 022', Image.open(ROOT / ('history/bishop-mission-022/' + before)))]
    items += [('Trial ' + v, Image.open(ROOT / ('build/bishop-mission/173-flare-' + v + '/' + filename)))
              for v in ['gentle', 'round']]
    box = (220, 750, 770, 1130)
    canvas = Image.new('RGB', (550 * len(items), 410), '#14181c')
    draw = ImageDraw.Draw(canvas)
    for i, (name, im) in enumerate(items):
        im = im.convert('RGBA').crop(box)
        canvas.paste(im, (i * 550, 30), im)
        draw.text((i * 550 + 10, 8), name, fill='white')
    canvas.save(out / ('flare-' + kind + '.png'))

paths = [('Accepted 022', 'build/bishop-mission/171-studio/side.png')]
paths += [('Trial ' + v, 'build/bishop-mission/173-flare-' + v + '/studio/side.png') for v in ['gentle', 'round']]
if all((ROOT / path).exists() for _, path in paths):
    canvas = Image.new('RGB', (480 * len(paths), 330), '#14181c')
    draw = ImageDraw.Draw(canvas)
    for i, (name, path) in enumerate(paths):
        im = Image.open(ROOT / path).convert('RGBA').crop((260, 680, 740, 980))
        canvas.paste(im, (i * 480, 30), im)
        draw.text((i * 480 + 10, 8), name, fill='white')
    canvas.save(out / 'flare-side.png')
print('Generated registered flare comparisons without modifying reference sources.')
