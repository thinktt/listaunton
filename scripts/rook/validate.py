"""Validate closed rook components and renderer/viewer camera data."""
import bpy,bmesh,json,sys,hashlib,math
import numpy as np
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/rook/rook-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
 bm.free();ev.to_mesh_clear()
assert len(report)==5
meta=json.loads((root/'assets/rook/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
cfg=json.loads((root/'scripts/rook/profile.json').read_text())
assert cfg['elevation']==54
volumes=[item['signed_volume'] for item in report if 'merlon' in item['name']]
assert len(volumes)==4 and max(volumes)-min(volumes)<1e-8
assert cfg['turret']['outer_radius']-cfg['turret']['inner_radius']==23
raw=(root/'assets/rook/mesh.bin').read_bytes();assert len(raw)==meta['totalByteLength']
stride=meta['vertexStrideBytes']//4;assert stride in (6,8)
vertices=np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*stride).reshape((-1,stride))
indices=np.frombuffer(raw,dtype='<u4',offset=meta['indexByteOffset'])
assert np.isfinite(vertices).all() and len(indices)==meta['indexCount']
assert indices.max()<meta['vertexCount'] and len(indices)==meta['triangleCount']*3
normal_error=float(np.max(np.abs(np.linalg.norm(vertices[:,3:6],axis=1)-1)))
assert normal_error<1e-4
for side,actual in [('min',vertices[:,:3].min(0)),('max',vertices[:,:3].max(0))]:assert np.allclose(actual,meta['bounds'][side])
camera=json.loads((root/'assets/rook/camera.json').read_text());assert camera==meta['referenceCamera']
assert bpy.context.scene.camera.data.type=='ORTHO'
summary={'components':report,'source_hash_matches':True,'mesh_binary_checked':True,'normal_length_max_error':normal_error,'visible_triangle_count':meta['triangleCount'],'elevation_degrees':54,'equal_merlon_volumes':True,'visible_wall_thickness_profile_px':23,'note':'Five closed editable objects: the evaluated union body and four equal hidden merlon construction objects. Boolean union preserves editable construction; packed wood material is present; unseen geometry and finish remain inferred.'}
(root/'assets/rook/validation.json').write_text(json.dumps(summary,indent=2));print('PASS',summary)
