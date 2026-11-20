"""Test fixed 64-sample rendering without adaptive early stopping."""
from pathlib import Path
import bpy,json,hashlib,argparse,sys
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=64);p.add_argument('--variant',default='171-uniform-finial');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/'build/queen-mission/169-finial-atlas/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
cfg=json.loads(s['mission_material_config']);cfg['variant']=args.variant
cfg['render_sampling']={'samples':args.samples,'adaptive':False,'seed':0,'reason':'Test fixed sampling at higher quality to reduce isolated specular variance. Geometry, material and lights unchanged.'}
s.cycles.samples=args.samples;s.cycles.use_adaptive_sampling=False;s.cycles.seed=0;s.cycles.use_animated_seed=False
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True);s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):bpy.context.scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('UNIFORM_SAMPLING_TRIAL_DONE',flush=True)
