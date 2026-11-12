"""Apply a fitted real diffuse light rig; save/reopen before its full beauty render."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from diffuse_study import configure
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fit',required=True);p.add_argument('--variant',required=True);p.add_argument('--samples',type=int,default=128)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);fit=json.loads((ROOT/a.fit).read_text());source=ROOT/fit['source']
digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==fit['source_sha256']
out=ROOT/'build/bishop-mission'/a.variant;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;lights,disabled=configure(s,fit['basis'])
for lamp,spec in zip(lights,fit['lights']):
    assert lamp.name==spec['name'];lamp.data.energy=spec['energy'];lamp.data.color=spec['color']
s['bishop_diffuse_study']=json.dumps(fit,sort_keys=True)
s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False;s.render.use_border=False;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
assert json.loads(s['bishop_diffuse_study'])==fit
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU';bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'parameters.json').write_text(json.dumps({'source':fit['source'],'source_sha256':digest,'fit':a.fit,
 'disabled_diffuse_lights':disabled,'reopened_before_render':True,'samples':a.samples,
 'model_sha256':hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest(),
 'render_sha256':hashlib.sha256((out/'wood.png').read_bytes()).hexdigest()},indent=2)+'\n')
print('JOINT_DIFFUSE_TRIAL_COMPLETE',a.variant,flush=True)
