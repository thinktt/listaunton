"""Reopen a material trial and render its fixed and side views without editing it."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('variant');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=ROOT/'build/queen-mission'/args.variant;source=out/'queen.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;s.cycles.samples=64;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.render.filepath=str(out/'wood-reopened.png');bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.6;cam.location=(0,-16,2.55);cam.rotation_euler=(Vector((0,0,2.55))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900
s.render.filepath=str(out/'wood-side.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'saved-material-check.json').write_text(json.dumps({'source_sha256':digest,'source_unchanged':True,'samples':64,'fixed_render':'wood-reopened.png','side_render':'wood-side.png'},indent=2));print('SAVED_MATERIAL_CHECK_DONE',flush=True)
