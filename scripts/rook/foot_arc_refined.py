"""Test two reflected-direction targets along the right foot arc."""
from pathlib import Path
import bpy,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from focused_reflections import target
source=ROOT/'build/rook-mission/086-foot-finish/rook.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((source.parent/'parameters.json').read_text())['model_sha256'];assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;old=s.objects['Rook foot flank right'];old.data.energy=0;rows=[]
for label,x,y in [('inner',560,1018),('outer',600,1003)]:
 ob,p,d,n=target(s,x+.5,y+.5);assert ob.get('rook_render_receiver')=='foot',ob.name
 data=bpy.data.lights.new('Rook foot arc '+label,'AREA');data.shape='RECTANGLE';data.size=.4;data.size_y=.03;data.energy=40
 light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light);light.location=p+d*4;light.rotation_euler=(p-light.location).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True;light.light_linking.receiver_collection=old.light_linking.receiver_collection
 rows.append({'name':light.name,'pixel':[x,y],'point':list(p),'normal':list(n),'reflection_direction':list(d),'light_position':list(light.location)})
out=ROOT/'build/rook-mission/090-foot-arc';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
(out/'parameters.json').write_text(json.dumps({'source_sha256':expected,'model_sha256':sha(out/'rook.blend'),'targets':rows,'old_right_power':0,'new_power_each':40,'size':[.4,.03],'note':'Geometry, material, left foot light and all other lights preserved from isolated086; accepted078 unchanged'},indent=2)+'\n')
