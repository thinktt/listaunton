"""Material-iteration invariants supplement the bishop anatomy validator."""
import bpy,json,hashlib,sys
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
buffers={}
def geometry(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);bpy.context.view_layer.update();g=bpy.context.evaluated_depsgraph_get();res={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or ob.hide_render:continue
        ev=ob.evaluated_get(g);me=ev.to_mesh();me.calc_loop_triangles()
        pos=np.array([tuple(v.co) for v in me.vertices],dtype='<f4');tris=np.array([tuple(t.vertices) for t in me.loop_triangles],dtype='<i4')
        buffers[(str(path),ob.name)]=(pos.copy(),tris.copy(),np.array([tuple(v.co) for v in ob.data.vertices],dtype='<f4'))
        assert np.isfinite(pos).all()
        # Boolean material slots can reorder vertices. Compare actual positions
        # and spatial triangles, independent of their storage indices.
        order=np.lexsort(pos.T[::-1]);sorted_pos=pos[order]
        corners=pos[tris].copy()
        for i in range(len(corners)):corners[i]=corners[i][np.lexsort(corners[i].T[::-1])]
        flat=corners.reshape(-1,9);flat=flat[np.lexsort(flat.T[::-1])]
        res[ob.name]={'positions':hashlib.sha256(sorted_pos.tobytes()).hexdigest(),'triangles':hashlib.sha256(flat.tobytes()).hexdigest(),'vertex_count':len(pos),'triangle_count':len(tris)};ev.to_mesh_clear()
    return res
baseline=geometry(ROOT/'history/bishop-mission-000/bishop-rebuilt.blend')
current=geometry(ROOT/'models/bishop/bishop-rebuilt.blend')
changes={}
for name in baseline:
    old,oldtri,oldcontrol=buffers[(str(ROOT/'history/bishop-mission-000/bishop-rebuilt.blend'),name)]
    new,newtri,newcontrol=buffers[(str(ROOT/'models/bishop/bishop-rebuilt.blend'),name)]
    diff=float(np.max(np.abs(new-old)));same_tri=bool(np.array_equal(oldtri,newtri));same_control=bool(np.array_equal(oldcontrol,newcontrol))
    changes[name]={'max_evaluated_coordinate_difference':diff,'triangle_indices_unchanged':same_tri,'control_vertices_exactly_unchanged':same_control}
print('GEOMETRY_NUMERICAL_COMPARISON',json.dumps(changes,indent=2),flush=True)
assert all(v['triangle_indices_unchanged'] and v['control_vertices_exactly_unchanged'] and v['max_evaluated_coordinate_difference']<5e-6 for v in changes.values()),'Material work changed actual geometry beyond floating-point precision.'
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
report={'passed':True,'all_evaluated_geometry_preserved_within_5e_6':True,'geometry_comparison':changes,'components':current,'camera_exactly_unchanged':True,'reference_pixels_unchanged':True,'shader':'Principled BSDF','albedo_bakes_lighting':False,'texture_hash_matches':True,'finite_uvs_and_unit_normals':True,'model_sha256':meta['sourceSha256']}
(ROOT/'assets/bishop/mission-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
