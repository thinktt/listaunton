"""Check a small reflector with fixed non-adaptive sample counts and camera."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--samples',type=int,nargs='+',default=[96,384,1024])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
w,h=s.render.resolution_x,s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=False;s.render.border_min_x=445/w;s.render.border_max_x=565/w
s.render.border_min_y=1-480/h;s.render.border_max_y=1-385/h;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
for samples in a.samples:
    s.cycles.samples=samples;s.render.filepath=str(out/f'samples-{samples}.png');bpy.ops.render.render(write_still=True)
    print('TIP_CONVERGENCE_RENDER',samples,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':sha,'samples':a.samples,
 'adaptive_sampling':False,'denoising':True,'source_and_camera_unchanged':True,'crop_pixels':[445,385,565,480]},indent=2)+'\n')
