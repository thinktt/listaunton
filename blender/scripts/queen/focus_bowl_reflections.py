"""Aim confined real specular lights at the reference bowl glints."""
from pathlib import Path
import sys,json,hashlib,math,argparse
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import link
p=argparse.ArgumentParser();p.add_argument('--arc',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/'history/queen-mission-010/queen-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='6bbc7d1dbeffd54e846895eb1f9f3854092c8b57d4267fa49c621e7f67e74325'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;obj=editable_mesh(s);cam=s.camera
for m in obj.modifiers:
 if m.type=='SUBSURF':m.levels=m.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
v=np.array([tuple(v.co) for v in mesh.vertices]);n=np.array([tuple(v.normal) for v in mesh.vertices]);tris=np.array([tuple(t.vertices) for t in mesh.loop_triangles]);tree=BVHTree.FromPolygons(v.tolist(),tris.tolist(),all_triangles=True)
W=s.render.resolution_x;H=s.render.resolution_y;inv=(cam.calc_matrix_camera(graph,x=W,y=H)@cam.matrix_world.inverted()).inverted();view=cam.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
body=next(o for o in s.objects if o.get('mission_render_region')=='turned-body')
cfg=json.loads(s['mission_material_config']);disabled=['Display fitted bowl-left','Display fitted bowl-back','Display fitted bowl-arc']
for name in disabled:
 bpy.data.objects[name].data.energy=0
 for spec in cfg['lights']:
  if spec['name']==name:spec['energy']=0
specs=[]
targets=[('Bowl focused left',428,168,5500),('Bowl focused rear',505,148,8500)]
if args.arc:
 targets=[('Bowl focused left-0',415,175,100),('Bowl focused left-1',423,170,155),('Bowl focused left-2',432,165,135),('Bowl focused left-3',446,159,60),('Bowl focused rear-0',490,145,110),('Bowl focused rear-1',501,146,250),('Bowl focused rear-2',510,148,220),('Bowl focused rear-3',522,152,105)]
size=.025 if args.arc else .6;degrees=.75 if args.arc else 2.8
for name,x,y,power in targets:
 near=inv@Vector((2*x/W-1,1-2*y/H,-1,1));near=near.xyz/near.w
 loc,_,idx,_=tree.ray_cast(near,-view,100);assert loc is not None
 tri=tris[idx];a,b,c=v[tri];uv=np.linalg.lstsq(np.column_stack((b-a,c-a)),np.array(loc)-a,rcond=None)[0]
 normal=Vector(n[tri[0]]*(1-sum(uv))+n[tri[1]]*uv[0]+n[tri[2]]*uv[1]);normal.normalize()
 direction=2*normal.dot(view)*normal-view;position=loc+direction*6
 data=bpy.data.lights.new(name,'SPOT');data.energy=power;data.color=(1,.7,.5);data.shadow_soft_size=size/2;data.spot_size=math.radians(degrees);data.spot_blend=.8
 o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=position;o.rotation_euler=(loc-position).to_track_quat('-Z','Y').to_euler();o.visible_diffuse=False;o.visible_glossy=True;link(o,[body],'turned-body')
 spec={'name':name,'position':list(position),'target':list(loc),'target_pixel':[x,y],'type':'SPOT','energy':power,'size':size,'spot_degrees':degrees,'spot_blend':.8,'color':[1,.7,.5],'diffuse_factor':0,'receiver_parts':['turned-body']}
 specs.append(spec);cfg['lights'].append(spec);cfg['finial_receiver_isolation']['excluded_reflectors'].append(name)
ev.to_mesh_clear()
s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.context.preferences.filepaths.save_version=0
cases=[('108-shaped-bowl-arcs',1),('109-soft-bowl-arcs',.6)] if args.arc else [('100-focused-bowl',1),('101-soft-focused-bowl',.4)]
for variant,gain in cases:
 for spec in specs:bpy.data.objects[spec['name']].data.energy=spec['energy']*gain
 current=json.loads(json.dumps(cfg))
 for spec in current['lights']:
  if spec['name'].startswith('Bowl focused'):spec['energy']*=gain
 current['variant']=variant;current['bowl_reflection_trial']={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'disabled_lights':disabled,'gain':gain,'method':'Physical spot lights aimed by reflected camera rays at reference glints; material and geometry unchanged.','arc_preset':args.arc}
 s['mission_material_config']=json.dumps(current);s['mission_variant']=variant
 out=ROOT/'build/queen-mission'/variant;out.mkdir(exist_ok=True,parents=True)
 s.render.filepath=str(out/'wood.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
 (out/'parameters.json').write_text(json.dumps(current,indent=2));print('BOWL_TRIAL_DONE',variant,flush=True)
