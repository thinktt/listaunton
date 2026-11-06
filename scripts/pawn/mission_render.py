"""Small Blender utilities for reproducible pawn trials at the saved camera."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build/pawn-mission"
ASSETS = ROOT / "assets/pawn"
CAMERA = json.loads((ASSETS / "camera.json").read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def control(scene):
    bodies = [ob for ob in scene.objects if ob.type == "MESH" and not ob.hide_render]
    assert len(bodies) == 1, [ob.name for ob in bodies]
    return bodies[0]

def setup(scene, samples=64):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.use_persistent_data = True
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.cycles.device = "CPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == "OPTIX"
        if any(device.use for device in prefs.devices):
            scene.cycles.device = "GPU"
    except (RuntimeError, TypeError) as exc:
        print("Using CPU:", exc)
    bpy.context.preferences.filepaths.save_version = 0

def fixed_camera(scene):
    cam = scene.camera
    assert cam.data.type == "ORTHO"
    back = cam.matrix_world.to_3x3() @ Vector((0, 0, 1))
    assert abs(math.degrees(math.asin(back.z)) - 54) < .001
    actual = [v for row in cam.matrix_world.inverted() for v in row]
    assert np.allclose(actual, CAMERA["worldToCamera"], atol=1e-6, rtol=0)
    assert abs(cam.data.ortho_scale-CAMERA["orthoScale"]) < 1e-6
    assert abs(cam.data.shift_x-CAMERA["shiftX"]) < 1e-6 and abs(cam.data.shift_y) < 1e-6
    assert (scene.render.resolution_x, scene.render.resolution_y) == (1254, 1254)

def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)

def side_camera(scene):
    cam = scene.camera
    cam.location = (0,-12,1.35)
    cam.rotation_euler = (Vector((0,0,1.35))-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.shift_x = cam.data.shift_y = 0
    cam.data.ortho_scale = 3.5
    scene.render.resolution_x = scene.render.resolution_y = 640

def area(scene, name, position, target, energy, size, *, diffuse=True, glossy=True, color=(1,1,1), size_y=None):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK" if size_y is None else "RECTANGLE"
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.visible_diffuse, obj.visible_glossy = diffuse, glossy
    return obj

class Surface:
    """Raycast the evaluated pawn and interpolate its smooth shading normals."""
    def __init__(self, scene, obj):
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        self.xyz = np.array([tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices])
        self.normals = np.array([tuple((evaluated.matrix_world.to_3x3().inverted().transposed() @ v.normal).normalized()) for v in mesh.vertices])
        self.triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
        self.tree = BVHTree.FromPolygons(self.xyz.tolist(), self.triangles, all_triangles=True)
        evaluated.to_mesh_clear()
        cam = scene.camera
        self.camera_world = cam.matrix_world.copy()
        self.inverse_projection = cam.calc_matrix_camera(graph,x=1254,y=1254).inverted()
        self.back = (cam.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()

    def hit(self, x, y):
        ndc = Vector((2*(x+.5)/1254-1, 1-2*(y+.5)/1254, -1, 1))
        local = self.inverse_projection @ ndc
        origin = self.camera_world @ (local.xyz/local.w)
        hit, _, face, _ = self.tree.ray_cast(origin, -self.back, 100)
        if hit is None:
            raise ValueError(f"No pawn at target pixel {(x,y)}")
        ids = list(self.triangles[face])
        a,b,c = self.xyz[ids]
        u,v = np.linalg.lstsq(np.column_stack((b-a,c-a)), np.asarray(hit)-a, rcond=None)[0]
        normal = Vector((np.array([1-u-v,u,v]) @ self.normals[ids]).tolist()).normalized()
        return hit, normal
