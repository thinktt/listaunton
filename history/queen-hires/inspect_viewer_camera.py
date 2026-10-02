"""Read the saved Blender camera and project diagnostic points; never save .blend."""
import hashlib
import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "outputs" / "queen-hires" / "queen-rebuilt.blend"
OUTPUT = Path(__file__).resolve().parent / "viewer-camera.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


before_hash = digest(BLEND)
before_stat = BLEND.stat()
bpy.ops.wm.open_mainfile(filepath=str(BLEND), load_ui=False)
scene = bpy.context.scene
camera = scene.camera
if camera is None:
    raise RuntimeError("Saved scene has no active camera.")
width = int(scene.render.resolution_x * scene.render.resolution_percentage / 100)
height = int(scene.render.resolution_y * scene.render.resolution_percentage / 100)
world_to_camera = camera.matrix_world.inverted()
projection_matrix = camera.calc_matrix_camera(
    bpy.context.evaluated_depsgraph_get(), x=width, y=height,
    scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
reference_camera = {
    "type": camera.data.type,
    "worldToCamera": [float(value) for row in world_to_camera for value in row],
    "projectionMatrix": [float(value) for row in projection_matrix for value in row],
    "orthoScale": float(camera.data.ortho_scale),
    "shiftX": float(camera.data.shift_x),
    "shiftY": float(camera.data.shift_y),
    "width": width, "height": height,
    "pixelAspectX": float(scene.render.pixel_aspect_x),
    "pixelAspectY": float(scene.render.pixel_aspect_y),
    "clipStart": float(camera.data.clip_start), "clipEnd": float(camera.data.clip_end),
}
points = []
for z in [0, 1, 2, 3, 4, 4.495]:
    points.append((f"axis-z{z:g}", (0, 0, z)))
for name, point in [("unit+x", (1, 0, 0)), ("unit-x", (-1, 0, 0)),
                    ("unit+y", (0, 1, 0)), ("unit-y", (0, -1, 0))]:
    points.append((name, point))
for name, radius, z in [("foot", .999, .20), ("socket", .537, 1.29),
                        ("middle-collar", .590, 3.137)]:
    for index in range(4):
        angle = index * math.pi / 2
        points.append((f"{name}-{index}", (radius * math.cos(angle), radius * math.sin(angle), z)))
for index in range(8):
    angle = math.pi / 8 + index * math.pi / 4
    points.append((f"crown-plane-{index}", (.64 * math.cos(angle), .64 * math.sin(angle), 4.395)))
samples = []
for name, point in points:
    projected = world_to_camera_view(scene, camera, Vector(point))
    samples.append({"name": name, "world": list(point),
                    "ndc": list(projected),
                    "pixel": [float(projected.x * width), float((1 - projected.y) * height)]})
after_hash = digest(BLEND)
after_stat = BLEND.stat()
if before_hash != after_hash or before_stat.st_mtime_ns != after_stat.st_mtime_ns:
    raise RuntimeError("Source .blend changed during inspection.")
report = {
    "sourceBlend": str(BLEND), "sourceSha256": before_hash, "sourceUnchanged": True,
    "resolutionPercentage": scene.render.resolution_percentage,
    "referenceCamera": reference_camera,
    "cameraName": camera.name,
    "cameraLocation": list(camera.location),
    "matrixWorld": [float(value) for row in camera.matrix_world for value in row],
    "matrixConvention": "4x4 row-major; multiplication by a column vector",
    "pixelConvention": "top-left origin; x=ndc.x*width; y=(1-ndc.y)*height",
    "sampleCount": len(samples), "samples": samples,
}
OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("CAMERA_INSPECTION " + json.dumps({key: value for key, value in report.items() if key != "samples"}))
