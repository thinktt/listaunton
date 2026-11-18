"""Audit the reopened editable bishop against both donors and its original upper cage."""
import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np

from shared_turning import (ROOT, BODY, BUTTON, BISHOP_ANCHORS, DONOR_ANCHORS, SEGMENTS,
                            atlas_rows, control_rings, digest, donor_controls, fitted_profile,
                            meridian, read_source)
from validate_render_receivers import array, check, snapshot


def packed_images():
    return {im.name:hashlib.sha256(im.packed_file.data).hexdigest()
            for im in bpy.data.images if im.packed_file}


def audit(model, profile):
    declaration=profile['shared_turning']
    spec=json.loads((ROOT/declaration['config']).read_text())
    case=spec['cases'][declaration['case']]
    donor=donor_controls(spec)
    old_path=read_source(spec,'bishop')
    bpy.ops.wm.open_mainfile(filepath=str(old_path),load_ui=False)
    before=snapshot()
    images=packed_images()
    body=bpy.data.objects[BODY]
    old=control_rings(body).copy()
    button=control_rings(bpy.data.objects[BUTTON]).copy()
    cut=next(m.object for m in body.modifiers if m.type=='BOOLEAN')
    cutter_name=cut.name
    source_matrix=np.array(cut.matrix_world)
    source_rz=meridian(old)
    atlas={l.name:array(l.data,'uv',2) for l in body.data.uv_layers}
    original_coverage=array(body.data.attributes['Pigment coverage'].data,'value').reshape(-1,SEGMENTS)
    receiver=json.loads(bpy.context.scene['bishop_receiver_trial'])
    scale=case['donor_scale']
    rows=atlas_rows(source_rz,donor)
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene
    body=bpy.data.objects[BODY]
    after=snapshot()
    assert before['objects']==after['objects']
    for key in ['lights','materials','camera','world','color_management','render_path']:
        assert before[key]==after[key],key
    assert images==packed_images(), 'Packed images changed'
    for name in (BODY,BUTTON,cutter_name):
        for key in ['hide_render','visibility','modifiers']:
            assert before['meshes'][name][key]==after['meshes'][name][key],(name,key)
    assert before['meshes'][cutter_name]['mesh']==after['meshes'][cutter_name]['mesh']
    new_cut=bpy.data.objects[cutter_name]
    expected_matrix=source_matrix.copy()
    expected_matrix[2,3]-=case['head_drop']
    np.testing.assert_allclose(np.array(new_cut.matrix_world),expected_matrix,rtol=0,atol=6e-7)
    new=control_rings(body)
    assert new.shape==(len(old)+7,128,3)
    actual_r=np.linalg.norm(new[:40,:,:2],axis=2)
    expected_r=np.broadcast_to(donor[:,0,None]*scale,(40,128))
    expected_z=np.broadcast_to((source_rz[0,1]+(donor[:,1]-donor[0,1])*scale)[:,None],(40,128))
    base_error=float(max(np.max(abs(actual_r-expected_r)),np.max(abs(new[:40,:,2]-expected_z))))
    assert base_error<5e-7, 'Donor cross-sections changed'
    np.testing.assert_allclose(new[:40,:,:2]/actual_r[:,:,None], np.broadcast_to(old[32,:,:2]/source_rz[32,0],(40,128,2)),atol=4e-7)
    sections=fitted_profile(source_rz,donor,case)
    np.testing.assert_allclose(meridian(new),sections,rtol=0,atol=5e-7)
    # Source head, translated with its saw, is exact outside the listed edits.
    custom=set(map(int,case.get('upper_edits',{})))
    for i in range(65,len(old)):
        if i not in custom:
            np.testing.assert_array_equal(new[i+7,:,:2],old[i,:,:2])
        np.testing.assert_allclose(new[i+7,:,2],old[i,:,2]-case['head_drop']+case.get('upper_edits',{}).get(str(i),[0,0])[0],rtol=0,atol=7e-7)
    final_button=control_rings(bpy.data.objects[BUTTON])
    np.testing.assert_array_equal(final_button[:,:,:2],button[:,:,:2])
    weights=np.array([0,0,0,0,0,0,0,0,.12,.55,.93,1])
    np.testing.assert_allclose(final_button[:,:,2],button[:,:,2]-case['head_drop']-case.get('cap_drop',0)*weights[:,None],rtol=0,atol=6e-7)
    for key in before['meshes'][BUTTON]['mesh']['hashes']:
        if key not in ['positions','normals']:
            assert before['meshes'][BUTTON]['mesh']['hashes'][key]==after['meshes'][BUTTON]['mesh']['hashes'][key]
    mesh=body.data
    assert set(atlas)=={l.name for l in mesh.uv_layers}
    for key in ['material_slots','uv_active_index','uv_render']:
        assert before['meshes'][BODY]['mesh'][key]==after['meshes'][BODY]['mesh'][key]
    # On each original axial side sample the old two adjacent UV loops. This
    # verifies interpolation through the extra bands and both sides of seams.
    worst_uv=0.
    for layer in mesh.uv_layers:
        old_uv=atlas[layer.name]
        new_uv=array(layer.data,'uv',2)
        old_faces=old_uv[:-256].reshape(-1,128,4,2)
        new_faces=new_uv[:-256].reshape(-1,128,4,2)
        np.testing.assert_array_equal(old_faces[33:],new_faces[40:])
        np.testing.assert_array_equal(old_uv[-256:],new_uv[-256:])
        for j,t in enumerate(rows[:41]):
            for band, corner, dest in [(max(0,math.ceil(t)-1),2,j-1),(math.floor(t),0,j)]:
                if dest<0 or dest>=len(new_faces):continue
                weight=t-band
                for k in (0,1):
                    start=old_faces[band,:,k]
                    end=old_faces[band,:,3-k]
                    expected=start+weight*(end-start).astype(float)
                    actual=new_faces[dest,:,3-k if corner==2 else k]
                    worst_uv=max(worst_uv,float(np.abs(actual-expected).max()))
    assert worst_uv<2e-7,worst_uv
    cov=array(mesh.attributes['Pigment coverage'].data,'value').reshape(-1,SEGMENTS)
    for column in range(SEGMENTS):
        np.testing.assert_allclose(cov[:,column],np.interp(rows,np.arange(len(old)),original_coverage[:,column]),rtol=0,atol=1e-7)
    np.testing.assert_array_equal(cov[40:],original_coverage[33:])
    provenance=json.loads(scene['bishop_shared_turning'])
    assert provenance==declaration
    # Verify the written editable profile in original-image units against the
    # reopened cage, independently of the pages and their exported buffers.
    a=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
    factor=1254/300/a['scale']/profile['scale']
    cosine=math.cos(math.radians(54))
    for cage,pairs in [(new,profile['profile']),(final_button,profile['finial']['profile'])]:
        rz=meridian(cage)
        measure=np.stack([rz[:,0]/factor,profile['y0']-rz[:,1]*cosine/factor],axis=1)
        np.testing.assert_allclose(measure,np.array(pairs),atol=4e-5,rtol=0)
    cfg=json.loads(scene['bishop_receiver_trial'])
    for k in receiver:
        if k!='socket_z_band':
            assert cfg[k]==receiver[k],k
    np.testing.assert_allclose(cfg['socket_z_band'],np.interp(receiver['socket_z_band'],source_rz[BISHOP_ANCHORS[3:],1],sections[DONOR_ANCHORS[3:],1]),atol=1e-7)
    receivers=check(scene,cfg)
    assets=ROOT/'assets/bishop'
    for original,asset in [('White-Bishop','original.png'),('Black-Bishop','black-original.png')]:
        assert digest(assets/asset)==digest(ROOT/'references/lichess-staunton-3d'/(original+'.png'))
    assert digest(assets/'reference.png')==digest(ROOT/'assets/candidates/bishop/white-candidate-3.png')
    meta=json.loads((assets/'mesh.json').read_text())
    raw=(assets/'mesh.bin').read_bytes()
    verts=np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8)
    indices=np.frombuffer(raw,dtype='<u4',offset=meta['indexByteOffset'])
    model_hash=digest(model)
    assert meta['sourceSha256']==model_hash and len(raw)==meta['totalByteLength']
    assert len(indices)==meta['indexCount'] and np.array_equal(indices,np.arange(len(verts)))
    assert np.isfinite(verts).all()
    np.testing.assert_allclose(np.linalg.norm(verts[:,3:6],axis=1),1,atol=2e-6)
    cut=(verts[:,6:]==-1).all(axis=1)
    assert cut.any() and verts[~cut,6:].min()>-.01 and verts[~cut,6:].max()<1.01
    assert digest(assets/'bishop-boxwood-albedo.png')==digest(old_path.parent/'bishop-boxwood-albedo.png')==meta['material']['textureSha256']
    assert meta['referenceCamera']==json.loads((old_path.parent/'camera.json').read_text())
    assert abs(meta['bounds']['min'][2])<1e-6
    old_size=json.loads((old_path.parent/'mesh.json').read_text())['bounds']['size']
    assert meta['bounds']['size'][0]>old_size[0] and meta['bounds']['size'][2]<old_size[2]
    return {'passed':True,'model_sha256':model_hash,'source':spec['bishop']['file'],'source_sha256':spec['bishop']['sha256'],
            'configuration':declaration,'donor_sha256':{k:spec[k]['sha256'] for k in ['queen','king']},
            'scale':scale,'donor_rings':40,'max_base_radius_or_height_error':base_error,
            'upper_controls_match_specification':True,'supported_head_and_button_join_cage_checked':True,
            'cutter_translation_z':-case['head_drop'],'cutter_shape_and_rotation_preserved':True,
            'lower_uv_interpolation_max_error':worst_uv,'original_upper_uvs_exact':True,
            'packed_images_and_material_graphs_preserved':True,'packed_images':images,'lights_exact':True,
            'reference_pixels_unchanged':True,'camera_exactly_unchanged':True,'geometry_phase':True,
            'saved_and_reopened':True,'render_receivers':receivers,'finite_uvs_and_unit_normals':True,
            'exported_triangles':meta['triangleCount'],'bounds':meta['bounds'],'old_size':old_size,
            'socket_receiver_band':cfg['socket_z_band']}
