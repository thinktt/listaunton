"""Small Blender helpers for the fixed-camera Staunton knight mission."""
from pathlib import Path
import hashlib
import json
import math

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/knight"
BUILD = ROOT / "build/knight-mission"
MODEL = ROOT / "models/knight/knight-rebuilt.blend"
INITIAL_HASH = "2c0c11c5d29bdb417ec415723f9aadf825acbf4a6bc769922dce953c288de333"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_file(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def visible_meshes(scene):
    return [obj for obj in scene.objects if obj.type == "MESH" and not obj.hide_render]


def world_vertices(obj):
    points = np.empty((len(obj.data.vertices), 3), dtype=np.float32)
    obj.data.vertices.foreach_get("co", points.ravel())
    transform = np.array(obj.matrix_world)
    return points @ transform[:3, :3].T + transform[:3, 3]


def configure_render(scene, samples=64):
    scene.render.engine = "CYCLES"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.seed = 0
    scene.render.use_persistent_data = True
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == "OPTIX"
        if any(device.use for device in prefs.devices):
            scene.cycles.device = "GPU"
    except (TypeError, RuntimeError):
        scene.cycles.device = "CPU"


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def use_side_camera(scene):
    framing = json.loads((ASSETS / "guide-camera.json").read_text())
    camera = scene.camera
    target = Vector(framing["target"])
    target.x += float(scene.get("knight_foot_center_x",0.0))
    elevation = math.radians(framing["elevation"])
    camera.data.ortho_scale = framing["orthoScale"]
    camera.data.shift_x = framing["shiftX"]
    camera.data.shift_y = 0
    camera.location = target + Vector((0, -12*math.cos(elevation), 12*math.sin(elevation)))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()


def save_model(scene, path):
    bpy.context.preferences.filepaths.save_version = 0
    # The file opens on the fixed camera. Other cameras are used after saving.
    scene.render.filepath = "//../../assets/knight/render.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
