"""Fit bounded powers for measured white socket-light responses.

This creates a prediction and a trial config, not an accepted beauty render.
All lamps retain the same warm-white color and measured placement.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from image_math import blur

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--responses", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--variant", default="078-fitted-socket-spots")
parser.add_argument("--upper-weight", type=float, default=1, help="Extra penalty for reflection spill onto the stem above the lip.")
args = parser.parse_args()
folder = ROOT / args.responses
manifest = json.loads((folder / "manifest.json").read_text())
config = manifest["config"]
box = [350, 740, 640, 870]
region = np.s_[box[1]:box[3], box[0]:box[2], :3]
base = np.load(folder / "base.npy")[region]
reference = np.asarray(Image.open(ROOT / "assets/bishop/reference.png").convert("RGB"), dtype=np.float32)[region] / 255
color = np.array([1, .97, .88], dtype=np.float32)
responses = []
for index in range(len(config["lights"]) - 1):
    response = np.load(folder / ("lamp-" + str(index + 1) + ".npy"))[region] - base
    responses.append(blur(response, 1) * color)
responses = np.array(responses)
base = blur(base, 1)
reference = blur(reference, 1)

def srgb(value):
    value = np.maximum(value, 0)
    return np.clip(np.where(value <= .0031308, value * 12.92, 1.055 * value ** (1 / 2.4) - .055), 0, 1)

weights = np.ones(reference.shape[:2], dtype=np.float32)
weights[reference[:, :, 2] > .65] = 4
weights[85:, :] *= 2
assert args.upper_weight >= 1
weights[:35, :] *= args.upper_weight

def loss(factors):
    prediction = srgb(base + np.tensordot(factors, responses, axes=1))
    return float((np.abs(prediction - reference).mean(2) * weights).sum() / weights.sum())

factors = np.zeros(len(responses), dtype=np.float32)
for step in (1, .25, .05, .01):
    for sweep in range(3):
        previous = factors.copy()
        for index in range(len(factors)):
            values = np.arange(max(0, factors[index] - 4 * step), min(12, factors[index] + 4 * step) + step / 2, step)
            trials = []
            for value in values:
                candidate = factors.copy()
                candidate[index] = value
                trials.append(loss(candidate))
            factors[index] = values[int(np.argmin(trials))]
        if np.array_equal(previous, factors):
            break
prediction = srgb(base + np.tensordot(factors, responses, axes=1))
for spec, factor in zip(config["lights"][1:], factors):
    spec["energy"] *= float(factor)
    spec["color"] = color.tolist()
config["variant"] = args.variant
config["fit"] = {"responses": args.responses, "box": box, "power_factors": factors.tolist(),
                 "warm_white_color": color.tolist(), "max_factor": 12,
                 "reference_cream_core_weight": 4, "lower_spill_weight": 2, "upper_spill_weight": args.upper_weight,
                 "predicted_weighted_rgb_error_before": loss(np.zeros(len(factors))) * 255,
                 "predicted_weighted_rgb_error_after": loss(factors) * 255,
                 "note": "Bounded fit to real BSDF passes; inspect a fresh full render for acceptance."}
config["hypothesis"] = "Measured localized socket reflections can fill the cream lip crescent while avoiding the old lower streak."
path = ROOT / args.out
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(config, indent=2) + "\n")
canvas = Image.new("RGB", (1200, 270), "#171b21")
draw = ImageDraw.Draw(canvas)
for index, (name, values) in enumerate([("Reference", reference), ("Socket light off", srgb(base)), ("Prediction only", prediction)]):
    image = Image.fromarray(np.rint(values * 255).astype("uint8")).resize((400, 225))
    canvas.paste(image, (index * 400, 40))
    draw.text((index * 400 + 12, 12), name, fill="white")
canvas.save(folder / "fit-prediction.png")
print(json.dumps(config["fit"], indent=2))
