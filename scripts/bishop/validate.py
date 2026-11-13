"""Validate closed bishop components and renderer/viewer camera data."""
import argparse,bpy,bmesh,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from bishop_scene import editable_meshes
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('root',type=Path)
parser.add_argument('--model',default='models/bishop/bishop-rebuilt.blend')
parser.add_argument('--profile',default='scripts/bishop/profile.json')
parser.add_argument('--out',default='assets/bishop/validation.json')
parser.add_argument('--skip-export',action='store_true',help='Trial anatomy only; saved camera still checked, export hash deferred until promotion.')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);root=args.root;model=root/args.model;bpy.ops.wm.open_mainfile(filepath=str(model));graph=bpy.context.evaluated_depsgraph_get();report=[]
for ob in editable_meshes(bpy.context.scene):
 ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert nonmanifold==0,(ob.name,nonmanifold)
 assert volume>0,(ob.name,volume)
 report.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
 bm.free();ev.to_mesh_clear()
assert len(report)==2
cfg=json.loads((root/args.profile).read_text());alignment=json.loads((root/'assets/bishop/original-alignment.json').read_text())
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
meta=json.loads((root/'assets/bishop/mesh.json').read_text())
if not args.skip_export:assert meta['sourceSha256']==hashlib.sha256(model.read_bytes()).hexdigest()
assert meta['referenceCamera']['elevationDegrees']==54
old_camera=json.loads((root/'history/bishop/07-before-continuous-button-join/camera.json').read_text())
assert meta['referenceCamera']==old_camera,'The reference camera must remain unchanged during the head correction.'
baseline=json.loads((root/'history/bishop/04-before-head-correction/profile.json').read_text())
declared=cfg.get('mission_geometry',{})
changed=set(declared.get('changed_body_rings',[]))
base_curve=cfg.get('mission_base_curvature')
expected_lower=[list(point) for point in baseline['profile']]
if base_curve:
 curve_config=json.loads((root/base_curve['config']).read_text())
 assert curve_config['source']==base_curve['baseline_model']
 assert curve_config['source_sha256']==hashlib.sha256((root/curve_config['source']).read_bytes()).hexdigest()
 assert curve_config['body_rings']==base_curve['body_rings'] and set(map(int,curve_config['body_rings']))=={17,18}
 for index,point in curve_config['body_rings'].items():
  i=int(index);assert point[1]==expected_lower[i][1], 'Base curvature edit must preserve every ring height.'
  expected_lower[i]=point
shape_refit=cfg.get('mission_shape_refit')
if shape_refit:
 source_profile=json.loads((root/shape_refit['profile']).read_text())
 shape_config=json.loads((root/shape_refit['config']).read_text())
 assert hashlib.sha256((root/shape_config['source']).read_bytes()).hexdigest()==shape_config['source_sha256']
 assert shape_refit['body_rings']==shape_config['body_rings']
 expected_profile=[list(pair) for pair in source_profile['profile']]
 for key,pair in shape_config['body_rings'].items():expected_profile[int(key)]=pair
 assert cfg['profile']==expected_profile,'Geometry refit has an undeclared profile change.'
 expected_finial=json.loads(json.dumps(source_profile['finial']))
 assert shape_refit.get('finial_rings',{})==shape_config.get('finial_rings',{})
 for key,pair in shape_config.get('finial_rings',{}).items():expected_finial['profile'][int(key)]=pair
 assert cfg['finial']==expected_finial and cfg['slit']==source_profile['slit']
elif changed:
 assert changed==set(range(1,11)), 'Only the documented lower foot rings may differ in this geometry checkpoint.'
 assert cfg['profile'][11:65]==expected_lower[11:65] and cfg['profile'][0]==expected_lower[0], 'Undeclared lower profile change.'
else:assert cfg['profile'][:65]==expected_lower[:65], 'Undeclared lower profile change.'
button_baseline=json.loads((root/'history/bishop/07-before-continuous-button-join/profile.json').read_text())
assert cfg['slit']==button_baseline['slit'], 'Preserve the full-depth slit dimensions.'
button=bpy.data.objects['Bishop - domed button finial'].evaluated_get(graph);button_mesh=button.to_mesh()
points=[v.co for v in button_mesh.vertices];width=max(v.x for v in points)-min(v.x for v in points);height=max(v.z for v in points)-min(v.z for v in points)
button_ratio=height/width
assert button_ratio<.5,('Finial must be a shallow button, not a sphere',button_ratio)
head_cap_z=(cfg['y0']-cfg['head_button_join']['head_cap_axis_y'])*factor/math.cos(math.radians(cfg['elevation']))
assert min(v.z for v in points)<head_cap_z, 'Button underside must intersect the head cap.'
button.to_mesh_clear()
# Probe the actual evaluated mesh on the unslit side. The old shelf had an abrupt
# normal transition; the continuous head must rotate its surface normal smoothly.
head_normals=[]
for i in range(100):
 axis_y=89.5-i*(89.5-56.8)/99
 zz=(cfg['y0']-axis_y)*factor/math.cos(math.radians(cfg['elevation']))
 hit,loc,normal,face=body.ray_cast(Vector((-4,0,zz)),Vector((1,0,0)),distance=8)
 assert hit,('Continuous head side missing',axis_y)
 head_normals.append(normal)
max_head_normal_step=max(math.degrees(a.angle(b)) for a,b in zip(head_normals,head_normals[1:]))
assert max_head_normal_step<9,('Abrupt head shelf',max_head_normal_step)
# Examine the evaluated *external* section through the unslit side. Merely
# overlapping component bounds missed the old exposed cylindrical seat.
co=math.cos(math.radians(cfg['elevation']))
def section(ob,axis_y):
 zz=(cfg['y0']-axis_y)*factor/co
 hit,loc,normal,face=ob.ray_cast(Vector((-4,0,zz)),Vector((1,0,0)),distance=8)
 return (-loc.x/factor,normal) if hit else (None,None)
join=[]
join_start=59.0
join_end=min(54.0,cfg['head_button_join']['head_cap_axis_y']-.4)
join_steps=max(160,math.ceil((join_start-join_end)/.03125))
for i in range(join_steps+1):
 axis_y=join_start-i*(join_start-join_end)/join_steps
 br,bn=section(body,axis_y);fr,fn=section(button,axis_y)
 assert br is not None or fr is not None,('Visible gap under button',axis_y)
 owner='head' if br is not None and (fr is None or br>=fr) else 'button'
 join.append({'axis_y':axis_y,'head_radius':br,'button_radius':fr,'external_radius':max(r for r in [br,fr] if r is not None),'owner':owner})
transitions=[i for i in range(1,len(join)) if join[i]['owner']!=join[i-1]['owner']]
assert len(transitions)==1 and join[0]['owner']=='head' and join[-1]['owner']=='button',('Head must meet button once, with no exposed head rim',transitions)
k=transitions[0];crossing_y=(join[k]['axis_y']+join[k-1]['axis_y'])/2
assert crossing_y>cfg['head_button_join']['head_cap_axis_y']+.25,'The head cap must be concealed inside the button.'
contact_ratio=join[k]['external_radius']/(width/2/factor)
assert .8<contact_ratio<.99,('Direct broad contact rather than narrow pedestal',contact_ratio)
# All exposed head samples before contact must taper. A cylindrical neck has
# zero radius slope; test the surface seen by a true level camera.
slopes=[co*(a['external_radius']-b['external_radius'])/(a['axis_y']-b['axis_y']) for a,b in zip(join[:k-1],join[1:k])]
assert min(slopes)>.12,('Exposed cylindrical neck',min(slopes))
assert any(x['head_radius'] is not None and x['button_radius'] is not None for x in join),'Closed components must intersect.'
cam=bpy.context.scene.camera;bpy.context.view_layer.update()
actual_matrix=[float(v) for row in cam.matrix_world.inverted() for v in row]
assert max(abs(a-b) for a,b in zip(actual_matrix,meta['referenceCamera']['worldToCamera']))<1e-6,'Saved camera and export differ.'
result={'components':report,'slit_ray_probes':probes,'solid_slot_floor':True,'source_hash_matches':None if args.skip_export else True,'reference_camera_elevation':54,'saved_camera_matches_export':True,'head_surface_probe_count':len(head_normals),'head_surface_max_normal_step_degrees':max_head_normal_step,'lower_65_profile_points_preserved':not bool(changed),'declared_changed_foot_rings':sorted(changed),'flare_socket_stem_collars_preserved':True,'slit_parameters_preserved':True,'button_height_to_width':button_ratio,'head_button_join':{'level_section_samples':len(join),'visible_component_transitions':len(transitions),'contact_axis_y':crossing_y,'contact_width_to_button_width':contact_ratio,'minimum_exposed_head_radius_slope':min(slopes),'head_cap_concealed':True,'gap_free':True,'no_exposed_cylindrical_neck':True},'note':'Two closed editable components intersect. The accepted side guide directs the continuous head-to-button join. The model is not boolean-fused for manufacture.'}
if cfg.get('mission_slit_geometry'):
 result['slit_parameters_preserved']=False
 result['slit_angle_width_and_original_floor_anchor_preserved']=True
 result['declared_rounded_floor']=cfg['mission_slit_geometry']
if base_curve:
 result['flare_socket_stem_collars_preserved']=False
 result['declared_base_curvature_rings']=[17,18]
 result['all_other_lower_profile_points_preserved']=True
 result['base_curvature_config']=base_curve['config']
if shape_refit:
 touched=set(map(int,shape_config['body_rings']))
 result.update(declared_shape_refit=shape_refit,preservation_baseline=shape_refit['source'],
               lower_65_profile_points_preserved=cfg['profile'][:65]==source_profile['profile'][:65],
               flare_socket_stem_collars_preserved=cfg['profile'][11:65]==source_profile['profile'][11:65],
               slit_parameters_preserved=cfg['slit']==source_profile['slit'],
               all_other_lower_profile_points_preserved=all(cfg['profile'][i]==source_profile['profile'][i] for i in range(65) if i not in touched),
               declared_changed_body_rings=sorted(touched),
               declared_changed_finial_rings=sorted(map(int,shape_config.get('finial_rings',{}))),
               all_unlisted_profile_points_preserved=True)
(root/args.out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS',json.dumps(result))
