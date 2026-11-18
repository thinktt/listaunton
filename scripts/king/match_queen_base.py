"""Copy the queen's complete turned base into the current king in native units.

The king keeps its angular resolution, materials, upper geometry, UV seams and
logical profile coordinates. Run in Blender with the stage configuration after --.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from focused_reflections import target
from render_regions import controls, link, regenerate
from turn_chavet_profile import BASE_RINGS, coordinates, digest

SEGMENTS = 96
QUEEN_JOIN = BASE_RINGS[-1] + 1
KING_JOIN = len(BASE_RINGS)


def native_queen(path):
    with bpy.data.libraries.load(str(path), link=False) as (source, selected):
        selected.objects = [n for n in source.objects if n.startswith('01 Queen - continuous body')]
    queen, = selected.objects
    count = int(queen['ring_segments'])
    assert count % SEGMENTS == 0 and queen.get('mission_editable_control')
    bsdf = next(n for n in queen.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    varnish = {}
    for name in ('Roughness', 'Coat Roughness', 'Specular IOR Level'):
        assert not bsdf.inputs[name].is_linked
        varnish[name] = bsdf.inputs[name].default_value
    cage = coordinates(queen, count)[:QUEEN_JOIN + 1, ::count // SEGMENTS].astype(np.float32)
    return cage, varnish


def profile_rows(count):
    # Preserve the old king landmarks for texture and lighting. Intermediate
    # queen rings get fractional coordinates between their two king neighbors.
    base = np.interp(np.arange(QUEEN_JOIN), BASE_RINGS, np.arange(KING_JOIN))
    return np.r_[base, np.arange(KING_JOIN, count)]


def side_faces(rows):
    grid = np.arange(rows * SEGMENTS).reshape(rows, SEGMENTS)
    around = np.roll(grid, -1, axis=1)
    sides = np.stack([grid[:-1], around[:-1], around[1:], grid[1:]], axis=-1)
    return sides.reshape(-1, 4)


def split_face_uvs(values, old_count, rows):
    quads = values[:-2 * SEGMENTS].reshape(old_count - 1, SEGMENTS, 4, 2)
    bands = np.floor((rows[:-1] + rows[1:]) / 2).astype(int)
    t0 = (rows[:-1] - bands)[:, None, None, None]
    t1 = (rows[1:] - bands)[:, None, None, None]
    start = quads[bands][:, :, [0, 1]]
    end = quads[bands][:, :, [3, 2]]
    low = (1 - t0) * start + t0 * end
    high = (1 - t1) * start + t1 * end
    faces = np.concatenate([low, high[:, :, ::-1]], axis=2)
    return np.vstack([faces.reshape(-1, 2), values[-2 * SEGMENTS:]]).astype(np.float32)


def insert_native_base(body, queen_coordinates, size):
    old = body.data
    king_coordinates = coordinates(body, SEGMENTS).astype(np.float32)
    count = len(king_coordinates)
    rows = profile_rows(count)
    vertices = np.concatenate([queen_coordinates * size, king_coordinates[KING_JOIN + 1:]])
    assert len(vertices) == len(rows) and old.shape_keys is None and not len(body.vertex_groups)
    old_sides = side_faces(count)
    loops = np.empty(len(old.loops), dtype=np.int32)
    old.loops.foreach_get('vertex_index', loops)
    np.testing.assert_array_equal(loops[:-2*SEGMENTS], old_sides.ravel())
    np.testing.assert_array_equal(loops[-2*SEGMENTS:-SEGMENTS], np.arange(SEGMENTS)[::-1])
    np.testing.assert_array_equal(loops[-SEGMENTS:], np.arange((count-1)*SEGMENTS, count*SEGMENTS))
    faces = side_faces(len(rows)).tolist()
    faces.extend([list(reversed(range(SEGMENTS))), list(range((len(rows)-1)*SEGMENTS, len(rows)*SEGMENTS))])
    new = bpy.data.meshes.new('King with shared queen base')
    new.from_pydata(vertices.reshape(-1, 3).tolist(), [], faces)
    new.update()
    assert all(p.use_smooth and p.material_index == 0 for p in old.polygons)
    new.polygons.foreach_set('use_smooth', np.ones(len(new.polygons), dtype=bool))
    for mat in old.materials:
        new.materials.append(mat)
    for layer in old.uv_layers:
        uv = np.empty((len(old.loops), 2), dtype=np.float32)
        layer.data.foreach_get('uv', uv.ravel())
        data = split_face_uvs(uv, count, rows)
        new.uv_layers.new(name=layer.name).data.foreach_set('uv', data.ravel())
    new.uv_layers.active = new.uv_layers[old.uv_layers.active.name]
    for layer in old.uv_layers:
        if layer.active_render:
            new.uv_layers[layer.name].active_render = True
    lo = np.floor(rows).astype(int)
    hi = np.ceil(rows).astype(int)
    mix = (rows-lo)[:, None]
    for attr in old.attributes:
        if attr.data_type != 'FLOAT':
            continue
        assert attr.domain == 'POINT', attr.name
        values = np.empty((count, SEGMENTS), dtype=np.float32)
        attr.data.foreach_get('value', values.ravel())
        interpolated = ((1 - mix)*values[lo] + mix*values[hi]).astype(np.float32)
        new.attributes.new(attr.name, 'FLOAT', 'POINT').data.foreach_set('value', interpolated.ravel())
    name = old.name
    body.data = new
    assert old.users == 0
    bpy.data.meshes.remove(old)
    new.name = name


def apply_base_varnish(body, varnish, weight):
    # Other controls, including the cross, read zero for this body-only mask.
    mesh = body.data
    coord = np.empty(len(mesh.vertices), dtype=np.float32)
    mesh.attributes['King profile ring'].data.foreach_get('value', coord)
    fade = np.clip((coord - (KING_JOIN-1)) / 2, 0, 1)
    mask = weight * (1 - fade*fade*(3-2*fade))
    field = mesh.attributes.new('Queen base varnish 017', 'FLOAT', 'POINT')
    field.data.foreach_set('value', mask)
    tree = mesh.materials[0].node_tree
    bsdf = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    factor = tree.nodes.new('ShaderNodeAttribute')
    factor.attribute_name = field.name
    factor.label = 'Queen base varnish'
    factor.location = bsdf.location.x-700, bsdf.location.y-500
    for i, (name, value) in enumerate(varnish.items()):
        target = bsdf.inputs[name]
        prior = target.links[0].from_socket if target.is_linked else None
        mix = tree.nodes.new('ShaderNodeMixRGB')
        mix.name = 'Shared base '+name
        mix.label = 'Base '+name
        mix.location = bsdf.location.x-380, bsdf.location.y-280*(i+1)
        tree.links.new(factor.outputs['Fac'], mix.inputs[0])
        if prior:
            tree.links.new(prior, mix.inputs[1])
        else:
            mix.inputs[1].default_value = [target.default_value]*3+[1]
        mix.inputs[2].default_value = [value]*3+[1]
        tree.links.new(mix.outputs[0], target)


def light_shared_base(scene, reflectors):
    # The source photograph is the queen's level profile. Probe in a temporary
    # side camera and restore the original camera and frame before saving.
    saved_camera = scene.camera
    width, height = scene.render.resolution_x, scene.render.resolution_y
    data = bpy.data.cameras.new('Queen base measurement')
    camera = bpy.data.objects.new('Queen base measurement',data)
    scene.collection.objects.link(camera)
    camera.location = (0,-16,2.65)
    camera.rotation_euler = Vector((0,1,0)).to_track_quat('-Z','Y').to_euler()
    data.type, data.sensor_fit, data.ortho_scale = 'ORTHO','VERTICAL',6
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 600,900
    try:
        for item in reflectors:
            bpy.context.view_layer.update()
            x, z = item['side_xz']
            part, point, direction, _ = target(scene,300+150*x,450+150*(2.65-z))
            assert part.get('king_render_region') == item['receiver'], (item['name'],part.name)
            name = 'Shared base '+item['name']
            lamp = bpy.data.lights.new(name,'AREA')
            lamp.shape = 'DISK'
            lamp.size, lamp.energy = item['size'],item['energy']
            lamp.spread = math.radians(item.get('spread_degrees',35))
            lamp.color = (1,.82,.64)
            lamp.diffuse_factor, lamp.specular_factor = 0,1
            lamp.use_shadow = True
            light = bpy.data.objects.new(name,lamp)
            scene.collection.objects.link(light)
            light.visible_diffuse, light.visible_glossy = False,True
            light.location = point + item.get('distance',4) * direction
            light.rotation_euler = (-direction).to_track_quat('-Z','Y').to_euler()
            link(light,[part],name)
    finally:
        scene.camera = saved_camera
        scene.render.resolution_x, scene.render.resolution_y = width,height
        bpy.data.objects.remove(camera,do_unlink=True)
        bpy.data.cameras.remove(data)


def build(config_path):
    spec = json.loads(config_path.read_text(encoding='utf-8-sig'))
    source, donor = (ROOT / spec[k] for k in ('king_source','queen_source'))
    assert digest(source) == spec['king_sha256'] and digest(donor) == spec['queen_sha256']
    variant = spec['variant']
    assert Path(variant).name == variant and variant not in ('', '.', '..')
    out = ROOT / 'build/king-mission' / variant
    out.mkdir(parents=True, exist_ok=True)
    queen, varnish = native_queen(donor)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    body = next(o for o in controls(scene) if o.get('king_editable_control'))
    insert_native_base(body, queen, spec['uniform_size'])
    if spec.get('varnish_weight', 0):
        apply_base_varnish(body, varnish, spec['varnish_weight'])
    scene['king_mapped_profile_rings'] = True
    regenerate(scene)
    if spec.get('base_lights'):
        light_shared_base(scene,spec['base_lights'])
    scene['king_mission_variant'] = variant
    scene['king_queen_base_017'] = json.dumps(spec, sort_keys=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene.render.filepath = '//king-render.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'king.blend'), compress=True)
    assert digest(source) == spec['king_sha256'] and digest(donor) == spec['queen_sha256']
    print('Saved continuous king with', len(body.data.vertices), 'control vertices', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    build(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).config)
