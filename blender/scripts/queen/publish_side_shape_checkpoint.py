"""Promote a validated, explicitly recorded queen side-shape checkpoint.

This is intentionally separate from ``publish_mission_trial.py``: that older
publisher prohibits any outline change, while this checkpoint has a reviewed
geometric scope and reports its source-fit tradeoff separately.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh, set_material
from write_finished_landmarks import write


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('variant')
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    variant = args.variant
    if Path(variant).name != variant or variant in ('', '.', '..'):
        raise ValueError('Expected a simple trial directory name')
    trial = ROOT / 'build' / 'queen-mission' / variant / 'queen.blend'
    # Geometry checkpoints are validated by the scoped side-shape validator.
    # It records the candidate blend digest as ``model_sha256``.  Older finish
    # reports instead describe the subsequently saved active blend, whose
    # compressed-file digest legitimately differs from the staged trial.
    validation_path = args.evidence / 'side-shape-validation.json'
    if not validation_path.is_file():
        validation_path = args.evidence / 'finish-validation.json'
    validation = json.loads(validation_path.read_text())
    assert validation['passed']
    # The general finish validator calls the active file ``source_sha256``;
    # the scoped geometry validator calls it ``model_sha256``.
    trial_sha = validation.get('model_sha256', validation.get('source_sha256'))
    assert trial_sha == sha256(trial)
    assert validation['variant'] == variant
    assert validation['camera_type'] == 'ORTHO'
    assert abs(validation['camera_elevation_degrees'] - 54) < 1e-4

    bpy.ops.wm.open_mainfile(filepath=str(trial), load_ui=False)
    scene = bpy.context.scene
    obj = editable_mesh(scene)
    settings = json.loads(scene['mission_material_config'])
    feature = settings.get('side_shape_study')
    assert feature and feature['config']['variant'] == variant
    checkpoint_sha = validation.get('shape_source_sha256', validation['source_sha256'])
    assert feature['source_sha256'] == checkpoint_sha
    wood = obj.data.materials[0]
    sampling = settings.get('render_sampling', {})
    scene.cycles.samples = sampling.get('samples', 64)
    scene.cycles.use_denoising = True
    scene.cycles.device = 'CPU'
    scene.render.use_persistent_data = True
    if 'adaptive' in sampling:
        scene.cycles.use_adaptive_sampling = sampling['adaptive']
    if 'light_tree' in sampling:
        scene.cycles.use_light_tree = sampling['light_tree']
    scene['mission_accepted_variant'] = variant
    bpy.context.preferences.filepaths.save_version = 0
    active = ROOT / 'models' / 'queen' / 'queen-rebuilt.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(active), compress=True)
    assert sha256(active) != checkpoint_sha
    write(scene, obj, json.loads((ROOT / 'assets/queen/finish-fit.json').read_text()))

    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == 'OPTIX'
        if any(device.use for device in prefs.devices):
            scene.cycles.device = 'GPU'
    except Exception as error:
        print('CPU fallback:', error)
    clay = bpy.data.materials.new('Side-shape inspection clay')
    clay.use_nodes = True
    bsdf = clay.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (.24, .26, .29, 1)
    bsdf.inputs['Roughness'].default_value = .32
    assets = ROOT / 'assets' / 'queen'
    for material, name in ((wood, 'queen-brown.png'), (clay, 'queen-matched.png')):
        set_material(scene, material)
        scene.render.filepath = str(assets / name)
        bpy.ops.render.render(write_still=True)
    camera = scene.camera
    camera.data.shift_x = camera.data.shift_y = 0
    camera.data.sensor_fit = 'VERTICAL'
    camera.data.ortho_scale = 6.6
    camera.location = (0, -16, 2.55)
    camera.rotation_euler = (Vector((0, 0, 2.55)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x = 600
    scene.render.resolution_y = 900
    for material, name in ((wood, 'queen-wood-profile.png'), (clay, 'queen-finished-profile.png')):
        set_material(scene, material)
        scene.render.filepath = str(assets / name)
        bpy.ops.render.render(write_still=True)
    report = {
        'passed': True,
        'variant': variant,
        'source_trial_sha256': sha256(trial),
        'active_model_sha256': sha256(active),
        'source_checkpoint_sha256': checkpoint_sha,
        'assets': [str(assets / name) for name in ('queen-brown.png', 'queen-matched.png', 'queen-wood-profile.png', 'queen-finished-profile.png')],
        'saved_model_camera_preserved': 'The active blend is saved before the temporary side camera is set.',
    }
    (args.evidence / 'publish-side-shape.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
