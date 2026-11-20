"""Verify the king's queen-derived turning, single cross seat and preserved scene."""

from pathlib import Path
import argparse
import json
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_base_light_checkpoint import snapshot
from check_local_finish import remaining_settings
from check_socket_checkpoint import extra
from render_regions import controls
from turn_chavet_profile import ROOT, coordinates, digest, meridian, turn


def inspect(source):
    state, lights, receivers = snapshot(source)
    scene = bpy.context.scene
    body = next(obj for obj in controls(scene) if obj.get('king_editable_control'))
    control_positions = coordinates(body, 96)
    for modifier in body.modifiers:
        if modifier.type == 'SUBSURF':
            modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points = np.array([vertex.co[:] for vertex in mesh.vertices])
    rings = np.array([datum.value for datum in mesh.attributes['King profile ring'].data])
    positive_x = (np.abs(points[:, 1]) < 1e-7) & (points[:, 0] > 1e-7)
    section = np.column_stack((rings[positive_x], points[positive_x, 0], points[positive_x, 2]))
    section = section[np.argsort(section[:, 0])]
    evaluated.to_mesh_clear()
    extras = extra()
    sampling = remaining_settings()
    return state, lights, receivers, extras, sampling, control_positions, section, body.name


def dimensions(section):
    def span(low, high):
        return section[(section[:, 0] >= low) & (section[:, 0] <= high)]

    def z(ring):
        return float(np.interp(ring, section[:, 0], section[:, 2]))

    def radius(ring):
        return float(np.interp(ring, section[:, 0], section[:, 1]))

    def crest(low, high):
        rows = span(low, high)
        ring, r, height = rows[np.argmax(rows[:, 1])]
        return {'ring': float(ring), 'radius': float(r), 'z': float(height)}

    seat = span(74.5, 86.5)
    slope = np.diff(seat[:, 1])
    peaks = np.where((slope[:-1] > 1e-5) & (slope[1:] < -1e-5))[0] + 1
    collar_crests = [crest(*interval) for interval in [(36, 44), (46, 51), (54.5, 60)]]
    return {
        'socket_height_rings_20_to_27': z(27) - z(20),
        'socket_diameter_at_22': 2 * radius(22),
        'head_radius_at_neck_61': radius(61),
        'head_radius_at_64': radius(64),
        'head_radius_at_rim': crest(67, 71)['radius'],
        'lower_to_upper_collar_crest_height': collar_crests[2]['z'] - collar_crests[0]['z'],
        'upper_collar_height_rings_54_to_61': z(61) - z(54),
        'collar_crests': collar_crests,
        'cross_seat_crests': [float(seat[i, 0]) for i in peaks]
    }


def main(config_path, output_path):
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    donor = ROOT / config['queen_source']
    before_path = ROOT / config['king_source']
    after_path = ROOT / 'build/king-mission' / config['variant'] / 'king.blend'
    assert digest(donor) == config['queen_sha256'] and digest(before_path) == config['king_sha256']
    accepted_hash = digest(after_path)

    bpy.ops.wm.open_mainfile(filepath=str(donor), load_ui=False)
    queen = next(obj for obj in bpy.context.scene.objects if obj.get('mission_editable_control'))
    queen_profile = meridian(coordinates(queen, int(queen['ring_segments'])))
    a, al, ar, ax, sampling, old_positions, section_a, body_name = inspect(before_path)
    b, bl, br, bx, new_sampling, new_positions, section_b, new_name = inspect(after_path)
    old_meridian = meridian(old_positions)
    target = turn(old_meridian, queen_profile, config)
    # Blender stores each vertex as float32. Reconstruct at that precision,
    # rather than comparing a mean of stored vertices with float64 targets.
    expected = old_positions.copy()
    xy = old_positions[1:-1, :, :2]
    radii = np.linalg.norm(xy, axis=2)
    expected[1:-1, :, :2] = xy * (target[1:-1, 0, None] / radii)[:, :, None]
    expected[1:-1, :, 2] += (target[1:-1, 1] - old_meridian[1:-1, 1])[:, None]
    np.testing.assert_array_equal(expected.astype(np.float32), new_positions)
    assert new_name == body_name
    assert a['objects'][body_name].pop('positions') != b['objects'][body_name].pop('positions')
    assert a == b and ax == bx, 'Unexpected change in topology, cross, UVs, material, packed images, camera or world'
    assert al == bl and sampling == new_sampling, 'Light rig or render settings changed'
    assert ar['lightRoutes'] == br['lightRoutes'] and ar['receiverCount'] == br['receiverCount'] == 9

    old, new = dimensions(section_a), dimensions(section_b)
    print('Evaluated dimensions', json.dumps([old, new]), flush=True)
    assert new['socket_height_rings_20_to_27'] < .8 * old['socket_height_rings_20_to_27']
    assert new['socket_diameter_at_22'] >= .98 * old['socket_diameter_at_22']
    assert new['lower_to_upper_collar_crest_height'] < .89 * old['lower_to_upper_collar_crest_height']
    assert new['upper_collar_height_rings_54_to_61'] < .65 * old['upper_collar_height_rings_54_to_61']
    assert len(old['cross_seat_crests']) == 2 and len(new['cross_seat_crests']) == 1
    assert new['head_radius_at_64'] - new['head_radius_at_neck_61'] > .085
    cone = section_b[(section_b[:, 0] >= 61.5) & (section_b[:, 0] <= 68.5)]
    assert np.min(np.diff(cone[:, 1])) > 0 and np.min(np.diff(cone[:, 2])) > 0
    assert digest(after_path) == accepted_hash and digest(donor) == config['queen_sha256']
    result = dict(source_sha256=config['king_sha256'], queen_sha256=config['queen_sha256'],
                  model_sha256=accepted_hash, previous=old, revised=new, exact_receiver_count=9,
                  receiver_normal_max_error=br['normalMaxError'], control_vertices_exact=True,
                  cross_topology_uv_attributes_packed_images_lights_camera_world_preserved=True,
                  source_queen_unchanged=True, section='Evaluated positive-X body meridian in model units')
    output_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('output', type=Path)
    params = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(params.config, params.output)
