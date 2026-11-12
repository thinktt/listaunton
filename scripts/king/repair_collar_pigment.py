"""Blend inferred unlit wood into a bounded collar region, optionally bake it.

This is pigment inference, not source evidence. It never changes reference
pixels, geometry, accepted UVs, relief, camera or lights. The baked result is
an ordinary diffuse-color atlas used by the same real Principled material.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mission_trial import ROOT, gpu, run
from render_regions import controls, regenerate
from local_pigment_trial import mask_values
from validate_render_regions import check

ATTRIBUTE = 'Collar pigment repair'
TEMP_UV = 'Collar inferred wood sample'

def main(cfg):
    source = ROOT / cfg['source']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == cfg['source_sha256']
    tile_path = ROOT / cfg['generated_source']
    assert hashlib.sha256(tile_path.read_bytes()).hexdigest() == cfg['generated_source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    s = bpy.context.scene
    obs = controls(s)
    body = next(o for o in obs if 'body' in o.name)
    mat = body.data.materials[0]
    assert all(o.data.materials[0] == mat for o in obs)
    n, l = mat.node_tree.nodes, mat.node_tree.links
    bs = n['Principled BSDF']
    oldcolor = bs.inputs['Base Color'].links[0].from_socket
    original_nodes = set(n)
    old = bpy.data.images[s['king_pigment_image']]
    assert tuple(old.size) == (2048, 2048) and not old.is_float
    previous = np.array(old.pixels[:], dtype=np.float32).reshape(2048, 2048, 4)
    for ob in obs:
        assert not ob.data.attributes.get(ATTRIBUTE) and not ob.data.uv_layers.get(TEMP_UV)
        attr = ob.data.attributes.new(ATTRIBUTE, 'FLOAT', 'POINT')
        attr.data.foreach_set('value', mask_values(ob, cfg) * cfg['strength'])
        original = ob.data.uv_layers['Pigment atlas']
        uv = ob.data.uv_layers.new(name=TEMP_UV)
        for loop in ob.data.loops:
            u, v = original.data[loop.index].uv
            uv.data[loop.index].uv = ((u - .01) / .77, (v - .01) / .98)
        ob.data.uv_layers.active = original
        original.active_render = True
    coord = n.new('ShaderNodeUVMap'); coord.uv_map = TEMP_UV
    sampled = n.new('ShaderNodeTexImage'); sampled.name = 'Collar inferred unlit wood'
    tile = bpy.data.images.load(str(tile_path), check_existing=False); tile.pack()
    sampled.image = tile; sampled.extension = 'REPEAT'
    l.new(coord.outputs[0], sampled.inputs['Vector'])
    inferred = sampled.outputs['Color']
    grade = n.new('ShaderNodeMixRGB'); grade.blend_type = 'MULTIPLY'
    grade.inputs[0].default_value = 1
    grade.inputs[2].default_value = (*cfg.get('linear_multiplier', [1, 1, 1]), 1)
    l.new(inferred, grade.inputs[1]); inferred = grade.outputs[0]
    if cfg.get('mode') == 'neutral_residual':
        # Approximate neutral glare carried by the old pigment. Only subtract
        # a component supported by BOTH green/red and blue/red excess; this
        # preserves warmer wood and its fine chromatic/luminance variation.
        split = n.new('ShaderNodeSeparateColor'); split.mode = 'RGB'
        l.new(oldcolor, split.inputs['Color'])
        def math_node(op, a, b):
            node = n.new('ShaderNodeMath'); node.operation = op
            for sock, value in zip(node.inputs, (a, b)):
                if isinstance(value, (int, float)): sock.default_value = value
                else: l.new(value, sock)
            return node.outputs[0]
        residuals = []
        for channel, ratio in zip(('Green', 'Blue'), cfg['diffuse_ratios']):
            excess = math_node('SUBTRACT', split.outputs[channel], math_node('MULTIPLY', split.outputs['Red'], ratio))
            residuals.append(math_node('DIVIDE', excess, 1-ratio))
        residual = math_node('MAXIMUM', math_node('MINIMUM', *residuals), 0)
        combine = n.new('ShaderNodeCombineColor'); combine.mode = 'RGB'
        for channel in ('Red', 'Green', 'Blue'):
            cleaned = math_node('MAXIMUM', math_node('SUBTRACT', split.outputs[channel], residual), .0001)
            l.new(cleaned, combine.inputs[channel])
        inferred = combine.outputs['Color']
    attrnode = n.new('ShaderNodeAttribute'); attrnode.attribute_name = ATTRIBUTE
    mix = n.new('ShaderNodeMixRGB'); mix.name = 'Inferred collar pigment blend'
    l.new(attrnode.outputs['Fac'], mix.inputs[0]); l.new(oldcolor, mix.inputs[1])
    l.new(inferred, mix.inputs[2]); l.new(mix.outputs[0], bs.inputs['Base Color'])
    out = ROOT / 'build/king-mission' / cfg['variant']; out.mkdir(parents=True, exist_ok=True)
    report = dict(source_sha256=digest, geometry_camera_lights_relief_unchanged_by_construction=True,
                  inferred_not_observed=True, baked=bool(cfg.get('bake')), mask={k: cfg[k] for k in ['lower_fade', 'upper_fade', 'angular_fade', 'strength']})
    if cfg.get('bake'):
        output = next(x for x in n if x.type == 'OUTPUT_MATERIAL')
        emission = n.new('ShaderNodeEmission'); l.new(emission.outputs[0], output.inputs['Surface'])
        target = n.new('ShaderNodeTexImage'); target.name = 'Repaired collar pigment atlas'
        hidden = {o: o.hide_render for o in s.objects if o.type == 'MESH'}
        for ob in bpy.context.selected_objects: ob.select_set(False)
        for ob in hidden: ob.hide_render = ob not in obs
        for ob in obs: ob.select_set(True)
        bpy.context.view_layer.objects.active = body
        gpu(s); s.cycles.samples = 1; s.render.bake.margin = 6
        for node in n: node.select = False
        target.select = True; n.active = target
        mask = bpy.data.images.new('King collar pigment mask', width=2048, height=2048, alpha=False, float_buffer=True)
        mask.colorspace_settings.name = 'Non-Color'; target.image = mask
        l.new(attrnode.outputs['Fac'], emission.inputs['Color']); bpy.ops.object.bake(type='EMIT', use_clear=True)
        weights = np.array(mask.pixels[:], dtype=np.float32).reshape(2048, 2048, 4)[:, :, 0]
        atlas = bpy.data.images.new('King repaired pigment ' + Path(cfg['texture']).stem, width=2048, height=2048, alpha=False)
        atlas.colorspace_settings.name = 'sRGB'; target.image = atlas
        l.new(mix.outputs[0], emission.inputs['Color']); bpy.ops.object.bake(type='EMIT', use_clear=True)
        baked = np.array(atlas.pixels[:], dtype=np.float32).reshape(2048, 2048, 4)
        preserve = weights < 1e-5; preserve[:, 1618:] = True
        baked[preserve] = previous[preserve]
        atlas.pixels.foreach_set(baked.reshape(-1))
        path = ROOT / cfg['texture']; path.parent.mkdir(parents=True, exist_ok=True)
        atlas.filepath_raw = str(path); atlas.file_format = 'PNG'; atlas.save(); atlas.pack()
        l.new(bs.outputs['BSDF'], output.inputs['Surface'])
        for node in list(n):
            if node not in original_nodes and node != target: n.remove(node)
        final_uv = n.new('ShaderNodeUVMap'); final_uv.uv_map = 'Pigment atlas'
        l.new(final_uv.outputs[0], target.inputs['Vector']); l.new(target.outputs['Color'], bs.inputs['Base Color'])
        for ob in obs:
            ob.data.uv_layers.remove(ob.data.uv_layers[TEMP_UV])
            ob.data.attributes.remove(ob.data.attributes[ATTRIBUTE])
            ob.data.uv_layers.active = ob.data.uv_layers['Pigment atlas']; ob.data.uv_layers.active.active_render = True
        for ob, state in hidden.items(): ob.hide_render = state
        bpy.data.images.remove(mask)
        if tile.users == 0: bpy.data.images.remove(tile)
        s['king_pigment_image'] = atlas.name; s['king_pigment_atlas'] = cfg['texture']
        s['king_pigment_atlas_bakes_lighting'] = False
        np.savez_compressed(out / 'repair-mask.npz', weights=weights, preserved=preserve)
        report.update(changed_texels=int(np.any(baked != previous, 2).sum()), preserved_texels=int(preserve.sum()),
                      cross_atlas_exact=bool(np.array_equal(baked[:, 1618:], previous[:, 1618:])),
                      outside_mask_exact=bool(np.array_equal(baked[preserve], previous[preserve])), atlas_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        expected = np.array(atlas.pixels[:], dtype=np.float32); atlas_name = atlas.name
    regenerate(s); report['receivers'] = check(s)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'prepared.blend'))
    if cfg.get('bake'):
        bpy.ops.wm.open_mainfile(filepath=str(out / 'prepared.blend'), load_ui=False)
        actual = np.array(bpy.data.images[atlas_name].pixels[:], dtype=np.float32)
        report['packed_roundtrip_max_error'] = float(abs(expected - actual).max())
        assert report['packed_roundtrip_max_error'] == 0
    (out / 'repair.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    rendercfg = dict(cfg)
    rendercfg.update(source=(out / 'prepared.blend').relative_to(ROOT).as_posix(),
                     source_sha256=hashlib.sha256((out / 'prepared.blend').read_bytes()).hexdigest(),
                     original_source=cfg['source'], original_source_sha256=digest)
    run(rendercfg)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('config')
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))
