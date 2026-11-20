"""Infer bounded wood-polish variation from measured roughness response.

Only use variation the genuine smooth/matte renders can explain. Preserve
fine contrast preferentially. All hidden and uninformative regions use a
small variation derived from the unlit wood pigment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

from derive_wood import ROOT, blur, ramp, sample
from lathe_projection import visible_tiles


def image(path):
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255


def run(cfg):
    directory = ROOT / "build/pawn-mission" / cfg["measurement"]
    record = json.loads((directory / "measurement.json").read_text())
    reference = ROOT / "assets/pawn/reference.png"
    assert hashlib.sha256(reference.read_bytes()).hexdigest() == record["reference_sha256"]
    basis = {}
    for entry in record["response_passes"]:
        path = directory / (entry["name"] + ".png")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        basis[entry["name"]] = image(path)
    reference = image(reference)
    middle = basis["middle"]
    common = (middle[:, :, 3] > .99) & (reference[:, :, 3] > .99)
    base = middle[:, :, :3]
    target = reference[:, :, :3] - base
    target -= (1 - cfg["broad_scale_fraction"]) * blur(target, r=5, passes=2)
    # Perceptual channel weights. Where neither roughness change explains
    # a discrepancy, the regression leaves the original finish in place.
    weights = np.array([.24, .53, .23], dtype=np.float32)
    penalty = (cfg["prior_255"] / 255) ** 2
    neutral_error = np.sum(weights * target * target, axis=2)
    best_error = neutral_error.copy()
    gain = np.ones(base.shape[:2], dtype=np.float32)
    strength = np.zeros_like(gain)
    for name, end in (("smooth", cfg["range"][0]), ("matte", cfg["range"][1])):
        delta = basis[name][:, :, :3] - base
        sensitivity = np.sum(weights * delta * delta, axis=2)
        drift = np.log(end)
        amount = np.clip(np.sum(weights * target * delta, axis=2) / (sensitivity + penalty * drift * drift), 0, 1)
        err = np.sum(weights * (target - amount[:, :, None] * delta) ** 2, axis=2) + penalty * (amount * drift) ** 2
        better = err < best_error
        best_error[better] = err[better]
        gain[better] = np.exp(amount[better] * drift)
        strength[better] = np.sqrt(sensitivity[better])
    confidence = common * ramp(strength, 2.0/255, 12.0/255) * ramp(neutral_error-best_error, 0, (6/255)**2)
    pigment = image(ROOT / cfg["pigment"])[:, :, :3]
    size = len(pigment)
    log_wood = np.log(.03 + np.sum(pigment * weights, axis=2))
    background = np.clip(1 - .15 * (log_wood - blur(log_wood, r=5, passes=2)), .87, 1.15)
    atlas = background.copy()
    depth = np.load(directory / "depth.npy")
    meridian = np.load(directory / "meridian.npy")
    camera = json.loads((ROOT / "assets/pawn/camera.json").read_text())
    for rows, _, _, _, px, py, visible in visible_tiles(meridian, depth, camera, size):
        use = visible * sample(confidence, px, py)
        inferred = sample(gain, px, py)
        atlas[rows] = background[rows] * (1 - use) + inferred * use
    lo, hi = cfg["range"]
    output = ROOT / cfg["texture"]
    Image.fromarray(np.uint8(np.rint(np.clip((atlas-lo)/(hi-lo), 0, 1)*255))).save(output)
    report = {
        "source_calibration": record, "parameters": cfg, "property": "non-color linear roughness multiplier",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "common_foreground": int(common.sum()), "confident_pixels": int((confidence>.5).sum()),
        "fraction_of_atlas_beyond_10_percent": float(np.mean(np.abs(atlas-1)>.1)),
        "measured_range": [float(atlas.min()),float(atlas.max())],
    }
    (directory / "roughness-fit.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf8")
    print(json.dumps({k:report[k] for k in ("sha256","confident_pixels","fraction_of_atlas_beyond_10_percent","measured_range")}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("config",type=Path)
    args=parser.parse_args()
    run(json.loads(args.config.read_text()))
