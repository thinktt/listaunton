"""Render current saved rook views without modifying the model file."""
from pathlib import Path
import sys,hashlib,json,math
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
model=ROOT/'models/rook/rook-rebuilt.blend';out=ROOT/'assets/rook'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(model);bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene;gpu(s);cam=s.camera
axis=cam.matrix_world.to_3x3()@Vector((0,0,1));assert abs(math.degrees(math.asin(axis.z))-54)<.001
s.render.resolution_percentage=100;s.cycles.samples=64;s.render.filepath=str(out/'render.png');bpy.ops.render.render(write_still=True)
cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3
s.render.resolution_x=600;s.render.resolution_y=900
for name,loc in [('profile',(0,-12,1.4)),('rear',(0,12,1.4))]:
    cam.location=loc;cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(model)==before
(out/'render-source.json').write_text(json.dumps({'source_sha256':before,'fixed_camera_degrees':54,'views':{name:sha(out/(name+'.png')) for name in ['render','profile','rear']}},indent=2)+'\n')
print('ROOK_CURRENT_VIEWS_COMPLETE')
