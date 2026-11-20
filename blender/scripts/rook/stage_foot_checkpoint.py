"""Stage accepted foot-light candidate without overwriting public assets."""
from pathlib import Path
import bpy,sys,json,hashlib,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
sys.path.insert(0,str(ROOT/'scripts/rook'));from render_regions import validate,closed_body
stage=Path(sys.argv[sys.argv.index('--')+1]);source=ROOT/'build/rook-mission/021-foot-light-40/rook.blend';out=stage/'assets/rook';out.mkdir(parents=True,exist_ok=True);model=stage/'models/rook/rook-rebuilt.blend';model.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;validate(s);closed_body(s).hide_set(True);gpu(s)
s['reconstruction']='Rook checkpoint 021: foot-only reflector, retained editable geometry and wood checkpoint 004. Assumed 54-degree camera; finish incomplete.'
s['rook_pigment_atlas']='assets/rook/pigment.png';s.render.filepath=str(out/'render.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(model));bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;gpu(s);validate(s);bpy.ops.render.render(write_still=True)
c=s.camera;c.data.shift_x=0;c.data.shift_y=0;c.data.sensor_fit='VERTICAL';c.data.ortho_scale=4.3;c.location=(0,-12,1.4);c.rotation_euler=(Vector((0,0,1.4))-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'profile.png');bpy.ops.render.render(write_still=True)
c.location=(0,12,1.4);c.rotation_euler=(Vector((0,0,1.4))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'rear.png');bpy.ops.render.render(write_still=True)
(out/'checkpoint.json').write_text(json.dumps({'checkpoint':21,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source_trial_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'change':'40W foot-linked glossy strip; original geometry, pigment and lights retained','unfinished':['turret and shoulder reflections','baked lighting contamination','side neck pigment transitions','inferred hidden form']},indent=2)+'\n');print('FOOT_CHECKPOINT_STAGED')
