"""Reopen the native model to render its fixed, registered side, studio controls and real turns."""
from pathlib import Path
import sys,json,math
import bpy
from mathutils import Vector
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from sculpt import load,configure_render,render,use_side_camera,crop,clay,sha
def previews(name,tag):
 for k in ('wood','clay'):
  s=load(name);configure_render(s,30)
  if k=='clay':clay(s)
  crop(s,(240,270,530,431));render(s,D/f'{tag}-{k}-fixed.png')
  use_side_camera(s);crop(s,(220,90,780,325));render(s,D/f'{tag}-{k}-side.png')
def orbit(s,az,elev=18):
 a,e=map(math.radians,(az+10.3,elev));t=Vector((-.45,-.035,4.23));cam=s.camera
 cam.data.ortho_scale=3.85;cam.data.shift_x=cam.data.shift_y=0
 cam.location=t+Vector((8*math.sin(a)*math.cos(e),-8*math.cos(a)*math.cos(e),8*math.sin(e)));cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
def sides(name):
 for k in ['wood','clay']:
  s=load(name);configure_render(s,24);s.render.resolution_x=520;s.render.resolution_y=387
  if k=='clay':clay(s)
  for n,az,el in [('near',0,7),('rear-quarter',-47,23),('front-quarter',48,28),('rear',-90,24),('opposite',180,7),('front',90,25)]:
   orbit(s,az,el);render(s,D/f'{name}-{k}-{n}.png')
def pair():
 s=load('knight');configure_render(s,144);render(s,D/'wood.png');use_side_camera(s);render(s,D/'wood-side.png')
 (D/'renders.json').write_text(json.dumps({'scene_sha256':sha(D/'knight.blend'),'fixed_sha256':sha(D/'wood.png'),'side_sha256':sha(D/'wood-side.png'),'samples':144},indent=2)+'\n')
def common():
 before=load('parent');q=before.objects['Walnut | poll rear oval'];mat=q.matrix_world.copy();color=list(q.data.color);energy=q.data.energy;wi=q.data.size;hi=q.data.size_y
 name='knight' if (D/'knight.blend').exists() else 'inspection'
 for k in ['parent','new']:
  s=load(name);rear=s.objects['Walnut | poll rear oval']
  if k=='parent':
   front=s.objects.get('Walnut | shaped front shoulder bounce')
   if front:front.hide_render=True
   rear.matrix_world=mat;rear.data.color=color;rear.data.energy=energy;rear.data.size=wi;rear.data.size_y=hi
  configure_render(s,36);crop(s,(240,270,530,431));render(s,D/f'common-studio-{k}.png')
if __name__=='__main__':
 action=sys.argv[-1]
 if action=='test':previews('inspection','trial')
 if action=='turn-test':sides('inspection')
 if action=='turn-parent':sides('parent')
 if action=='parent-crops':previews('parent','parent')
 if action=='final':pair();previews('knight','knight');sides('knight');common()
 if action=='common':common()
