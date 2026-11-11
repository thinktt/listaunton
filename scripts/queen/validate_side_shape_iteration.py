"""Validate an authorized queen side-shape checkpoint without weakening prior validators.

The earlier finish validator deliberately freezes checkpoint-22's profile.
This companion validator instead proves that a candidate is exactly the
recorded, deliberately changed meridian relative to the frozen checkpoint,
while still checking the real editable surface, receiver partition, material,
and orthographic camera.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bmesh
import bpy
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh
from validate_render_receivers import records


def controls(mesh, segments):
    value = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', value)
    return value.reshape((-1, segments, 3))


def ring_radius(value, ring):
    return float(np.linalg.norm(value[ring, :, :2], axis=1).mean())


def load_source_controls(path, mesh_name, segments):
    with bpy.data.libraries.load(str(path), link=False) as (names, loaded):
        assert mesh_name in names.meshes, (mesh_name, names.meshes)
        loaded.meshes = [mesh_name]
    source = loaded.meshes[0]
    try:
        return controls(source, segments)
    finally:
        bpy.data.meshes.remove(source)


def expected_controls(before, cfg):
    after = before.copy()
    for key, radius in cfg.get('radii', {}).items():
        ring = int(key)
        lengths = np.linalg.norm(after[ring, :, :2], axis=1)
        after[ring, :, :2] *= (float(radius) / lengths)[:, None]
    for key, delta in cfg.get('z_offsets', {}).items():
        after[int(key), :, 2] += float(delta)
    return after


def elevation_degrees(camera):
    back = camera.matrix_world.to_3x3() @ __import__('mathutils').Vector((0, 0, 1))
    return math.degrees(math.atan2(back.z, math.hypot(back.x, back.y)))


def validate_shape_intent(before, after, cfg):
    intent = cfg.get('intent', {})
    report = {}
    if intent.get('flare_lifted_into_shorter_socket'):
        before_wall = float(before[31, 0, 2] - before[29, 0, 2])
        after_wall = float(after[31, 0, 2] - after[29, 0, 2])
        assert after[38, 0, 2] < before[38, 0, 2]
        assert after_wall < before_wall
        assert ring_radius(after, 31) < ring_radius(before, 31)
        report['socket'] = {
            'seat_height_before_after': [float(before[38, 0, 2]), float(after[38, 0, 2])],
            'straight_wall_before_after': [before_wall, after_wall],
            'upper_wall_radius_before_after': [ring_radius(before, 31), ring_radius(after, 31)],
        }
    if intent.get('rounded_lower_and_finer_upper_collars'):
        lower = [ring_radius(after, i) for i in range(50, 63)]
        upper = [ring_radius(after, i) for i in range(74, 83)]
        assert max(lower) > lower[0] and max(lower) > lower[-1]
        assert max(upper) < max(ring_radius(before, i) for i in range(74, 83))
        assert after[82, 0, 2] - after[74, 0, 2] < before[82, 0, 2] - before[74, 0, 2]
        report['collars'] = {
            'lower_peak_radius': max(lower),
            'lower_end_radii': [lower[0], lower[-1]],
            'upper_peak_radius_before_after': [
                max(ring_radius(before, i) for i in range(74, 83)), max(upper)
            ],
            'upper_height_before_after': [
                float(before[82, 0, 2] - before[74, 0, 2]),
                float(after[82, 0, 2] - after[74, 0, 2]),
            ],
        }
    return report


def check_side_shape_receivers(scene, control):
    """Validate receiver topology by face/UV identity, not stale z bands.

    The historical receiver checker intentionally encodes checkpoint-22's
    collar coordinate intervals.  A documented shape edit moves those faces,
    so here the stronger invariant is that the regenerated receivers contain
    exactly the same evaluated surface faces, atlas UVs, normals, material,
    transform and declared light links as the closed editable control.
    """
    parts = [o for o in scene.objects if o.type == 'MESH' and o.get('mission_render_region')]
    assert parts and control.hide_render
    expected = {'turned-body', 'stem-socket', 'finial', 'lower-collar', 'middle-collar', 'upper-collar'}
    assert {o['mission_render_region'] for o in parts} == expected
    for part in parts:
        assert not part.hide_render and not part.modifiers
        assert part.matrix_world == control.matrix_world
        assert part.data.materials[0] == control.data.materials[0]
    levels = [(m, m.levels) for m in control.modifiers if m.type == 'SUBSURF']
    for modifier, _ in levels:
        modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    evaluated = control.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        original = records(mesh)
        received = [records(part.data) for part in parts]
        rows = np.concatenate([row[0] for row in received])
        normals = np.concatenate([row[1] for row in received])
        faces = [face for row in received for face in row[2]]
        assert sorted(faces) == sorted(original[2])
        assert sum(row[3] for row in received) == original[3]
        source_keys = original[0].view('V20').reshape(-1)
        receiver_keys = rows.view('V20').reshape(-1)
        source_order = np.argsort(source_keys, kind='stable')
        receiver_order = np.argsort(receiver_keys, kind='stable')
        assert np.array_equal(source_keys[source_order], receiver_keys[receiver_order])
        normal_error = abs(original[1][source_order] - normals[receiver_order])
        assert float(normal_error.max()) < .0002
    finally:
        evaluated.to_mesh_clear()
        for modifier, level in levels:
            modifier.levels = level
    settings = json.loads(scene['mission_material_config'])
    declared = {
        entry['name']: set(entry['receiver_parts'])
        for entry in settings['lights'] if 'receiver_parts' in entry
    }
    checked_lights = 0
    for light in (o for o in scene.objects if o.type == 'LIGHT'):
        collection = light.light_linking.receiver_collection
        if not collection:
            continue
        actual = {obj.get('mission_render_region') for obj in collection.objects}
        expected_parts = declared.get(light.name)
        if expected_parts == {'collars'}:
            expected_parts = {'lower-collar', 'middle-collar', 'upper-collar'}
        if expected_parts is not None:
            assert actual == expected_parts, (light.name, actual, expected_parts)
        checked_lights += 1
    return {
        'used': True,
        'receivers': len(parts),
        'regions': sorted(expected),
        'surface_faces_and_atlas_uvs_exact': True,
        'triangles': original[3],
        'custom_normal_max_component_error': float(normal_error.max()),
        'light_receiver_links_checked': checked_lights,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blend', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    cfg = json.loads(args.config.read_text(encoding='utf-8'))
    source = args.source_root / cfg['source_archive']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['source_sha256']

    bpy.ops.wm.open_mainfile(filepath=str(args.blend), load_ui=False)
    scene = bpy.context.scene
    obj = editable_mesh(scene)
    camera = scene.camera
    assert camera.data.type == 'ORTHO'
    elevation = elevation_degrees(camera)
    assert abs(elevation - float(cfg.get('elevation', 54))) < 1e-4
    expected_scale = float(cfg.get('axial_scale', 1))
    assert all(abs(obj.matrix_world[i][i] - expected_scale if i == 2 else obj.matrix_world[i][i] - 1) < 1e-6 for i in range(3))
    assert obj.data.materials and 'Walnut' in obj.data.materials[0].name

    after = controls(obj.data, int(obj['ring_segments']))
    before = load_source_controls(source, obj.data.name, after.shape[1])
    expected = expected_controls(before, cfg)
    assert np.allclose(after, expected, atol=1e-6, rtol=0), 'Meridian differs from recorded side-shape config'
    changed = {int(key) for key in cfg.get('radii', {})} | {int(key) for key in cfg.get('z_offsets', {})}
    unchanged = np.array([i not in changed for i in range(len(after))])
    assert np.array_equal(after[unchanged], before[unchanged]), 'An undeclared profile ring changed'

    graph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    try:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        boundary = sum(edge.is_boundary for edge in bm.edges)
        nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
        volume = bm.calc_volume(signed=True)
        bm.free()
        assert boundary == nonmanifold == 0 and volume > 0, (boundary, nonmanifold, volume)
    finally:
        evaluated.to_mesh_clear()

    settings = json.loads(scene['mission_material_config'])
    feature = settings.get(cfg.get('feature_key', 'side_shape_study'))
    assert feature and feature['source_sha256'] == cfg['source_sha256']
    assert feature['config'] == cfg
    assert feature['control_sha256'] == hashlib.sha256(after.tobytes()).hexdigest()
    intent_report = validate_shape_intent(before, after, cfg)
    receivers = check_side_shape_receivers(scene, obj)
    report = {
        'passed': True,
        'model_sha256': hashlib.sha256(args.blend.read_bytes()).hexdigest(),
        'source_sha256': cfg['source_sha256'],
        'variant': cfg['variant'],
        'camera_type': camera.data.type,
        'camera_elevation_degrees': elevation,
        'matrix_scale_xyz': [float(obj.matrix_world[i][i]) for i in range(3)],
        'changed_rings': sorted(changed),
        'undeclared_control_rings_identical': True,
        'intent_measurements': intent_report,
        'boundary_edges': boundary,
        'nonmanifold_edges': nonmanifold,
        'signed_volume': volume,
        'receivers': receivers,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
