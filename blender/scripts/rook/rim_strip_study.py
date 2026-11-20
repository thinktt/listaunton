"""Isolated rim strip studies from accepted checkpoint 025."""
from pathlib import Path
import bpy, sys, json, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'models/rook/rook-rebuilt.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='082b79a1712cd07eaab76af0f945688ff04281ba9678e568ac1077698ad7b8a2'
for number,loc in [(27,(0,3,6)),(28,(0,-3,6)),(29,(0,0,7))]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    s=bpy.context.scene;gpu(s)
    out=ROOT/f'build/rook-mission/{number:03d}-rim-strip';out.mkdir(parents=True,exist_ok=True)
    data=bpy.data.lights.new('Rook trial rim strip','AREA');data.energy=300;data.shape='RECTANGLE';data.size=6;data.size_y=.12
    light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light)
    light.location=loc;light.rotation_euler=(Vector((0,0,2.7))-light.location).to_track_quat('-Z','Y').to_euler()
    light.visible_diffuse=False;light.visible_glossy=True
    receivers=bpy.data.collections.new('Trial rim only')
    receivers.objects.link(next(o for o in s.objects if o.get('rook_render_receiver')=='rim'))
    light.light_linking.receiver_collection=receivers
    s.cycles.samples=64;s.render.filepath=str(out/'wood.png')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);gpu(bpy.context.scene)
    bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':sha(source),'model_sha256':sha(out/'rook.blend'),'position':loc,'target':[0,0,2.7],'watts':300,'size':[6,.12],'receiver':'rim','samples':64},indent=2)+'\n')
    print('RIM_TRIAL_DONE',number,flush=True)
