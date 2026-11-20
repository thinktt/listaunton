"""Narrow the emitter and beam after the broad focused-bowl diagnostic."""
from pathlib import Path
import bpy,json,math,hashlib,argparse,sys
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--variants',nargs=2,default=['102-tight-bowl','103-subtle-tight-bowl']);p.add_argument('--gains',nargs=2,type=float,default=[.4,.15]);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert all(Path(v).name==v and v not in ('.','..') for v in args.variants)
assert all(0<g<=1 for g in args.gains)
source=ROOT/'build/queen-mission/100-focused-bowl/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cfg=json.loads(s['mission_material_config'])
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('Bowl focused'):
  o.data.shadow_soft_size=.025;o.data.spot_size=math.radians(1.3);o.data.spot_blend=.8
s.render.use_persistent_data=True;s.cycles.samples=64
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.context.preferences.filepaths.save_version=0
for variant,gain in zip(args.variants,args.gains):
 current=json.loads(json.dumps(cfg));current['variant']=variant
 for spec in current['lights']:
  if spec['name'].startswith('Bowl focused'):
   spec['energy']*=gain;spec['size']=.05;spec['spot_degrees']=1.3;bpy.data.objects[spec['name']].data.energy=spec['energy']
 current['bowl_reflection_trial'].update({'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'gain':gain,'emitter_diameter':.05,'beam_degrees':1.3})
 s['mission_material_config']=json.dumps(current);s['mission_variant']=variant
 out=ROOT/'build/queen-mission'/variant;out.mkdir(exist_ok=True,parents=True)
 s.render.filepath=str(out/'wood.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
 (out/'parameters.json').write_text(json.dumps(current,indent=2));print('TIGHT_BOWL_DONE',variant,flush=True)
