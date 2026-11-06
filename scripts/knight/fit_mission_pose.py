"""Fit a modest carving placement against fixed, registered reference boundaries.

The 54-degree camera, floor, pedestal and Z coordinates are held fixed.
Shape and dimensions of the upper head are preserved by a rigid transform.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from mission_pose import posed

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/knight"
OUT = ROOT / "build/knight-mission/001-carving-pose"
OUT.mkdir(parents=True, exist_ok=True)
BASELINE = ROOT / "history/knight/mission-start"
MODEL = BASELINE / "knight-rebuilt.blend"
EXPECTED = "2c0c11c5d29bdb417ec415723f9aadf825acbf4a6bc769922dce953c288de333"
assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == EXPECTED
meta = json.loads((BASELINE / "mesh.json").read_text())
assert meta["sourceSha256"] == EXPECTED
pixels = np.fromfile(BASELINE / "mesh.bin", dtype="<f4", count=meta["vertexCount"] * 6).reshape(-1, 6)
camera = meta["referenceCamera"]
projection = np.array(camera["projectionMatrix"]).reshape(4, 4) @ np.array(camera["worldToCamera"]).reshape(4, 4)
frame = camera["width"]


def screen(world):
    xy = world @ projection[:2, :3].T + projection[:2, 3]
    return (xy * [1.0, -1.0] + 1) * frame / 2


def boundaries(mask):
    return np.where(mask.any(1), mask.argmax(1), np.nan), np.where(mask.any(1), frame - 1 - mask[:, ::-1].argmax(1), np.nan)


def mask(image):
    a = np.asarray(image.convert("RGBA"))
    return (a[:, :, 3] > 127) & (a[:, :, :3].max(2) > 12)


align = json.loads((ASSETS / "original-alignment.json").read_text())
sx = align["scale"] * 300 / frame
original = Image.open(ASSETS / "original.png").convert("RGBA").transform(
    (frame, frame), Image.Transform.AFFINE,
    (sx, 0, align["x"] * 3, 0, sx, align["y"] * 3), Image.Resampling.BILINEAR)
orig_edges = boundaries(mask(original))
hi_edges = boundaries(mask(Image.open(ASSETS / "ref.png")))
# Sample six-pixel scan bands. Finial/ground rows and sudden transitions are
# checked in actual renders. Leave the pedestal out of the fitting objective.
rows = np.arange(325, 674, 6)
targets = [np.array([e[max(0, y-2):y+3].mean() for y in rows]) for e in orig_edges + hi_edges]
target_l = 0.8 * targets[0] + 0.2 * targets[2]
target_r = 0.8 * targets[1] + 0.2 * targets[3]
base_points, carving_parts = [], []
for part in meta["parts"]:
    i = part["vertexOffset"]
    points = np.unique(pixels[i:i+part["vertexCount"], :3], axis=0)
    if "pedestal" in part["name"]:
        base_points = screen(points)
    else:
        carving_parts.append(points)
    if "near eye" in part["name"]:
        eye = points.mean(0, keepdims=True)
carving = np.concatenate(carving_parts)
# Manual landmark in both elevated sources. It stabilizes the placement of
# the eye while outside contour alone admits several plausible poses.
target_eye = np.array([507., 478.])
bands = np.arange(len(rows))


def loss(params):
    dx, dy, twist = params
    uv = np.vstack((screen(posed(carving, dx, dy, twist)), base_points))
    ids = np.floor((uv[:, 1] - rows[0] + 3) / 6).astype(int)
    good = (ids >= 0) & (ids < len(rows))
    left, right = np.full(len(rows), np.inf), np.full(len(rows), -np.inf)
    np.minimum.at(left, ids[good], uv[good, 0])
    np.maximum.at(right, ids[good], uv[good, 0])
    boundary = np.mean(np.abs(np.r_[left-target_l, right-target_r]))
    eye_error = np.linalg.norm(screen(posed(eye, *params))[0] - target_eye)
    return float(boundary + 0.14 * eye_error + 1.6 * np.hypot(dx, dy) + 0.045 * abs(twist))


params = np.zeros(3)
initial = best = loss(params)
for step in [[.12, .10, 5.], [.055, .045, 2.], [.02, .015, .75], [.008, .008, .3]]:
    for _ in range(12):
        previous = best
        for axis, delta in enumerate(step):
            for sign in (-1, 1):
                new = params.copy()
                new[axis] += delta * sign
                if any(abs(new) > [.43, .30, 25.]): continue
                score = loss(new)
                if score < best - .001:
                    params, best = new, score
        if previous == best: break
report = dict(baseline_sha256=EXPECTED, variant=OUT.name, dx=float(params[0]),
              dy=float(params[1]), twist_degrees=float(params[2]),
              initial_loss=initial, final_loss=best,
              target_eye_pixel=target_eye.tolist(), original_contour_weight=.8,
              elevation=54, camera_changed=False, pedestal_changed=False,
              note="Smooth transition above the socket. Upper head is moved rigidly in XY. All heights are locked. Fit uses the registered original and selected image; actual renders determine acceptance.")
(OUT / "pose.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
