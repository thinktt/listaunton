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
baseline=json.loads((root/'history/bishop/04-before-head-correction/profile.json').read_text())
assert cfg['profile'][:65]==baseline['profile'][:65], 'Lower collars, stem and base must be preserved.'
button_baseline=json.loads((root/'history/bishop/06-before-button-correction/profile.json').read_text())
assert cfg['profile']==button_baseline['profile'] and cfg['slit']==button_baseline['slit'], 'Preserve the corrected continuous head, lower body and full-depth slit.'
button=bpy.data.objects['Bishop - domed button finial'].evaluated_get(graph);button_mesh=button.to_mesh()
points=[v.co for v in button_mesh.vertices];width=max(v.x for v in points)-min(v.x for v in points);height=max(v.z for v in points)-min(v.z for v in points)
button_ratio=height/width
assert button_ratio<.5,('Finial must be a shallow button, not a sphere',button_ratio)
head_cap_z=(cfg['y0']-57.5)*factor/math.cos(math.radians(cfg['elevation']))
assert min(v.z for v in points)<head_cap_z, 'Button seat must intersect the head cap.'
button.to_mesh_clear()
# Probe the actual evaluated mesh on the unslit side. The old shelf had an abrupt
# normal transition; the continuous head must rotate its surface normal smoothly.
head_normals=[]
for i in range(80):
 axis_y=89.5-i*(89.5-59.0)/79
 zz=(cfg['y0']-axis_y)*factor/math.cos(math.radians(cfg['elevation']))
 hit,loc,normal,face=body.ray_cast(Vector((-4,0,zz)),Vector((1,0,0)),distance=8)
 assert hit,('Continuous head side missing',axis_y)
 head_normals.append(normal)
max_head_normal_step=max(math.degrees(a.angle(b)) for a,b in zip(head_normals,head_normals[1:]))
assert max_head_normal_step<9,('Abrupt head shelf',max_head_normal_step)
(root/'assets/bishop/validation.json').write_text(json.dumps({'components':report,'slit_ray_probes':probes,'solid_slot_floor':True,'source_hash_matches':True,'reference_camera_elevation':54,'head_surface_probe_count':len(head_normals),'head_surface_max_normal_step_degrees':max_head_normal_step,'lower_profile_preserved':True,'corrected_head_and_slit_preserved':True,'button_height_to_width_including_seat':button_ratio,'button_seated_in_head':True,'note':'Two closed editable components, continuous rounded mitre body with open slot, and domed button. Button seat intersects the mitre; not boolean-fused for manufacture.'},indent=2));print('PASS',report,probes,'head max normal step',max_head_normal_step,'button height/width',button_ratio)
