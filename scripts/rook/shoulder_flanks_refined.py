"""Place real glossy shoulder reflectors from the two observed flank glints."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from focused_reflections import target
source=ROOT/'history/rook-mission-072/models/rook/rook-rebuilt.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)=='ea195e8973c460c777b92b80f4b609f298ab61367494ef27b5229db52affabc1'
for num,power in [(78,650)]:
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;old=s.objects['Rook shoulder strip'];old.data.energy=0;rows=[]
 for label,x,y in [('left',400,882),('right',560,888)]:
  chosen=None
  for dy in [0,*[sign*i for i in range(1,16) for sign in [-1,1]]]:
   ob,p,d,n=target(s,x+.5,y+dy+.5)
   if ob.get('rook_render_receiver')=='shoulder':chosen=(ob,p,d,n,dy);break
  assert chosen,(x,y);ob,p,d,n,dy=chosen;data=bpy.data.lights.new('Rook shoulder flank '+label,'AREA');data.shape='RECTANGLE';data.size=.75;data.size_y=.14;data.energy=power;light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light);light.location=p+d*4;light.rotation_euler=(p-light.location).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True;light.light_linking.receiver_collection=old.light_linking.receiver_collection;rows.append({'name':light.name,'reference_pixel':[x,y],'target_pixel':[x,y+dy],'position':list(light.location),'point':list(p),'normal':list(n),'receiver':ob.name})
 out=ROOT/f'build/rook-mission/{num:03d}-shoulder-flanks';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));(out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'power_each':power,'reflectors':rows,'old_shoulder_power':0,'size':[.75,.14],'method':'Two real glossy-only shadowed area lights, same shoulder receiver. Existing broad shoulder strip disabled; material, geometry and other lights unchanged.'},indent=2)+'\n')

