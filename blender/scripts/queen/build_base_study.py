"""Compress the complete foot-to-stem assembly of the raised-socket queen."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh
from refine_socket_flare import read_controls, replace_meridian

CONFIG = ROOT / "scripts/queen/base-study-profile.json"
MODELS = ROOT / "models/queen-base-studies"
STUDY_ID = "compressed"


def shape(before, cfg):
    """Scale height about the foot and smoothly return to the existing upper stem."""
    after = before.copy()
    z = before[:, :, 2]
    floor = float(z.min())
    seat = float(z[cfg["stem_seat_ring"], 0])
    end = cfg["lower_stem_blend_end_z"]
    factor = cfg["base_height_factor"]
    if not 0 < factor < 1 or not floor < seat < end:
        raise ValueError("Expected a positive height reduction and a transition above the socket")
    t = np.clip((z-seat)/(end-seat), 0, 1)
    weight = (1-t)**2 * (1+2*t)
    after[:, :, 2] = z - (1-factor)*(z-floor)*weight
    return after


def verify_shape(before, after, cfg):
    """Independently check the width and height of every original base ring."""
    seat = cfg["stem_seat_ring"]
    floor = float(before[:, :, 2].min())
    factor = cfg["base_height_factor"]
    expected = floor + factor*(before[:seat+1, :, 2].astype(float)-floor)
    error = float(np.max(np.abs(after[:seat+1, :, 2]-expected)))
    assert error < 2e-7, "Base rings did not receive one uniform height scale"
    assert np.array_equal(after[:, :, :2], before[:, :, :2]), "A horizontal coordinate changed"
    upper = before[:, :, 2] >= cfg["lower_stem_blend_end_z"]
    assert np.array_equal(after[upper], before[upper]), "The upper body moved"
    assert float(after[:, :, 2].min()) == floor
    assert np.all(np.diff(after[:89, :, 2].mean(1)) >= -1e-5)
    return {
        "rings_scaled_together": [0, seat], "height_factor": factor,
        "max_base_height_error": error, "all_horizontal_coordinates_identical": True,
        "floor_and_upper_body_identical": True,
        "ring_heights_before_after": {
            name: [float(a[ring, 0, 2]-floor) for a in (before, after)]
            for name, ring in [("foot_groove",11),("flare_to_socket",29),("stem_seat",seat)]
        },
        "socket_straight_wall_before_after": [float(a[31,0,2]-a[29,0,2]) for a in (before,after)],
    }


def build():
    cfg = json.loads(CONFIG.read_text())
    source = MODELS / "socket.blend"
    if hashlib.sha256(source.read_bytes()).hexdigest() != cfg["source_sha256"]:
        raise ValueError("The compression study requires the checkpoint 18 raised-socket queen")
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    settings = json.loads(scene["mission_material_config"])
    before = read_controls(control.data, int(control["ring_segments"]))
    after = shape(before, cfg)
    measurements = verify_shape(before, after, cfg)
    boundary = replace_meridian(scene, control, settings, after)
    settings["queen_base_study"] = {
        "variant": STUDY_ID, "source_sha256": cfg["source_sha256"],
        "socket_partition": boundary, "measurements": measurements,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["variant"] = "base-study-" + STUDY_ID
    scene["mission_material_config"] = json.dumps(settings)
    scene["mission_variant"] = settings["variant"]
    scene["mission_accepted_variant"] = "base-study candidate"
    scene.render.filepath = f"//../../assets/queen-base-studies/{STUDY_ID}/fixed-wood.png"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(MODELS/(STUDY_ID+".blend")), compress=True)
    print("Compressed raised socket", json.dumps(measurements), flush=True)


if __name__ == "__main__":
    build()
