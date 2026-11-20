"""Rebuild the project's 008 geometry and wood finish in a single editable scene."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bpy
import numpy as np

HERE = Path(__file__).resolve().parent


def read(relative):
    return json.loads((HERE / relative).read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def material_state(scene):
    obj = scene.objects['Knight | turned pedestal']
    links = obj.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].links
    return links[0].from_node


def scalar_values(attribute):
    values = np.empty(len(attribute.data), np.float32)
    attribute.data.foreach_get('value', values)
    return values


def scene_state(scene):
    from combine_carvings import evaluated_digest
    geometry, polish, lights = {}, {}, {}
    for obj in scene.objects:
        if obj.type == 'MESH':
            geometry[obj.name] = evaluated_digest(obj)
            coverage = obj.data.attributes.get('Knight varnish coverage')
            if coverage:
                polish[obj.name] = sha256(scalar_values(coverage).tobytes()).hexdigest()
        elif obj.type == 'LIGHT':
            light = obj.data
            receiver = obj.light_linking.receiver_collection
            lights[obj.name] = {
                'receivers': sorted(other.name for other in receiver.all_objects) if receiver else [],
                'shape': getattr(light, 'shape', ''),
                'numeric': [float(light.energy), *light.color, getattr(light, 'size', 0.),
                            getattr(light, 'size_y', 0.), getattr(light, 'spread', 0.),
                            *np.asarray(obj.matrix_world).ravel().tolist()]}
    cam = scene.camera
    return {'geometry': geometry, 'polish': polish, 'lights': lights,
            'pigment': sha256(material_state(scene).image.packed_file.data).hexdigest(),
            'camera': [cam.data.type, cam.data.ortho_scale, cam.data.shift_x, cam.data.shift_y,
                       *np.asarray(cam.matrix_world).ravel().tolist()]}


def open_scene(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    return bpy.context.scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path, help='Checkout containing scripts/knight')
    parser.add_argument('parent', type=Path, help='Unmodified 16A Blender scene')
    parser.add_argument('pigment', type=Path, help='Checkpoint 008 walnut atlas')
    parser.add_argument('--variant', choices=['042', '043'], default='043')
    parser.add_argument('--compare', type=Path, help='Reopen a frozen or published scene to verify attributes and studio')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--out', type=Path, help='Optional new path to save the editable rebuild')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    sys.path[:0] = [str(HERE), str(args.project.resolve()/'scripts/knight'), str(HERE/'mission008-neck'),
                    str(HERE/'mission008-mane'), str(HERE/'mane-finish')]
    import geometry
    import neck
    import turn_platform
    import apply_component
    from mission_scene import configure_render, save_model

    parent, pigment = args.parent.resolve(), args.pigment.resolve()
    level = read('level/platform.json')
    assert digest(parent) == level['source']
    assert digest(pigment) == read('cove/grade.json')['pigment_sha256']
    scene = open_scene(parent)
    node = material_state(scene)
    prior = node.image
    assert sha256(prior.packed_file.data).hexdigest() == level['atlas']
    geometry.carve(scene, registered=True)
    neck.apply(scene, 2)
    pedestal = scene.objects['Knight | turned pedestal']
    turn_platform.turn(pedestal, level['profile_r_z'])
    varnish = pedestal.data.attributes['Knight varnish coverage']
    values = scalar_values(varnish).reshape(31, 64)
    values[22:] *= np.asarray(level['upper_ring_polish_factors'])[:, None]
    varnish.data.foreach_set('value', values.ravel())
    pedestal.data.update()
    image = bpy.data.images.load(str(pigment), check_existing=False)
    image.name = 'Knight | walnut and turned platform'
    image.colorspace_settings.name = 'sRGB'
    raw = pigment.read_bytes()
    image.pack(data=raw, data_len=len(raw))
    node.image = image
    if prior.users == 0:
        bpy.data.images.remove(prior)
    if args.variant == '043':
        apply_component.apply(scene, HERE/'mane-finish')
        for side, factor in [('left', .50), ('right', .30)]:
            strip = scene.objects[f'Walnut | {side} collar strip']
            assert {obj.name for obj in strip.light_linking.receiver_collection.all_objects} == {pedestal.name}
            strip.data.energy *= factor
    configure_render(scene, 144)
    bpy.context.view_layer.update()
    if args.out:
        out = args.out.resolve()
        if out.exists():
            raise ValueError(f'Output already exists: {out}')
        save_model(scene, out)
        scene = open_scene(out)
    actual = scene_state(scene)
    assert actual['geometry'] == read('level/combination.json')['geometry_sha256_by_part']
    assert actual['pigment'] == digest(pigment)
    proof = {'blender': bpy.app.version_string, 'variant': args.variant, 'parent_sha256': digest(parent),
             'nine_geometry_fingerprints_match': len(actual['geometry']) == 9, 'packed_pigment_sha256': actual['pigment']}
    if args.compare:
        reference = args.compare.resolve()
        target = scene_state(open_scene(reference))
        for key in ('geometry', 'polish', 'pigment', 'camera'):
            assert actual[key] == target[key], key
        assert actual['lights'].keys() == target['lights'].keys()
        max_error = 0.
        for name, lamp in actual['lights'].items():
            expected = target['lights'][name]
            assert (lamp['shape'], lamp['receivers']) == (expected['shape'], expected['receivers']), name
            difference = np.abs(np.asarray(lamp['numeric']) - expected['numeric']).max()
            max_error = max(max_error, float(difference))
            assert difference < 5.e-5, (name, difference)
        proof.update({'compared_sha256': digest(reference), 'identical_local_polish_attributes': sorted(actual['polish']),
                      'identical_fixed_camera': True, 'studio_light_count': len(actual['lights']),
                      'all_light_shapes_and_receiver_sets_match': True, 'max_light_numeric_difference': max_error})
    if args.report:
        args.report.write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(proof, indent=2), flush=True)


if __name__ == '__main__':
    main()
