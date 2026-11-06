"""Validate and render a saved base study under the same cameras and wood lighting as checkpoint 18."""
import hashlib
import json
from pathlib import Path
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from build_base_study import CONFIG, MODELS, STUDY_ID, shape, verify_shape
from queen_scene import editable_mesh, set_material
from refine_socket_flare import read_controls
from validate_render_receivers import check as check_receivers


def camera_record(scene):
    cam = scene.camera
    return {"world_matrix": [float(v) for row in cam.matrix_world for v in row],
            "ortho_scale": cam.data.ortho_scale, "shift": [cam.data.shift_x,cam.data.shift_y],
            "size": [scene.render.resolution_x, scene.render.resolution_y], "type": cam.data.type}


def run(variant):
    cfg = json.loads(CONFIG.read_text())
    control_path = MODELS/"socket.blend"
    assert hashlib.sha256(control_path.read_bytes()).hexdigest() == cfg["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(control_path),load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    baseline = read_controls(control.data,int(control["ring_segments"]))
    camera = camera_record(scene)
    path = MODELS/(variant+".blend")
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    actual = read_controls(control.data,int(control["ring_segments"]))
    assert np.array_equal(actual, shape(baseline,cfg))
    measurements = verify_shape(baseline, actual, cfg)
    assert camera_record(scene) == camera
    receivers = check_receivers(scene,control)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = control.evaluated_get(dg)
    mesh = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
    bm.free()
    ev.to_mesh_clear()
    out = ROOT/"assets/queen-base-studies"/variant
    out.mkdir(parents=True,exist_ok=True)
    wood = control.data.materials[0]
    settings = json.loads(scene["mission_material_config"])
    bs = wood.node_tree.nodes["Principled BSDF"]
    ink = bs.inputs["Base Color"].links[0].from_node.image
    assert hashlib.sha256(bytes(ink.packed_file.data)).hexdigest() == settings["texture_sha256"]
    clay = bpy.data.materials.new("Base study inspection clay")
    clay.use_nodes = True
    shader = clay.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value=(.24,.26,.29,1)
    shader.inputs["Roughness"].default_value=.32
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type="OPTIX"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use=dev.type=="OPTIX"
        if any(dev.use for dev in prefs.devices):
            scene.cycles.device="GPU"
    except TypeError:
        scene.cycles.device="CPU"
    scene.render.use_persistent_data = True
    assert scene.cycles.samples==256 and not scene.cycles.use_light_tree
    for view in ("fixed","side"):
        if view=="side":
            cam=scene.camera
            cam.data.shift_x=cam.data.shift_y=0
            cam.data.sensor_fit="VERTICAL"
            cam.data.ortho_scale=6.6
            cam.location=(0,-16,2.55)
            cam.rotation_euler=(Vector((0,0,2.55))-cam.location).to_track_quat("-Z","Y").to_euler()
            scene.render.resolution_x,scene.render.resolution_y=600,900
            bpy.context.view_layer.update()
            side_camera = camera_record(scene)
        for surface,material in (("wood",wood),("neutral",clay)):
            set_material(scene,material)
            scene.render.filepath=str(out/f"{view}-{surface}.png")
            bpy.ops.render.render(write_still=True)
    report={"model_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"based_on":cfg["source_sha256"],
            "variant":variant,"closed_manifold":True,"source_profile_verified":True,"same_reference_camera":True,
            "fixed_camera":camera,"side_camera":side_camera,"texture_sha256":settings["texture_sha256"],
            "seat_z":float(actual[cfg["stem_seat_ring"],0,2]),"profile_measurements":measurements,
            "same_footprint_and_overall_height":bool(np.array_equal(actual[:19,:,:2],baseline[:19,:,:2]) and actual[:,:,2].max()==baseline[:,:,2].max()),
            "receivers":receivers}
    assert report["same_footprint_and_overall_height"]
    (out/"validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("Rendered base study",variant,report["seat_z"],flush=True)


if __name__=="__main__":
    run(STUDY_ID)
