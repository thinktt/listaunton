"""Validate closed bishop components and renderer/viewer camera data."""
import bpy,bmesh,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[0]);model=root/'models/bishop/bishop-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
 bm.free();ev.to_mesh_clear()
assert len(report)==2
cfg=json.loads((root/'scripts/bishop/profile.json').read_text());alignment=json.loads((root/'assets/bishop/original-alignment.json').read_text())
factor=1254/300/alignment['scale']/cfg['scale'];sl=cfg['slit'];angle=math.radians(sl['angle'])
bottom=(cfg['y0']-sl['bottom_center_y'])*factor/math.cos(math.radians(cfg['elevation']))
body=bpy.data.objects['Bishop - continuous turned body'].evaluated_get(graph)
probes=[]
for dz in [7,12,17]:
 x=(sl['x']+dz*math.tan(angle))*factor;z=bottom+dz*factor
 clear=not body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)),distance=8)[0]
 near=body.ray_cast(Vector((x-6*factor,-4,z)),Vector((0,1,0)),distance=8)[0]
 assert clear and near,('Slit must pass through thickness with material beside it',dz,clear,near)
 probes.append({'height_above_slot_bottom_original_units':dz,'through_slot_clear':clear,'adjacent_material_hit':near})
assert body.ray_cast(Vector((sl['x']*factor,-4,bottom-3*factor)),Vector((0,1,0)),distance=8)[0], 'Slot requires a solid floor.'
meta=json.loads((root/'assets/bishop/mesh.json').read_text());assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
assert meta['referenceCamera']['elevationDegrees']==54
(root/'assets/bishop/validation.json').write_text(json.dumps({'components':report,'slit_ray_probes':probes,'solid_slot_floor':True,'source_hash_matches':True,'reference_camera_elevation':54,'note':'Two closed editable components, turned body with open mitre slot, and finial. Finial intersects the mitre; not boolean-fused for manufacture.'},indent=2));print('PASS',report,probes)
