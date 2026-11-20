"""Validate the editable pawn, exported geometry and unchanged reference bytes."""
import bpy,bmesh,json,sys,hashlib,math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]) if args else Path(__file__).resolve().parents[2]
model=root/'models/pawn/pawn-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 seen=set();components=0
 for v in bm.verts:
  if v in seen:continue
  components+=1;stack=[v];seen.add(v)
  while stack:
   curr=stack.pop()
   for e in curr.link_edges:
    other=e.other_vert(curr)
    if other not in seen:seen.add(other);stack.append(other)
 euler=len(bm.verts)-len(bm.edges)+len(bm.faces)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0 and components==1 and euler==2,(ob.name,volume,components,euler)
 assert all(math.isfinite(c) for v in bm.verts for c in v.co)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'connected_components':components,'euler_characteristic':euler,'vertices':len(bm.verts),'faces':len(bm.faces)})
 bm.free();ev.to_mesh_clear()
assert len(report)==1
meta=json.loads((root/'assets/pawn/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
assert meta['referenceCamera']['elevationDegrees']==54
packed=[im.name for im in bpy.data.images if im.packed_file]
assert set(['reference.png','original.png','white-original.png']).issubset(packed)
references={}
for copied,source in [('original.png','references/lichess-staunton-3d/Black-Pawn.png'),('white-original.png','references/lichess-staunton-3d/White-Pawn.png'),('reference.png','assets/candidates/pawn/candidate-2.png')]:
 a=(root/'assets/pawn'/copied).read_bytes();b=(root/source).read_bytes();assert a==b;references[copied]=hashlib.sha256(a).hexdigest()
# The editable meridian must not cross itself. Adjacent segments share endpoints.
body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render)
profile=[(math.hypot(v.co.x,v.co.y),v.co.z) for v in list(body.data.vertices)[::96]]
def orientation(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
for i,(a,b) in enumerate(zip(profile,profile[1:])):
 for j in range(i+2,len(profile)-1):
  c,d=profile[j:j+2]
  assert not (orientation(a,b,c)*orientation(a,b,d)<-1e-10 and orientation(c,d,a)*orientation(c,d,b)<-1e-10),('Crossing meridian',i,j)
result={'components':report,'source_hash_matches':True,'reference_camera_elevation':54,'packed_references':packed,'unchanged_reference_hashes':references,'meridian_self_crossings':0,'note':'One connected closed editable lathe, including head, saucer collar and full base. Subdivision remains editable. Unseen underside inferred as closed flat base.'}
(root/'assets/pawn/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
