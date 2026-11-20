"""Validate closed knight components and renderer/viewer camera data."""
import bpy,bmesh,json,sys,hashlib
from mathutils.bvhtree import BVHTree
import numpy as np
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/knight/knight-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 unseen=set(bm.verts);connected=0
 while unseen:
  connected+=1;stack=[unseen.pop()]
  while stack:
   v=stack.pop()
   for edge in v.link_edges:
    other=edge.other_vert(v)
    if other in unseen:unseen.remove(other);stack.append(other)
 assert connected==1,(ob.name,connected)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'connected_components':connected,'vertices':len(bm.verts),'faces':len(bm.faces),'hidden_construction':ob.hide_render})
 bm.free();ev.to_mesh_clear()
assert len(report)==9
assert sum(not item['hidden_construction'] for item in report)==7
meta=json.loads((root/'assets/knight/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
raw=(root/'assets/knight/mesh.bin').read_bytes();assert len(raw)==meta['totalByteLength']
stride=meta['vertexStrideBytes']//4
assert stride in (6,8)
vertices=np.frombuffer(raw[:meta['vertexByteLength']],dtype='<f4').reshape(-1,stride);indices=np.frombuffer(raw[meta['indexByteOffset']:],dtype='<u4')
assert np.isfinite(vertices).all();assert len(indices)==meta['indexCount'];assert int(indices.max())<len(vertices)
assert np.max(np.abs(np.linalg.norm(vertices[:,3:6],axis=1)-1))<1e-4
if stride==8:
 assert np.all((vertices[:,6:]>=-.0001)&(vertices[:,6:]<=1.0001))
 texture=root/meta['texture'];assert hashlib.sha256(texture.read_bytes()).hexdigest()==meta['textureSha256']
 visible=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
 for ob in visible:
  mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');atlas=bs.inputs['Base Color'].links[0].from_node
  assert atlas.type=='TEX_IMAGE' and atlas.image.packed_file and bytes(atlas.image.packed_file.data)==texture.read_bytes()
  assert atlas.inputs['Vector'].links[0].from_node.uv_map==meta['uvLayer']
assert len(meta['parts'])==7
assert sum(part['vertexCount'] for part in meta['parts'])==meta['vertexCount']
if 'finish' in meta:
 finish=meta['finish'];packed=(root/finish['file']).read_bytes()
 assert hashlib.sha256(packed).hexdigest()==finish['sha256'] and len(packed)==len(vertices)
 values=np.frombuffer(packed,np.uint8)
 for part in meta['parts']:
  ob=bpy.data.objects[part['name']].evaluated_get(graph);me=ob.to_mesh()
  attr=me.attributes[finish['attribute']]
  coverage=np.empty(len(me.vertices),np.float32);attr.data.foreach_get('value',coverage)
  block=values[part['vertexOffset']:part['vertexOffset']+part['vertexCount']]
  assert block.min()==round(float(coverage.min())*255) and block.max()==round(float(coverage.max())*255)
  ob.to_mesh_clear()
assert np.allclose(vertices[:,:3].min(0),meta['bounds']['min'])
assert np.allclose(vertices[:,:3].max(0),meta['bounds']['max'])
assert np.allclose(np.array(meta['referenceCamera']['worldToCamera']).reshape(4,4),np.array(bpy.context.scene.camera.matrix_world.inverted()),atol=1e-7)
cam=bpy.context.scene.camera
assert np.allclose(np.array(meta['referenceCamera']['projectionMatrix']).reshape(4,4),np.array(cam.calc_matrix_camera(graph,x=1254,y=1254)),atol=1e-7)
def world_mesh(obj):
 evaluated=obj.evaluated_get(graph)
 mesh=bmesh.new()
 mesh.from_mesh(evaluated.data)
 mesh.transform(evaluated.matrix_world)
 mesh.normal_update()
 return mesh

skin=world_mesh(bpy.data.objects['Knight | continuous horse head and neck'])
tree=BVHTree.FromBMesh(skin)
eyes=[]
for name in ('near','far'):
 eye=world_mesh(bpy.data.objects[f'Knight | {name} eye'])
 intersections=tree.overlap(BVHTree.FromBMesh(eye))
 assert intersections,(name,'eye surface does not intersect the head')
 # An editable object's origin can stay at its old position after sculpting.
 # Check the exposed lens and its buried seat on the evaluated carving.
 depths=[]
 for vertex in eye.verts:
  hit,normal,_,_=tree.find_nearest(vertex.co)
  depths.append((vertex.co-hit).dot(normal))
 buried=sum(d < -1e-5 for d in depths)
 exposed=sum(d > 1e-5 for d in depths)
 assert buried and exposed,(name,buried,exposed)
 eyes.append({'name':name,'seated_in_surface':True,'intersecting_face_pairs':len(intersections),
              'buried_vertices':buried,'exposed_vertices':exposed,'max_inset':-min(depths),
              'max_exposure':max(depths)})
 eye.free()
skin.free()
(root/'assets/knight/validation.json').write_text(json.dumps({'components':report,'eyes':eyes,'source_hash_matches':True,'mesh_finite':True,'bounds_match':True,'normals_unit_length':True,'camera_matches_saved_blend':True,'visible_component_count':7,'hidden_construction_count':2,'note':'One continuous broad skull, cheek and rounded gently conical muzzle envelope joins the neck; two closed construction lofts remain hidden. Mane, ears, eyes and pedestal are separate overlapping closed parts. Artistic reconstruction, not prepared for manufacture.'},indent=2));print('PASS',report)
