"""Verify a localized finish/normal-map edit with the rest of the pawn held."""
import argparse,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,control,fixed_camera,save_json,sha
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from validate_collar_finish import pixels
from mix_varnish import validate

MAPS={'finish':'Pawn varnish roughness','slopes':'Pawn fine slope atlas'}


def surface(body):
    nodes=body.data.materials[0].node_tree.nodes
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
    return output.inputs['Surface'].links[0].from_socket


def sampling(scene):
    return {'samples':scene.cycles.samples,'seed':scene.cycles.seed,
            'light_tree':scene.cycles.use_light_tree,'denoising':scene.cycles.use_denoising}


def run(cfg,target,out):
    source=ROOT/cfg['source'];assert sha(source)==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene)
    old=fingerprint(scene,body);old_graph=graph(surface(body),tuple(MAPS.values()))
    old_band=validate(scene,body);old_sampling=sampling(scene)
    n=body.data.materials[0].node_tree.nodes
    prior={key:pixels(n[name].image) for key,name in MAPS.items()}
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);body=control(scene);new=fingerprint(scene,body)
    for key in ('evaluated_mesh_normals_uv_sha256','world','ray_depth','prior_finish_inputs'):
        assert old[key]==new[key],key
    permitted={row['name']:row for row in cfg.get('lamp_colors',[])}
    assert len(permitted)==len(cfg.get('lamp_colors',[])),'Duplicate lamp-color specification'
    assert set(old['lights'])==set(new['lights']) and set(permitted)<=set(old['lights'])
    changed_colors={}
    for name,previous in old['lights'].items():
        current=dict(new['lights'][name]);before=dict(previous)
        if name in permitted:
            spec=permitted[name]
            assert not current['diffuse'] and current['glossy']
            assert np.isfinite(spec['energy']) and spec['energy']>0
            assert len(spec['color'])==3 and all(np.isfinite(v) and 0<=v<=1 for v in spec['color'])
            assert np.isclose(current['energy'],spec['energy'],atol=1e-8,rtol=1e-6),name
            assert np.allclose(current['color'],spec['color'],atol=1e-7,rtol=0),name
            changed_colors[name]={'energy':current['energy'],'color':current['color']}
            for key in ('energy','color'):current[key]=before[key]
        assert current==before,'Unexpected lamp change: '+name
    unchanged_images={k:v for k,v in old['other_packed_images'].items() if k not in MAPS.values()}
    assert unchanged_images=={k:v for k,v in new['other_packed_images'].items() if k not in MAPS.values()}
    assert graph(surface(body),tuple(MAPS.values()))==old_graph,'Full BSDF graph changed'
    assert validate(scene,body)==old_band
    assert sampling(scene)==old_sampling
    assert old_sampling=={'samples':cfg['samples'],'seed':cfg['seed'],'light_tree':cfg['light_tree'],'denoising':True}
    checks={};n=body.data.materials[0].node_tree.nodes
    for key,name in MAPS.items():
        spec=cfg[key];im=n[name].image;path=ROOT/spec['texture']
        assert sha(path)==spec['texture_sha256'] and im.packed_file.data==path.read_bytes()
        assert im.colorspace_settings.name=='Non-Color'
        a=prior[key];b=pixels(im);assert a.shape==b.shape
        v=(np.arange(len(a))+.5)/len(a);lo,_,_,hi=cfg['uv_focus']
        outside=(v<=lo)|(v>=hi)
        assert np.array_equal(a[outside],b[outside]),'Map escaped permitted surface band: '+name
        checks[key]={'file':spec['texture'],'sha256':spec['texture_sha256'],
                     'outside_focus_identical':True,'changed_fraction':float(np.any(a!=b,axis=2).mean())}
    report={'passed':True,'source_sha256':sha(source),'model_sha256':sha(target),
            'camera_above_board':54,'mesh_normals_uv_unchanged':True,
            'lights_total':len(new['lights']),'lights_unchanged':len(new['lights'])-len(permitted),
            'changed_lamp_colors':changed_colors,'all_lamp_positions_shapes_and_visibility_preserved':True,
            'world_ray_depth_unchanged':True,
            'pigment_and_prior_relief_unchanged':unchanged_images,
            'full_shader_graph_and_matte_band_preserved':True,
            'sampling':old_sampling,'uv_focus':cfg['uv_focus'],'maps':checks}
    save_json(out,report);print(json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')),ROOT/a.model,ROOT/a.output)
