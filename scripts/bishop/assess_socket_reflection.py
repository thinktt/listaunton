"""Compare real socket renders at unchanged registration, with enlarged evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("renders", nargs="+")
parser.add_argument("--out", required=True)
args = parser.parse_args()
out = ROOT / args.out
out.mkdir(parents=True, exist_ok=True)
reference = Image.open(ROOT / "assets/bishop/reference.png").convert("RGBA")
target = np.array(reference, dtype=np.float32)
regions = {"whole_socket": (350, 735, 640, 870), "lip": (400, 775, 605, 825),
           "lower_streak": (510, 830, 600, 860)}
core = np.zeros(target.shape[:2], dtype=bool)
core[770:822, 410:600] = target[770:822, 410:600, 2] > 190
report = {"note": "Fixed registered RGB measurements on actual renders, not fidelity scores. No image alignment or color adjustment.",
          "core_pixels": int(core.sum()), "regions": regions, "renders": {}}
images = [("Selected white 3", reference)]
for filename in args.renders:
    path = ROOT / filename
    image = Image.open(path).convert("RGBA")
    assert image.size == reference.size
    values = np.array(image, dtype=np.float32)
    records = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "reference_cream_core_rgb_error": float(np.abs(values[core, :3] - target[core, :3]).mean())}
    for name, (x0, y0, x1, y1) in regions.items():
        ref = target[y0:y1, x0:x1]
        ren = values[y0:y1, x0:x1]
        opaque = (ref[:, :, 3] > 127) & (ren[:, :, 3] > 254) & (ref[:, :, :3].max(2) > 12)
        assert opaque.sum() > 100
        records[name] = {"pixels": int(opaque.sum()),
                         "rgb_mae": float(np.abs(ren[opaque, :3] - ref[opaque, :3]).mean()),
                         "cream_pixels": int(((ren[:, :, 2] > 190) & opaque).sum())}
    report["renders"][filename] = records
    images.append((path.parent.name + "/" + path.name, image))
canvas = Image.new("RGB", (450 * len(images), 280), "#171b21")
draw = ImageDraw.Draw(canvas)
for index, (name, image) in enumerate(images):
    crop = image.crop(regions["whole_socket"]).convert("RGB").resize((450, 230), Image.Resampling.LANCZOS)
    canvas.paste(crop, (index * 450, 40))
    draw.text((index * 450 + 10, 12), name, fill="white")
canvas.save(out / "socket-comparison.png")
(out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
