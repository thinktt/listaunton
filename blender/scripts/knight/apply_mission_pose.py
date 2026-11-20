"""Apply the measured carving placement to the original editable mesh."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from mission_pose import posed
from mission_scene import ROOT, BUILD, MODEL, INITIAL_HASH, sha, configure_render, render, save_model, use_side_camera, world_vertices

parser = argparse.ArgumentParser()
parser.add_argument("--baseline", type=Path, default=ROOT/"history/knight/mission-start/knight-rebuilt.blend")
parser.add_argument("--config", type=Path, default=BUILD/"001-carving-pose/pose.json")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
cfg = json.loads(args.config.read_text())
assert sha(args.baseline) == cfg["baseline_sha256"] == INITIAL_HASH
bpy.ops.wm.open_mainfile(filepath=str(args.baseline), load_ui=False)
scene = bpy.context.scene
out = BUILD / cfg["variant"]
out.mkdir(parents=True, exist_ok=True)
params = [cfg["dx"], cfg["dy"], cfg["twist_degrees"]]
for obj in scene.objects:
    if obj.type != "MESH" or "pedestal" in obj.name:
        continue
    old_matrix = np.array(obj.matrix_world)
    old = world_vertices(obj)
    new = posed(old, *params)
    assert np.array_equal(old[:,2],new[:,2])
    new_origin = posed(old_matrix[None,:3,3], *params)[0]
    local = (new - new_origin) @ np.linalg.inv(old_matrix[:3,:3]).T
    obj.data.vertices.foreach_set("co", np.asarray(local, dtype=np.float32).ravel())
    obj.data.update()
    obj.location = Vector(new_origin)
bpy.context.view_layer.update()
scene["knight_mission_pose"] = json.dumps(cfg, sort_keys=True)
configure_render(scene, 48)
save_model(scene, out/"knight.blend")
render(scene, out/"neutral.png")
use_side_camera(scene)
render(scene, out/"side-neutral.png")
print("KNIGHT_POSE_RENDERED", sha(out/"knight.blend"), flush=True)
