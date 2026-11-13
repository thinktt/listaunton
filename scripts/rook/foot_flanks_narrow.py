"""Place real glossy foot reflectors from the two observed flank glints."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from focused_reflections import target
source=ROOT/'models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='bfc8e7c5aca140363d67c379532f57412e0bac8206c0bd617591e0e993d94914'
for num,left_power,right_power in [(83,3,115)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;old=s.objects['Rook foot strip'];old.data.energy=0;rows=[]
 for label,x,y in [('left',400,1015),('right',580,1011)]:
  chosen=None
  for dy in [0,*[sign*i for i in range(1,16) for sign in [-1,1]]]:
   ob,p,d,n=target(s,x+.5,y+dy+.5)
   if ob.get('rook_render_receiver')=='foot':chosen=(ob,p,d,n,dy);break
  assert chosen,(x,y);ob,p,d,n,dy=chosen;data=bpy.data.lights.new('Rook foot flank '+label,'AREA');data.shape='RECTANGLE';data.size=.75;data.size_y=.04;data.energy=left_power if label=='left' else right_power;light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light);light.location=p+d*4;light.rotation_euler=(p-light.location).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True;light.light_linking.receiver_collection=old.light_linking.receiver_collection;rows.append({'name':light.name,'reference_pixel':[x,y],'target_pixel':[x,y+dy],'position':list(light.location),'point':list(p),'normal':list(n),'receiver':ob.name})
 out=ROOT/f'build/rook-mission/{num:03d}-foot-flanks';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));(out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'left_power':left_power,'right_power':right_power,'reflectors':rows,'old_foot_power':0,'size':[.75,.04],'method':'Two real glossy-only shadowed area lights, same foot receiver. Existing broad foot strip disabled; material, geometry and other lights unchanged.'},indent=2)+'\n')
