"""Rebuild the measured bishop with Blender; --root overrides project location."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--root')+1]) if '--root' in args else Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/bishop';OUT.mkdir(parents=True,exist_ok=True);MODEL=ROOT/'models/bishop/bishop-rebuilt.blend';MODEL.parent.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'scripts/bishop/profile.json').read_text())
A=json.loads((OUT/'original-alignment.json').read_text());F=1254/300/A['scale']
cfg['profile']=[[r*F,(y-A['y']*3)*F] for r,y in cfg['profile']]
cfg['cx']=(cfg['cx']-A['x']*3)*F;cfg['y0']=(cfg['y0']-A['y']*3)*F
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
body=mesh('Bishop - continuous turned body',vs,fs);sub=body.modifiers.new('Smooth lathe profile','SUBSURF');sub.levels=1;sub.render_levels=1
# The mitre is a real saw cut across the entire front-to-back thickness.
# Preserve the Boolean cutter as an editable, hidden object in the blend.
def outward(ob):
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
outward(body)
sl=cfg['slit'];ang=math.radians(sl['angle']);length=100*F/S
anchor=Vector((sl['x']*F/S,0,z((sl['bottom_center_y']-A['y']*3)*F)))
direction=Vector((math.sin(ang),0,math.cos(ang)))
bpy.ops.mesh.primitive_cube_add(size=1,location=anchor+direction*length/2)
cutter=bpy.context.object;cutter.name='Mitre saw cut - editable cutter';cutter.rotation_euler[1]=ang;cutter.dimensions=(sl['width']*F/S,160*F/S,length)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
cut=body.modifiers.new('Open slit through mitre','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=cutter
bev=body.modifiers.new('Soft cut edges','BEVEL');bev.width=.23*F/S;bev.segments=3;bev.limit_method='ANGLE';bev.angle_limit=.5
# Rounded, slightly flattened top finial, intersecting its turned neck.
fi=cfg['finial'];bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=1)
finial=bpy.context.object;finial.name='Bishop - rounded finial'
finial.location=(0,0,z((fi['center_y']-A['y']*3)*F));finial.scale=(fi['radius']*F/S,fi['radius']*F/S,fi['radius']*fi['height_ratio']*F/S)
bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
finial.data.materials.append(mat)
for face in finial.data.polygons:face.use_smooth=True
outward(finial)
components=[body,finial]
reference=bpy.data.images.load(str(OUT/'reference.png'));reference.pack()
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
scene['reconstruction']='Measured orthographic bishop reconstruction; materials are diagnostic, not recovered wood.'
body.select_set(True);finial.select_set(True);bpy.context.view_layer.objects.active=body
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.region_3d.view_distance=9;sp.region_3d.view_location=(0,0,2.4);sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
# Export evaluated triangle corner normals so the cross keeps flat faces.
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();blocks=[];parts=[];count=0
for ob in components:
 ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles();block=[]
 for tri in me.loop_triangles:
  for vi,li in zip(tri.vertices,tri.loops):block.append(tuple(me.vertices[vi].co)+tuple(me.corner_normals[li].vector))
 a=np.array(block,dtype='<f4');blocks.append(a);parts.append({'name':ob.name,'vertexCount':len(a),'indexCount':len(a),'indexOffset':count,'vertexOffset':count,'triangleCount':len(a)//3});count+=len(a);ev.to_mesh_clear()
a=np.concatenate(blocks);indices=np.arange(len(a),dtype='<u4');raw=a.tobytes()+indices.tobytes();(OUT/'mesh.bin').write_bytes(raw);lo=a[:,:3].min(0);hi=a[:,:3].max(0)
projection=cam.calc_matrix_camera(graph,x=W,y=H);camera={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':W,'height':H,'orthoScale':d.ortho_scale,'shiftX':d.shift_x,'shiftY':0,'elevationDegrees':cfg['elevation']}
meta={'vertexCount':len(a),'indexCount':len(a),'triangleCount':len(a)//3,'vertexStrideBytes':24,'vertexByteLength':a.nbytes,'indexByteOffset':a.nbytes,'totalByteLength':len(raw),'bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist(),'center':((hi+lo)/2).tolist()},'parts':parts,'sourceSha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'referenceCamera':camera}
(OUT/'mesh.json').write_text(json.dumps(meta,indent=2));(OUT/'camera.json').write_text(json.dumps(camera,indent=2))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
bpy.ops.render.render(write_still=True)
print('BISHOP_BUILD_COMPLETE',meta['triangleCount'])
