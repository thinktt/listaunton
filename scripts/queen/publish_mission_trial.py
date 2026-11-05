"""Promote an inspected trial in the staging tree and render all current views."""
from pathlib import Path
import argparse,json,sys,hashlib
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
p=argparse.ArgumentParser();p.add_argument('variant');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
trial=ROOT/'build/queen-mission'/args.variant/'queen.blend'
digest=hashlib.sha256(trial.read_bytes()).hexdigest()
validation=json.loads((trial.parent/'finish-validation.json').read_text())
metrics=json.loads((trial.parent/'metrics.json').read_text())
assert validation['passed'] and validation['source_sha256']==digest
assert metrics['trial_blend_sha256']==digest
assert metrics['trial_render_sha256']==hashlib.sha256((trial.parent/'wood.png').read_bytes()).hexdigest()
# Allow only pixel/AA precision, not the rejected trial's outline regression.
assert metrics['original_iou']>=metrics['previous_original_iou']-1e-5
assert metrics['highres_iou']>=metrics['previous_highres_iou']-5e-5
print('Validated promotion:',args.variant,'original IoU',metrics['original_iou'],'high-res IoU',metrics['highres_iou'],flush=True)
bpy.ops.wm.open_mainfile(filepath=str(trial),load_ui=False)
scene=bpy.context.scene;cam=scene.camera
obj=editable_mesh(scene)
wood=obj.data.materials[0]
scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.cycles.device='CPU';scene.render.use_persistent_data=True
scene.render.filepath='//../../assets/queen/queen-brown.png'
scene['mission_accepted_variant']=args.variant
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/queen/queen-rebuilt.blend'))
sys.path.insert(0,str(Path(__file__).parent))
from write_finished_landmarks import write
write(scene,obj,json.loads((ROOT/'assets/queen/finish-fit.json').read_text()))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e)
clay=bpy.data.materials.new('Mission inspection clay');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32
out=ROOT/'assets/queen'
for mat,name in [(wood,'queen-brown.png'),(clay,'queen-matched.png')]:
 set_material(scene,mat);scene.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.6
cam.location=(0,-16,2.55);cam.rotation_euler=(Vector((0,0,2.55))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=600;scene.render.resolution_y=900
for mat,name in [(wood,'queen-wood-profile.png'),(clay,'queen-finished-profile.png')]:
 set_material(scene,mat);scene.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
print('MISSION_PUBLISHED',args.variant,flush=True)
