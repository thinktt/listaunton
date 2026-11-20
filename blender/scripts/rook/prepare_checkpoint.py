"""Prepare a reviewable rook checkpoint in a separate site root."""
from pathlib import Path
import sys,shutil,json,hashlib
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
target=Path(sys.argv[sys.argv.index('--')+1])
source=ROOT/'build/rook-mission/004-continuous-atlas/rook.blend'
out=target/'assets/rook';out.mkdir(parents=True,exist_ok=True)
model=target/'models/rook/rook-rebuilt.blend';model.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
shutil.copy2(source.parent/'pigment.png',out/'pigment.png')
s['rook_pigment_atlas']='assets/rook/pigment.png'
s['reconstruction']='Rook wood checkpoint 004; original sprites authoritative, assumed orthographic 54-degree camera. Reflections and inferred hidden finish remain incomplete.'
s.render.filepath=str(out/'render.png');s.render.resolution_percentage=100
bpy.data.images[s['rook_pigment_image']].filepath='//../../assets/rook/pigment.png'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(model))
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'profile.png');bpy.ops.render.render(write_still=True)
cam.location=(0,12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'rear.png');bpy.ops.render.render(write_still=True)
(out/'checkpoint.json').write_text(json.dumps({'checkpoint':4,'source_trial_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source_trial':'build/rook-mission/004-continuous-atlas','unfinished':['highlight placement and edge crescents','inferred hidden pigment and residual projection artifacts','interior curvature vs original']},indent=2))
print('ROOK_CHECKPOINT_STAGED')
