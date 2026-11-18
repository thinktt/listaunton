"""Fit the lower foot and groove arcs in the generated side guide."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
guide = ROOT / "assets/pawn/concepts/side-01-cutout.png"
with Image.open(guide) as image:
    rgba = np.asarray(image.convert("RGBA"))
    gray = np.asarray(image.convert("L").filter(ImageFilter.GaussianBlur(3)))
mask = rgba[:, :, 3] > 127
assert mask.shape == (1254, 1254)
xs = np.arange(mask.shape[1])
radius = max(np.sum(mask[1000:1150], axis=1)) / 2
middle = (np.nonzero(mask)[1].min() + np.nonzero(mask)[1].max()) / 2
results = []
for feature, radius_px in (("bottom silhouette", radius), ("dark turned groove", 318)):
    for fraction in (.68, .78, .88):
        x = xs[np.abs(xs - middle) < fraction * radius_px]
        if feature == "bottom silhouette":
            y = np.array([np.flatnonzero(mask[:, i])[-1] for i in x])
        else:
            y = 980 + np.argmin(gray[980:1080, x], axis=0)
        arc = np.sqrt(1 - ((x - middle) / radius_px) ** 2)
        height, center_y = np.polyfit(arc, y, 1)
        error = y - (center_y + height * arc)
        results.append({"feature": feature, "horizontal_radius_px": float(radius_px),
                        "fitted_fraction": fraction, "semi_minor_px": float(height),
                        "angle_degrees": float(np.degrees(np.arcsin(height / radius_px))),
                        "residual_rms_px": float(np.sqrt(np.mean(error ** 2)))})
print(json.dumps({"source_sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
                  "assumption": "Circular horizontal turnings in an approximately orthographic image.",
                  "fits": results}, indent=2))
