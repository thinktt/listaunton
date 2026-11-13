"""Verify the chosen foot-light checkpoint against accepted wood checkpoint 004."""
from pathlib import Path
import sys,json,hashlib,bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_regions import validate,closed_body
code=(ROOT/'scripts/rook/validate_lighting_trial.py').read_text().split("base=ROOT/")[0];exec(compile(code,'lighting-snapshot','exec'))
base=ROOT/'history/rook-mission-004/models/rook/rook-rebuilt.blend';trial=out/'rook.blend'
def geometry():
 s=bpy.context.scene;rows={}
 for ob in s.objects:
  if ob.type!='MESH' or ob.get('rook_render_receiver'):continue
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
  rows[ob.name]={'control':hashlib.sha256(np.array([v.co[:] for v in ob.data.vertices],np.float32).tobytes()).hexdigest(),'evaluated':hashlib.sha256(np.array([v.co[:] for v in me.vertices],np.float32).tobytes()).hexdigest(),'triangles':hashlib.sha256(np.array([t.vertices[:] for t in me.loop_triangles],np.int32).tobytes()).hexdigest(),'matrix':list(map(list,ob.matrix_world))};ev.to_mesh_clear()
 c=s.camera;return rows,{'matrix':list(map(list,c.matrix_world)),'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y],'size':[s.render.resolution_x,s.render.resolution_y]}
ma,la,wa=snapshot(base);ga,ca=geometry();mb,lb,wb=snapshot(trial);gb,cb=geometry()
assert ga==gb and ca==cb
assert all(mb[k]==v for k,v in ma.items());assert wa==wb
assert all(lb[k]==v for k,v in la.items())
assert set(lb)-set(la)=={'Rook foot strip'};assert lb['Rook foot strip']['energy']==40
rr=validate(bpy.context.scene)
report={'control_and_evaluated_geometry_exact':True,'camera_exact':True,'original_shaders_packed_images_world_and_lights_exact':True,'new_light':'40W glossy-only foot-linked rectangular strip','receivers':rr,'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(trial.read_bytes()).hexdigest()}
(out/'checkpoint-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FOOT_CHECKPOINT_VALID',json.dumps(report))
# Reopen and reproduce both fixed and side renders from the saved file.
bpy.ops.wm.open_mainfile(filepath=str(trial),load_ui=False);s=bpy.context.scene
sys.path.insert(0,str(ROOT/'scripts/king'));from mission_trial import gpu
from mathutils import Vector
gpu(s);s.render.filepath=str(out/'reopened.png');bpy.ops.render.render(write_still=True)
c=s.camera;c.data.shift_x=0;c.data.shift_y=0;c.data.sensor_fit='VERTICAL';c.data.ortho_scale=4.3;c.location=(0,-12,1.4);c.rotation_euler=(Vector((0,0,1.4))-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
