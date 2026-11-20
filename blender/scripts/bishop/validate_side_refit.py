"""Audit the editable 026 cage, live saw, render surfaces and native side dimensions on reopen."""
import hashlib
import json
import math

import bpy
import numpy as np

from shared_turning import BODY, BUTTON, ROOT, control_rings, meridian, digest
from validate_render_receivers import array, check, snapshot
from validate_shared_turning import packed_images
from side_refit import COLLAR, MITRE, SOCKET, shape


def audit(model,profile):
    d=profile['side_refit']
    spec=json.loads((ROOT/d['config']).read_text())
    case=spec['cases'][d['case']]
    src=ROOT/spec['source']
    assert digest(src)==spec['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False)
    old_state=snapshot()
    old_images=packed_images()
    old_scene=bpy.context.scene
    old_receiver=json.loads(old_scene['bishop_receiver_trial'])
    body=bpy.data.objects[BODY]
    cut=next(m.object for m in body.modifiers if m.type=='BOOLEAN')
    saw_name=cut.name
    matrix=np.array(cut.matrix_world)
    saw=array(cut.data.vertices,'co',3).astype(float)
    before=control_rings(body)
    old_button=control_rings(bpy.data.objects[BUTTON])
    base=meridian(before)
    meta0=json.loads((src.parent/'mesh.json').read_text())
    height=meta0['bounds']['size'][2]
    old_profile=json.loads((ROOT/spec['source_profile']).read_text())
    donors=json.loads((ROOT/old_profile['shared_turning']['config']).read_text())
    old_transfer=donors['cases'][old_profile['shared_turning']['case']]['donor_scale']
    if 'side_refit' in old_profile:
        provenance=(ROOT/old_profile['side_refit']['config']).parent/'validation/mission-validation.json'
        source_audit=json.loads(provenance.read_text())
        assert source_audit['passed'] and source_audit['model_sha256']==digest(src)
        old_transfer=source_audit['scale']
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene
    assert json.loads(scene['bishop_side_refit'])==d
    assert json.loads(scene['bishop_shared_turning'])==old_profile['shared_turning']
    after=snapshot()
    healing=case.get('healed_atlas')
    new_images=packed_images()
    if healing:
        matname=bpy.data.objects[BODY].data.materials[0].name
        node='Baked boxwood pigment'
        old=old_state['materials'][matname]['nodes'][node]['image']
        now=after['materials'][matname]['nodes'][node]['image']
        assert old['packed'] and now['packed'] and old['colorspace']==now['colorspace']=='sRGB'
        assert old['size']==now['size']==[2048,2048] and old['pixels']!=now['pixels']
        assert old_images[old['name']]==healing['source_sha256']
        assert new_images.pop(now['name'])==healing['sha256']
        # Unused old pigment may be purged when Blender saves the file.
        if old['name'] not in new_images:old_images.pop(old['name'])
        old_state['materials'][matname]['nodes'][node]['image']=now
    for key in ['objects','lights','materials','camera','world','color_management','render_path']:
        assert after[key]==old_state[key],key
    assert new_images==old_images
    body=bpy.data.objects[BODY]
    new=control_rings(body)
    base_factor=case.get('base_factor',spec['base_factor'])
    # Each angular sample and every one of the donor rows must agree in XYZ.
    assert new.shape==before.shape==(114,128,3)
    err=float(np.abs(new[:SOCKET+1]-before[:SOCKET+1].astype(float)*base_factor).max())
    assert err<4e-7
    rows,dz=shape(base,height,spec,case)
    np.testing.assert_allclose(meridian(new),rows,atol=8e-7,rtol=0)
    np.testing.assert_allclose(new[:,:,:2],before[:,:,:2]*(rows[:,0]/base[:,0])[:,None,None],atol=3e-7,rtol=0)
    hr,hz=case['head_radius'],case['head_height']
    xyz=np.array([hr,hr,hz])
    shift=np.array([0.,0.,dz])
    z_start=110 if case.get('mitre_lift') else MITRE
    np.testing.assert_allclose(new[z_start:,:,2],before[z_start:,:,2].astype(float)*hz+dz,atol=8e-7,rtol=0)
    seat=110 if any(k in case for k in ('mitre_lower','mitre_upper','mitre_lift')) else MITRE
    np.testing.assert_allclose(new[seat:],before[seat:]*xyz+shift,atol=8e-7,rtol=0)
    button=control_rings(bpy.data.objects[BUTTON])
    expected_button=old_button*xyz+shift
    expected_button[-4:,:,2]+=d.get('cap_roundoff_correction',0.)
    np.testing.assert_allclose(button,expected_button,atol=8e-7,rtol=0)
    cut=next(m.object for m in body.modifiers if m.type=='BOOLEAN')
    assert cut.name==saw_name and np.array_equal(np.array(cut.matrix_world),matrix)
    def world(coords):
        return coords@matrix[:3,:3].T+matrix[:3,3]
    expected_saw=world(saw)*xyz+shift
    plane=case.get('placed_slit')
    if plane:
        assert d['placed_slit']==plane
        turn=np.array(d['placed_slit_world_transform'])
        rot=turn[:3,:3]
        np.testing.assert_allclose(rot.T@rot,np.eye(3),atol=2e-7,rtol=0)
        assert abs(np.linalg.det(rot)-1)<3e-7
        expected_saw=expected_saw@rot.T+turn[:3,3]
        delta=expected_saw[0]-expected_saw[1]
        a,b=plane['dx_dz'],plane['dx_dy']
        assert abs(delta[0]-a*delta[2]-b*delta[1])<2e-6
        assert abs(expected_saw[:,2].min()-plane['floor_z'])<2e-6
        x,z=plane['anchor_xz']
        v=expected_saw[:,0]-a*expected_saw[:,2]-b*expected_saw[:,1]
        assert abs((v.max()+v.min())/2-(x-a*z))<2e-6
    np.testing.assert_allclose(world(array(cut.data.vertices,'co',3)),expected_saw,atol=1.5e-6,rtol=0)
    for name in [BODY,BUTTON,saw_name]:
        orig=old_state['meshes'][name]
        now=after['meshes'][name]
        for key in ['visibility','hide_render','matrix','modifiers']:
            assert orig[key]==now[key],(name,key)
        assert orig['mesh']['hashes'].keys()==now['mesh']['hashes'].keys()
        for key,digest_old in orig['mesh']['hashes'].items():
            if key not in ('positions','normals'):
                assert now['mesh']['hashes'][key]==digest_old,(name,key)
    src_alignment=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
    factor=1254/300/src_alignment['scale']/profile['scale']
    cos=math.cos(math.radians(54))
    for cage,data in [(new,profile['profile']),(button,profile['finial']['profile'])]:
        rz=meridian(cage)
        np.testing.assert_allclose(np.stack([rz[:,0]/factor,profile['y0']-rz[:,1]*cos/factor],axis=1),data,rtol=0,atol=6e-5)
    receiver=json.loads(scene['bishop_receiver_trial'])
    for k,value in old_receiver.items():
        if k!='socket_z_band':assert receiver[k]==value
    np.testing.assert_allclose(receiver['socket_z_band'],np.asarray(old_receiver['socket_z_band'])*base_factor,atol=2e-7,rtol=0)
    exact=check(scene,receiver)
    assets=ROOT/'assets/bishop'
    meta=json.loads((assets/'mesh.json').read_text())
    model_hash=digest(model)
    assert meta['sourceSha256']==model_hash and meta['referenceCamera']==meta0['referenceCamera']
    assert abs(meta['bounds']['min'][2])<1e-7
    actual=np.array(meta['bounds']['size'])
    wanted=np.array(meta0['bounds']['size'])*[base_factor,base_factor,spec['height_factor']]
    np.testing.assert_allclose(actual,wanted,rtol=0,atol=1e-5)
    if 'locked_height' in spec:
        assert abs(float(actual[2])-spec['locked_height'])<=5e-7
    raw=(assets/'mesh.bin').read_bytes()
    v=np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8)
    i=np.frombuffer(raw,dtype='<u4',offset=meta['indexByteOffset'])
    assert np.array_equal(i,np.arange(len(v))) and np.isfinite(v).all()
    np.testing.assert_allclose(np.linalg.norm(v[:,3:6],axis=1),1.,atol=3e-6,rtol=0)
    walls=(v[:,6:]==-1.).all(1)
    assert walls.any() and v[~walls,6:].min()>-.01 and v[~walls,6:].max()<1.01
    old_atlas=digest(src.parent/'bishop-boxwood-albedo.png')
    atlas=digest(assets/'bishop-boxwood-albedo.png')
    assert atlas==meta['material']['textureSha256']
    if healing:
        assert atlas==healing['sha256'] and old_atlas==healing['source_sha256']
    else:
        assert atlas==old_atlas
    for filename,src_name in [('original.png','White-Bishop.png'),('black-original.png','Black-Bishop.png')]:
        assert digest(assets/filename)==digest(ROOT/'references/lichess-staunton-3d'/src_name)
    assert digest(assets/'reference.png')==digest(ROOT/'assets/candidates/bishop/white-candidate-3.png')
    anchor_indices=[0,SOCKET,COLLAR,MITRE]
    a=np.r_[base[anchor_indices,1],height]
    b=np.r_[rows[anchor_indices,1],actual[2]]
    return {'passed':True,'model_sha256':model_hash,'source':spec['source'],'source_sha256':spec['source_sha256'],
            'configuration':d,'donor_rings':40,'donor_sha256':{key:donors[key]['sha256'] for key in ('queen','king')},
            'scale':old_transfer*base_factor,'max_base_radius_or_height_error':err,
            'upper_controls_match_specification':True,'cutter_translation_z':dz,'head_radius_factor':hr,'head_height_factor':hz,
            'cutter_and_button_transform_matches_mitre':not bool(plane),'placed_slit':plane,'all_control_uvs_exact':True,
            'original_upper_uvs_exact':True,'lower_uv_interpolation_max_error':0.,
            'packed_images_and_material_graphs_preserved':not bool(healing),'healed_atlas':healing,
            'material_graph_preserved':True,'lights_exact':True,'reference_pixels_unchanged':True,
            'camera_exactly_unchanged':True,'geometry_phase':True,'saved_and_reopened':True,'render_receivers':exact,
            'finite_uvs_and_unit_normals':True,'exported_triangles':meta['triangleCount'],'bounds':meta['bounds'],
            'old_size':meta0['bounds']['size'],'target_size':wanted.tolist(),'height_ratio':float(actual[2]/height),
            'foot_ratio':float(actual[0]/meta0['bounds']['size'][0]),'physical_sections':{
                name:{'old':float(u),'new':float(v),'change':float(v-u)} for name,u,v in
                zip(['sole_to_first_stem_support','stem','collar_stack','mitre_and_button'],np.diff(a),np.diff(b))}}
