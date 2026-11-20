"""Build an isolated socket-light configuration from measured surface normals."""
import argparse
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--landmarks", required=True)
parser.add_argument("--normals", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--variant", required=True)
parser.add_argument("--beam-degrees", type=float, default=1)
parser.add_argument("--radius", type=float, default=.015)
parser.add_argument("--basis-energy", type=float, default=150)
parser.add_argument("--distance", type=float, default=7)
args = parser.parse_args()
assert args.beam_degrees >= 1, 'Blender 5.2 clamps spot cones below one degree; use a shorter distance instead.'
assert args.distance > 0 and args.radius >= 0
geometry = json.loads((ROOT / args.landmarks).read_text())
normals = json.loads((ROOT / args.normals).read_text())
assert geometry["_provenance"]["source_sha256"] == normals["source_sha256"]
view = np.array(json.loads((ROOT / "assets/bishop/camera.json").read_text())["worldToCamera"]).reshape(4, 4)[2, :3]
view /= np.linalg.norm(view)
config = {"source": normals["source"], "variant": args.variant,
          "samples": 128, "adaptive_sampling": False,
          "hypothesis": "Localized glossy reflections following measured socket lip normals.",
          "lights": [{"name": "socket reflection", "energy": 0}],
          "measurement": {"landmarks": args.landmarks, "normals": args.normals,
                          "beam_degrees": args.beam_degrees, "radius": args.radius, "distance": args.distance}}
for index, (name, measured) in enumerate(normals["points"].items()):
    assert geometry[name]["pixel"] == measured["pixel"]
    normal = np.array(measured["normal"])
    normal /= np.linalg.norm(normal)
    point = np.array(geometry[name]["surface"])
    direction = 2 * np.dot(normal, view) * normal - view
    config["lights"].append({"name": "socket arc " + str(index + 1), "type": "SPOT",
        "energy": args.basis_energy, "color": [1, .97, .88],
        "position": (point + args.distance * direction).tolist(), "target": point.tolist(),
        "spot_size": math.radians(args.beam_degrees), "spot_blend": .6,
        "shadow_soft_size": args.radius, "diffuse": False, "glossy": True, "receiver": "body"})
path = ROOT / args.out
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(config, indent=2) + "\n")
print("Prepared", len(config["lights"]) - 1, "measured socket lights.")
