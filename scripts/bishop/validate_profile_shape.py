"""Audit a saved geometry refit against its exact preserved accepted source."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from validate_render_receivers import snapshot, check, array
from bishop_scene import editable_meshes
BODY='Bishop - continuous turned body'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def audit(model,config,profile_path):
    cfg=json.loads(config.read_text());source=ROOT/cfg['source']
    assert sha(source)==cfg['source_sha256'],'Preserved source differs.'
    old_profile=json.loads((ROOT/cfg['profile']).read_text())
    profile=json.loads(profile_path.read_text())
    expected_profile=json.loads(json.dumps(old_profile))
    for i,pair in cfg['body_rings'].items():expected_profile['profile'][int(i)]=pair
    for key in old_profile:
        if key not in ['revision','mission_shape_refit']:
            assert profile[key]==expected_profile[key],('Undeclared profile change',key)
    declaration=profile['mission_shape_refit']
    assert declaration['source']==cfg['source'] and declaration['source_sha256']==cfg['source_sha256']
    assert declaration['body_rings']==cfg['body_rings'] and declaration['profile']==cfg['profile']
    assert (ROOT/declaration['config']).resolve()==config.resolve()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
    old=array(bpy.data.objects[BODY].data.vertices,'co',3).copy()
    expected=old.astype(np.float64)
    al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
    factor=1254/300/al['scale']/old_profile['scale']/math.cos(math.radians(54))
    touched=np.zeros(len(old),dtype=bool)
    for key,(r,y) in cfg['body_rings'].items():
        i=int(key);r0,y0=old_profile['profile'][i];sl=slice(i*128,(i+1)*128)
        expected[sl,:2]*=r/r0;expected[sl,2]+=(y0-y)*factor;touched[sl]=True
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;after=snapshot()
    actual=array(bpy.data.objects[BODY].data.vertices,'co',3)
    max_error=float(np.max(abs(actual-expected)))
    assert max_error<5e-6,('Actual control positions differ from declared edit',max_error)
    assert np.array_equal(old[~touched],actual[~touched]),'Unlisted controls changed.'
    assert json.loads(s['bishop_shape_refit'])==declaration
    regions=[o.name for o in s.objects if o.get('bishop_render_region')]
    for key in ['lights','materials','camera','world','color_management','render_path','objects']:
        assert before[key]==after[key],('Undeclared scene change',key)
    for name,row in before['meshes'].items():
        if name in regions:continue
        new=after['meshes'][name]
        if name!=BODY:assert row==new,('Unlisted mesh changed',name);continue
        for key,value in row.items():
            if key!='mesh':assert value==new[key],(name,key)
        for key,value in row['mesh'].items():
            if key!='hashes':assert value==new['mesh'][key],(name,key)
        for key,value in row['mesh']['hashes'].items():
            if key not in ['positions','normals']:assert value==new['mesh']['hashes'][key],(name,key)
    receivers=check(s,json.loads(s['bishop_receiver_trial']))
    assert all(mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED'
               for ob in editable_meshes(s) for mat in ob.data.materials if mat)
    assert s.get('bishop_albedo_bakes_lighting')==False
    for original,asset in [('White-Bishop','original.png'),('Black-Bishop','black-original.png')]:
        assert (ROOT/f'assets/bishop/{asset}').read_bytes()==(ROOT/f'references/lichess-staunton-3d/{original}.png').read_bytes()
    assert (ROOT/'assets/bishop/reference.png').read_bytes()==(ROOT/'assets/candidates/bishop/white-candidate-3.png').read_bytes()
    return {'passed':True,'model_sha256':sha(model),'source':cfg['source'],'source_sha256':sha(source),
        'config_sha256':sha(config),'changed_body_rings':sorted(map(int,cfg['body_rings'])),
        'max_control_error_from_declared_edit':max_error,'unlisted_controls_exact':True,
        'topology_modifiers_uvs_cutter_button_materials_packed_pixels_lights_and_camera_preserved':True,
        'reference_pixels_unchanged':True,'camera_exactly_unchanged':True,
        'shader':'Principled BSDF','saved_scene_albedo_bakes_lighting_flag':False,
        'render_receivers':receivers,'saved_and_reopened':True,
        'note':'The separate anatomy validator checks closed components, actual slit opening and continuous button join. Scope validation is not a visual fidelity score. The preserved albedo metadata flag is not proof that pigment is illumination-free; the inherited atlas still contains photographic shading.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True);p.add_argument('--config',required=True)
    p.add_argument('--profile',required=True);p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    report=audit(ROOT/a.model,ROOT/a.config,ROOT/a.profile)
    (ROOT/a.out).write_text(json.dumps(report,indent=2)+'\n')
    print('PROFILE_SHAPE_AUDIT_PASSED',json.dumps(report),flush=True)
