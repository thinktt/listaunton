"""Fit the complete queen/king turning below the bishop's own mitre and stem.

From the repository root, run in Blender with -- CASE [--samples N]. The
configuration pins the three editable sources and uses native model units.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from render_regions import BODY, BUTTON, partition_socket
from validate_render_receivers import array

CONFIG = 'docs/bishop-mission/iteration-025/turning.json'
SEGMENTS = 128
# Corresponding landmarks only transport the bishop's UVs and coverage. All 40
# geometry pairs come directly from the donor, including rings between anchors.
DONOR_ANCHORS = [0, 1, 2, 5, 7, 11, 17, 23, 26, 29, 31, 33, 35, 38, 39]
BISHOP_ANCHORS = [0, 1, 2, 4, 7, 10, 13, 17, 20, 24, 25, 27, 28, 31, 32]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_source(spec, key):
    path = ROOT / spec[key]['file']
    assert digest(path) == spec[key]['sha256'], (key, path)
    return path


def control_rings(obj, count=SEGMENTS):
    return array(obj.data.vertices, 'co', 3).reshape(-1, count, 3)


def meridian(rings):
    return np.stack([np.linalg.norm(rings[:, 0, :2], axis=1), rings[:, 0, 2]], axis=1).astype(float)


def donor_controls(spec):
    sections = []
    for key, prefix, n in [('queen', '01 Queen - continuous body', 192), ('king', 'King - continuous turned body', 96)]:
        bpy.ops.wm.open_mainfile(filepath=str(read_source(spec, key)), load_ui=False)
        obj, = [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]
        vertices = control_rings(obj, n)[:40]
        section = meridian(vertices)
        np.testing.assert_allclose(np.linalg.norm(vertices[:, :, :2], axis=2), np.broadcast_to(section[:, :1], (40, n)), atol=4e-7)
        np.testing.assert_allclose(vertices[:, :, 2], np.broadcast_to(section[:, 1:], (40, n)), atol=1e-7)
        sections.append(section)
    np.testing.assert_allclose(*sections, rtol=0, atol=2e-7)
    return sections[0]


def atlas_rows(old, donor):
    rows = np.arange(40, dtype=float)
    for da, db, ba, bb in zip(DONOR_ANCHORS, DONOR_ANCHORS[1:], BISHOP_ANCHORS, BISHOP_ANCHORS[1:]):
        def distance(section):
            dist = np.r_[0., np.linalg.norm(np.diff(section, axis=0), axis=1).cumsum()]
            return dist / dist[-1]
        rows[da:db+1] = np.interp(distance(donor[da:db+1]), distance(old[ba:bb+1]), np.arange(ba, bb+1))
    return np.r_[rows, np.arange(33, len(old))]


def fitted_profile(old, donor, case):
    base = donor.copy() * case['donor_scale']
    base[:, 1] += old[0, 1] - base[0, 1]
    upper = old[33:].copy()
    # Respect the donor's first stem support. Blend its radius and height into
    # the bishop's own taper before reaching the underside of the first collar.
    t = np.clip((upper[:, 1] - old[32, 1]) / (old[39, 1] - old[32, 1]), 0, 1)
    weight = 1 - t * t * (3 - 2*t)
    upper[:, 0] += (base[-1, 0] - old[32, 0]) * weight
    upper[:, 1] += (base[-1, 1] - old[32, 1])*weight - case['collar_drop']*(1-weight)
    head_ramp = np.interp(np.arange(33, len(old)), [62, 65], [0, 1])
    upper[:, 1] -= (case['head_drop'] - case['collar_drop']) * head_ramp
    for index, (dz, dr) in case.get('upper_edits', {}).items():
        assert 33 <= int(index) < len(old)
        upper[int(index)-33] += [dr, dz]
    return np.vstack([base, upper])


def mapped_uv(uv, rows, count):
    sides = uv[:-2*SEGMENTS].reshape(count-1, SEGMENTS, 4, 2)
    # Every seam between bands must occur at an actual new ring. Splitting a
    # band preserves its angular seam by interpolating each face corner alone.
    seam = np.max(np.abs(sides[1:, :, :2] - sides[:-1, :, 2:][:, :, ::-1]), axis=(1,2,3))
    for row in np.flatnonzero(seam > 2e-6) + 1:
        assert np.any(np.isclose(rows, row, atol=1e-7)), ('UV seam lost', row)
    def edge(t, band):
        frac = (t-band)[:, None, None, None]
        return (1-frac)*sides[band, :, :2] + frac*sides[band, :, 2:][:, :, ::-1]
    a = rows[:-1]
    b = rows[1:]
    lo = edge(a, np.floor(a).astype(int))
    hi = edge(b, np.ceil(b).astype(int)-1)
    return np.vstack([np.concatenate([lo, hi[:, :, ::-1]], axis=2).reshape(-1,2), uv[-2*SEGMENTS:]]).astype(np.float32)


def replace_mesh(obj, sections, rows, old_rings):
    old = obj.data
    assert not obj.vertex_groups and old.shape_keys is None
    source_rz = meridian(old_rings)
    # Keep the bishop's actual angular samples, including original upper cage.
    angles = old_rings[32, :, :2].astype(float) / source_rz[32, 0]
    out = np.empty((len(sections), SEGMENTS, 3), dtype=np.float32)
    out[:, :, :2] = sections[:, None, :1] * angles[None]
    out[:, :, 2] = sections[:, None, 1]
    out[40:, :, :2] = old_rings[33:, :, :2] * (sections[40:, 0]/source_rz[33:, 0])[:, None, None]
    grid = np.arange(len(out)*SEGMENTS).reshape(-1, SEGMENTS)
    nxt = np.roll(grid, -1, axis=1)
    faces = np.stack([grid[:-1], nxt[:-1], nxt[1:], grid[1:]], axis=-1).reshape(-1,4).tolist()
    faces.extend([list(reversed(grid[0].tolist())), grid[-1].tolist()])
    mesh = bpy.data.meshes.new('Bishop with shared turned base')
    mesh.from_pydata(out.reshape(-1,3).tolist(), [], faces)
    mesh.update()
    assert all(p.use_smooth and p.material_index == 0 for p in old.polygons)
    mesh.polygons.foreach_set('use_smooth', np.ones(len(mesh.polygons), dtype=bool))
    for mat in old.materials:
        mesh.materials.append(mat)
    for layer in old.uv_layers:
        values = mapped_uv(array(layer.data, 'uv', 2), rows, len(old_rings))
        new = mesh.uv_layers.new(name=layer.name)
        new.data.foreach_set('uv', values.ravel())
    mesh.uv_layers.active_index = old.uv_layers.active_index
    for layer in old.uv_layers:
        mesh.uv_layers[layer.name].active_render = layer.active_render
    for attr in old.attributes:
        if attr.data_type == 'FLOAT':
            assert attr.domain == 'POINT'
            values = array(attr.data, 'value', 1).reshape(-1, SEGMENTS)
            t = (rows - np.floor(rows))[:, None]
            vals = (1-t)*values[np.floor(rows).astype(int)] + t*values[np.ceil(rows).astype(int)]
            mesh.attributes.new(attr.name, 'FLOAT', 'POINT').data.foreach_set('value', vals.astype(np.float32).ravel())
    name = old.name
    obj.data = mesh
    assert old.users == 0
    bpy.data.meshes.remove(old)
    mesh.name = name


def remove_receivers(scene):
    parts = [o for o in scene.objects if o.get('bishop_render_region')]
    names = {p.name for p in parts}
    memberships = {c.name: [o.name for o in c.objects] for c in bpy.data.collections if any(p.name in names for p in c.objects)}
    for obj in parts:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(mesh)
    for collection in list(bpy.data.collections):
        if collection.name.startswith('Bishop exact render regions') and not collection.objects and not collection.children:
            bpy.data.collections.remove(collection)
    bpy.data.objects[BODY].hide_render = False
    return memberships


def restore_receivers(scene, memberships, old, sections):
    cfg = json.loads(scene['bishop_receiver_trial'])
    # Move the socket-specific lighting region to the corresponding height on
    # the new socket. Membership still exactly partitions the evaluated mesh.
    ba, da = BISHOP_ANCHORS[3:], DONOR_ANCHORS[3:]
    band = np.interp(cfg['socket_z_band'], old[ba, 1], sections[da, 1]).tolist()
    restore_receiver_band(scene, memberships, band)


def restore_receiver_band(scene, memberships, band):
    cfg = json.loads(scene['bishop_receiver_trial'])
    cfg['socket_z_band'] = band
    scene['bishop_receiver_trial'] = json.dumps(cfg, sort_keys=True)
    partition_socket(scene, *cfg['socket_z_band'])
    for name, names in memberships.items():
        collection = bpy.data.collections[name]
        for obj in list(collection.objects):
            if obj.name not in names:
                collection.objects.unlink(obj)
        for objname in names:
            if objname not in collection.objects:
                collection.objects.link(bpy.data.objects[objname])


def setup_device(scene):
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    scene.cycles.device = 'GPU' if any(d.use for d in prefs.devices) else 'CPU'


def render_saved(out, samples):
    bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'), load_ui=False)
    scene = bpy.context.scene
    setup_device(scene)
    scene.cycles.samples = samples
    scene.render.filepath = str(out/'wood.png')
    bpy.ops.render.render(write_still=True)
    mat = bpy.data.materials.new('Geometry comparison neutral')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    balance = json.loads(scene.get('bishop_diffuse_balance','{}')).get('diffuse_light_factor',1)
    bsdf.inputs['Base Color'].default_value = (.28/balance,.30/balance,.34/balance,1)
    bsdf.inputs['Roughness'].default_value = .3
    for obj in scene.objects:
        if obj.type=='MESH' and not obj.hide_render:
            obj.data.materials.clear()
            obj.data.materials.append(mat)
    scene.cycles.samples = min(64, samples)
    scene.render.filepath = str(out/'neutral.png')
    bpy.ops.render.render(write_still=True)


def build(spec, case_name, config, samples):
    donor = donor_controls(spec)
    source = read_source(spec, 'bishop')
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    body = bpy.data.objects[BODY]
    case = spec['cases'][case_name]
    profile = json.loads((ROOT/spec['profile']).read_text())
    factor = 1254/300/json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())['scale']/profile['scale']
    co = math.cos(math.radians(54))
    rings = control_rings(body)
    old = meridian(rings)
    sections = fitted_profile(old, donor, case)
    rows = atlas_rows(old, donor)
    memberships = remove_receivers(scene)
    replace_mesh(body, sections, rows, rings)
    button = bpy.data.objects[BUTTON]
    verts = array(button.data.vertices, 'co', 3)
    cap_weights = np.array([0,0,0,0,0,0,0,0,.12,.55,.93,1])
    cap_lowering = case['head_drop'] + case.get('cap_drop',0)*cap_weights
    verts[:, 2] -= np.repeat(cap_lowering, SEGMENTS)
    button.data.vertices.foreach_set('co', verts.ravel())
    button.data.update()
    cutter = next(m.object for m in body.modifiers if m.type=='BOOLEAN')
    cutter.location.z -= case['head_drop']
    bpy.context.view_layer.update()
    restore_receivers(scene, memberships, old, sections)
    # Keep the source units for anatomy checks. Record the actual cage as the
    # current profile and the former top translation for local landmark probes.
    offset = case['head_drop']*co/factor
    profile['profile'] = np.stack([sections[:,0]/factor, profile['y0']-sections[:,1]*co/factor], axis=1).tolist()
    for pair, dz in zip(profile['finial']['profile'], cap_lowering):
        pair[1] += float(dz)*co/factor
    for key in ['head_cap_axis_y','button_bottom_axis_y']:
        profile['head_button_join'][key] += offset
    profile['slit']['bottom_center_y'] += offset
    for key in ['mission_shape_refit', 'mission_base_curvature', 'mission_geometry']:
        profile.pop(key, None)
    profile['revision'] = 'shared-turning-'+case_name
    profile['shared_turning'] = {'config':config, 'case':case_name, 'upper_axis_offset':offset, 'upper_index_offset':7}
    if 'bishop_shape_refit' in scene:
        del scene['bishop_shape_refit']
    scene['bishop_shared_turning'] = json.dumps(profile['shared_turning'], sort_keys=True)
    out = ROOT/'build/bishop-mission'/('turning-'+case_name)
    out.mkdir(parents=True, exist_ok=True)
    (out/'profile.json').write_text(json.dumps(profile, indent=2)+'\n')
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_percentage = 100
    scene.render.use_border = scene.render.use_crop_to_border = False
    scene.render.filepath = '//render.png'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
    print('BISHOP_SHARED_TURNING_SAVED', case_name, flush=True)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', nargs='+')
    parser.add_argument('--config', default=CONFIG)
    parser.add_argument('--samples', type=int, default=48)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec = json.loads((ROOT/args.config).read_text())
    for name in args.case:
        out = build(spec, name, args.config, args.samples)
        render_saved(out, args.samples)
        print('BISHOP_SHARED_TURNING_RENDERED', name, flush=True)
