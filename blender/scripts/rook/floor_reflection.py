from pathlib import Path
import bpy,sys,json,math,hashlib,importlib.util
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
sys.path.insert(0,str(ROOT/'scripts/rook'));from rebuild_receivers import rebuild
source=ROOT/'build/rook-mission/041-floor-pigment/rook.blend'
for num,depth in [(42,0),(43,6)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.get('rook_editable_control'))
 if depth:
  for v in body.data.vertices:
   if v.index//128>=53:v.co.z-=depth/(280*math.cos(math.radians(54)))
  body.data.update();bpy.context.view_layer.update()
 parts=rebuild(s,floor_receiver=True);floor=parts['floor_edge'];m=floor.data;view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized();proj=s.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1254,y=1254)@s.camera.matrix_world.inverted();candidates=[]
 for loop in m.loops:
  p=m.vertices[loop.vertex_index].co;n=m.corner_normals[loop.index].vector
  if not .75<n.z<.97 or p.y<0:continue
  q=proj@p.to_4d();pixel=((q.x/q.w+1)*627,(1-q.y/q.w)*627);candidates.append(((pixel[0]-483)**2+(pixel[1]-347)**2,p.copy(),n.copy(),pixel))
 dist,p,n,pixel=min(candidates,key=lambda row:row[0]);direction=(2*n.dot(view)*n-view).normalized();position=p+direction*4
 d=bpy.data.lights.new('Rook floor-edge strip','AREA');d.shape='RECTANGLE';d.size=6;d.size_y=.07;d.energy=500;light=bpy.data.objects.new(d.name,d);s.collection.objects.link(light);light.location=position;light.rotation_euler=(p-position).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False
 receiver=bpy.data.collections.new('Floor-edge only');receiver.objects.link(floor);light.light_linking.receiver_collection=receiver
 out=ROOT/f'build/rook-mission/{num:03d}-floor-reflection';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
 (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'depth_profile_pixels':depth,'target_pixel':[483,347],'actual_pixel':pixel,'normal':list(n),'point':list(p),'light_position':list(position),'watts':500,'size':[6,.07],'receiver':'floor_edge'},indent=2)+'\n');print('FLOOR_REFLECTION_SAVED',num,flush=True)
