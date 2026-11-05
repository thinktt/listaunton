"""Refit confined real lights with a fresh diffuse pass of the accepted pigment."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
import PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
p=argparse.ArgumentParser();p.add_argument('--source',default='build/queen-mission/072-confined-reflections/queen.blend');p.add_argument('--variant',default='073-refitted-confined-rig')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cfg=json.loads(s['mission_material_config'])
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(parents=True,exist_ok=True)
# Diffuse lights are unchanged. Remove all explicit glossy-light response;
# the weak world contribution remains in this measured baseline.
for light in s.objects:
 if light.type=='LIGHT':light.visible_glossy=False
s.render.resolution_x=s.render.resolution_y=418;s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=False
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(out/'diffuse-baseline.exr')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(s.render.filepath,check_existing=False);a=np.empty(418*418*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(418,418,4)[::-1].copy();bpy.data.images.remove(im);np.save(out/'diffuse-baseline.npy',a)
mask=a[:,:,3]>.995;baseline=a[:,:,:3][mask].astype(np.float64)
basis=ROOT/'build/queen-mission/specular-expanded-039';manifest=json.loads((basis/'manifest.json').read_text());specs={v['name']:v for v in manifest['specs']}
lights=[v for v in cfg['lights'] if v.get('diffuse_factor',1)==0 and v['name'] not in cfg.get('disabled_global_reflections',[])];responses=[];initial=[];inputs=[]
confined={v['name']:v for v in cfg['confined_reflections']['lights']}
for light in lights:
 name=light['name'].removeprefix('Display fitted ');spec=specs[name]
 if name=='base-key':path=ROOT/'build/queen-mission/071-limited-base-reflector/diagnostic-limited-reflector.npy'
 elif name in confined:path=ROOT/confined[name].get('response_path','build/queen-mission/072-confined-reflections/diagnostic-'+name+'.npy')
 else:path=basis/(name+'.npy')
 response=np.load(path)[:,:,:3].mean(2)[mask];responses.append(response);initial.append(light['energy']/spec['energy'])
 inputs.append({'name':name,'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'basis_energy':spec['energy']})
X=np.stack(responses,axis=1).astype(np.float64);f=np.array(initial,dtype=np.float64)
reference=ROOT/'build/queen-mission/pigment-fit-039/reference-srgb.npy'
ref=np.load(reference).reshape(418,3,418,3,3).mean((1,3))[mask]
weight=.35+np.clip(ref.min(1)*3,0,1);color=np.array([1,.7,.5])
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
processor=config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
def display(v):
 a=np.asarray(v,dtype=np.float32).copy();processor.applyRGB(a);return a.astype(np.float64)
def loss(f):
 predicted=display(baseline+(X@f)[:,None]*color);return float(np.mean(weight[:,None]*(predicted-ref)**2)),predicted
history=[]
for step in range(30):
 value,predicted=loss(f);amp=X@f;linear=baseline+amp[:,None]*color;epsilon=np.maximum(.0001,amp*.005)
 derivative=(display(linear+epsilon[:,None]*color)-display(np.maximum(linear-epsilon[:,None]*color,0)))/(2*epsilon[:,None])
 norm=(derivative**2).sum(1)*weight;rhs_pixel=((ref-predicted)*derivative).sum(1)*weight+norm*amp
 scale=np.maximum(np.sqrt((X*X*norm[:,None]).sum(0)),1e-6);A=X/scale;gram=A.T@(A*norm[:,None])+np.eye(len(lights))*1e-4;rhs=A.T@rhs_pixel;proposal=f*scale
 for iteration in range(500):
  previous=proposal.copy()
  for i in range(len(lights)):proposal[i]=max(0,proposal[i]+(rhs[i]-gram[i]@proposal)/gram[i,i])
  if np.max(abs(proposal-previous))<1e-6:break
 target=proposal/scale;chosen=f;newvalue=value
 for rate in (1,.5,.25,.125,.0625):
  trial=f+(target-f)*rate;v,_=loss(trial)
  if v<newvalue:chosen=trial;newvalue=v;break
 history.append({'step':step,'loss':value,'accepted_loss':newvalue});f=chosen;print('CONFINED_FIT',history[-1],flush=True)
 if value-newvalue<1e-8:break
for light,factor,record in zip(lights,f,inputs):light['energy']=float(record['basis_energy']*factor)
cfg['variant']=args.variant;cfg['source']=source.relative_to(ROOT).as_posix();cfg['confined_display_fit']={'source_sha256':source_hash,'actual_diffuse_baseline_sha256':hashlib.sha256((out/'diffuse-baseline.npy').read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'basis_inputs':inputs,'history':history,'method':'Nonnegative real-light powers fitted through AgX using the current pigment diffuse pass and confined reflection responses. Requires full render and visual assessment.'}
configure(s,cfg);s['mission_material_config']=json.dumps(cfg,sort_keys=True);s.render.resolution_x=s.render.resolution_y=1254;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('REFITTED_CONFINED_RIG_DONE',flush=True)
