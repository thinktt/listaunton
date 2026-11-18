"""Turn the king using the accepted queen's lower profile and a flared Chavet head.

Run in Blender with the study configuration after --. All outputs are staged
under build/king-mission. The two input Blender scenes are read only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mission_trial import gpu
from render_regions import controls, regenerate


# Corresponding landmarks along each meridian, in order from floor to stem
# and from lower-collar undercut to the crown neck. The rings stay attached
# to their original king UVs, finish attributes and light receivers.
BASE_RINGS = [0, 1, 2, 4, 5, 6, 8, 10, 11, 12, 14, 16, 17, 20,
              22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 34, 36, 37, 38]
COLLAR_RINGS = [49, 49.55, 50.8, 53.2, 55.3, 57, 59.4, 61, 61.7,
                62, 62.5, 63.4, 64.8, 65.8, 67, 69.3, 71, 72.6,
                73.7, 74, 75.8, 77, 78, 79, 80.3, 81.5, 82]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinates(obj, segments):
    data = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.vertices.foreach_get('co', data)
    return data.reshape(-1, segments, 3).astype(np.float64)


def meridian(co):
    return np.column_stack((np.linalg.norm(co[:, :, :2], axis=2).mean(axis=1),
                            co[:, :, 2].mean(axis=1)))


def sample(meridian_points, rings):
    indices = np.arange(len(meridian_points))
    return np.column_stack([np.interp(rings, indices, axis) for axis in meridian_points.T])


def interpolate(values, anchors):
    positions, targets = np.asarray(anchors, dtype=float).T
    return np.interp(values, positions, targets)


def turn(king, queen, spec):
    result = king.copy()
    # Socket and foot use the same turning as the queen. Their landmarks
    # are registered separately so the wider king still fits its sprite.
    base = sample(queen, BASE_RINGS)
    base[:, 0] *= interpolate(BASE_RINGS, spec['base_radial_scale'])
    base[:, 1] = interpolate(base[:, 1], spec['base_height_map'])
    result[1:28] = base[1:]

    collar = sample(queen, COLLAR_RINGS)
    collar[:, 0] *= interpolate(COLLAR_RINGS, spec['collar_radial_scale'])
    collar[:, 1] = interpolate(collar[:, 1], spec['collar_height_map'])
    result[35:62] = collar

    # Fade the join corrections through the original concave stem.
    for axis in (0, 1):
        anchors = [(27, result[27, axis] - king[27, axis]), (31, 0),
                   (33, 0), (35, result[35, axis] - king[35, axis])]
        result[28:35, axis] += interpolate(np.arange(28, 35), anchors)

    neck = result[61]
    rim = np.asarray(spec['crown_rim'])
    for index, fraction in enumerate(spec['cone_fractions'], start=62):
        result[index] = neck + fraction * (rim - neck)
    result[68:87] = np.array(spec['rim_and_cross_seat'])
    # Keep the tiny center cap and its original overlap with the cross.
    assert len(result) == 88 and result[87, 0] < .001
    return result


def main(config_path, render_preview):
    spec = json.loads(config_path.read_text(encoding='utf-8-sig'))
    source = ROOT / spec['king_source']
    donor = ROOT / spec['queen_source']
    assert digest(source) == spec['king_sha256'] and digest(donor) == spec['queen_sha256']
    variant = spec['variant']
    assert Path(variant).name == variant and variant not in ('', '.', '..')
    out = ROOT / 'build/king-mission' / variant
    out.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=str(donor), load_ui=False)
    queen_obj = next(obj for obj in bpy.context.scene.objects if obj.get('mission_editable_control'))
    queen_profile = meridian(coordinates(queen_obj, int(queen_obj['ring_segments'])))
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    body = next(obj for obj in controls(scene) if obj.get('king_editable_control'))
    positions = coordinates(body, 96)
    before = meridian(positions)
    after = turn(before, queen_profile, spec)
    for index in range(1, 87):
        ring = positions[index]
        lengths = np.linalg.norm(ring[:, :2], axis=1)
        ring[:, :2] *= (after[index, 0] / lengths)[:, None]
        ring[:, 2] += after[index, 1] - before[index, 1]
    body.data.vertices.foreach_set('co', positions.astype(np.float32).ravel())
    body.data.update()
    scene['king_free_receiver_normals'] = True
    regenerate(scene)
    scene['king_mission_variant'] = variant
    scene['king_turning_016'] = json.dumps(spec, sort_keys=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene.render.filepath = '//king-render.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'king.blend'), compress=True)
    (out / 'profile-controls.json').write_text(json.dumps(
        dict(before=before.tolist(), after=after.tolist(), queen=queen_profile.tolist()),
        indent=2) + '\n', encoding='utf-8')
    if render_preview:
        bpy.ops.wm.open_mainfile(filepath=str(out / 'king.blend'), load_ui=False)
        scene = bpy.context.scene
        gpu(scene)
        scene.render.filepath = str(out / 'fixed.png')
        bpy.ops.render.render(write_still=True)
        camera = scene.camera
        camera.data.shift_x = camera.data.shift_y = 0
        camera.data.sensor_fit = 'VERTICAL'
        camera.data.ortho_scale = 6
        camera.location = (0, -16, 2.65)
        camera.rotation_euler = (Vector((0, 0, 2.65)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 600, 900
        scene.render.filepath = str(out / 'profile.png')
        bpy.ops.render.render(write_still=True)
    assert digest(source) == spec['king_sha256'] and digest(donor) == spec['queen_sha256']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(args.config, args.preview)
