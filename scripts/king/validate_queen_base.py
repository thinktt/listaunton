"""Check the shared base on reopened king and queen meshes at their render levels."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_base_light_checkpoint import graph, snapshot
from check_local_finish import remaining_settings
from check_socket_checkpoint import extra
from match_queen_base import KING_JOIN, QUEEN_JOIN, ROOT, SEGMENTS, coordinates, digest
from render_regions import controls


def section(body):
    for modifier in body.modifiers:
        if modifier.type == 'SUBSURF':
            modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    obj = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = obj.to_mesh()
    data = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get('co', data.ravel())
    obj.to_mesh_clear()
    pts = data[(np.abs(data[:, 1]) < 1e-7) & (data[:, 0] > .3) & (data[:, 2] < 1.4)][:, [0, 2]]
    pts = pts[np.lexsort((pts[:, 0], pts[:, 1]))].astype(np.float64)
    return pts


def cropped(profile):
    z0, z1 = .006, 1.225
    left, right = np.interp([z0,z1], profile[:,1], profile[:,0])
    return np.vstack([[left,z0], profile[(profile[:,1] > z0) & (profile[:,1] < z1)], [right,z1]])


def profile_error(a, b):
    # Sample each polygonal meridian densely and measure to segments of the
    # other one. Normal distance remains well defined at the near-flat bevel.
    def directed(curve, target):
        delta = np.diff(target, axis=0)
        lengths = np.sum(delta*delta, axis=1)
        assert np.min(lengths) > 0
        worst = 0.
        for start, stop in zip(curve, curve[1:]):
            count = max(2, int(np.ceil(np.linalg.norm(stop-start)/.0005))+1)
            samples = np.linspace(start, stop, count)
            dist = samples[:,None,:] - target[None,:-1,:]
            u = np.clip(np.sum(dist*delta, axis=2)/lengths, 0, 1)
            error = np.linalg.norm(dist - u[:,:,None]*delta, axis=2)
            worst = max(worst, float(error.min(1).max()))
        return worst
    a, b = cropped(a), cropped(b)
    return max(directed(a,b), directed(b,a))


def dimensions(profile):
    def band(lo, hi):
        return profile[(profile[:,1] >= lo) & (profile[:,1] <= hi)]
    groove, flare = band(.19,.315), band(.302,.43)
    groove_height = float(groove[np.argmin(groove[:,0]),1])
    foot = band(0,groove_height)
    return dict(foot_diameter=float(2*foot[:,0].max()),
                groove_center_height=groove_height,
                flare_crest_height=float(flare[np.argmax(flare[:,0]),1]),
                socket_diameter_at_z_1=float(2*np.interp(1.,profile[:,1],profile[:,0])))


def king_data(path):
    scene, lights, regions = snapshot(path)
    body = next(o for o in controls(bpy.context.scene) if o.get('king_editable_control'))
    mesh = body.data
    uvs, fields = {}, {}
    for layer in mesh.uv_layers:
        v = np.empty((len(mesh.loops),2),dtype=np.float32)
        layer.data.foreach_get('uv',v.ravel())
        uvs[layer.name] = v
    for field in mesh.attributes:
        if field.data_type == 'FLOAT' and field.domain == 'POINT':
            v = np.empty(len(mesh.vertices),dtype=np.float32)
            field.data.foreach_get('value',v)
            fields[field.name] = v.reshape(-1,SEGMENTS)
    return (scene, lights, regions, coordinates(body,SEGMENTS), fields, uvs,
            section(body), extra()['all_packed_images'], remaining_settings(), body.name)


def unwrap_varnish(body, donor, weight, fields):
    tree = body.data.materials[0].node_tree
    bsdf = next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    mask_node = None
    for name, target in donor.items():
        socket = bsdf.inputs[name]
        mix = socket.links[0].from_node
        assert mix.name == 'Shared base '+name and mix.blend_type == 'MIX'
        assert list(mix.inputs[2].default_value[:3]) == [target]*3
        factor = mix.inputs[0].links[0].from_node
        assert factor.attribute_name == 'Queen base varnish 017'
        assert mask_node is None or mask_node == factor
        mask_node = factor
        prior = mix.inputs[1].links[0].from_socket if mix.inputs[1].is_linked else None
        if prior is None:
            assert list(mix.inputs[1].default_value[:3]) == [socket.default_value]*3
        tree.nodes.remove(mix)
        if prior is not None:
            tree.links.new(prior,socket)
    tree.nodes.remove(mask_node)
    rings = fields['King profile ring']
    t = np.clip((rings-27)/2,0,1)
    np.testing.assert_allclose(fields.pop('Queen base varnish 017'), weight*(1-t*t*(3-2*t)), atol=1e-7)


def main(config, output):
    spec = json.loads(config.read_text(encoding='utf-8-sig'))
    original, donor = (ROOT/spec[k] for k in ('king_source','queen_source'))
    candidate = ROOT/'build/king-mission'/spec['variant']/'king.blend'
    saved = digest(candidate)
    assert digest(original)==spec['king_sha256'] and digest(donor)==spec['queen_sha256']
    # Only link the editable donor object into a fresh scene for subdivision.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(donor),link=False) as (src, loaded):
        loaded.objects=[n for n in src.objects if n.startswith('01 Queen - continuous body')]
    queen, = loaded.objects
    bpy.context.scene.collection.objects.link(queen)
    queen.hide_viewport=False
    queen.hide_set(False)
    queen_profile = section(queen)
    queen_cage = coordinates(queen, int(queen['ring_segments']))
    qbsdf = next(n for n in queen.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    finish = {k:qbsdf.inputs[k].default_value for k in ('Roughness','Coat Roughness','Specular IOR Level')}

    old, old_lamps, old_receivers, old_co, old_fields, old_uv, old_meridian, old_images, old_settings, old_name = king_data(original)
    new, lamps, receivers, points, fields, uvs, meridian, images, settings, name = king_data(candidate)
    assert name == old_name and images == old_images
    routes = receivers['lightRoutes'].copy()
    for item in spec.get('base_lights',[]):
        key = 'Shared base '+item['name']
        light = bpy.data.objects[key]
        assert light.data.type=='AREA' and light.data.use_shadow and light.visible_glossy and not light.visible_diffuse
        assert abs(light.data.energy-item['energy']) < .001 and abs(light.data.size-item['size']) < .0001
        assert list(routes.pop(key)) == [item['receiver']]
        assert settings['shadows'].pop(key)
        del lamps[key]
    assert lamps == old_lamps and routes == old_receivers['lightRoutes'] and settings == old_settings
    assert receivers['receiverCount'] == 9 and receivers['normalMaxError'] == 0
    assert old_uv.keys() == uvs.keys()
    body = bpy.data.objects[name]
    if spec.get('varnish_weight',0):
        for o in controls(bpy.context.scene):
            if o != body:
                assert 'Queen base varnish 017' not in o.data.attributes
        unwrap_varnish(body,finish,spec['varnish_weight'],fields)
        for o in controls(bpy.context.scene):
            new['objects'][o.name]['material']=graph(o.data.materials[0].node_tree)
    assert old_fields.keys() == fields.keys()
    # Float UV/finish attributes and the original crown/cross are independently
    # checked. Ignore only the body arrays whose length changes with new loops.
    for state in (old,new):
        for key in ('positions','faces','uv','attributes'):
            del state['objects'][name][key]
    assert old == new, 'Unexpected camera, cross, shader, world or upper scene edit'
    source_rows = fields['King profile ring'][:,0]
    assert np.all(np.diff(source_rows)>0)
    indexed = np.searchsorted(source_rows,np.arange(len(old_co)))
    for k, value in old_fields.items():
        np.testing.assert_array_equal(fields[k][indexed],value)
    for k,value in old_uv.items():
        a=value[:-2*SEGMENTS].reshape(-1,SEGMENTS,4,2)
        b=uvs[k][:-2*SEGMENTS].reshape(-1,SEGMENTS,4,2)
        np.testing.assert_array_equal(a[:,:,:2], b[indexed[:-1],:,:2])
        np.testing.assert_array_equal(a[:,:,2:], b[indexed[1:]-1,:,2:])
        np.testing.assert_array_equal(value[-2*SEGMENTS:],uvs[k][-2*SEGMENTS:])
    native = queen_cage[:QUEEN_JOIN+1,::queen_cage.shape[1]//SEGMENTS].astype(np.float32)
    np.testing.assert_array_equal(points[:len(native)], native*spec['uniform_size'])
    np.testing.assert_array_equal(points[len(native):], old_co[KING_JOIN+1:])
    base_metrics={k:dimensions(p) for k,p in [('queen',queen_profile),('previous_king',old_meridian),('revised_king',meridian)]}
    old_error = profile_error(old_meridian,queen_profile)
    new_error = profile_error(meridian/spec['uniform_size'],queen_profile)
    assert new_error < .005 and new_error < old_error/4, (old_error,new_error)
    assert saved==digest(candidate) and digest(original)==spec['king_sha256'] and digest(donor)==spec['queen_sha256']
    report=dict(model_sha256=saved, queen_sha256=spec['queen_sha256'], previous_king_sha256=spec['king_sha256'],
                base_rings=QUEEN_JOIN, adjoining_stem_support_rings=1, extra_control_rings=len(points)-len(old_co),
                donor_control_coordinates_exact=True, upper_controls_exact=True, original_uvs_and_float_landmarks_exact=True,
                camera_cross_previous_lights_other_shaders_packed_textures_preserved=True, exact_receivers=receivers['receiverCount'],
                receiver_normal_error=receivers['normalMaxError'], dimensions=base_metrics,
                max_profile_distance_model_units=dict(previous=old_error,revised_at_donor_size=new_error),
                tested_height_model_units=[.006,1.225], base_varnish=dict(weight=spec.get('varnish_weight',0),queen=finish),
                base_reflectors=spec.get('base_lights',[]))
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('config',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(a.config,a.output)
