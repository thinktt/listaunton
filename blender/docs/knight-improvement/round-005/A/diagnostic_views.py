"""Studio and orbit inspection of a reopened candidate."""
from pathlib import Path
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/knight"))
from lower_carving_fit import ease, rest_coords
from mission_pose import posed
from mission_scene import configure_render, json_file, render, save_model, sha
from mission_scene import use_side_camera, visible_meshes, world_vertices
from refine_eye import apply_world


def open_model(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name), load_ui=False)
    return bpy.context.scene


def orbit(scene, az, elevation, target):
    a,e = map(math.radians,(az,elevation))
    cam = scene.camera
    cam.data.ortho_scale = 6.1
    cam.data.shift_x = cam.data.shift_y = 0
    cam.location = target + Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()


def clay_studio(scene, yaw):
    clay = bpy.data.materials['Neutral satin clay']
    for obj in visible_meshes(scene):
        for slot in obj.material_slots:
            slot.material = clay
    for obj in scene.objects:
        if obj.type=='LIGHT':
            obj.hide_render = True
    target = Vector((-.30,-.04,3.3))
    for sign in (-1,1):
        lamp = bpy.data.lights.new('Clay softbox','AREA')
        lamp.energy = 650
        lamp.shape = 'DISK'
        lamp.size = 5.5
        ob = bpy.data.objects.new('Clay softbox',lamp)
        scene.collection.objects.link(ob)
        a = math.radians(yaw)
        dx,dy = 3.8,sign*5.5
        ob.location = target + Vector((dx*math.cos(a)-dy*math.sin(a),dx*math.sin(a)+dy*math.cos(a),5))
        ob.rotation_euler = (target-ob.location).to_track_quat('-Z','Y').to_euler()


def pictures():
    scene = open_model('knight.blend')
    evidence = json.loads((OUT/'parameters.json').read_text())
    assert sha(OUT/'knight.blend')==evidence['model_sha256']
    assert scene.camera.data.type=='ORTHO'
    configure_render(scene,144)
    fixed = {'location':list(scene.camera.location),'rotation':list(scene.camera.rotation_euler),
             'ortho_scale':scene.camera.data.ortho_scale, 'shift': [scene.camera.data.shift_x,scene.camera.data.shift_y]}
    render(scene,OUT/'wood.png')
    use_side_camera(scene)
    render(scene,OUT/'wood-side.png')
    evidence['reopened_renders'] = {'samples':144, 'fixed_camera':fixed,
        'fixed_sha256':sha(OUT/'wood.png'), 'side_sha256':sha(OUT/'wood-side.png'),
        'device':json.loads(scene['knight_render_device'])}
    json_file(OUT/'parameters.json', evidence)
    scene.render.resolution_x = scene.render.resolution_y = 480
    scene.cycles.samples = 24
    yaw = evidence['pose'][2]
    target = Vector((0,0,2.62))
    for name, az in [('front',90),('opposite',180),('rear',270)]:
        orbit(scene, az+yaw, 10, target)
        render(scene,OUT/('wood-'+name+'.png'))
    clay_studio(scene,yaw)
    frames = OUT/'clay-turn'
    frames.mkdir(exist_ok=True)
    for n in range(16):
        orbit(scene, yaw+22.5*n, 8, target)
        render(scene,frames/f'{n:02d}.png')
    print('ROUND_5A_DIAGNOSTICS_COMPLETE',flush=True)
