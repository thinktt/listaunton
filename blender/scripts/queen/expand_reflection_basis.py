"""Add real area lights aimed by surface normals at missing reference glints."""
from pathlib import Path
import hashlib,json,math,shutil,sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/039-rolled-collar-refit/queen.blend'
choices=list((ROOT/'build/queen-mission').glob('specular*039/manifest.json'))
base=next(p.parent for p in choices if len(json.loads(p.read_text())['specs'])==19 and any(s.get('spot_degrees')==1.2 for s in json.loads(p.read_text())['specs']))
manifest=json.loads((base/'manifest.json').read_text());assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
out=ROOT/'build/queen-mission/specular-expanded-039';out.mkdir(parents=True,exist_ok=True)
specs=manifest['specs']
for spec in specs:shutil.copyfile(base/(spec['name']+'.npy'),out/(spec['name']+'.npy'))
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
for mod in o.modifiers:
 if mod.type=='SUBSURF':mod.levels=mod.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
verts=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',verts);verts=verts.reshape(-1,3)
normals=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('normal',normals);normals=normals.reshape(-1,3)
tris=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',tris);tris=tris.reshape(-1,3)
tree=BVHTree.FromPolygons(verts.tolist(),tris.tolist(),all_triangles=True)
camera=s.camera;inverse=(camera.calc_matrix_camera(graph,x=1254,y=1254)@camera.matrix_world.inverted()).inverted();view=camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
targets={'middle-left':(426,501),'upper-right':(543,439),'lower-right':(566,528),'socket-right':(553,764),'socket-left-precise':(432,759),'foot-right':(618,1012),'foot-left-precise':(384,1020),'rim-front-left':(417,325),'rim-front-right':(560,317),'tip-back-left':(412,81),'bowl-inner-front':(484,272),'bowl-inner-left':(428,168)}
added=[]
for name,(x,y) in targets.items():
 near=inverse@Vector((2*x/1254-1,1-2*y/1254,-1,1));near=near.xyz/near.w
 loc,_,idx,_=tree.ray_cast(near,-view,100)
 if loc is None:continue
 tri=tris[idx];a,b,c=verts[tri];uv=np.linalg.lstsq(np.column_stack((b-a,c-a)),np.array(loc)-a,rcond=None)[0]
 normal=Vector(normals[tri[0]]*(1-sum(uv))+normals[tri[1]]*uv[0]+normals[tri[2]]*uv[1]);normal.normalize();direction=2*normal.dot(view)*normal-view
 added.append({'name':name,'position':list(loc+direction*6),'target':list(loc),'energy':300,'size':.5,'target_pixel':[x,y]})
ev.to_mesh_clear()
b=o.data.materials[0].node_tree.nodes.get('Principled BSDF');links=o.data.materials[0].node_tree.links
for link in list(b.inputs['Base Color'].links):links.remove(link)
b.inputs['Base Color'].default_value=(0,0,0,1)
s.render.resolution_x=s.render.resolution_y=418;s.render.resolution_percentage=100;s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for index,spec in enumerate(added):
 for light in list(s.objects):
  if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
 s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
 data=bpy.data.lights.new(spec['name'],'AREA');data.energy=spec['energy'];data.shape='DISK';data.size=spec['size']
 light=bpy.data.objects.new(spec['name'],data);s.collection.objects.link(light);light.location=spec['position'];light.rotation_euler=(Vector(spec['target'])-light.location).to_track_quat('-Z','Y').to_euler()
 path=out/(spec['name']+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(str(path),check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im);np.save(out/(spec['name']+'.npy'),a)
 print('EXPANDED_REFLECTION_BASIS',index+1,len(added),spec['name'],flush=True)
manifest['specs']=specs+added;manifest['reused_from']=base.relative_to(ROOT).as_posix();manifest['method']='Area lights placed on reflected view rays of measured smooth surface normals; actual black-BSDF render basis.'
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
