"""Rebuild the measured rook with Blender; --root overrides project location."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--root')+1]) if '--root' in args else Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/rook';OUT.mkdir(parents=True,exist_ok=True);MODEL=ROOT/'models/rook/rook-rebuilt.blend';MODEL.parent.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'scripts/rook/profile.json').read_text())
S=cfg['scale'];E=math.radians(cfg['elevation']);C=math.cos(E);SN=math.sin(E);CX=cfg['cx'];Y0=cfg['y0'];W=H=1254
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
def material():
 m=bpy.data.materials.new('Satin clay - geometry study');m.diffuse_color=(.28,.30,.34,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.28,.30,.34,1);p.inputs['Roughness'].default_value=.30;return m
mat=material()
def mesh(name,vs,fs,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);ob.data.materials.append(mat)
 for p in me.polygons:p.use_smooth=smooth
 return ob
def z(y):return (Y0-y)/(S*C)
N=128;profile=cfg['profile'];vs=[(r/S*math.cos(i*math.tau/N),r/S*math.sin(i*math.tau/N),z(y)) for r,y in profile for i in range(N)];fs=[]
for j in range(len(profile)-1):
 for i in range(N):k=(i+1)%N;fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
fs+=[tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))]
body=mesh('Rook - continuous turned body and recessed floor',vs,fs);sub=body.modifiers.new('Smooth lathe profile','SUBSURF');sub.levels=1;sub.render_levels=1
parts_objects=[body]
# Four equal curved merlons. Every merlon uses the same inner and outer radii:
# the rear walls cannot be thickened to fake the high-camera silhouette.
d=cfg['turret'];ro=d['outer_radius']/S;ri=d['inner_radius']/S;zt=z(d['top_y']);zb=z(d['notch_y']+d['overlap_px']);gap=math.radians(d['slot_angle_degrees']);az=math.radians(d['azimuth_degrees'])
for merlon in range(4):
 aa=az+merlon*math.pi/2+gap/2;bb=az+(merlon+1)*math.pi/2-gap/2;seg=40
 vs=[(r*math.cos(aa+(bb-aa)*i/seg),r*math.sin(aa+(bb-aa)*i/seg),zz) for zz in [zb,zt] for r in [ri,ro] for i in range(seg+1)];row=seg+1
 fs=[]
 for i in range(seg):
  # inner, outer, bottom, top surfaces
  fs.extend([(i,i+1,2*row+i+1,2*row+i),(row+i,3*row+i,3*row+i+1,row+i+1),(i,row+i,row+i+1,i+1),(2*row+i,2*row+i+1,3*row+i+1,3*row+i)])
 fs.extend([(0,2*row,3*row,row),(seg,row+seg,3*row+seg,2*row+seg)])
 ob=mesh('Rook - thin curved merlon '+str(merlon+1),vs,fs)
 for p in ob.data.polygons:p.use_smooth=p.index<seg*4 and p.index%4<2
 bevel=ob.modifiers.new('Soft carved merlon edges','BEVEL');bevel.width=d['bevel_px']/S;bevel.segments=4;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(20)
 wn=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40
 parts_objects.append(ob)
for ob in parts_objects:
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
# Editable exact unions remove construction seams while keeping the four equal
# merlons accessible as named construction objects in the blend file.
for merlon in parts_objects[1:]:
 mod=body.modifiers.new('Join '+merlon.name,'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=merlon
 merlon.hide_render=True;merlon.hide_set(True)
parts_objects=[body]
reference=bpy.data.images.load(str(OUT/'ref.png'));reference.pack()
world=bpy.data.worlds.new('Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,2.5))
area('Key',(-3,-4,8),650,2.5);area('Fill',(3,-4,5),240,2);area('Rim',(2,3,7),220,3)
d=bpy.data.cameras.new('Reference camera');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=W/S;d.clip_end=100
ZT=(Y0-H/2)/(S*C);cam.location=(0,-12*C,ZT+12*SN);aim(cam,(0,0,ZT));d.shift_x=(W/2-CX)/W
bpy.context.view_layer.update();cam.matrix_world=cam.matrix_world @ Matrix.Rotation(math.radians(cfg.get('roll_degrees',0)),4,'Z')
bg=d.background_images.new();bg.image=reference;bg.alpha=.5;bg.display_depth='FRONT';bg.frame_method='FIT';d.show_background_images=True
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.filepath=str(OUT/'render.png')
scene['reconstruction']='Original-sprite rook reconstruction: uniform thin walls, four crenels and recessed floor. Geometry study; wood remains later.'
body.select_set(True);bpy.context.view_layer.objects.active=body
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.region_3d.view_distance=9;sp.region_3d.view_location=(0,0,2.4);sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
# Export evaluated triangle corner normals so the cross keeps flat faces.
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();blocks=[];parts=[];count=0
for ob in parts_objects:
 ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles();block=[]
 for tri in me.loop_triangles:
  for vi,li in zip(tri.vertices,tri.loops):block.append(tuple(me.vertices[vi].co)+tuple(me.corner_normals[li].vector))
 a=np.array(block,dtype='<f4');blocks.append(a);parts.append({'name':ob.name,'vertexCount':len(a),'indexCount':len(a),'indexOffset':count,'vertexOffset':count,'triangleCount':len(a)//3});count+=len(a);ev.to_mesh_clear()
a=np.concatenate(blocks);indices=np.arange(len(a),dtype='<u4');raw=a.tobytes()+indices.tobytes();(OUT/'mesh.bin').write_bytes(raw);lo=a[:,:3].min(0);hi=a[:,:3].max(0)
projection=cam.calc_matrix_camera(graph,x=W,y=H);camera={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':W,'height':H,'orthoScale':d.ortho_scale,'shiftX':d.shift_x,'shiftY':0}
meta={'vertexCount':len(a),'indexCount':len(a),'triangleCount':len(a)//3,'vertexStrideBytes':24,'vertexByteLength':a.nbytes,'indexByteOffset':a.nbytes,'totalByteLength':len(raw),'bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist(),'center':((hi+lo)/2).tolist()},'parts':parts,'sourceSha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'referenceCamera':camera}
(OUT/'mesh.json').write_text(json.dumps(meta,indent=2));(OUT/'camera.json').write_text(json.dumps(camera,indent=2))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
bpy.ops.render.render(write_still=True)
print('ROOK_BUILD_COMPLETE',meta['triangleCount'])
