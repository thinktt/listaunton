import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
collection=bpy.data.collections.new('QUEEN - new measured reconstruction');scene.collection.children.link(collection)
S=273.5; ELEV=51.5; CX=483.625; Y0=880.0; W=H=1254
C=math.cos(math.radians(ELEV));SN=math.sin(math.radians(ELEV))

def mat(name,col,rough=.28):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 return m
clay=mat('Neutral satin - shape inspection',(.24,.26,.29),.32)
brown=mat('Brown gloss - diagnostic only, no wood texture',(.12,.045,.018),.24)

def mesh(name,vs,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 ob=bpy.data.objects.new(name,me);collection.objects.link(ob);ob.data.materials.append(clay)
 for p in me.polygons:p.use_smooth=True
 return ob

def lathe(name,profile,n=192,sub=2):
 vs=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for r,z in profile for i in range(n)]
 fs=[]
 for j in range(len(profile)-1):
  for i in range(n):
   k=(i+1)%n;fs.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
 fs+=[tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
 ob=mesh(name,vs,fs)
 if sub:
  m=ob.modifiers.new('Smooth measured turned section','SUBSURF');m.levels=sub;m.render_levels=sub
 return ob

# Fuller proportions: compress the lower flare and socket, shorten the stem
# about 11%, and bring the upper assembly down. Fill the flare's middle, widen
# the socket modestly, and thicken the stem waist by 12%. The collar stack is
# lifted .06 within the lowered upper assembly, shortening the crown body.
# Foot, shallow groove and crown shape remain. Camera is refitted to 51.5deg.
UPPER_DROP=.3651
body_profile=[
(0.00100000,0.21900000),(0.93800000,0.21900000),(1.01300000,0.21900000),(1.02500000,0.22540000),
(1.03400000,0.23580000),(1.03700000,0.24940000),(1.03700000,0.36220000),(1.03500000,0.37300000),
(1.02800000,0.38300000),(1.01700000,0.39300000),(1.00400000,0.40200000),(0.99600000,0.41200000),
(0.99600000,0.42200000),(1.00000000,0.43400000),(1.00700000,0.44800000),(1.01300000,0.46500000),
(1.01400000,0.48200000),(1.01100000,0.49730000),(1.00300000,0.51685000),(0.98800000,0.54065000),
(0.96500000,0.56955000),(0.93000000,0.60185000),(0.90500000,0.63166071),(0.83200000,0.68625352),
(0.73300000,0.75423702),(0.62502605,0.82428063),(0.58374370,0.84881756),(0.56122694,0.85933339),
(0.54868277,0.87832029),(0.54400000,0.89730720),(0.54400000,1.00976813),(0.54400000,1.07549204),
(0.53722500,1.10124337),(0.52245000,1.12699470),(0.50167500,1.15274602),(0.47893875,1.17720978),
(0.46331875,1.19781084),(0.43279563,1.21519298),(0.40635000,1.23000000),(0.38908649,1.28886121),
(0.35670520,1.38425697),(0.31736372,1.52430606),(0.28767234,1.70190455),(0.27621712,1.89980000),
(0.25322811,2.04740431),(0.24304000,2.18294034),(0.24841614,2.29155483),(0.26893735,2.38624439),
(0.30066030,2.46700901),(0.34060755,2.54034700),(0.41500000,2.61090000),(0.50500000,2.63290000),
(0.58600000,2.64190000),(0.63700000,2.64690000),(0.65100000,2.65790000),(0.65400000,2.67290000),
(0.65400000,2.68490000),(0.64800000,2.69790000),(0.63200000,2.70490000),(0.59200000,2.70690000),
(0.55000000,2.71290000),(0.53363123,2.73170282),(0.53666579,2.76053380),(0.55345450,2.80190000),
(0.58045450,2.81290000),(0.59445450,2.81790000),(0.60145450,2.82890000),(0.60345450,2.84190000),
(0.60345450,2.85790000),(0.59745450,2.86990000),(0.58345450,2.87690000),(0.54745450,2.87990000),
(0.50545450,2.89190000),(0.46443126,2.91752329),(0.44317115,2.94791370),(0.44663142,2.97890000),
(0.46563142,2.99590000),(0.47663142,3.00590000),(0.47963142,3.01690000),(0.47863142,3.02990000),
(0.46963142,3.04290000),(0.45063142,3.05290000),(0.41163142,3.05790000),(0.40863142,3.07890000),
(0.41875514,3.14207577),(0.42873696,3.20427962),(0.44446920,3.30244505),(0.46309760,3.41907725),
(0.48320313,3.54445687),(0.49770015,3.63484682),(0.50673054,3.69121906),(0.51400000,3.73690000),
(0.49900000,3.74490000),(0.44000000,3.71215627),(0.40000000,3.69840975),(0.00100000,3.69840975),]
body=lathe('01 Body - foot groove, raised socket, stem and collars',body_profile)

# Crown is a scooped annulus with a substantial rounded lip.
# Amount of scalloping rises toward the rim. Tips curl up, not separate teeth.
# radius,z,scallop weight
crown_profile=[(.001,3.998,0),(.40,3.998,0),(.499,4.012,0),
(.532,4.041,.06),(.572,4.078,.20),(.614,4.112,.44),
(.650,4.133,.69),(.661,4.151,.91),(.646,4.174,1),
(.617,4.184,1),(.586,4.174,.94),(.550,4.152,.80),
(.500,4.150,.56),(.450,4.150,.32),(.405,4.165,.11),
(.355,4.163,0),(.303,4.161,0),(.254,4.160,0),
(.226,4.160,0),(.211,4.150,0),(.198,4.170,0),
(.195,4.209,0),(.191,4.260,0),(.177,4.320,0),
(.150,4.382,0),(.114,4.439,0),(.066,4.475,0),(.024,4.493,0),(.001,4.495,0)]
N=256;vs=[]
for j,(r,z,w) in enumerate(crown_profile):
 for i in range(N):
  a=math.tau*i/N
  peak=((1+math.cos(8*(a-math.pi/8)))/2)**3.1
  # Small inward roll at the tall tips, consistent with the visible crown.
  rr=r-w*.090+w*.080*peak
  zz=z+w*.150+w*.074*peak
  rr -= .010*w*(1-peak)
  zz -= .025*w*(1-peak)
  if j <= 7: zz += .075*(1-w)**2
  vs.append((rr*math.cos(a),rr*math.sin(a),zz))
fs=[]
for j in range(len(crown_profile)-1):
 for i in range(N):
  k=(i+1)%N;fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
fs+=[tuple(reversed(range(N))),tuple((len(crown_profile)-1)*N+i for i in range(N))]
crown=mesh('02 Crown - rolled scallops, shallow scoop and egg finial',vs,fs)
crown.location.z=-UPPER_DROP
m=crown.modifiers.new('Rounded carved surface','SUBSURF');m.levels=2;m.render_levels=2

# Semantic ring locations for inspection overlay, stored with the model.
features={
 'foot_groove':(0.99600000,0.41700000),
 'foot_lower_lip':(1.01700000,0.39300000),
 'base_shoulder':(1.01400000,0.48200000),
 'socket_shoulder':(0.52245000,1.12699470),
 'stem_seat':(0.46331875,1.19781084),
 'lowest_collar':(0.65300000,2.67890000),
 'middle_collar':(0.60245450,2.84990000),
 'small_bead':(0.47763142,3.02090000),
 'egg_base':(0.19800000,3.80490000),
}
(OUT/'profile-landmarks.json').write_text(json.dumps({'scale':S,'elevation':ELEV,'cx':CX,'y0':Y0,'rings':features},indent=2))

# Packed reference, plus a camera background usable as a live overlay in Blender.
reference=bpy.data.images.load(str(OUT/'reference.png'));reference.pack()
world=bpy.data.worlds.new('Controlled studio');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.14,.14,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.16

def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,2.3));return o
area('Key - upper left',(-3,-4,8),700,2.0)
area('Front right soft highlight',(3,-4,5),260,1.3)
area('Gentle rim',(2,3,7),300,3)
d=bpy.data.cameras.new('Aligned reference camera');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
d.type='ORTHO';d.ortho_scale=W/S
# Camera target chosen analytically so z=0 projects to y0.
ZT=(Y0-H/2)/(S*C)
cam.location=(0,-12*C,ZT+12*SN);aim(cam,(0,0,ZT))
d.shift_x=(W/2-CX)/W;d.shift_y=0
bg=d.background_images.new();bg.image=reference;bg.alpha=.50;bg.display_depth='FRONT';bg.frame_method='FIT';d.show_background_images=True
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16 if '--draft' in sys.argv else 32
scene.cycles.use_denoising=True
scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene['reconstruction']='New profile from hi-res-queen.png; camera elevation fitted to eight crown points. Geometry review material; wood finish deferred.'
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True);crown.select_set(True);bpy.context.view_layer.objects.active=body
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.region_3d.view_distance=8;sp.region_3d.view_location=(0,0,2.2);sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='CAMERA';sp.shading.type='SOLID';sp.overlay.show_overlays=False
bpy.context.preferences.filepaths.save_version=0
scene.render.filepath=str(OUT/'queen-matched.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'queen-rebuilt.blend'))
# GPU is used only for this script's render; the saved model retains CPU fallback.
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences
 prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices: dev.use=(dev.type=='CUDA')
 if any(dev.type=='CUDA' for dev in prefs.devices): scene.cycles.device='GPU'
except Exception as error: print('CPU rendering fallback:',error)
bpy.ops.render.render(write_still=True)
if '--draft' not in sys.argv:
 for ob in (body,crown): ob.data.materials[0]=brown
 scene.render.filepath=str(OUT/'queen-brown.png');bpy.ops.render.render(write_still=True)
 for ob in (body,crown): ob.data.materials[0]=clay
 d.shift_x=0;d.ortho_scale=5.4;cam.location=(7,-11,6.0);aim(cam,(0,0,2.2))
 scene.render.resolution_x=900;scene.render.resolution_y=1000
 scene.render.filepath=str(OUT/'queen-three-quarter.png');bpy.ops.render.render(write_still=True)
print('HIRES_QUEEN_COMPLETE')
