"""Keep the scene fixed and isolate sampling/denoising quality."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--variant',required=True);p.add_argument('--samples',type=int,default=512);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
scene.cycles.samples=args.samples;scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
scene.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32';bpy.data.images['Render Result'].save_render(str(out/'wood-linear.exr'),scene=scene)
scene.cycles.use_denoising=False;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'without-denoising.png');bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps({'source':args.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'samples':args.samples,'adaptive_sampling':False,'geometry_material_lights_unchanged':True,'primary_denoised':True,'additional_raw_render':'without-denoising.png'},indent=2)+'\n');print('QUALITY_TRIAL_DONE',flush=True)
