"""Validate closed knight components and renderer/viewer camera data."""
import bpy,bmesh,json,sys,hashlib
import numpy as np
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/knight/knight-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces),'hidden_construction':ob.hide_render})
 bm.free();ev.to_mesh_clear()
assert len(report)==9
assert sum(not item['hidden_construction'] for item in report)==7
meta=json.loads((root/'assets/knight/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
raw=(root/'assets/knight/mesh.bin').read_bytes();assert len(raw)==meta['totalByteLength']
vertices=np.frombuffer(raw[:meta['vertexByteLength']],dtype='<f4').reshape(-1,6);indices=np.frombuffer(raw[meta['indexByteOffset']:],dtype='<u4')
assert np.isfinite(vertices).all();assert len(indices)==meta['indexCount'];assert int(indices.max())<len(vertices)
assert np.max(np.abs(np.linalg.norm(vertices[:,3:],axis=1)-1))<1e-4
assert len(meta['parts'])==7
assert sum(part['vertexCount'] for part in meta['parts'])==meta['vertexCount']
assert np.allclose(vertices[:,:3].min(0),meta['bounds']['min'])
assert np.allclose(vertices[:,:3].max(0),meta['bounds']['max'])
assert np.allclose(np.array(meta['referenceCamera']['worldToCamera']).reshape(4,4),np.array(bpy.context.scene.camera.matrix_world.inverted()),atol=1e-7)
(root/'assets/knight/validation.json').write_text(json.dumps({'components':report,'source_hash_matches':True,'mesh_finite':True,'bounds_match':True,'normals_unit_length':True,'camera_matches_saved_blend':True,'visible_component_count':7,'hidden_construction_count':2,'note':'One continuous skull, cheek and conical muzzle envelope joins the neck; two closed construction lofts remain hidden. Mane, ears, eyes and pedestal are separate overlapping closed parts. Artistic reconstruction, not prepared for manufacture.'},indent=2));print('PASS',report)
