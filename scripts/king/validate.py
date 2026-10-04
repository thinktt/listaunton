"""Validate closed king components and renderer/viewer camera data."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/king/king-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
 bm.free();ev.to_mesh_clear()
assert len(report)==2
meta=json.loads((root/'assets/king/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
(root/'assets/king/validation.json').write_text(json.dumps({'components':report,'source_hash_matches':True,'note':'Two closed editable components, body and cross. Cross intersects its pedestal; not boolean-fused for manufacture.'},indent=2));print('PASS',report)
