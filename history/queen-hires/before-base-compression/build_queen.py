import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
collection=bpy.data.collections.new('QUEEN - new measured reconstruction');scene.collection.children.link(collection)
S=273.5; ELEV=55.32; CX=483.625; Y0=874.0; W=H=1254
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

# Fresh profile derived from the large reference's visible internal rings.
# Distinct groove, main base sweep, raised socket, stem, and three upper moldings.
# User-directed shaping: coin-like foot, simple rounded socket shoulder,
# more tapered stem, thin shelf-like collars, and a simple widening crown body.
# Crown mesh and the reference camera are deliberately unchanged.
body_profile=[
(.001,.070),(.90,.070),(.975,.070),(.987,.078),(.996,.091),
(.999,.108),(.999,.249),(.998,.272),(.991,.288),(.978,.301),
(.960,.313),(.942,.328),
(.936,.349),(.939,.379),(.955,.408),(.978,.430),(.989,.456),
(.986,.483),(.974,.510),(.951,.553),(.912,.616),
(.86,.671),(.793,.777),(.715,.909),(.638,1.045),(.586,1.087),
(.548,1.105),(.540,1.130),(.537,1.170),(.537,1.290),
(.536,1.350),(.531,1.390),(.519,1.430),(.497,1.467),
(.473,1.493),(.449,1.519),(.433,1.550),(.419,1.594),
(.403,1.649),(.367,1.738),(.327,1.851),(.288,1.994),
(.251,2.15),(.228,2.309),(.217,2.455),(.228,2.572),
(.253,2.674),(.289,2.761),(.334,2.840),(.415,2.916),
(.505,2.938),(.586,2.947),(.637,2.952),(.651,2.963),
(.654,2.978),(.654,2.990),(.648,3.003),(.632,3.010),
# Equal collar centers at z2.984,3.155,3.326. Radius corrections follow
# dr=cot(camera elevation)*dz to retain the reference's front arc positions.
(.592,3.012),(.550,3.018),(.53363123,3.03680282),(.53666579,3.0656338),
(.5534545,3.107),(.5804545,3.118),(.5944545,3.123),(.6014545,3.134),
(.6034545,3.147),(.6034545,3.163),(.5974545,3.175),(.5834545,3.182),
(.5474545,3.185),(.5054545,3.197),(.46443126,3.22262329),(.44317115,3.2530137),
(.44663142,3.284),(.46563142,3.301),(.47663142,3.311),(.47963142,3.322),
(.47863142,3.335),(.46963142,3.348),(.45063142,3.358),(.41163142,3.363),
# Continue the straight crown-body taper into the unchanged rim connection.
(.40863142,3.384),(.41875514,3.45293648),(.42873696,3.52081241),(.4444692,3.6279291),
(.4630976,3.75519645),(.48320313,3.89200886),(.49770015,3.99064106),(.50673054,4.05215362),
(.514,4.102),(.499,4.110),
(.44,4.075),(.40,4.06),(.001,4.06)]
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
m=crown.modifiers.new('Rounded carved surface','SUBSURF');m.levels=2;m.render_levels=2

# Semantic ring locations for inspection overlay, stored with the model.
features={
 'foot_groove':(.937,.360), 'foot_lower_lip':(.995,.277),
 'base_shoulder':(.989,.456), 'socket_shoulder':(.528,1.403),
 'stem_seat':(.473,1.493), 'lowest_collar':(.653,2.984),
 'middle_collar':(.6024544974,3.155), 'small_bead':(.4776314226,3.326),
 'egg_base':(.198,4.170)}
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
