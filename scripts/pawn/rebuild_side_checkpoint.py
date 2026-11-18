"""Build a scoped pawn profile edit and save a second real side-lighting scene.

The two scenes share the same editable object, geometry, UVs and wood material.
The primary scene retains its exact reference camera and all existing lights.
"""
import argparse,json,math,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,ASSETS,control,fixed_camera,render,save_json,setup,sha,side_camera
from polish_trial import open_source
from study_side_quality import profile_edit,studio
from validate_finish_scope import fingerprint
from validate_contact_checkpoint import graph
from validate_groove_reflector import ramps
from validate_local_surface import surface
from deliver_mission import export


def make_studio(reference,body,cfg):
    side=bpy.data.scenes.new('Pawn side studio')
    side.world=reference.world.copy()
    side.collection.objects.link(body)
    camera=reference.camera.copy();camera.data=reference.camera.data.copy()
    camera.name='Pawn side studio camera';side.collection.objects.link(camera);side.camera=camera
    side.display_settings.display_device=reference.display_settings.display_device
    for attr in ('view_transform','look','exposure','gamma'):
        setattr(side.view_settings,attr,getattr(reference.view_settings,attr))
    for attr in ('use_light_tree','use_adaptive_sampling','adaptive_threshold','adaptive_min_samples','seed',
                 'diffuse_bounces','glossy_bounces','transmission_bounces','transparent_max_bounces','max_bounces'):
        setattr(side.cycles,attr,getattr(reference.cycles,attr))
    setup(side,cfg['samples']);side_camera(side)
    side.render.resolution_x=side.render.resolution_y=cfg['side_resolution']
    studio(side,cfg['studio'])
    side['pawn_presentation']='Same pawn object and wood; separate photographic side studio. Two broad fill cards are diffuse-only artistic lights.'
    side.render.filepath='//../../assets/pawn/profile.png'
    reference['pawn_side_scene']=side.name
    return side


def build(cfg):
    reference,body=open_source(cfg);before=fingerprint(reference,body)
    old_graph=graph(surface(body),());old_ramps=ramps(body)
    old_controls=np.array([v.co[:] for v in body.data.vertices],np.float32)
    edits=profile_edit(body,cfg['profile_rz'])
    after=fingerprint(reference,body)
    if not cfg['profile_rz']:
        assert before['evaluated_mesh_normals_uv_sha256']==after['evaluated_mesh_normals_uv_sha256']
    for key in ('lights','other_packed_images','world','ray_depth','prior_finish_inputs'):
        assert before[key]==after[key],key
    assert graph(surface(body),())==old_graph and ramps(body)==old_ramps
    controls=np.array([v.co[:] for v in body.data.vertices],np.float32)
    changed=np.flatnonzero(np.any(controls.reshape(-1,96,3)!=old_controls.reshape(-1,96,3),axis=(1,2)))
    assert set(changed.tolist())==set(map(int,cfg['profile_rz']))
    side=make_studio(reference,body,cfg)
    assert reference.world!=side.world and reference.camera!=side.camera
    assert control(reference) is control(side)
    assert fingerprint(reference,body)['lights']==before['lights']
    reference['pawn_accepted_trial']='side-quality-001'
    reference['pawn_side_checkpoint']=json.dumps(cfg,sort_keys=True)
    reference.render.filepath='//../../assets/pawn/render.png'
    for sc in (reference,side):sc.cycles.device='CPU'
    model=ROOT/'models/pawn/pawn-rebuilt.blend'
    bpy.context.window.scene=reference
    bpy.ops.wm.save_as_mainfile(filepath=str(model),relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    reference=bpy.context.scene;body=control(reference);fixed_camera(reference)
    side=bpy.data.scenes[reference['pawn_side_scene']]
    assert control(side) is body and len([o for o in reference.objects if o.type=='LIGHT'])==len(before['lights'])
    saved=fingerprint(reference,body)
    for key in ('lights','other_packed_images','world','ray_depth','prior_finish_inputs'):
        assert saved[key]==before[key],key
    assert graph(surface(body),())==old_graph and ramps(body)==old_ramps
    setup(reference,cfg['samples']);report=export(reference,body,model)
    render(reference,ASSETS/'render.png')
    wood=body.data.materials[0]
    clay=bpy.data.materials.get('Satin clay - geometry study')
    if clay is None:
        clay=bpy.data.materials.new('Pawn inspection clay');clay.use_nodes=True
        bs=clay.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.28,.30,.34,1);bs.inputs['Roughness'].default_value=.30
    body.data.materials[0]=clay;render(reference,ASSETS/'neutral.png');body.data.materials[0]=wood
    bpy.context.window.scene=side;setup(side,cfg['samples'])
    render(side,ASSETS/'profile.png')
    body.data.materials[0]=clay;render(side,ASSETS/'side-seating.png');body.data.materials[0]=wood
    presentation={'scene':side.name,'model_sha256':sha(model),'profile_sha256':sha(ASSETS/'profile.png'),
        'same_editable_object_and_material':True,'camera_elevation':0,'resolution':cfg['side_resolution'],
        'lighting_preset':cfg['studio'],'reference_lights_preserved':len(before['lights']),
        'studio_lights':fingerprint(side,body)['lights'],'studio_world':fingerprint(side,body)['world'],
        'note':side['pawn_presentation']}
    save_json(ASSETS/'side-presentation.json',presentation)
    report.update(variant='side-quality-001',reference_camera_above_board=54,source_trial_sha256=cfg['source_sha256'],
        texture_packed_after_reopen=True,render_sha256=sha(ASSETS/'render.png'),side_sha256=sha(ASSETS/'profile.png'),
        geometry_changed_rings=changed.tolist(),reference_lights_and_material_preserved=True,side_presentation_scene=side.name)
    save_json(ASSETS/'mission-validation.json',report)
    out=ROOT/cfg['evidence'];out.mkdir(parents=True,exist_ok=True)
    save_json(out/'scope-validation.json',{'passed':True,'source_sha256':cfg['source_sha256'],'model_sha256':sha(model),
        'changed_controls':edits,'reference_lights':len(before['lights']),'same_shader_graph_and_ramps':True,
        'unchanged_packed_images':saved['other_packed_images'],'mesh_normals_uv_sha256':saved['evaluated_mesh_normals_uv_sha256'],
        'shared_side_object':True,'reference_camera_54_degrees':True})
    # Check the actual static wood all the way around in one unchanged studio.
    side.render.resolution_x=side.render.resolution_y=640;side.cycles.samples=128
    for angle in (0,90,180,270):
        body.rotation_euler.z=math.radians(angle)
        render(side,out/('orbit-'+str(angle)+'.png'))
    body.rotation_euler.z=0
    bpy.context.window.scene=reference
    print('PAWN_SIDE_CHECKPOINT_SAVED',json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(json.loads(a.config.read_text(encoding='utf8')))
