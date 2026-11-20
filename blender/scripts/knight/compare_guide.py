"""Compare the registered walnut and clay side renders from the accepted model."""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageChops, ImageDraw

from side_profile import read_profile

root = Path(__file__).resolve().parents[2]
assets = root / 'assets/knight'
model = root / 'models/knight/knight-rebuilt.blend'
registration = read_profile(root, hashlib.sha256(model.read_bytes()).hexdigest())
wood, clay = [Image.open(root / registration[key]).convert('RGBA') for key in ('profile', 'neutral')]
width, height = wood.size
sheet = Image.new('RGB', (2 * width, height + 50), '#17191d')
draw = ImageDraw.Draw(sheet)
for col, (view, material) in enumerate([(wood, 'Walnut'), (clay, 'Neutral clay')]):
    sheet.paste(view, (col * width, 50), view)
    label = f"{material} / {registration['elevation']} degree side camera"
    draw.text((col * width + 24, 18), label, fill='white')
sheet.save(assets / 'guide-comparison.png')
Image.blend(clay, wood, .5).save(assets / 'guide-overlay.png')

# The two materials should occupy the same projected shape. This diagnostic
# measures their registration, not a match to a photographic side reference.
masks = [im.getchannel('A').point(lambda a: 255 if a > 127 else 0) for im in (wood, clay)]
overlap = ImageChops.darker(*masks).histogram()[255]
union = ImageChops.lighter(*masks).histogram()[255]
assert union > 0
report = {
    'registration': registration,
    'side_render_mask_iou': overlap / union,
    'review': 'Inspect the same carved surfaces in wood and neutral clay from the registered side camera.'
}
(assets / 'guide-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
