"""Round 2A. Cut a rounded arris along the poll and plane the swept ear faces."""
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


PARENT_HASH = '3d2ccb939f7b96b114cabcd179d8856e8922f734eeb034eb8bc711f641b23f17'
RING_SUPPORT = np.array([.42,.90,1.0,1.0,.88,.50,.12,0,0,0,0,0,0])
SHOULDER = np.array([.72,.60,.44,.40,.37,.34,.34,0,0,0,0,0,0])
EAR_SUPPORT = np.array([0,.30,.85,1.0,1.0,.68,0])


def sculpt_poll(rings):
    result = rings.copy()
    theta = np.arange(64)*2*np.pi/64
    upper = -np.cos(theta)
    depth = np.abs(np.sin(theta))
    for i,ring in enumerate(rings):
        if RING_SUPPORT[i]==0:
            continue
        # The radial axis is the local pole-to-root direction of this ring.
        # The signed width axis remains symmetric in the unposed carving.
        axis = (ring[32]-ring[0])/2
        axis[1] = 0
        s = SHOULDER[i]
        flat_crown = 1 - .17*depth**2
        bevel = ease(depth,s-.09,s+.10)
        undercut = .068*np.exp(-((depth-s-.18)/.19)**2)
        return_to_root = (1 - ease(depth,.84,.995))
        offset = ((flat_crown-upper)*(1-bevel)-undercut*bevel) * return_to_root
        # Keep the shoulder continuous, taper it as it meets the rounded mane.
        offset *= RING_SUPPORT[i]*(upper>0)
        result[i] += offset[:,None]*axis
    return result


def sculpt_ears(rings, side):
    result = rings.copy()
    # Each ring has a top, an outer lip, an underside and an embedded root.
    # Plane the outer faces toward their chord to clarify the lip in silhouette.
    for i,ring in enumerate(rings):
        w = EAR_SUPPORT[i]
        for first,last,factor in [(0,16,.72),(16,32,.46)]:
            t = np.linspace(0,1,last-first+1)[:,None]
            line = (1-t)*ring[first]+t*ring[last]
            result[i,first:last+1] += w*factor*(line-ring[first:last+1])
        # Seat the underside into the skull, retaining both end points and
        # the height of the top edge in each of the original seven sections.
        sector = np.arange(64)*2*np.pi/64
        under = ease(-np.cos(sector),-.15,.84)
        result[i,:,1] -= side*.018*w*under
    return result


def open_model(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name), load_ui=False)
    return bpy.context.scene


def build():
    assert sha(OUT/'parent.blend') == PARENT_HASH
    scene = open_model('parent.blend')
    data = json.loads(scene['knight_mission_pose'])
    pose = tuple(data[k] for k in ('dx','dy','twist_degrees'))
    cfg = {'parent_sha256':PARENT_HASH,'pose':pose,'mane_ring_weights':RING_SUPPORT.tolist(),
           'mane_fraction_at_crest':SHOULDER.tolist(),'ear_ring_weights':EAR_SUPPORT.tolist(),
           'ear_outer_chord_blend':[.72,.46],'ear_underside_seat':.018,'geometry':{}}
    for suffix in ['swept rounded mane','near swept ear','far swept ear']:
        obj = bpy.data.objects['Knight | '+suffix]
        world = world_vertices(obj)
        rings = rest_coords(world,pose).reshape(-1,64,3)
        reshaped = sculpt_poll(rings) if suffix.startswith('swept') else sculpt_ears(rings,-1 if suffix.startswith('near') else 1)
        moved = posed(reshaped.reshape(-1,3),*pose)
        d = np.linalg.norm(moved-world,axis=1)
        apply_world(obj,moved)
        cfg['geometry'][suffix]={'max_displacement':float(d.max()),'vertices_moved_over_0.001':int((d>.001).sum())}
    bpy.context.view_layer.update()
    scene['knight_improvement_002_A'] = json.dumps(cfg)
    configure_render(scene,144)
    save_model(scene,OUT/'knight.blend')
    cfg['model_sha256'] = sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',cfg)


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
    print('ROUND_2A_COMPLETE',flush=True)


if __name__ == '__main__':
    build()
    pictures()
