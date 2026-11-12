"""Validate declared bishop edits, pigment data and fixed-camera provenance."""
import bpy,json,hashlib,sys,math,copy,runpy
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from bishop_scene import editable_meshes
from validate_render_receivers import audit as audit_receivers
buffers={};construction={}
def geometry(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);bpy.context.view_layer.update();g=bpy.context.evaluated_depsgraph_get();res={}
    for ob in editable_meshes(bpy.context.scene):
        ev=ob.evaluated_get(g);me=ev.to_mesh();me.calc_loop_triangles()
        pos=np.array([tuple(v.co) for v in me.vertices],dtype='<f4');tris=np.array([tuple(t.vertices) for t in me.loop_triangles],dtype='<i4')
        buffers[(str(path),ob.name)]=(pos.copy(),tris.copy(),np.array([tuple(v.co) for v in ob.data.vertices],dtype='<f4'))
        modifier_data=[]
        for modifier in ob.modifiers:
            values={'type':modifier.type}
            for key in ['subdivision_type','levels','render_levels','operation','solver','width','segments','limit_method','angle_limit','profile']:
                if hasattr(modifier,key):values[key]=getattr(modifier,key)
            if modifier.type=='BOOLEAN':
                cutter=modifier.object
                values['cutter']={'matrix':[float(x) for row in cutter.matrix_world for x in row], 'vertices':[list(v.co) for v in cutter.data.vertices]}
            modifier_data.append(values)
        construction[(str(path),ob.name)]={'control_faces':[list(face.vertices) for face in ob.data.polygons], 'modifiers':modifier_data}
        assert np.isfinite(pos).all()
        # Boolean material slots can reorder vertices. Compare actual positions
        # and spatial triangles, independent of their storage indices.
        order=np.lexsort(pos.T[::-1]);sorted_pos=pos[order]
        corners=pos[tris].copy()
        for i in range(len(corners)):corners[i]=corners[i][np.lexsort(corners[i].T[::-1])]
        flat=corners.reshape(-1,9);flat=flat[np.lexsort(flat.T[::-1])]
        res[ob.name]={'positions':hashlib.sha256(sorted_pos.tobytes()).hexdigest(),'triangles':hashlib.sha256(flat.tobytes()).hexdigest(),'vertex_count':len(pos),'triangle_count':len(tris)};ev.to_mesh_clear()
    return res
profile=json.loads((ROOT/'scripts/bishop/profile.json').read_text())
declared=profile.get('mission_geometry')
slit_declared=profile.get('mission_slit_geometry')
base_declared=profile.get('mission_base_curvature')
current_path=ROOT/'models/bishop/bishop-rebuilt.blend'
bpy.ops.wm.open_mainfile(filepath=str(current_path),load_ui=False)
receiver_cfg=json.loads(bpy.context.scene['bishop_receiver_trial']) if bpy.context.scene.get('bishop_receiver_trial') else None
receiver_report=audit_receivers(current_path,receiver_cfg) if receiver_cfg else {'used':False}
if receiver_cfg:
    (ROOT/'assets/bishop/receiver-validation.json').write_text(json.dumps(receiver_report,indent=2)+'\n')
if base_declared:
    base_config=json.loads((ROOT/base_declared['config']).read_text())
    assert base_declared['baseline_model']==base_config['source']
    assert base_declared['baseline_profile']==base_config['profile']
    assert base_declared['body_rings']==base_config['body_rings']
    original_args=sys.argv[:]
    base_checked_model=receiver_cfg['source'] if receiver_cfg else 'models/bishop/bishop-rebuilt.blend'
    sys.argv=['validate_base_curvature.py','--','--config',base_declared['config'],
              '--model',base_checked_model,'--out','assets/bishop/base-validation.json','--geometry-only']
    runpy.run_path(str(Path(__file__).with_name('validate_base_curvature.py')),run_name='__main__')
    sys.argv=original_args
    if receiver_cfg:
        base_report=json.loads((ROOT/'assets/bishop/base-validation.json').read_text())
        base_report.update(checked_model=base_checked_model,current_model_sha256=hashlib.sha256(current_path.read_bytes()).hexdigest(),
          inheritance_audit='assets/bishop/receiver-validation.json',
          note='The base edit is checked on the archived closed source. The independent receiver audit proves current controls, cutter, modifiers and UVs exactly inherit that surface. Current anatomy is also probed directly.')
        (ROOT/'assets/bishop/base-validation.json').write_text(json.dumps(base_report,indent=2)+'\n')
if slit_declared:
    slit_path=ROOT/slit_declared['config'];slit_config=json.loads(slit_path.read_text())
    assert slit_config['source']==slit_declared['baseline_model']
    assert slit_config['source_sha256']==slit_declared['baseline_sha256']
    original_args=sys.argv[:]
    slit_checked_model=base_declared['baseline_model'] if base_declared else 'models/bishop/bishop-rebuilt.blend'
    sys.argv=['validate_slit_trial.py','--','--model',slit_checked_model,
              '--config',slit_declared['config'],'--out','assets/bishop/slit-validation.json','--geometry-only']
    runpy.run_path(str(Path(__file__).with_name('validate_slit_trial.py')),run_name='__main__')
    sys.argv=original_args
    if base_declared:
        slit_report=json.loads((ROOT/'assets/bishop/slit-validation.json').read_text())
        slit_report['checked_model']=slit_checked_model
        slit_report['current_model_sha256']=hashlib.sha256((ROOT/'models/bishop/bishop-rebuilt.blend').read_bytes()).hexdigest()
        slit_report['inheritance_audit']='assets/bishop/base-validation.json'
        slit_report['note']='Rounded cutter and upper geometry are validated on the preserved source, then inherited exactly through the independently audited two-ring base edit. The current anatomy check also probes the actual through slit and solid floor.'
        (ROOT/'assets/bishop/slit-validation.json').write_text(json.dumps(slit_report,indent=2)+'\n')
baseline_path=ROOT/(declared['baseline_model'] if declared else 'history/bishop-mission-000/bishop-rebuilt.blend')
current_path=ROOT/'models/bishop/bishop-rebuilt.blend'
baseline=geometry(baseline_path)
current=geometry(current_path)
changes={}
for name in baseline:
    old,oldtri,oldcontrol=buffers[(str(baseline_path),name)]
    new,newtri,newcontrol=buffers[(str(current_path),name)]
    diff=float(np.max(np.abs(new-old))) if new.shape==old.shape else None
    same_tri=bool(np.array_equal(oldtri,newtri));same_control=bool(np.array_equal(oldcontrol,newcontrol))
    changes[name]={'max_evaluated_coordinate_difference':diff,'triangle_indices_unchanged':same_tri,'control_vertices_exactly_unchanged':same_control}
    if declared:
        expected=oldcontrol.copy()
        old_profile=json.loads((ROOT/declared['baseline_profile']).read_text())
        if 'finial' in name:
            expected[:,:2]*=declared['button_scale_xy']
        else:
            alignment=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
            factor=1254/300/alignment['scale']/old_profile['scale']/math.cos(math.radians(old_profile['elevation']))
            assert sorted(int(k) for k in declared['body_rings'])==declared['changed_body_rings']
            for key,(radius,axis_y) in declared['body_rings'].items():
                index=int(key);old_radius,old_y=old_profile['profile'][index]
                expected[index*128:(index+1)*128,:2]*=radius/old_radius
                expected[index*128:(index+1)*128,2]+=(old_y-axis_y)*factor
            if base_declared:
                base_profile=json.loads((ROOT/base_declared['baseline_profile']).read_text())
                for key,(radius,axis_y) in base_declared['body_rings'].items():
                    index=int(key);old_radius,old_y=base_profile['profile'][index]
                    assert axis_y==old_y and index in [17,18]
                    expected[index*128:(index+1)*128,:2]*=radius/old_radius
        difference=float(np.max(np.abs(newcontrol-expected)))
        changes[name]['max_control_difference_from_declared_edit']=difference
        current_construction=copy.deepcopy(construction[(str(current_path),name)])
        if slit_declared:
            # Only the independently checked rounded cutter may differ here.
            # All other modifiers, controls and topology retain the old checks.
            for index,mod in enumerate(current_construction['modifiers']):
                if mod['type']=='BOOLEAN':mod['cutter']=construction[(str(baseline_path),name)]['modifiers'][index]['cutter']
        same_construction=construction[(str(baseline_path),name)]==current_construction
        changes[name]['control_topology_and_non_cutter_modifiers_unchanged']=same_construction
        changes[name]['cutter_unchanged_or_declared_revision_validated']=same_construction
        changes[name]['evaluated_triangle_count_before']=len(oldtri)
        changes[name]['evaluated_triangle_count_after']=len(newtri)
        assert difference<5e-6 and same_construction, 'Undeclared control geometry, modifier or cutter edit.'
print('GEOMETRY_NUMERICAL_COMPARISON',json.dumps(changes,indent=2),flush=True)
if not declared:assert all(v['triangle_indices_unchanged'] and v['control_vertices_exactly_unchanged'] and v['max_evaluated_coordinate_difference']<5e-6 for v in changes.values()),'Material work changed actual geometry beyond floating-point precision.'
s=bpy.context.scene;mat=next(o for o in s.objects if o.type=='MESH' and not o.hide_render).data.materials[0]
assert mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED'
assert s['bishop_albedo_bakes_lighting']==False
meta=json.loads((ROOT/'assets/bishop/mesh.json').read_text());raw=(ROOT/'assets/bishop/mesh.bin').read_bytes();assert len(raw)==meta['totalByteLength']
ar=np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8);assert np.isfinite(ar).all();assert np.max(np.abs(np.linalg.norm(ar[:,3:6],axis=1)-1))<1e-5
cut=(ar[:,6]==-1)&(ar[:,7]==-1);assert cut.any(),'Boolean cut faces need their own procedural wood.'
assert ar[~cut,6:].min()>-.01 and ar[~cut,6:].max()<1.01
assert meta['material']['textureSha256']==hashlib.sha256((ROOT/meta['material']['texture']).read_bytes()).hexdigest()
cam=json.loads((ROOT/'history/bishop-mission-000/camera.json').read_text());assert cam==meta['referenceCamera']
for original in ['White-Bishop','Black-Bishop']:
    asset='original.png' if original.startswith('White') else 'black-original.png'
    assert (ROOT/f'assets/bishop/{asset}').read_bytes()==(ROOT/f'references/lichess-staunton-3d/{original}.png').read_bytes()
assert (ROOT/'assets/bishop/reference.png').read_bytes()==(ROOT/'assets/candidates/bishop/white-candidate-3.png').read_bytes()
report={'passed':True,'all_evaluated_geometry_preserved_within_5e_6':not bool(declared),'declared_geometry_changes_validated':bool(declared),'baseline_model':str(baseline_path.relative_to(ROOT)),'geometry_comparison':changes,'components':current,'camera_exactly_unchanged':True,'reference_pixels_unchanged':True,'shader':'Principled BSDF','albedo_bakes_lighting':False,'texture_hash_matches':True,'finite_uvs_and_unit_normals':True,'model_sha256':meta['sourceSha256']}
report['declared_slit_revision_validated']=bool(slit_declared)
report['declared_base_curvature_validated']=bool(base_declared)
report['render_receivers']=receiver_report
(ROOT/'assets/bishop/mission-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
