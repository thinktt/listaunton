"""Closed sculptural lofts for the Lichess knight; Blender --background --python this.py."""
import bpy, bmesh, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--root')+1]) if '--root' in args else Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/knight'; OUT.mkdir(parents=True,exist_ok=True)
MODEL=ROOT/'models/knight/knight-rebuilt.blend'; MODEL.parent.mkdir(parents=True,exist_ok=True)
cfg=json.loads((ROOT/'scripts/knight/profile.json').read_text())
S=cfg['scale']; E=math.radians(cfg['elevation']); C=math.cos(E); SN=math.sin(E); CX=cfg['cx']; Y0=cfg['y0']; W=H=1254; R=W/300
bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene; objects=[]
mat=bpy.data.materials.new('Neutral satin clay');mat.diffuse_color=(.32,.35,.39,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.32,.35,.39,1);bsdf.inputs['Roughness'].default_value=.30
def mx(x):return (x-CX)/S
def mz(v):return (Y0-v)/(S*C)
def mesh(name,vs,fs,sub=1):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 if sub:m=ob.modifiers.new('Smooth sculpted cross sections','SUBSURF');m.levels=sub;m.render_levels=sub
 objects.append(ob);return ob
def closedrings(name,rings,sub=1):
 n=len(rings[0]);vs=[v for ring in rings for v in ring];fs=[]
 for j in range(len(rings)-1):
  for i in range(n):k=(i+1)%n;fs.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
 fs+=[tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
 return mesh(name,vs,fs,sub)
def densify(rows,steps=6):
 out=[]
 for i in range(len(rows)-1):
  p0=np.array(rows[max(0,i-1)]);p1=np.array(rows[i]);p2=np.array(rows[i+1]);p3=np.array(rows[min(len(rows)-1,i+2)])
  for t in np.linspace(0,1,steps,endpoint=False):out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 out.append(rows[-1]);return out
N=64;theta=[i*math.tau/N for i in range(N)]
base=closedrings('Knight | turned pedestal', [[(r*math.cos(t),r*math.sin(t),z) for t in theta] for r,z in cfg['base']],2)
# Broad chest becomes a narrow arched neck; full elliptical sections in all directions.
neckrings=[]
for z,x,rx,ry in densify(cfg['neck'],4):
 ring=[]
 for t in theta:
  xx=mx(x)+rx*math.cos(t); yy=ry*math.sin(t)
  # Fluted tendon channels on both sides, with stronger round shoulder volume.
  side=abs(math.sin(t));line=float(np.interp(z,[2.1,2.4,2.8,3.3,3.8,4.2],[136,129,113,98,88,87])); taper=math.exp(-((z-3.15)/.94)**4)
  panel=math.exp(-((xx-mx(line))/.25)**4)*taper
  border=math.exp(-((xx-mx(line-8))/.070)**2)*taper
  yy*=1-(.31*panel+.12*border)*side**2
  ring.append((xx,yy,z))
 neckrings.append(ring)
neck=closedrings('Knight | curved neck and chest',neckrings,2)
def headloft(name,rows):
 rings=[]
 rows=densify(rows)
 for x,z,ry,rz in rows:
  ring=[]
  for t in theta:
   yy=ry*math.sin(t);zz=z+rz*math.cos(t)
   # Sockets and nostrils are sculpted into the side, not painted on.
   socket=math.exp(-((x-118)/4.5)**2-((zz-4.17)/.105)**2)
   nostril=math.exp(-((x-167)/2.8)**2-((zz-3.80)/.085)**2)
   muzzle_groove=(math.exp(-((x-(151+(zz-3.8)*15))/1.25)**2)+.6*math.exp(-((x-(163+(zz-3.7)*12))/1.0)**2))
   mouth=math.exp(-((zz-(z-.60*rz))/.040)**2)*math.exp(-((x-160)/16)**8) if x>138 else 0
   yy*=1-.35*socket-.34*nostril-.30*mouth
   ring.append((mx(x),yy,zz))
  rings.append(ring)
 return closedrings(name,rings,1)
head=headloft('Knight | forehead and tapered muzzle',cfg['head']); jaw=headloft('Knight | rounded jaw and chin',cfg['jaw'])
# Rounded swept mane follows the arch. Its oval depth is real and symmetric.
mane=[];path=cfg['mane']
for j,(x,v,r,dep) in enumerate(path):
 prev=Vector((mx(path[max(0,j-1)][0]),mz(path[max(0,j-1)][1])));nxt=Vector((mx(path[min(len(path)-1,j+1)][0]),mz(path[min(len(path)-1,j+1)][1])))
 tangent=(nxt-prev).normalized();normal=Vector((-tangent.y,tangent.x))
 mane.append([(mx(x)+normal.x*r*math.cos(t),dep*math.sin(t),mz(v)+normal.y*r*math.cos(t)) for t in theta])
closedrings('Knight | swept rounded mane',mane,2)
# Flattened pointed ears laid back along the poll, cupped and mirrored.
for side in [-1,1]:
 rings=[]
 for x,z,y,ry,rz in [[70,4.98,.22,.01,.012],[76,4.92,.35,.06,.055],[88,4.75,.43,.09,.075],[102,4.57,.40,.085,.08],[114,4.44,.31,.06,.09],[119,4.43,.24,.01,.02]]:
  rings.append([(mx(x),side*(y+ry*math.sin(t)),z+rz*math.cos(t)) for t in theta])
 closedrings('Knight | '+('near' if side<0 else 'far')+' swept ear',rings,2)
 # A small closed almond form sits in the recessed orbital plane.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(mx(119),side*.30,4.09));ob=bpy.context.object;ob.name='Knight | '+('near' if side<0 else 'far')+' eye';ob.scale=(.115,.050,.067)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mat)
 for p in ob.data.polygons:p.use_smooth=True
 objects.append(ob)
# An editable sculpted skin joins the cheek, neck and head. Source lofts remain hidden.
construction=bpy.data.collections.new('Construction lofts | hidden');scene.collection.children.link(construction)
skinparts=[]
for source in [neck,head,jaw]:
 copy=source.copy();copy.data=source.data.copy();scene.collection.objects.link(copy);copy.hide_render=False;copy.hide_viewport=False;skinparts.append(copy)
 for collection in list(source.users_collection):collection.objects.unlink(source)
 construction.objects.link(source);source.hide_render=True;source.hide_set(True);objects.remove(source)
bpy.ops.object.select_all(action='DESELECT')
for ob in skinparts:
 ob.select_set(True);bpy.context.view_layer.objects.active=ob
 for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
for ob in skinparts:ob.select_set(True)
bpy.context.view_layer.objects.active=skinparts[0];bpy.ops.object.join();skin=bpy.context.object;skin.name='Knight | continuous sculpted head and neck'
remesh=skin.modifiers.new('Joined anatomical skin','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.018;remesh.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=skin.modifiers.new('Soften carved transitions','SMOOTH');smooth.factor=.40;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
dec=skin.modifiers.new('Efficient sculpt surface','DECIMATE');dec.ratio=.48;bpy.ops.object.modifier_apply(modifier=dec.name)
for p in skin.data.polygons:p.use_smooth=True
objects.append(skin);neck=skin
# Recalculate every closed component outwards before export.
for ob in objects:
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
world=bpy.data.worlds.new('Neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.30;scene.world=world
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,2.5))
area('Key',(-3,-4,8),700,3);area('Fill',(4,-3,5),150,3);area('Rim',(2,4,8),320,3)
d=bpy.data.cameras.new('Reference camera | 54 degrees');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=300/S;d.clip_end=100
ZT=(Y0-150)/(S*C);cam.location=(0,-12*C,ZT+12*SN);aim(cam,(0,0,ZT));d.shift_x=(150-CX)/300
reference=bpy.data.images.load(str(OUT/'ref.png'));reference.pack();bg=d.background_images.new();bg.image=reference;bg.alpha=.5;bg.display_depth='FRONT';bg.frame_method='FIT';d.show_background_images=True
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.render.filepath=str(OUT/'render.png')
scene['reconstruction']=cfg['note'];scene['reference_camera_elevation_degrees']=54
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=neck
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':sp=ar.spaces.active;sp.region_3d.view_distance=9;sp.region_3d.view_location=(0,0,2.4);sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_perspective='CAMERA'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(MODEL))
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();blocks=[];parts=[];count=0
for ob in objects:
 ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles();block=[]
 for tri in me.loop_triangles:
  for vi,li in zip(tri.vertices,tri.loops):block.append(tuple(ob.matrix_world@me.vertices[vi].co)+tuple(ob.matrix_world.to_3x3()@me.corner_normals[li].vector))
 a=np.array(block,dtype='<f4');blocks.append(a);parts.append({'name':ob.name,'vertexCount':len(a),'indexCount':len(a),'indexOffset':count,'vertexOffset':count,'triangleCount':len(a)//3});count+=len(a);ev.to_mesh_clear()
a=np.concatenate(blocks);indices=np.arange(len(a),dtype='<u4');raw=a.tobytes()+indices.tobytes();(OUT/'mesh.bin').write_bytes(raw);lo=a[:,:3].min(0);hi=a[:,:3].max(0)
projection=cam.calc_matrix_camera(graph,x=W,y=H);camera={'type':'ORTHO','elevationDegrees':54,'worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':W,'height':H,'orthoScale':d.ortho_scale,'shiftX':d.shift_x,'shiftY':0}
meta={'vertexCount':len(a),'indexCount':len(a),'triangleCount':len(a)//3,'vertexStrideBytes':24,'vertexByteLength':a.nbytes,'indexByteOffset':a.nbytes,'totalByteLength':len(raw),'bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist(),'center':((hi+lo)/2).tolist()},'parts':parts,'sourceSha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'referenceCamera':camera}
(OUT/'mesh.json').write_text(json.dumps(meta,indent=2));(OUT/'camera.json').write_text(json.dumps(camera,indent=2))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='CUDA'
 if any(dev.type=='CUDA' for dev in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
bpy.ops.render.render(write_still=True);print('KNIGHT_BUILD_COMPLETE',meta['triangleCount'])
