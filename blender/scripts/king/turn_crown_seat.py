"""Turn and verify the two concentric beads under the king's cross."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_regions import controls, regenerate
from turn_chavet_profile import ROOT, coordinates, digest
from validate_chavet_profile import inspect


def profile_rows(body):
    field = body.data.attributes['King profile ring']
    logical = np.empty(len(body.data.vertices), dtype=np.float32)
    field.data.foreach_get('value', logical)
    rows = logical.reshape(-1, 96)
    assert np.all(rows == rows[:, :1])
    return rows[:, 0]


def turn(source, destination, spec):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    body = next(obj for obj in controls(scene) if obj.get('king_editable_control'))
    rows = profile_rows(body)
    co = coordinates(body, 96)
    for logical, radius, height in spec['seat_profile']:
        assert 74 <= logical <= 87
        index, = np.flatnonzero(rows == logical)
        row = co[index]
        if radius is not None:
            length = np.linalg.norm(row[:, :2], axis=1)
            row[:, :2] *= (radius / length)[:, None]
        row[:, 2] = height
    body.data.vertices.foreach_set('co', co.astype(np.float32).ravel())
    body.data.update()
    regenerate(scene)
    scene['king_mission_variant'] = spec['variant']
    scene['king_crown_seat_018'] = json.dumps(spec, sort_keys=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)


def features(meridian):
    # A bead creates a local maximum of radius on the evaluated side meridian.
    seat = meridian[(meridian[:, 0] >= 74.5) & (meridian[:, 0] <= 86.5)]
    slope = np.diff(seat[:, 1])
    indices = np.flatnonzero((slope[:-1] > 1e-5) & (slope[1:] < -1e-5)) + 1
    def point(row):
        return dict(ring=float(row[0]), radius=float(row[1]), height=float(row[2]))
    report = {'beads': [point(seat[i]) for i in indices]}
    if len(indices) == 2:
        lower, upper = (seat[i] for i in indices)
        middle = seat[indices[0]:indices[1]+1]
        saddle = middle[np.argmin(middle[:, 1])]
        report.update(groove=point(saddle), separation=float(upper[2]-lower[2]),
                      upper_to_lower_diameter=float(upper[1]/lower[1]),
                      upper_bead_proud_of_groove=float(upper[1]-saddle[1]))
    return report


def validate(source, destination, spec, report_path):
    original, lights, regions, extras, sampling, old, old_section, name = inspect(source)
    current, lights_now, regions_now, extras_now, sampling_now, new, section, name_now = inspect(destination)
    scene = bpy.context.scene
    body = scene.objects[name_now]
    rows = profile_rows(body)
    edited = {row[0] for row in spec['seat_profile']}
    frozen = ~np.isin(rows, list(edited))
    assert name == name_now and np.array_equal(old[frozen], new[frozen])
    for logical, radius, height in spec['seat_profile']:
        i, = np.flatnonzero(rows == logical)
        assert np.all(new[i,:,2] == np.float32(height))
        if radius is not None:
            assert np.max(abs(np.linalg.norm(new[i,:,:2],axis=1)-radius)) < 5e-8
            assert np.max(abs(old[i,:,0]*new[i,:,1]-old[i,:,1]*new[i,:,0])) < 1e-8
        else:
            np.testing.assert_array_equal(old[i,:,:2], new[i,:,:2])
    assert original['objects'][name].pop('positions') != current['objects'][name].pop('positions')
    assert original == current and extras == extras_now and lights == lights_now and sampling == sampling_now
    assert regions['lightRoutes'] == regions_now['lightRoutes']
    assert regions_now['receiverCount'] == 9 and regions_now['normalMaxError'] == 0
    # Catmull-Clark interpolation reaches the neighboring control intervals.
    below = min(edited) - 1.5
    np.testing.assert_array_equal(old_section[old_section[:,0] < below], section[section[:,0] < below])
    before, after = features(old_section), features(section)
    assert len(before['beads']) == 1 and len(after['beads']) == 2
    assert after['upper_bead_proud_of_groove'] > .008 and .76 < after['upper_to_lower_diameter'] < .9
    assert .065 < after['separation'] < .14
    cross = next(obj for obj in controls(scene) if obj != body)
    cross_floor = min((cross.matrix_world @ v.co).z for v in cross.data.vertices)
    crown_top = float(np.min(new[rows == 87,:,2]))
    assert crown_top - cross_floor > .08
    result = dict(model_sha256=digest(destination), source_sha256=digest(source),
                  previous=before, revised=after, edited_logical_rows=sorted(edited),
                  control_rows_preserved=int(frozen.sum()), fixed_camera_degrees=54,
                  body_below_seat_exact=True, cross_material_uv_packed_textures_lights_camera_exact=True,
                  cross_floor=cross_floor, seat_center_height=crown_top,
                  receiver_count=regions_now['receiverCount'], receiver_normal_error=regions_now['normalMaxError'])
    report_path.write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec = json.loads(args.config.read_text(encoding='utf-8-sig'))
    source = ROOT / spec['king_source']
    assert digest(source) == spec['king_sha256']
    name = spec['variant']
    assert Path(name).name == name and name not in ('','.','..')
    out = ROOT / 'build/king-mission' / name
    out.mkdir(parents=True, exist_ok=True)
    if args.validate:
        validate(source, out/'king.blend', spec, out/'seat-measurements.json')
    else:
        turn(source, out/'king.blend', spec)
    assert digest(source) == spec['king_sha256']


if __name__ == '__main__':
    main()
