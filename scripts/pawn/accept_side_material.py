"""Save, reopen and verify a scoped pawn material/profile checkpoint."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,ASSETS,control,fixed_camera,render,setup,sha,save_json
from polish_trial import open_source
from study_paired_material import attach
from study_side_quality import profile_edit
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from validate_local_surface import surface
from validate_groove_reflector import ramps
from deliver_mission import export

def coordinates(body):
    return np.array([v.co[:] for v in body.data.vertices],np.float32).reshape(-1,96,3)

def run(cfg):
    scene,body=open_source(cfg);side=bpy.data.scenes[scene['pawn_side_scene']]
    assert control(side) is body
    original=fingerprint(scene,body);studio_before=fingerprint(side,body)
    before=coordinates(body)
    uv_before=np.array([d.uv[:] for d in body.data.uv_layers['Pawn pigment'].data],np.float32)
    nodes=body.data.materials[0].node_tree.nodes
    replacements={s.get('old_sha256') for s in cfg['material']['maps'] if not s.get('node')}
    ignored=tuple(n.name for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.packed_file and
        (n.name in ('Pawn walnut pigment','Pawn varnish roughness','Pawn fine slope atlas') or hashlib.sha256(n.image.packed_file.data).hexdigest() in replacements))
    before_graph=graph(surface(body),ignored);before_ramps=ramps(body)
    edits=profile_edit(body,cfg['profile_rz']);attach(scene,body,cfg['material'])
    scene['pawn_accepted_trial']=cfg['checkpoint']
    scene['pawn_side_checkpoint']=json.dumps(cfg,sort_keys=True)
    known={sha(path):path for path in ASSETS.glob('pawn-*.png')}
    for node in nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.packed_file:
            digest=hashlib.sha256(node.image.packed_file.data).hexdigest()
            if digest in known:node.image.filepath='//../../'+known[digest].relative_to(ROOT).as_posix()
    for sc in (scene,side):
        setup(sc,cfg['samples']);sc.cycles.device='CPU'
    side.render.resolution_x=side.render.resolution_y=cfg['side_resolution']
    side.render.filepath='//../../assets/pawn/profile.png'
    scene.render.filepath='//../../assets/pawn/render.png'
    model=ROOT/'models/pawn/pawn-rebuilt.blend'
    bpy.context.window.scene=scene;bpy.ops.wm.save_as_mainfile(filepath=str(model),relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene;body=control(scene);fixed_camera(scene)
    side=bpy.data.scenes[scene['pawn_side_scene']];assert control(side) is body
    after=coordinates(body);changed=np.flatnonzero(np.any(after!=before,axis=(1,2)))
    assert set(changed)==set(map(int,cfg['profile_rz']))
    for i in changed:
        r,z=cfg['profile_rz'][str(i)]
        if r is not None:assert np.allclose(np.linalg.norm(after[i,:,:2],axis=1),r,atol=1e-7,rtol=0)
        if z is None:assert np.array_equal(after[i,:,2],before[i,:,2])
        else:assert np.allclose(after[i,:,2],z,atol=1e-7,rtol=0)
    uv_after=np.array([d.uv[:] for d in body.data.uv_layers['Pawn pigment'].data],np.float32)
    assert np.array_equal(uv_before,uv_after)
    current=fingerprint(scene,body);studio_after=fingerprint(side,body)
    for key in ('lights','world','ray_depth','prior_finish_inputs'):
        assert current[key]==original[key],key
        assert studio_after[key]==studio_before[key],('side',key)
    assert graph(surface(body),ignored)==before_graph and ramps(body)==before_ramps
    nodes=body.data.materials[0].node_tree.nodes
    specs=[{'path':cfg['material']['pigment'],'sha256':cfg['material']['pigment_sha256'],'node':'Pawn walnut pigment','encoding':'sRGB'}]+cfg['material']['maps']
    expected={s['sha256'] for s in specs};actual=set()
    for node in nodes:
        if node.name in ignored:
            digest=hashlib.sha256(node.image.packed_file.data).hexdigest();assert digest in expected
            spec=next(s for s in specs if s['sha256']==digest)
            path=ROOT/spec['path'];assert node.image.packed_file.data==path.read_bytes()
            assert node.image.colorspace_settings.name==spec['encoding']
            assert Path(bpy.path.abspath(node.image.filepath)).resolve()==path.resolve()
            actual.add(digest)
    assert actual==expected
    setup(scene,cfg['samples']);report=export(scene,body,model)
    render(scene,ASSETS/'render.png')
    wood=body.data.materials[0]
    clay=bpy.data.materials.new('Pawn side checkpoint inspection clay');clay.use_nodes=True
    bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.28,.30,.34,1);bs.inputs['Roughness'].default_value=.30
    body.data.materials[0]=clay;render(scene,ASSETS/'neutral.png');body.data.materials[0]=wood
    bpy.context.window.scene=side;setup(side,cfg['samples']);render(side,ASSETS/'profile.png')
    body.data.materials[0]=clay;render(side,ASSETS/'side-seating.png');body.data.materials[0]=wood
    presentation={'scene':side.name,'model_sha256':sha(model),'profile_sha256':sha(ASSETS/'profile.png'),
        'same_editable_object_and_material':True,'camera_elevation':0,'resolution':cfg['side_resolution'],
        'lighting_preset':'balanced','reference_lights_preserved':len(original['lights']),
        'studio_lights':studio_after['lights'],'studio_world':studio_after['world'],'note':side['pawn_presentation']}
    save_json(ASSETS/'side-presentation.json',presentation)
    report.update(variant=cfg['checkpoint'],reference_camera_above_board=54,source_trial_sha256=cfg['source_sha256'],
        texture_packed_after_reopen=True,render_sha256=sha(ASSETS/'render.png'),side_sha256=sha(ASSETS/'profile.png'),
        geometry_changed_rings=changed.tolist(),side_presentation_scene=side.name)
    save_json(ASSETS/'mission-validation.json',report)
    out=ROOT/cfg['evidence'];out.mkdir(parents=True,exist_ok=True)
    save_json(out/'scope-validation.json',{'passed':True,'source_sha256':cfg['source_sha256'],'model_sha256':sha(model),
        'changed_controls':edits,'all_other_control_coordinates_exact':True,'uv_coordinates_exact':True,
        'mesh_normals_uv_sha256':current['evaluated_mesh_normals_uv_sha256'],
        'reference_lights_preserved':len(original['lights']),'side_lights_preserved':len(studio_after['lights']),
        'both_worlds_unchanged':True,'same_shader_graph_except_four_image_inputs':True,'same_shader_ramps':True,
        'packed_maps_match_external_files':specs,'shared_editable_object':True,'reference_camera_54_degrees':True,
        'originals':{name:sha(ASSETS/name) for name in ('original.png','white-original.png','reference.png')}})
    side.render.resolution_x=side.render.resolution_y=640;side.cycles.samples=128
    for angle in (0,90,180,270):
        body.rotation_euler.z=math.radians(angle);render(side,out/('orbit-'+str(angle)+'.png'))
    body.rotation_euler.z=0;bpy.context.window.scene=scene
    print('PAWN_SIDE_MATERIAL_VALIDATED',json.dumps(report),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text()))
