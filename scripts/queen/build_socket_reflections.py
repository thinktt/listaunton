"""Test isolated socket reflections on exact copies of the same closed surface."""
from pathlib import Path
import sys,json,hashlib,math,argparse
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import partition,link
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=='358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);cam=s.camera
cfg=json.loads(s['mission_material_config']);coordinates=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coordinates)
control_hash=hashlib.sha256(coordinates.tobytes()).hexdigest()
for o in s.objects:
    if o.type=='LIGHT':o.light_linking.receiver_collection=None
for o in list(s.objects):
    if o.get('mission_render_region'):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith(('Queen render regions','Receivers ')):bpy.data.collections.remove(c)
parts,report=partition(s,obj,socket_band=True);byname={o['mission_render_region']:o for o in parts}
excluded=['Display fitted '+name for name in ['base-key','upper-right','collars-right','foot-right','finial-right','lower-right']]
disabled=['Display fitted '+name for name in ['socket-right','socket-left','socket-left-precise']]
for spec in cfg['lights']:
    if spec['name'] in disabled:spec['energy']=0;bpy.data.objects[spec['name']].data.energy=0
    if spec.get('diffuse_factor',1)==0 and not ('finial-' in spec['name'] and spec['name'].endswith('-spot')):
        names=['turned-body'] if spec['name'] in excluded else ['turned-body','stem-socket']
        spec['receiver_parts']=names;link(bpy.data.objects[spec['name']],[byname[n] for n in names],'+'.join(names))
for part in parts:part.hide_set(True)
cfg['finial_receiver_isolation']['render_regions']=report
cfg['stem_socket_receiver_isolation']={'source_sha256':digest,'closed_controls_sha256':control_hash,'z_interval':[.83,2.78],
 'excluded_reflectors':excluded,'disabled_socket_lights':disabled,'method':'Exact evaluated face partition with unchanged positions, UVs, normals and material. Exclude the measured stray reflectors only from stem/socket; preserve their action everywhere else.'}
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True;bpy.context.preferences.filepaths.save_version=0
def save(variant):
    cfg['variant']=variant;s['mission_material_config']=json.dumps(cfg);s['mission_variant']=variant
    out=ROOT/'build/queen-mission'/variant;out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('SOCKET_TRIAL_DONE',variant,flush=True)
save('134-isolated-socket')
# Aim overlapping real emitters along the two observed crescent segments.
for m in obj.modifiers:
    if m.type=='SUBSURF':m.levels=m.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
v=np.array([tuple(a.co) for a in mesh.vertices]);n=np.array([tuple(a.normal) for a in mesh.vertices]);tris=np.array([tuple(a.vertices) for a in mesh.loop_triangles])
tree=BVHTree.FromPolygons(v.tolist(),tris.tolist(),all_triangles=True)
W=s.render.resolution_x;H=s.render.resolution_y;inv=(cam.calc_matrix_camera(graph,x=W,y=H)@cam.matrix_world.inverted()).inverted()
view=cam.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
targets=[(384,738),(400,747),(418,754),(438,760),(456,764),(515,757),(532,751),(548,744),(562,735),(575,723)]
specs=[]
for i,(x,y) in enumerate(targets):
    near=inv@Vector((2*x/W-1,1-2*y/H,-1,1));near=near.xyz/near.w
    loc,_,idx,_=tree.ray_cast(near,-view,100);assert loc is not None and .83<loc.z<2.78
    tri=tris[idx];a,b,c=v[tri];uv=np.linalg.lstsq(np.column_stack((b-a,c-a)),np.array(loc)-a,rcond=None)[0]
    normal=Vector(n[tri[0]]*(1-sum(uv))+n[tri[1]]*uv[0]+n[tri[2]]*uv[1]);normal.normalize()
    direction=2*normal.dot(view)*normal-view;position=loc+direction*6
    name='Socket crescent %02d'%i;data=bpy.data.lights.new(name,'SPOT');data.energy=400;data.color=(1,.7,.5)
    data.shadow_soft_size=.04;data.spot_size=math.radians(1.7);data.spot_blend=.85
    o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=position;o.rotation_euler=(loc-position).to_track_quat('-Z','Y').to_euler()
    o.visible_diffuse=False;o.visible_glossy=True;link(o,[byname['stem-socket']],'stem-socket')
    spec={'name':name,'position':list(position),'target':list(loc),'target_pixel':[x,y],'type':'SPOT','energy':400,'size':.08,'spot_degrees':1.7,'spot_blend':.85,'color':[1,.7,.5],'diffuse_factor':0,'receiver_parts':['stem-socket']}
    specs.append(spec);cfg['lights'].append(spec);cfg['finial_receiver_isolation']['excluded_reflectors'].append(name)
ev.to_mesh_clear();cfg['socket_crescent']={'targets':targets,'method':'Overlapping physical spot emitters placed on reflected view rays; no geometry or material change.'}
save('135-socket-crescent')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
