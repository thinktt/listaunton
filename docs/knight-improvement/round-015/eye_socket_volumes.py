"""Measure the accepted horse and two proposed eyes in their common head frame."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

root = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
number = int(sys.argv[sys.argv.index("--") + 2])
build = root / "build/knight-mission"
judge = build / f"round-{number:03}-judge"
worker = build / f"improvement-{number:03}-A"
spec = importlib.util.spec_from_file_location("solid_eye", worker / "seating.py")
seating = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seating)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

models = {"parent": root / "models/knight/knight-rebuilt.blend"}
for entry in ("A", "B"):
    models[entry] = build / f"improvement-{number:03}-{entry}/knight.blend"
results = {}
for name, model in models.items():
    bpy.ops.wm.open_mainfile(filepath=str(model), load_ui=False)
    scene = bpy.context.scene
    graph = bpy.context.evaluated_depsgraph_get()
    pose = json.loads(scene["knight_mission_pose"])
    angle = math.radians(pose["twist_degrees"])
    c, s = math.cos(angle), math.sin(angle)
    axes = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    offset = np.array([pose["dx"], pose["dy"], 0])
    skull = seating.mesh(scene.objects["Knight | continuous horse head and neck"], graph, axes, offset)
    record = {"model": digest(model), "sides": {}}
    for sign, side in [(-1, "near"), (1, "far")]:
        eye = seating.mesh(scene.objects[f"Knight | {side} eye"], graph, axes, offset)
        measure = seating.aperture(skull, eye, sign)
        record["sides"][side] = {field: measure[field] for field in (
            "transverse_segment_pairs_length_gt_1e-6", "estimated_eye_volume", "inside_fraction",
            "maximum_exposed_thickness", "valid_eye_rays", "odd_eye_rays_excluded", "odd_skull_rays_excluded"
        )}
    results[name] = record
report = {"method": "Strict native triangle crossings and sampled solid interval intersections on both flanks. The same grid, skull frame and evaluated mesh routines are used for all three scenes.", "analysis_sha256": digest(worker / "seating.py"), "models": results}
(judge / "eye-socket-volumes.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print({name: [round(side["inside_fraction"] * 100, 2) for side in row["sides"].values()] for name, row in results.items()})
