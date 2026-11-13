"""Calibrate a shoulder-only strip on accepted checkpoint 021."""
from pathlib import Path
import sys,json,hashlib,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
sys.path.insert(0,str(ROOT/'scripts/rook'));from render_regions import validate
source=ROOT/'history/rook-mission-021/models/rook/rook-rebuilt.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()=='3f09283860474bec2297ff8cdd5ff2bec9a10833d02e4e53fd0290f361babb05'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);validate(s)
s.objects['Rook front crescent'].data.energy=0
row=next(x for x in json.loads((ROOT/'build/rook-mission/019-normal-strips/parameters.json').read_text())['reflectors'] if x['region']=='shoulder')
data=bpy.data.lights.new('Rook shoulder strip','AREA');data.shape='RECTANGLE';data.size=6;data.size_y=.07;ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob);ob.location=row['position'];ob.rotation_euler=(Vector(row['point'])-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_diffuse=False
receiver=bpy.data.collections.new('Shoulder only');receiver.objects.link(next(o for o in s.objects if o.get('rook_render_receiver')=='shoulder'));ob.light_linking.receiver_collection=receiver
for index,power in [(22,40),(23,120),(24,300)]:
    data.energy=power;out=ROOT/'build/rook-mission'/f'{index:03d}-shoulder-light';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'new_light_watts':power,'receiver':'shoulder','disabled_light':'Rook front crescent','foot_light_unchanged':True,'shader_and_geometry_unchanged':True},indent=2)+'\n');print('SHOULDER_LIGHT_DONE',index,flush=True)
