"""Build and verify a domed Chavet shoulder and compact cross from the two-ring king."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_regions import controls, regenerate
from turn_chavet_profile import ROOT, coordinates, digest
from turn_crown_seat import features, profile_rows
from validate_chavet_profile import inspect


def editable_parts(scene):
    pieces = controls(scene)
    body, = [ob for ob in pieces if ob.get('king_editable_control')]
    cross, = [ob for ob in pieces if ob != body]
    return body, cross


def cross_positions(cross):
    # The cross was authored in world coordinates. Keep that convention and its UVs.
    np.testing.assert_allclose(np.asarray(cross.matrix_world), np.eye(4), atol=1e-7)
    return np.array([v.co[:] for v in cross.data.vertices])


def transform_cross(points, old_deck, new_deck, spec):
    result = points.copy()
    result[:, 0] *= spec['cross_width_scale']
    result[:, 1] *= spec.get('cross_depth_scale', spec['cross_width_scale'])
    result[:, 2] = new_deck + (points[:, 2] - old_deck) * spec['cross_height_scale']
    if 'arm_height_adjustments' in spec:
        heights, lifts = np.asarray(spec['arm_height_adjustments']).T
        result[:, 2] += np.interp(points[:, 2], heights, lifts)
    return result.astype(np.float32)


def turn_body(points, logical_rows, spec):
    result = points.copy()
    shoulder = {row: (radius, z) for row, radius, z in spec['shoulder_profile']}
    foot_height = spec['old_seat_start']
    for index, logical in enumerate(logical_rows):
        if logical in shoulder:
            radius, height = shoulder[logical]
            row = result[index]
            row[:, :2] *= (radius / np.linalg.norm(row[:, :2], axis=1))[:, None]
            row[:, 2] = height
        elif 75 <= logical <= 87:
            row = result[index]
            row[:, :2] *= spec['seat_width_scale']
            row[:, 2] = foot_height + spec['seat_drop'] + (row[:, 2] - foot_height) * spec['seat_height_scale']
    return result.astype(np.float32)


def build(source, output, spec):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    body, cross = editable_parts(scene)
    rows = profile_rows(body)
    old = coordinates(body, 96)
    new = turn_body(old, rows, spec)
    old_deck, new_deck = float(old[rows == 87][0, 0, 2]), float(new[rows == 87][0, 0, 2])
    new_cross = transform_cross(cross_positions(cross), old_deck, new_deck, spec)
    for obj, points in ((body, new), (cross, new_cross)):
        obj.data.vertices.foreach_set('co', points.ravel())
        obj.data.update()
    regenerate(scene)
    scene['king_mission_variant'] = spec['variant']
    scene['king_crown_019'] = json.dumps(spec, sort_keys=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)


def check(source, output, spec):
    before, lights, routes, extras, sampling, old, old_section, name = inspect(source)
    body, cross = editable_parts(bpy.context.scene)
    old_cross = cross_positions(cross)
    rows = profile_rows(body)
    after, new_lights, rerouted, new_extras, new_sampling, new, section, new_name = inspect(output)
    body, cross = editable_parts(bpy.context.scene)
    assert name == new_name and np.array_equal(rows, profile_rows(body))
    np.testing.assert_array_equal(new, turn_body(old, rows, spec))
    old_deck, new_deck = float(old[rows == 87][0, 0, 2]), float(new[rows == 87][0, 0, 2])
    new_cross = cross_positions(cross)
    np.testing.assert_array_equal(new_cross, transform_cross(old_cross, old_deck, new_deck, spec))
    for key in (name, cross.name):
        assert before['objects'][key].pop('positions') != after['objects'][key].pop('positions')
    assert before == after and lights == new_lights and extras == new_extras and sampling == new_sampling
    assert routes['lightRoutes'] == rerouted['lightRoutes'] and rerouted['receiverCount'] == 9
    assert rerouted['normalMaxError'] == 0
    first_ring = min(p[0] for p in spec['shoulder_profile'])
    np.testing.assert_array_equal(old[rows < first_ring], new[rows < first_ring])
    np.testing.assert_array_equal(old_section[old_section[:,0] < first_ring - 1.5],
                                  section[section[:,0] < first_ring - 1.5])
    # At increasing radii, a dome turns progressively downward. The old top
    # locally did the opposite, producing a broad lip and a lifted inner neck.
    def slopes(meridian):
        # Once inside the lower bead's radius, the wood turns back out to
        # form the seat. That undercut is hidden by the bead in profile.
        bead_radius = features(meridian)['beads'][0]['radius']
        rows = meridian[(meridian[:,0] >= 69.5) & (meridian[:,0] <= 75) & (meridian[:,1] >= bead_radius)]
        return (np.diff(rows[:,2]) / -np.diff(rows[:,1])).tolist()
    gradients = slopes(section)
    assert min(gradients) > 0 and max(np.diff(gradients)) < 0, gradients
    old_seat, seat = features(old_section), features(section)
    assert len(old_seat['beads']) == len(seat['beads']) == 2 and .065 < seat['separation'] < .14
    assert seat['upper_bead_proud_of_groove'] > .008 and new_deck - new_cross[:,2].min() > .08
    def geometry(points, deck):
        return dict(width=float(np.ptp(points[:,0])), depth=float(np.ptp(points[:,1])), tip=float(points[:,2].max()),
                    embedded_depth=float(deck - points[:,2].min()), deck=deck)
    report = dict(source_sha256=digest(source), model_sha256=digest(output),
                  previous_seat=old_seat, current_seat=seat,
                  previous_cross=geometry(old_cross, old_deck), current_cross=geometry(new_cross, new_deck),
                  previous_shoulder_slopes=slopes(old_section), current_shoulder_slopes=gradients,
                  unchanged_body_control_rings=int(np.count_nonzero(rows < first_ring)),
                  unchanged_evaluated_profile_below_logical_ring=first_ring-1.5,
                  uv_material_packed_images_camera_lights_exact=True, receiver_count=9, receiver_normal_error=0)
    output.with_name('crown-measurements.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('KING_DOMED_CROWN_PASS', json.dumps(report['current_cross']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec = json.loads(args.config.read_text(encoding='utf-8-sig'))
    source = ROOT / spec['king_source']
    assert digest(source) == spec['king_sha256']
    assert Path(spec['variant']).name == spec['variant'] and spec['variant'] not in ('','.','..')
    folder = ROOT / 'build/king-mission' / spec['variant']
    folder.mkdir(parents=True, exist_ok=True)
    (check if args.validate else build)(source, folder/'king.blend', spec)
    assert digest(source) == spec['king_sha256']
