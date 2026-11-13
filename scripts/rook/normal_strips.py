from pathlib import Path
import sys,bpy,json,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
from focused_reflections import target
source=ROOT/'build/rook-mission/018-repaired-strip/rook.blend';out=ROOT/'build/rook-mission/019-normal-strips';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
for ob in s.objects:
 if ob.type=='LIGHT' and ob.name.startswith('Rook '):ob.data.energy=0
im=bpy.data.images.load(str(ROOT/'assets/rook/ref.png'),check_existing=False);a=np.array(im.pixels[:]).reshape(im.size[1],im.size[0],4)[::-1];rows=[]
for label,box in [('shoulder',(445,860,520,930)),('foot',(445,995,520,1060)),('rim',(420,500,455,560))]:
 x0,y0,x1,y1=box;crop=a[y0:y1,x0:x1,:3];v=crop.min(2);iy,ix=np.unravel_index(v.argmax(),v.shape);x=x0+ix;y=y0+iy
 obj,p,direction,normal=target(s,x+.5,y+.5);data=bpy.data.lights.new('Rook normal strip '+label,'AREA');data.shape='RECTANGLE';data.size=6;data.size_y=.07;data.energy=200
 light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light);light.location=p+direction*4;light.rotation_euler=(p-light.location).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False
 rows.append({'region':label,'pixel':[int(x),int(y)],'point':list(p),'normal':list(normal),'position':list(light.location)})
body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render);bs=body.data.materials[0].node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.12;bs.inputs['Coat Weight'].default_value=.6;bs.inputs['Coat Roughness'].default_value=.08
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source':str(source),'reflectors':rows,'roughness':.12,'coat':.6,'coat_roughness':.08},indent=2)+'\n');print('NORMAL_STRIPS_DONE')
