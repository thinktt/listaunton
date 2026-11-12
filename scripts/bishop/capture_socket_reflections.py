"""Measure socket reflectors with actual BSDF passes; never save the source scene.

The declared existing socket lamp is disabled in every pass. Added spot lamps
are rendered one at a time in white, so their linear responses can guide a fit.
Only a fresh full beauty render can establish acceptance.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config")
parser.add_argument("--out", required=True)
parser.add_argument("--samples", type=int, default=128)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
config = json.loads((ROOT / args.config).read_text())
source = ROOT / config["source"]
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
out = ROOT / args.out
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
assert config["lights"][0] == {"name": "socket reflection", "energy": 0}
bpy.data.objects["socket reflection"].data.energy = 0

lamps = []
for spec in config["lights"][1:]:
    assert spec["type"] == "SPOT" and spec["name"] not in bpy.data.objects
    data = bpy.data.lights.new(spec["name"], "SPOT")
    lamp = bpy.data.objects.new(spec["name"], data)
    scene.collection.objects.link(lamp)
    lamp.location = spec["position"]
    lamp.rotation_euler = (Vector(spec["target"]) - lamp.location).to_track_quat("-Z", "Y").to_euler()
    for key in ("spot_size", "spot_blend", "shadow_soft_size"):
        setattr(data, key, spec[key])
        assert np.isclose(getattr(data,key),spec[key],rtol=2e-6,atol=1e-7), (key,'Blender clamped the requested value')
    lamp.visible_diffuse = False
    lamp.visible_glossy = True
    lamp.light_linking.receiver_collection = bpy.data.collections["Bishop light receiver body"]
    data.color = (1, 1, 1)
    data.energy = 0
    lamps.append(lamp)

box = [330, 710, 660, 885]
width, height = scene.render.resolution_x, scene.render.resolution_y
scene.render.resolution_percentage = 100
scene.render.use_border = True
scene.render.use_crop_to_border = False
scene.render.border_min_x, scene.render.border_max_x = box[0] / width, box[2] / width
scene.render.border_min_y, scene.render.border_max_y = 1 - box[3] / height, 1 - box[1] / height
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "32"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = False
scene.cycles.use_denoising = True
scene.render.use_persistent_data = True
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == "OPTIX"
if any(device.use for device in prefs.devices):
    scene.cycles.device = "GPU"

def render(name):
    path = out / (name + ".exr")
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    assert list(image.size) == [width, height]
    values = np.array(image.pixels[:], dtype=np.float32).reshape(height, width, 4)[::-1].copy()
    np.save(out / (name + ".npy"), values)
    bpy.data.images.remove(image)
    print("SOCKET_REFLECTION_PASS", name, flush=True)

render("base")
for index, (lamp, spec) in enumerate(zip(lamps, config["lights"][1:])):
    lamp.data.energy = spec["energy"]
    render("lamp-" + str(index + 1))
    lamp.data.energy = 0

assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
(out / "manifest.json").write_text(json.dumps({
    "source": config["source"], "source_sha256": source_hash,
    "config": config, "samples": args.samples, "adaptive_sampling": False,
    "effective_spot_sizes": [lamp.data.spot_size for lamp in lamps],
    "render_border_pixels": box, "basis_color": [1, 1, 1],
    "source_unchanged": True, "camera_unchanged": True,
    "note": "Actual BSDF response diagnostics, not accepted renders. Only the socket lamp is disabled."
}, indent=2) + "\n")
print("SOCKET_RESPONSES_COMPLETE", flush=True)
