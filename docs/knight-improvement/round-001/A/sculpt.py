"""Round 1A. A fuller rear cheek, swept jaw, and softly tapered nose."""
from pathlib import Path
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/knight"))
from lower_carving_fit import ease, rest_coords
from mission_pose import posed
from mission_scene import configure_render, json_file, render, save_model, sha
from mission_scene import use_side_camera, visible_meshes, world_vertices
from refine_eye import apply_world

PARENT_HASH = "c1254b0087c39e4506b34575d88b52d92a1cd376ed9ee4b891c207d5ce51995c"
STRENGTH = dict(cheek=0.082, jaw_roll=0.026, notch_fill=0.065,
                chin_lift=0.047, tip_drop=0.034, nose_taper=0.073, throat_recede=0.105)


def form(points):
    x, y, z = points.T
    key = STRENGTH
    result = points.copy()
    # Almond-shaped mass lies under the eye. The centerline stays at y=0.
    cheek_height = 3.83 - 0.19*x
    eye_guard = 1 - ease(z, 3.96-0.20*x, 4.13-0.20*x)
    cheek = np.exp(-((x-0.16)/0.52)**2 - ((z-cheek_height)/0.28)**2) * eye_guard
    jaw_height = 3.67 - 0.15*x
    roll = np.exp(-((x-0.59)/0.59)**2 - ((z-jaw_height)/0.14)**2)
    flank = np.tanh(y/0.23)
    result[:, 1] += flank * (key['cheek']*cheek + key['jaw_roll']*roll)
    # Maintain the terminal reach seen in the original sprite. Reduce the bulb
    # on the underside and turn the wood gently into the narrow tip.
    head = ease(z, 3.22, 3.44)
    low_face = (1-ease(z, 3.64-0.12*(x-0.8), 4.02-0.23*(x-0.8))) * head
    below = (-key['notch_fill']*np.exp(-((x-0.76)/0.34)**2)
             + key['chin_lift']*np.exp(-((x-1.26)/0.30)**2))
    nose = ease(x, 1.03, 1.68)*head
    result[:, 2] += low_face*below - key['tip_drop']*nose
    result[:, 1] -= key['nose_taper']*nose*y
    # Sweep the throat backwards directly below the jowl. Fade out before
    # reaching the chest's highlight or the lower muzzle.
    throat = np.exp(-((x-0.49)/0.30)**2 - ((z-3.38)/0.27)**2)
    result[:, 0] -= key['throat_recede']*throat
    return result


def surface_sample(obj, pose):
    """Opposite ray hits measured about the carving's own sagittal plane."""
    pts = rest_coords(world_vertices(obj), pose)
    obj.data.calc_loop_triangles()
    tri = np.empty((len(obj.data.loop_triangles), 3), np.int32)
    obj.data.loop_triangles.foreach_get("vertices", tri.ravel())
    tree = BVHTree.FromPolygons(pts.tolist(), tri.tolist(), all_triangles=True)
    result = {}
    for label, x, z in [('cheek',.16,3.81), ('jaw',.62,3.64), ('bridge',1.05,3.78),
                        ('nose',1.56,3.72), ('nose_end',1.66,3.74)]:
        locs = [tree.ray_cast(Vector((x,s*2,z)), Vector((0,-s,0)), 4)[0] for s in (-1,1)]
        if all(q is not None for q in locs):
            a, b = [q.y for q in locs]
            result[label] = dict(x=x,z=z,near=a,far=b,center=(a+b)/2,span=b-a)
    return result


def open_model(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name), load_ui=False)
    return bpy.context.scene


def build():
    assert sha(OUT/'parent.blend') == PARENT_HASH
    scene = open_model('parent.blend')
    data = json.loads(scene['knight_mission_pose'])
    pose = tuple(data[k] for k in ('dx','dy','twist_degrees'))
    skin = bpy.data.objects['Knight | continuous horse head and neck']
    evidence = {'parent_sha256':PARENT_HASH, 'strength_world_units':STRENGTH, 'pose':pose,
                'before':surface_sample(skin,pose), 'displacements':{}}
    for suffix in ('continuous horse head and neck','coherent skull cheek and conical muzzle','near eye','far eye'):
        obj = bpy.data.objects['Knight | '+suffix]
        world = world_vertices(obj)
        rest = rest_coords(world, pose)
        transformed = posed(form(rest), *pose)
        distance = np.linalg.norm(transformed-world, axis=1)
        apply_world(obj, transformed)
        evidence['displacements'][suffix] = {
            'vertices':len(world), 'over_0.002':int((distance>.002).sum()),
            'max_world_units':float(distance.max())}
    bpy.context.view_layer.update()
    evidence['after'] = surface_sample(skin,pose)
    scene['knight_improvement_001_A'] = json.dumps(STRENGTH)
    configure_render(scene, 144)
    save_model(scene, OUT/'knight.blend')
    evidence['model_sha256'] = sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json', evidence)


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
    print('CANDIDATE_A_COMPLETE',flush=True)


if __name__ == '__main__':
    build()
    pictures()
