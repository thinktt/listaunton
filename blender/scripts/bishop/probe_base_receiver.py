"""Test broader base reflection on an exact, isolated flare surface; never save."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from validate_render_receivers import array, VISIBILITY


def split_flare(scene, lower=.19, upper=.99):
    """Partition an existing exact receiver without changing any source loop."""
    rest = next(o for o in scene.objects if o.get('bishop_render_region') == 'body-rest')
    assert not any(o.get('bishop_render_region') == 'base-flare' for o in scene.objects)
    source = rest.data
    xyz = array(source.vertices, 'co', 3)
    vi = array(source.loops, 'vertex_index', dtype=np.int32)
    starts = array(source.polygons, 'loop_start', dtype=np.int32)
    counts = array(source.polygons, 'loop_total', dtype=np.int32)
    normals = array(source.corner_normals, 'vector', 3)
    centers = np.add.reduceat(xyz[vi], starts, axis=0) / counts[:, None]
    labels = (centers[:, 2] >= lower) & (centers[:, 2] < upper)
    report = []
    parts = []
    for chosen, name in [(~labels, 'body-rest'), (labels, 'base-flare')]:
        faces = np.flatnonzero(chosen)
        assert len(faces)
        loops = np.concatenate([np.arange(starts[f], starts[f]+counts[f]) for f in faces])
        vertices, inverse = np.unique(vi[loops], return_inverse=True)
        polygons = [v.tolist() for v in np.split(inverse, np.cumsum(counts[faces])[:-1])]
        me = bpy.data.meshes.new('Bishop receiver ' + name)
        me.from_pydata(xyz[vertices].tolist(), [], polygons)
        me.update()
        for material in source.materials:
            me.materials.append(material)
        for key, dtype in [('use_smooth', bool), ('material_index', np.int32)]:
            values = array(source.polygons, key, dtype=dtype)[faces]
            me.polygons.foreach_set(key, values)
            assert np.array_equal(array(me.polygons, key, dtype=dtype), values)
        for uv in source.uv_layers:
            layer = me.uv_layers.new(name=uv.name)
            values = array(uv.data, 'uv', 2)[loops]
            layer.data.foreach_set('uv', values.reshape(-1))
            layer.active_render = uv.active_render
            assert np.array_equal(array(layer.data, 'uv', 2), values)
        me.uv_layers.active_index = source.uv_layers.active_index
        for attr in source.attributes:
            # Custom normals are reconstructed below from the actual corner
            # vectors and checked, rather than copying compressed INT16 pairs.
            if attr.name.startswith('.') or attr.name == 'custom_normal' or attr.name in me.attributes:
                continue
            if attr.domain not in {'POINT', 'FACE', 'CORNER'}:
                continue
            assert attr.data_type in {'FLOAT', 'INT'}, (attr.name, attr.data_type)
            index = {'POINT': vertices, 'FACE': faces, 'CORNER': loops}[attr.domain]
            values = array(attr.data, 'value', dtype=np.int32 if attr.data_type == 'INT' else np.float32)[index]
            copied = me.attributes.new(attr.name, attr.data_type, attr.domain)
            copied.data.foreach_set('value', values)
            assert np.array_equal(array(copied.data, 'value', dtype=values.dtype), values)
        me.normals_split_custom_set(normals[loops].tolist())
        assert np.array_equal(array(me.vertices, 'co', 3), xyz[vertices])
        assert np.array_equal(vertices[array(me.loops, 'vertex_index', dtype=np.int32)], vi[loops])
        error = float(np.max(np.abs(array(me.corner_normals, 'vector', 3)-normals[loops])))
        assert error < 2e-4, error
        if name == 'body-rest':
            obj = rest
            obj.data = me
        else:
            obj = bpy.data.objects.new('Bishop receiver ' + name, me)
            for collection in rest.users_collection:
                collection.objects.link(obj)
            obj.matrix_world = rest.matrix_world.copy()
            for key in VISIBILITY:
                setattr(obj, key, getattr(rest, key))
            obj['bishop_render_region'] = name
            obj['bishop_control_name'] = rest['bishop_control_name']
        parts.append(obj)
        report.append(dict(name=name, faces=len(faces), vertices=len(vertices),
                           normal_max_component_error=error,
                           positions_uvs_materials_attributes_exact=True))
    assert sum(v['faces'] for v in report) == len(source.polygons)
    # Preserve the old illumination of each copied face before isolating one lamp.
    for lamp in [o for o in scene.objects if o.type == 'LIGHT']:
        collection = lamp.light_linking.receiver_collection
        if collection and rest.name in collection.objects and parts[1].name not in collection.objects:
            collection.objects.link(parts[1])
    return parts, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', default='history/bishop-mission-015/bishop-rebuilt.blend')
    p.add_argument('--out', default='build/bishop-mission/128-base-receiver-probe')
    p.add_argument('--samples', type=int, default=512)
    p.add_argument('--config', help='Optional probe variants and lower-flare z band.')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    source = ROOT/a.source
    out = ROOT/a.out
    assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
    out.mkdir(parents=True, exist_ok=True)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source_hash = sha(source)
    assert source_hash == 'dc3a11db2800b79bf45baee458d5b6a53a7602b3531137afe5db9b914a45cf07'
    variants = [
        dict(label='control', partition=False, isolated=False, size=.2, spread=3, power_factor=1),
        dict(label='partition-control', partition=True, isolated=False, size=.2, spread=3, power_factor=1),
        dict(label='isolated-control', partition=True, isolated=True, size=.2, spread=3, power_factor=1),
        dict(label='isolated-spread6', partition=True, isolated=True, size=.2, spread=6, power_factor=4),
        dict(label='isolated-spread12', partition=True, isolated=True, size=.2, spread=12, power_factor=16),
        dict(label='isolated-size04-spread6', partition=True, isolated=True, size=.4, spread=6, power_factor=4),
    ]
    spec = json.loads((ROOT/a.config).read_text()) if a.config else {}
    variants = spec.get('variants', variants)
    band = spec.get('z_band', [.19,.99])
    assert len(band) == 2 and 0 < band[0] < band[1] <= .99
    records = []
    for cfg in variants:
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
        s = bpy.context.scene
        lamp = bpy.data.objects['base reflection']
        assert lamp.type == 'LIGHT' and lamp.data.type == 'AREA' and lamp.data.shape == 'DISK'
        assert abs(lamp.data.energy-.1302) < 1e-6
        if cfg['partition']:
            parts, report = split_flare(s, *band)
            if cfg['isolated']:
                collection = bpy.data.collections.new('Diagnostic isolated base reflection')
                collection.objects.link(parts[1])
                lamp.light_linking.receiver_collection = collection
        else:
            report = []
        lamp.data.size = cfg['size']
        lamp.data.spread = math.radians(cfg['spread'])
        lamp.data.energy = .1302 * cfg['power_factor']
        s.render.resolution_percentage = 100
        s.render.use_border = True
        s.render.use_crop_to_border = False
        s.render.border_min_x = 240/1254
        s.render.border_max_x = 780/1254
        s.render.border_min_y = 1-1170/1254
        s.render.border_max_y = 1-825/1254
        s.render.image_settings.file_format = 'PNG'
        s.render.image_settings.color_mode = 'RGBA'
        s.render.image_settings.color_depth = '8'
        s.cycles.samples = a.samples
        s.cycles.use_adaptive_sampling = False
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = dev.type == 'OPTIX'
        s.cycles.device = 'GPU' if any(dev.use for dev in prefs.devices) else 'CPU'
        path = out/(cfg['label']+'.png')
        s.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append(dict(parameters=cfg, partition_check=report, render_sha256=sha(path)))
        print('BASE_RECEIVER_PROBE', cfg['label'], flush=True)
    assert sha(source) == source_hash
    (out/'manifest.json').write_text(json.dumps(dict(
        source=a.source, source_sha256=source_hash, source_unchanged=True,
        diagnostics_only=True, samples=a.samples, crop=[240,825,780,1170],
        z_band=band, variants=records, config=a.config,
        config_sha256=sha(ROOT/a.config) if a.config else None,
        note='Actual BSDF crop probes, unchanged geometry/color/normal inputs. Broader lamp illumination confined to exact lower flare faces. Powers are provisional, not fitted. Diagnostic scenes are not saved.'
    ), indent=2)+'\n', newline='\n')


if __name__ == '__main__':
    main()
