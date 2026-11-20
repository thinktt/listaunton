"""Validate listed thin groove reflectors, optionally with two polish-knot edits."""
import argparse,copy,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Euler,Vector
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,save_json,sha
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from validate_local_surface import surface,sampling
from mix_varnish import validate as validate_band

RAMP='Polish accessible to the lathe groove'

def ramps(body):
    return {n.name:{'interpolation':n.color_ramp.interpolation,'color_mode':n.color_ramp.color_mode,
                    'hue_interpolation':n.color_ramp.hue_interpolation,
                    'elements':[[e.position,*e.color] for e in n.color_ramp.elements]}
            for n in body.data.materials[0].node_tree.nodes if n.type=='VALTORGB'}

def run(cfg,target,out):
    source=ROOT/cfg['source'];assert sha(source)==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene)
    old=fingerprint(scene,body);old_graph=graph(surface(body),());old_sampling=sampling(scene)
    old_band=validate_band(scene,body);old_ramps=ramps(body);expected_ramps=copy.deepcopy(old_ramps)
    n=body.data.materials[0].node_tree.nodes
    old_finish=hashlib.sha256(n['Pawn varnish roughness'].image.packed_file.data).hexdigest()
    expected_positions={.18,.19};knots=cfg.get('groove_knots',[])
    assert not knots or (len(knots)==2 and {k['position'] for k in knots}==expected_positions)
    for spec in knots:
        assert 0<=spec['gain']<=1
        row=min(expected_ramps[RAMP]['elements'],key=lambda row:abs(row[0]-spec['position']))
        assert abs(row[0]-spec['position'])<1e-6
        row[1:]=[float(np.float32(spec['gain']))]*3+[1.]
    lights=[row for row in cfg['fitted_lights'] if row['energy']>.00001]
    assert 1<=len(lights)<=3 and len({row['name'] for row in lights})==len(lights)
    for light in lights:
        assert light['name']=='Inner groove ribbon' or light['name'] in {'Inner groove arc 535','Inner groove arc 550','Inner groove arc 565','Inner groove arc 595'}
        assert 0<light['size_y']<=.02 and 0<light['energy']<.1
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);new=fingerprint(scene,body)
    for key in ('evaluated_mesh_normals_uv_sha256','world','ray_depth','prior_finish_inputs','other_packed_images'):
        assert old[key]==new[key],key
    assert set(new['lights'])==set(old['lights'])|{row['name'] for row in lights}
    for name,value in old['lights'].items():assert new['lights'][name]==value,'Changed original light: '+name
    for light in lights:
        lamp=scene.objects[light['name']];d=lamp.data
        assert d.type=='AREA' and d.shape=='ELLIPSE' and not lamp.visible_diffuse and lamp.visible_glossy
        assert np.allclose(lamp.location,light['position'],atol=1e-7,rtol=0)
        expected=Euler(light['rotation'],'XYZ').to_matrix()
        assert np.allclose(lamp.matrix_world.to_3x3(),expected,atol=1e-7,rtol=0)
        for key,want in [('energy',light['energy']),('size',light['size']),('size_y',light['size_y']),('spread',math.radians(light['spread']))]:
            assert math.isclose(getattr(d,key),want,rel_tol=1e-6,abs_tol=1e-8),key
        assert np.allclose(d.color,light['color'],atol=1e-7,rtol=0)
    assert graph(surface(body),())==old_graph,'Shader wiring, image data or node inputs changed'
    assert ramps(body)==expected_ramps,'Unexpected color-ramp edit'
    n=body.data.materials[0].node_tree.nodes
    assert hashlib.sha256(n['Pawn varnish roughness'].image.packed_file.data).hexdigest()==old_finish
    assert sampling(scene)==old_sampling and old_sampling['samples']==cfg['samples']==512
    assert validate_band(scene,body)==old_band
    assert not scene.render.use_border and scene.render.resolution_percentage==100
    report={'passed':True,'source_sha256':sha(source),'model_sha256':sha(target),
            'camera_above_board':54,'mesh_normals_uv_sha256':new['evaluated_mesh_normals_uv_sha256'],
            'geometry_normals_uv_unchanged':True,'original_lights_unchanged':len(old['lights']),
            'light_count':len(new['lights']),'new_reflectors':{row['name']:new['lights'][row['name']] for row in lights},
            'groove_ramp_before':old_ramps[RAMP],'groove_ramp_after':expected_ramps[RAMP],
            'all_material_settings_preserved':not bool(knots),
            'other_ramps_and_full_shader_graph_preserved':True,'all_surface_map_pixels_preserved':True,
            'finish_sha256':old_finish,'other_packed_images':new['other_packed_images'],
            'world_and_ray_depth_preserved':True,'matte_band':old_band,'sampling':old_sampling}
    save_json(out,report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')),ROOT/a.model,ROOT/a.output)
